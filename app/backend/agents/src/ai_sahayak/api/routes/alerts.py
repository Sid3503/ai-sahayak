"""
Receive alerts from Lambda (BACKEND_WEBHOOK_URL) and serve them to the Live Alerts UI.
Lambda POSTs here; frontend polls GET /v1/alerts/for-user to show alerts in the WP-style chat.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query

from ai_sahayak.schemas.webhook import AlertIncomingPayload

router = APIRouter()

# In-memory store: user_id -> list of { id, text, time_iso, alert_type }
# user_id must match frontend retailer key (raju, ramesh, suresh, kanta, lakshmi) so My day shows the right alerts.
# For production, replace with DynamoDB. Keeps last 100 per user.
_ALERTS_BY_USER: dict[str, list[dict]] = {}
_MAX_ALERTS_PER_USER = 100
# Dedupe: don't store the same alert text for the same user within the last N alerts (avoids duplicates from multiple Lambda runs or tests).
_DEDUPE_LOOKBACK = 15


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


@router.post("/alerts/incoming")
async def alerts_incoming(payload: AlertIncomingPayload):
    """Lambda (alerts_handler) POSTs here. Store for the Live Alerts page to fetch. Duplicates (same text recently) are skipped."""
    user_id = (payload.user_id or "").strip() or "unknown"
    text = payload.text or ""
    text_norm = _normalize_text(text)
    if user_id not in _ALERTS_BY_USER:
        _ALERTS_BY_USER[user_id] = []
    recent = _ALERTS_BY_USER[user_id][-_DEDUPE_LOOKBACK:]
    if any(_normalize_text(a.get("text", "")) == text_norm for a in recent):
        return {"ok": True, "id": None, "duplicate": True}
    now_iso = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": str(uuid.uuid4()),
        "text": text,
        "time": now_iso,
        "alert_type": payload.alert_type or "alert",
        "event_confidence_score": payload.event_confidence_score,
    }
    _ALERTS_BY_USER[user_id].append(entry)
    _ALERTS_BY_USER[user_id] = _ALERTS_BY_USER[user_id][-_MAX_ALERTS_PER_USER:]
    return {"ok": True, "id": entry["id"]}


@router.get("/alerts/for-user")
async def get_alerts_for_user(user_id: str = Query(..., description="Retailer key: raju, ramesh, suresh, kanta, lakshmi (same as My day user_id)")):
    """Live Alerts page polls this to show Lambda-sent alerts in the WP UI."""
    user_id = (user_id or "").strip().lower() or "raju"
    alerts = _ALERTS_BY_USER.get(user_id, [])
    # Return newest first for display (frontend can append in order)
    out = list(reversed(alerts[-50:]))
    return {"alerts": out}
