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


@router.post("/alerts/incoming")
async def alerts_incoming(payload: AlertIncomingPayload):
    """Lambda (alerts_handler) POSTs here. Store for the Live Alerts page to fetch."""
    user_id = (payload.user_id or "").strip() or "unknown"
    now_iso = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": str(uuid.uuid4()),
        "text": payload.text or "",
        "time": now_iso,
        "alert_type": payload.alert_type or "alert",
        "event_confidence_score": payload.event_confidence_score,
    }
    if user_id not in _ALERTS_BY_USER:
        _ALERTS_BY_USER[user_id] = []
    _ALERTS_BY_USER[user_id].append(entry)
    # Trim to last N
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
