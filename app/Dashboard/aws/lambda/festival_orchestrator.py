import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import boto3

ORCHESTRATOR_VERSION = "2026-03-02.aws-calendar"

REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
API_BASE_URL = os.getenv("AI_SAHAYAK_API_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")
SNS_TOPIC_ARN = os.getenv("AI_SAHAYAK_SNS_TOPIC_ARN", "")
DEFAULT_DAYS = int(os.getenv("AI_SAHAYAK_FORECAST_DAYS", "7"))
DEFAULT_DATASET_KEY = os.getenv("AI_SAHAYAK_DATASET_KEY", "raju").strip() or "raju"
DEFAULT_SKU_LIST = [s.strip() for s in os.getenv("AI_SAHAYAK_SKU_LIST", "").split(",") if s.strip()]
TOP_SKU_LIMIT = max(1, int(os.getenv("AI_SAHAYAK_TOP_SKU_LIMIT", "8")))
HTTP_TIMEOUT_SECS = max(3, int(os.getenv("AI_SAHAYAK_HTTP_TIMEOUT_SECS", "30")))
MAX_RETRIES = max(1, int(os.getenv("AI_SAHAYAK_HTTP_RETRIES", "2")))
CALENDAR_EVENTS_JSON = os.getenv("AI_SAHAYAK_CALENDAR_EVENTS_JSON", "[]")
# Agents backend base URL (e.g. https://your-agents.example.com). Lambda POSTs daily summary to /v1/alerts/incoming so Live Alerts shows it.
BACKEND_ALERTS_URL = (os.getenv("BACKEND_ALERTS_URL") or os.getenv("BACKEND_WEBHOOK_URL") or "").rstrip("/")

sns = boto3.client("sns", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)


def _http_json(method: str, path: str, payload: Optional[Dict[str, Any]] = None, timeout: int = HTTP_TIMEOUT_SECS) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    body = None
    headers = {"Content-Type": "application/json"}
    if "ngrok" in API_BASE_URL.lower():
        headers["ngrok-skip-browser-warning"] = "true"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    last_error = None
    for _ in range(MAX_RETRIES):
        req = urllib.request.Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as exc:
            err_text = exc.read().decode("utf-8", errors="ignore")
            last_error = RuntimeError(f"{method} {path} failed: {exc.code} {err_text}")
        except Exception as exc:
            last_error = exc
    raise RuntimeError(str(last_error) if last_error else f"{method} {path} failed")


def _post_json(path: str, payload: Dict[str, Any], timeout: int = HTTP_TIMEOUT_SECS) -> Dict[str, Any]:
    return _http_json("POST", path, payload=payload, timeout=timeout)


def _get_json(path: str, timeout: int = HTTP_TIMEOUT_SECS) -> Dict[str, Any]:
    return _http_json("GET", path, payload=None, timeout=timeout)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _load_calendar_events() -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(CALENDAR_EVENTS_JSON)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _active_festivals(at_time_iso: str) -> List[Dict[str, Any]]:
    active: List[Dict[str, Any]] = []
    for ev in _load_calendar_events():
        arn = str(ev.get("calendar_arn", "")).strip()
        if not arn:
            continue
        try:
            resp = ssm.get_calendar_state(CalendarNames=[arn], AtTime=at_time_iso)
            if str(resp.get("State", "")).upper() == "CLOSED":
                active.append(ev)
        except Exception as exc:
            active.append({
                "name": ev.get("name", "CalendarError"),
                "boost": ev.get("boost", 1.0),
                "promo_depth_pct": ev.get("promo_depth_pct", 0.0),
                "calendar_arn": arn,
                "calendar_error": str(exc),
            })
    return active


def _discover_skus(dataset_key: str) -> Tuple[List[str], Optional[str]]:
    if DEFAULT_SKU_LIST:
        return DEFAULT_SKU_LIST, None

    try:
        meta = _get_json(f"/meta?dataset_key={dataset_key}")
        skus = meta.get("skus", [])
        if not isinstance(skus, list) or not skus:
            return [], f"No SKUs found in dataset metadata for dataset_key={dataset_key}"
        return [str(row.get("sku_id", "")).strip() for row in skus[:TOP_SKU_LIMIT] if str(row.get("sku_id", "")).strip()], None
    except Exception as exc:
        return [], f"SKU discovery failed via {API_BASE_URL}/meta: {exc}"


