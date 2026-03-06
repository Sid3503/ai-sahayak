import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import boto3
import requests

REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
API_BASE_URL = os.getenv("AI_SAHAYAK_API_BASE_URL", "http://your-api-domain/api")
SNS_TOPIC_ARN = os.getenv("AI_SAHAYAK_SNS_TOPIC_ARN", "")
STORE_CHANNEL = os.getenv("AI_SAHAYAK_CHANNEL", "GT")
STORE_REGION = os.getenv("AI_SAHAYAK_REGION", "West")
DEFAULT_DAYS = int(os.getenv("AI_SAHAYAK_FORECAST_DAYS", "7"))
SKU_LIST = [s.strip() for s in os.getenv("AI_SAHAYAK_SKU_LIST", "KR001,KR007,KR016").split(",") if s.strip()]
CALENDAR_EVENTS_JSON = os.getenv(
    "AI_SAHAYAK_CALENDAR_EVENTS_JSON",
    '[{"name":"Holi","calendar_arn":"arn:aws:ssm:ap-south-1:YOUR_ACCOUNT_ID:document/HoliCalendar","boost":1.85,"promo_depth_pct":14}]'
)

sns = boto3.client("sns", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)


def _post_json(path: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    url = f"{API_BASE_URL.rstrip('/')}{path}"
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _get_meta() -> Dict[str, Any]:
    url = f"{API_BASE_URL.rstrip('/')}/meta"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def _build_alert_lines(sku: str, fc_row: Dict[str, Any]) -> str:
    dq = fc_row.get("demand_quantiles", {})
    sel = fc_row.get("selection", {})
    date = fc_row.get("date")
    p50 = float(dq.get("p50", 0))
    p90 = float(dq.get("p90", 0))
    rec_price = float(sel.get("price_recommended", 0))
    return f"{date}: {sku} -> P50={p50:.1f}, P90={p90:.1f}, Recommended Price=INR {rec_price:.2f}"


def _load_calendar_events() -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(CALENDAR_EVENTS_JSON)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return []


def _active_festivals(at_time_iso: str) -> List[Dict[str, Any]]:
    active: List[Dict[str, Any]] = []
    for ev in _load_calendar_events():
        arn = ev.get("calendar_arn")
        if not arn:
            continue
        resp = ssm.get_calendar_state(CalendarNames=[arn], AtTime=at_time_iso)
        # For change calendars, OPEN usually means no event. CLOSED means event/blackout window active.
        if str(resp.get("State", "")).upper() == "CLOSED":
            active.append(ev)
    return active


def run_daily_orchestration(target_date: str, days: int = DEFAULT_DAYS) -> Dict[str, Any]:
    summary: List[str] = []
    at_time = f"{target_date}T00:00:00Z"
    active = _active_festivals(at_time)
    max_promo = max([float(x.get("promo_depth_pct", 0)) for x in active], default=0.0)
    festival_multiplier = max([float(x.get("boost", 1.0)) for x in active], default=1.0)
    active_names = [str(x.get("name", "Festival")) for x in active]

    for sku in SKU_LIST:
        payload = {
            "sku_id": sku,
            "channel": STORE_CHANNEL,
            "region": STORE_REGION,
            "start_date": target_date,
            "days": days,
            "festival_context": {
                "active_festivals": active_names,
                "festival_multiplier": festival_multiplier,
                "promo_depth_pct": max_promo,
            },
        }
        resp = _post_json("/forecast", payload)
        forecast = resp.get("forecast", []) if isinstance(resp, dict) else []
        if forecast:
            summary.append(_build_alert_lines(sku, forecast[0]))

    message = (
        "AI Sahayak Daily Festival Forecast\n\n"
        f"Date: {target_date}\n"
        f"Active Festivals: {', '.join(active_names) if active_names else 'None'}\n"
        f"Festival Multiplier: {festival_multiplier:.2f}\n\n"
        + "\n".join(summary)
    )
    if SNS_TOPIC_ARN:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject="AI Sahayak Daily Forecast", Message=message)

    return {
        "ok": True,
        "region": REGION,
        "target_date": target_date,
        "active_festivals": active_names,
        "festival_multiplier": festival_multiplier,
        "promo_depth_pct": max_promo,
        "skus": SKU_LIST,
        "summary_count": len(summary),
        "summary": summary,
        "sns_published": bool(SNS_TOPIC_ARN),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Supports EventBridge scheduler input override:
    # {"start_date":"2026-03-01", "days": 14}
    today = datetime.now(timezone.utc).date()
    start_date = event.get("start_date") if isinstance(event, dict) else None
    if not start_date:
        start_date = (today + timedelta(days=1)).isoformat()
    days = int(event.get("days", DEFAULT_DAYS)) if isinstance(event, dict) else DEFAULT_DAYS

    try:
        result = run_daily_orchestration(target_date=start_date, days=days)
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e), "region": REGION}),
        }
