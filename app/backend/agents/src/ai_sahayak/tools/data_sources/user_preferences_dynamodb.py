"""
Update user alert preferences in DynamoDB.
Uses ALERT_USERS_TABLE (same table the alerts Lambda reads: ai-sahayak-users) so
chat-updated times are used by Lambda. Onboarding/profile stay in USERS_TABLE (ai_sahayak_user_info).
"""
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from ai_sahayak.config.settings import settings

_USERS_TABLE = os.environ.get("USERS_TABLE", settings.USERS_TABLE)
# Table Lambda reads for alert_time_hour_ist, alert_days_before (the 5 retailers: raju, ramesh, etc.)
_ALERT_USERS_TABLE = os.environ.get("ALERT_USERS_TABLE", "").strip() or _USERS_TABLE
_REGION = os.environ.get("AWS_REGION", settings.AWS_REGION)
_alert_table = None


def _get_alert_table():
    global _alert_table
    if _alert_table is None:
        _alert_table = boto3.resource("dynamodb", region_name=_REGION).Table(_ALERT_USERS_TABLE)
        # So we write to same table Lambda reads (raju, ramesh, etc. get alert_time_* in ai-sahayak-users)
        print(f"[Alert prefs] Using table: {_ALERT_USERS_TABLE}", flush=True)
    return _alert_table


def update_alert_preferences(
    user_id: str,
    alert_days_before: Optional[int] = None,
    alert_time_hour_ist: Optional[int] = None,
    alert_time_minute_ist: Optional[int] = None,
    phone: Optional[str] = None,
) -> bool:
    """
    Update alert_days_before and/or alert_time_hour_ist and/or alert_time_minute_ist for the user in DynamoDB.
    Lambda reads these for per-user alert window and time (hour + optional minute 0 or 30).
    Returns True if update succeeded.
    """
    if not user_id or user_id == "unknown_user":
        return False
    updates = []
    expr_names = {}
    expr_values = {}
    if alert_days_before is not None:
        if not (1 <= alert_days_before <= 30):
            return False
        updates.append("#d = :d")
        expr_names["#d"] = "alert_days_before"
        expr_values[":d"] = alert_days_before
    if alert_time_hour_ist is not None:
        if not (0 <= alert_time_hour_ist <= 23):
            return False
        updates.append("#h = :h")
        expr_names["#h"] = "alert_time_hour_ist"
        expr_values[":h"] = alert_time_hour_ist
    if alert_time_minute_ist is not None:
        if alert_time_minute_ist not in (0, 30):
            return False
        updates.append("#m = :m")
        expr_names["#m"] = "alert_time_minute_ist"
        expr_values[":m"] = alert_time_minute_ist
    if phone is not None:
        updates.append("#p = :p")
        expr_names["#p"] = "phone"
        expr_values[":p"] = str(phone)[:20]
    if not updates:
        return True
    try:
        table = _get_alert_table()
        update_expr = "SET " + ", ".join(updates)
        params = {
            "Key": {"user_id": user_id},
            "UpdateExpression": update_expr,
            "ExpressionAttributeValues": expr_values,
        }
        if expr_names:
            params["ExpressionAttributeNames"] = expr_names
        table.update_item(**params)
        return True
    except ClientError as e:
        # Table may not exist in dev; log and continue
        print(f"DynamoDB update_alert_preferences failed: {e}")
        return False
