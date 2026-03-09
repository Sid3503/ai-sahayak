"""
Forecast workflow: fetches real forecast from Dashboard /api/forecast when possible;
otherwise uses Bedrock KB + dashboard context.
"""
import json
import os
import urllib.request
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.bedrock_knowledge_base import retrieve_from_panchang_kb
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data

DASHBOARD_API_BASE = (os.getenv("DASHBOARD_API_BASE_URL") or os.getenv("AI_SAHAYAK_DASHBOARD_API") or "http://127.0.0.1:8001").rstrip("/")


def _fetch_forecast_from_dashboard(dataset_key: str, sku_id: str = "") -> dict:
    """POST /api/forecast; returns { assistant_message, forecast, ... } or {} on failure."""
    try:
        url = f"{DASHBOARD_API_BASE}/api/forecast"
        body = {"dataset_key": dataset_key, "days": 14}
        if sku_id:
            body["sku_id"] = sku_id
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except Exception as e:
        print(f"[forecast_query_node] /api/forecast failed: {e}")
        return {}


async def forecast_query_node(state: ConversationState):
    """Answer forecast queries using real Dashboard /api/forecast + KB + dashboard context."""
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else "What is the demand forecast?"
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "unknown_user").strip().lower()
    if user_id in ("unknown_user", "demo", "web_demo"):
        user_id = "raju"
    onboarding_data = state.get("onboarding_data", {})

    kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
        dashboard = get_dashboard_data(user_id)
    
    # Fetch real forecast from Dashboard when available
    import asyncio
    forecast_res = await asyncio.to_thread(_fetch_forecast_from_dashboard, user_id, "")
    forecast_summary = (forecast_res.get("assistant_message") or "").strip() if forecast_res else ""

    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    if preferred_lang in ["english", "en"]:
        lang_instruction = "Reply in English. Max 2-3 sentences. No bullets."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi only, Devanagari script. Max 2-3 sentences."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = "Reply ONLY in Hinglish (Hindi + English Roman). Max 2-3 short sentences. No bullets or markdown."
    else:
        lang_instruction = "Reply in English. Max 2-3 sentences."

    system_prompt = """You are AI Sahayak, helping an Indian Kirana store owner with demand forecasting and seasonal/festival trends.
{lang_instruction}

## User Profile:
{user_profile}

## Knowledge Base (festivals / Panchang / seasonal):
{kb_context}

## Store context (from Dashboard):
{store_context}

## Real forecast from Dashboard (if available — use this for numbers and risk):
{forecast_from_dashboard}

Use ONLY the data above (Dashboard forecast + store context — do not invent). If real forecast is given, put key numbers in a **markdown table** (Metric | Value) and add 1 short sentence. If not, use KB and store context only. Simple, easy-to-understand language — like a local friend. No long paragraphs, no fancy AI English. Tables or bold labels for data."""

    user_profile = ""
    if onboarding_data:
        if onboarding_data.get("name"):
            user_profile += f"Owner: {onboarding_data['name']}. "
        if onboarding_data.get("store_name"):
            user_profile += f"Store: {onboarding_data['store_name']}. "
        if onboarding_data.get("resolved_location") or onboarding_data.get("location"):
            user_profile += f"Location: {onboarding_data.get('resolved_location') or onboarding_data.get('location')}. "
    if not user_profile:
        user_profile = "No user profile available."

    store_context = ""
    if dashboard.get("from_dashboard") and dashboard:
        store_info = dashboard.get("store_info", {})
        sales = dashboard.get("sales_summary", {})
        inv = dashboard.get("inventory_summary", {})
        if store_info:
            store_context += f"Store: {store_info.get('name', '')}, {store_info.get('city', '')}. "
        if sales:
            store_context += f"Sales last month: ₹{sales.get('last_month', 0):,.0f}; top items: {sales.get('top_items', [])}. "
        if inv:
            store_context += f"Low stock: {inv.get('low_stock', [])}. "
    if not store_context:
        store_context = "Dashboard not connected. No real store data."

    forecast_from_dashboard = forecast_summary if forecast_summary else "(Run forecast on Dashboard to get real demand band and risk radar.)"

    try:
        llm = get_llm(temperature=0.5)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
                lang_instruction=lang_instruction,
                user_profile=user_profile,
                kb_context=kb_context or "(No KB results.)",
                store_context=store_context,
                forecast_from_dashboard=forecast_from_dashboard,
            )),
            *[m for m in messages if hasattr(m, "content")][-3:],
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"Forecast node error: {e}")
        reply = "Forecast abhi load nahi ho paya. Dashboard pe Insights > Run forecast karein, phir poochhen." if preferred_lang in ["hinglish"] else "Forecast not available. Run forecast on Dashboard first, then ask again."

    return {"messages": [AIMessage(content=reply)]}
