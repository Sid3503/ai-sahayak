"""
Pricing and review: fetch real data from the Dashboard (Flask) API.
Returns the same price recommendation and explanation the dashboard shows.
Drive UI: dashboard switches to Price/Review tab and selects SKU when user asks for a product (e.g. sugar).
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional
from langchain_core.messages import AIMessage, HumanMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.dashboard_drive_ui import notify_dashboard_drive_ui

DASHBOARD_API_BASE = (
    os.getenv("DASHBOARD_API_BASE_URL") or os.getenv("AI_SAHAYAK_DASHBOARD_API") or "http://127.0.0.1:8001"
).rstrip("/")


def _fetch_price_from_dashboard(dataset_key: str, sku_id: Optional[str] = None) -> Optional[dict]:
    """Call Dashboard POST /api/price; returns parsed JSON or None on failure."""
    url = f"{DASHBOARD_API_BASE}/api/price"
    body = {"dataset_key": dataset_key}
    if sku_id:
        body["sku_id"] = sku_id
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else ""
        try:
            err_body = json.loads(raw) if raw else {}
            if err_body.get("assistant_source") == "bedrock_error":
                return {"ok": False, "error": "bedrock", "bedrock_status": err_body.get("bedrock_status")}
        except Exception:
            pass
        print(f"[pricing_query_node] Dashboard /api/price HTTP {e.code}: {raw[:200]}")
        return None
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"[pricing_query_node] Dashboard /api/price failed: {e}")
        return None


def _resolve_sku_from_message(message_text: str, skus: list) -> Optional[str]:
    """If user said e.g. 'sugar' or 'atta', return the matching sku_id from the list. skus = [{sku_id, item_name}, ...]."""
    if not message_text or not skus:
        return None
    text = (message_text or "").strip().lower()
    # Extract likely product words (skip common words)
    stop = {"ka", "ki", "ke", "ko", "batao", "chahiye", "review", "price", "recommendation", "kya", "kitna", "mein", "the", "for", "run"}
    words = [w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in stop]
    for s in skus:
        item = (s.get("item_name") or "").strip().lower()
        sid = (s.get("sku_id") or "").strip()
        if not item or not sid:
            continue
        for w in words:
            if w in item:
                return sid
        if any(w in item for w in words):
            return sid
    return None


def _fetch_meta_from_dashboard(dataset_key: str) -> Optional[dict]:
    """Call Dashboard GET /api/meta to get first SKU etc."""
    try:
        url = f"{DASHBOARD_API_BASE}/api/meta?dataset_key={urllib.parse.quote(dataset_key)}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except Exception as e:
        print(f"[pricing_query_node] Dashboard /api/meta failed: {e}")
        return None


async def pricing_query_node(state: ConversationState):
    """
    Call Dashboard /api/price for the current retailer and return the real
    price recommendation and explanation (same as Overview / Price tab).
    Handles both "price recommendation" and "last price run review" intents.
    If user mentions a product (e.g. sugar, atta), we resolve SKU and drive dashboard to that SKU.
    """
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "raju").strip().lower()
    if user_id in ("unknown_user", "demo", "web_demo"):
        user_id = "raju"

    messages = state.get("messages") or []
    last_user_text = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage) and hasattr(m, "content"):
            last_user_text = (m.content or "").strip()
            break

    meta = _fetch_meta_from_dashboard(user_id)
    first_sku = None
    if meta and meta.get("skus"):
        # If user said e.g. "sugar" or "atta", select that SKU so dashboard shows it
        first_sku = _resolve_sku_from_message(last_user_text, meta["skus"])
        if not first_sku:
            first_sku = meta["skus"][0].get("sku_id")

    # Fetch real price run from dashboard (uses Bedrock for explanation when available)
    import asyncio
    result = await asyncio.to_thread(_fetch_price_from_dashboard, user_id, first_sku)

    if not result:
        return {
            "messages": [
                AIMessage(
                    content="Dashboard price engine abhi reach nahi ho pa raha. Thodi der baad try karein ya Dashboard pe Price tab se direct run karein."
                )
            ]
        }

    if result.get("ok") is False or result.get("error"):
        err = result.get("error", "Unknown error")
        if "bedrock" in err.lower():
            return {
                "messages": [
                    AIMessage(
                        content="Price explanation ke liye Bedrock abhi ready nahi hai. Dashboard pe Price tab try karein; wahan short summary milegi."
                    )
                ]
            }
        return {
            "messages": [
                AIMessage(content=f"Price run mein issue aaya: {err[:200]}. Dashboard se dobara try karein.")
            ]
        }

    # Prefer short, readable reply for chat (Hinglish). If dashboard returned long formal English, build a brief one-liner.
    raw_short = (result.get("assistant_message") or result.get("assistant_detail") or "").strip()
    selection = result.get("selection") or {}
    item = result.get("item_name") or selection.get("item_name", "SKU")
    rec = selection.get("price_recommended") or selection.get("recommended_price") or selection.get("price")
    margin = selection.get("margin_pct")
    market = selection.get("market_price")

    if not raw_short or len(raw_short) > 380 or "Executive Summary" in raw_short or "Key Numbers" in raw_short:
        # Build short Hinglish one-liner like the Wheat Atta response
        rec_val = float(rec) if rec is not None else None
        parts = [f"{item} ke liye engine recommend karta hai ₹{rec_val:.2f}" if rec_val is not None else f"{item} ke liye price run ho chuka."]
        if margin is not None:
            parts.append(f"margin ~{float(margin):.1f}%")
        if market is not None:
            parts.append(f"market around ₹{float(market):.2f}")
        short_text = ". ".join(parts) + ". Detail ke liye Dashboard > Price tab dekhein."
    else:
        short_text = raw_short

    # Drive dashboard: price vs review from user message; include sku_id and dataset_key so dashboard selects the right SKU
    drive_action = "review" if "review" in last_user_text.lower() else "price"
    drive_payload = {**result, "dataset_key": user_id, "sku_id": first_sku or result.get("sku_id")}
    notify_dashboard_drive_ui(drive_action, drive_payload)

    return {"messages": [AIMessage(content=short_text)]}