def _merge_festival_context(event: Dict[str, Any], active: List[Dict[str, Any]]) -> Dict[str, Any]:
    override_ctx = event.get("festival_context", {}) if isinstance(event, dict) else {}
    active_names = [str(x.get("name", "Festival")) for x in active]
    festival_multiplier = max([_safe_float(x.get("boost", 1.0), 1.0) for x in active], default=1.0)
    promo_depth_pct = max([_safe_float(x.get("promo_depth_pct", 0.0), 0.0) for x in active], default=0.0)

    merged = {
        "active_festivals": override_ctx.get("active_festivals", active_names),
        "festival_multiplier": max(festival_multiplier, _safe_float(override_ctx.get("festival_multiplier", 1.0), 1.0)),
        "promo_depth_pct": max(promo_depth_pct, _safe_float(override_ctx.get("promo_depth_pct", 0.0), 0.0)),
    }
    if event.get("promo_flag") is not None:
        merged["promo_flag"] = int(bool(event.get("promo_flag")))
    elif merged["promo_depth_pct"] > 0:
        merged["promo_flag"] = 1
    return merged


def _build_action(forecast_row: Dict[str, Any]) -> Dict[str, Any]:
    demand_quantiles = forecast_row.get("demand_quantiles", {}) or {}
    selection = forecast_row.get("selection", {}) or {}

    p50 = _safe_float(demand_quantiles.get("p50"), 0.0)
    p90 = _safe_float(demand_quantiles.get("p90"), p50)
    opening_stock = _safe_float(selection.get("opening_stock"), _safe_float(selection.get("stock_on_hand"), 0.0))
    stock_on_hand = _safe_float(selection.get("stock_on_hand"), opening_stock)
    reorder_point = _safe_float(selection.get("reorder_point"), 0.0)
    price_recommended = _safe_float(selection.get("price_recommended"), 0.0)
    current_price = _safe_float(selection.get("price_current"), price_recommended)
    market_price = _safe_float(selection.get("market_price"), current_price)
    promo_depth = _safe_float(selection.get("promo_depth_pct"), 0.0)
    lead_time_days = max(1.0, _safe_float(selection.get("lead_time_days"), 3.0))
    inventory_days_cover = _safe_float(selection.get("inventory_days_cover"), stock_on_hand / max(p50, 1e-9))
    margin_pct = _safe_float(selection.get("margin_pct"), 0.0)
    unit_profit = _safe_float(selection.get("unit_profit_est"), 0.0)
    price_gap_pct = _safe_float(selection.get("price_gap_pct"), 0.0)

    stock_gap = stock_on_hand - p90
    risk_level = "stable"
    actions: List[str] = []

    reorder_qty = max(0.0, p90 * lead_time_days - stock_on_hand)

    if stock_on_hand <= reorder_point or inventory_days_cover < lead_time_days or stock_gap < 0:
        risk_level = "critical"
        actions.append("reorder_now")
    elif stock_gap < max(3.0, p50 * 0.35):
        risk_level = "watch"
        actions.append("prepare_restock")

    if price_recommended > current_price * 1.03 and price_recommended <= market_price * 1.08:
        actions.append("consider_price_uplift")
    elif promo_depth > 0 and stock_on_hand > p90:
        actions.append("run_targeted_promo")
    elif price_gap_pct > 6 and margin_pct > 14:
        actions.append("review_market_gap")
    else:
        actions.append("hold_price")

    if margin_pct < 10:
        actions.append("protect_margin")

    return {
        "date": forecast_row.get("date"),
        "risk_level": risk_level,
        "actions": actions,
        "metrics": {
            "p50_demand": round(p50, 2),
            "p90_demand": round(p90, 2),
            "opening_stock": round(opening_stock, 2),
            "stock_on_hand": round(stock_on_hand, 2),
            "reorder_point": round(reorder_point, 2),
            "stock_gap_vs_p90": round(stock_gap, 2),
            "inventory_days_cover": round(inventory_days_cover, 2),
            "lead_time_days": round(lead_time_days, 2),
            "reorder_qty_suggested": round(reorder_qty, 2),
            "recommended_price": round(price_recommended, 2),
            "current_price": round(current_price, 2),
            "market_price": round(market_price, 2),
            "price_gap_pct": round(price_gap_pct, 2),
            "promo_depth_pct": round(promo_depth, 2),
            "margin_pct": round(margin_pct, 2),
            "unit_profit_est": round(unit_profit, 2),
        },
    }


def _build_summary_line(sku: str, item_name: str, action: Dict[str, Any]) -> str:
    m = action["metrics"]
    action_text = ", ".join(action["actions"])
    return (
        f"{action['date']} | {sku} | {item_name or 'Item'} | risk={action['risk_level']} | "
        f"P50={m['p50_demand']:.1f} | P90={m['p90_demand']:.1f} | stock={m['opening_stock']:.1f} | "
        f"price={m['recommended_price']:.2f} | actions={action_text}"
    )


def _build_hinglish_alert_message(
    dataset_key: str,
    target_date: str,
    decision_rows: List[Dict[str, Any]],
    active_names: List[str],
    festival_multiplier: float,
) -> str:
    """Short Hinglish message for Live Alerts: daily snapshot, low stock, festivals."""
    critical = [r for r in decision_rows if (r.get("action") or {}).get("risk_level") == "critical"]
    watch = [r for r in decision_rows if (r.get("action") or {}).get("risk_level") == "watch"]
    parts = [f"📊 Aaj ka daily summary ({target_date})"]
    if critical:
        names = ", ".join((str(r.get("item_name") or r.get("sku_id", ""))[:20] for r in critical[:3]))
        parts.append(f"⚠️ Low stock / reorder: {names}" + (" …" if len(critical) > 3 else ""))
    if watch:
        parts.append(f"👀 Watch: {len(watch)} SKU restock jaldi karein.")
    if active_names:
        parts.append(f"📅 Festivals: {', '.join(active_names[:3])}" + (f" (multiplier {festival_multiplier:.1f}x)" if festival_multiplier != 1.0 else ""))
    if not (critical or watch or active_names):
        parts.append("Sab stable. Koi urgent action nahi.")
    return "\n".join(parts)


def _post_alert_to_live_alerts(user_id: str, text: str, alert_type: str = "daily_forecast") -> bool:
    """POST to agents backend so Live Alerts (WP UI) shows this message for the user."""
    if not BACKEND_ALERTS_URL or not user_id:
        return False
    url = f"{BACKEND_ALERTS_URL}/v1/alerts/incoming"
    payload = {
        "user_id": user_id.strip().lower(),
        "text": text,
        "alert_type": alert_type,
        "platform": "whatsapp",
        "is_alert": True,
    }
    headers = {"Content-Type": "application/json"}
    if "ngrok" in BACKEND_ALERTS_URL.lower():
        headers["ngrok-skip-browser-warning"] = "true"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            return 200 <= getattr(resp, "status", 0) < 300
    except Exception as exc:
        print(f"[orchestrator] POST alerts/incoming failed: {exc}")
        return False


def run_daily_orchestration(target_date: str, days: int = DEFAULT_DAYS, event: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    event = event or {}
    dataset_key = str(event.get("dataset_key", DEFAULT_DATASET_KEY)).strip() or DEFAULT_DATASET_KEY
    at_time = f"{target_date}T00:00:00Z"
    active = _active_festivals(at_time)
    festival_context = _merge_festival_context(event, active)
    warnings: List[str] = []
    api_reachable = True
    discovered_skus: List[str] = []
    discovery_error: Optional[str] = None
    if event.get("sku_list"):
        discovered_skus = list(event.get("sku_list"))
    else:
        discovered_skus, discovery_error = _discover_skus(dataset_key)
    sku_list = discovered_skus
    if discovery_error:
        api_reachable = False
        warnings.append(discovery_error)
    if "YOUR_REAL_BACKEND" in API_BASE_URL:
        api_reachable = False
        warnings.append("AI_SAHAYAK_API_BASE_URL is still a placeholder. Replace it with a real deployed backend URL.")
    if not sku_list:
        warnings.append("No SKUs available for orchestration. Lambda could not generate forecast decisions.")

    summary_lines: List[str] = []
    decision_rows: List[Dict[str, Any]] = []

    for sku in sku_list:
        payload = {
            "dataset_key": dataset_key,
            "sku_id": sku,
            "start_date": target_date,
            "days": days,
            "festival_context": festival_context,
        }
        resp = _post_json("/forecast", payload)
        forecast = resp.get("forecast", []) if isinstance(resp, dict) else []
        if not forecast:
            continue
        first_row = forecast[0]
        action = _build_action(first_row)
        item_name = str((first_row.get("selection", {}) or {}).get("item_name", ""))
        summary_lines.append(_build_summary_line(sku, item_name, action))
        decision_rows.append({
            "sku_id": sku,
            "item_name": item_name,
            "forecast": first_row,
            "action": action,
        })

    active_names = festival_context.get("active_festivals", [])
    message = (
        "AI Sahayak Daily Smart Forecast\n\n"
        f"Dataset: {dataset_key}\n"
        f"Date: {target_date}\n"
        f"Active Festivals: {', '.join(active_names) if active_names else 'None'}\n"
        f"Festival Multiplier: {_safe_float(festival_context.get('festival_multiplier', 1.0), 1.0):.2f}\n"
        f"Promo Depth: {_safe_float(festival_context.get('promo_depth_pct', 0.0), 0.0):.1f}%\n\n"
        + ("\n".join(summary_lines) if summary_lines else "No SKU decisions generated.")
    )

    if SNS_TOPIC_ARN:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject="AI Sahayak Daily Forecast", Message=message)

    # Push to Live Alerts (WP-style chat) so the retailer sees daily summary, low stock, festivals
    alerts_pushed = False
    if BACKEND_ALERTS_URL and summary_lines:
        short_msg = _build_hinglish_alert_message(
            dataset_key, target_date, decision_rows, active_names,
            _safe_float(festival_context.get("festival_multiplier", 1.0), 1.0),
        )
        alerts_pushed = _post_alert_to_live_alerts(dataset_key, short_msg, "daily_forecast")

    return {
        "ok": True,
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "alerts_pushed_to_live": alerts_pushed,
        "region": REGION,
        "api_base_url": API_BASE_URL,
        "api_reachable": api_reachable,
        "dataset_key": dataset_key,
        "target_date": target_date,
        "active_festivals": active_names,
        "festival_multiplier": _safe_float(festival_context.get("festival_multiplier", 1.0), 1.0),
        "promo_depth_pct": _safe_float(festival_context.get("promo_depth_pct", 0.0), 0.0),
        "skus": sku_list,
        "summary_count": len(summary_lines),
        "summary": summary_lines,
        "decisions": decision_rows,
        "warnings": warnings,
        "sns_published": bool(SNS_TOPIC_ARN),
    }


# When run_all_retailers is true (or dataset_keys list is passed), run for all 5 retailers in one invocation.
ALL_RETAILER_KEYS = ["raju", "ramesh", "suresh", "kanta", "lakshmi"]


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    if not isinstance(event, dict):
        event = {}

    start_date = str(event.get("start_date", "")).strip()
    if not start_date:
        start_date = (today + timedelta(days=1)).isoformat()
    days = max(1, min(int(event.get("days", DEFAULT_DAYS)), 90))

    # Optional: run for multiple retailers in one invocation (e.g. EventBridge daily trigger for all 5).
    dataset_keys = event.get("dataset_keys")
    if event.get("run_all_retailers") is True and not dataset_keys:
        dataset_keys = ALL_RETAILER_KEYS
    if isinstance(dataset_keys, list) and len(dataset_keys) > 1:
        results_per_key = []
        for dk in dataset_keys:
            dk = str(dk).strip().lower()
            if not dk:
                continue
            try:
                r = run_daily_orchestration(target_date=start_date, days=days, event={**event, "dataset_key": dk})
                results_per_key.append({
                    "dataset_key": dk,
                    "ok": r.get("ok", True),
                    "summary_count": r.get("summary_count", 0),
                    "alerts_pushed_to_live": r.get("alerts_pushed_to_live", False),
                })
            except Exception as exc:
                results_per_key.append({"dataset_key": dk, "ok": False, "error": str(exc)})
        return {
            "statusCode": 200,
            "body": json.dumps({
                "ok": True,
                "orchestrator_version": ORCHESTRATOR_VERSION,
                "target_date": start_date,
                "days": days,
                "retailers_run": len(results_per_key),
                "per_retailer": results_per_key,
            }),
        }

    try:
        result = run_daily_orchestration(target_date=start_date, days=days, event=event)
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as exc:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "ok": False,
                "orchestrator_version": ORCHESTRATOR_VERSION,
                "error": str(exc),
                "region": REGION,
                "dataset_key": str(event.get("dataset_key", DEFAULT_DATASET_KEY)),
                "target_date": start_date,
            }),
        }
