"""
EventBridge-triggered Lambda: reads calendar from S3, finds upcoming events,
and POSTs them to the backend webhook so the dashboard can show alerts (e.g. Holi in 10 days).

Daily-at-fixed-time (set from chat): User says "9 baje bhejo" in Live Alerts; backend saves
alert_time_hour_ist to DynamoDB (user_preferences_dynamodb). To respect it:
- Create an EventBridge rule that runs every hour (e.g. cron(0 0/1 * * ? *) for hourly).
- In this Lambda (or a separate daily-summary Lambda), read USERS_TABLE and filter users
  where alert_time_hour_ist == current_ist_hour; for each, POST to BACKEND_WEBHOOK_URL
  with user_id and daily summary text so Live Alerts shows it for that customer.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta
from typing import Any

import boto3

S3 = boto3.client("s3")


def get_calendar_events(bucket: str, key: str) -> list[dict[str, Any]]:
    """Load calendar JSON from S3."""
    resp = S3.get_object(Bucket=bucket, Key=key)
    data = json.loads(resp["Body"].read())
    return data.get("events", [])


def days_until(date_str: str, today: datetime) -> int:
    """Days until the given date (YYYY-MM-DD)."""
    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (event_date - today.date()).days


def handler(event: dict, context: object) -> dict:
    bucket = os.environ.get("CALENDAR_BUCKET")
    key = os.environ.get("CALENDAR_KEY", "panchang/events.json")
    webhook_url = os.environ.get("BACKEND_WEBHOOK_URL")

    if not bucket:
        return {"statusCode": 400, "body": "CALENDAR_BUCKET not set"}
    if not webhook_url:
        return {"statusCode": 200, "body": "BACKEND_WEBHOOK_URL not set; skipping webhook"}

    # Use IST for "today" (UTC+5:30)
    now_utc = datetime.utcnow()
    today_ist = now_utc + timedelta(hours=5, minutes=30)
    events = get_calendar_events(bucket, key)
    alerts_sent = 0

    for ev in events:
        date_str = ev.get("date")
        if not date_str:
            continue
        d = days_until(date_str, today_ist)
        # Alert when event is in 1, 3, 7, 14, or 30 days (or use event.days_advance_alert if present)
        advance = ev.get("days_advance_alert", [1, 3, 7, 14, 30])
        if d not in advance or d < 0:
            continue
        payload = {
            "event_id": ev.get("id"),
            "name": ev.get("name"),
            "type": ev.get("type", "festival"),
            "date": date_str,
            "days_until_event": d,
            "regions": ev.get("regions", []),
            "cities": ev.get("cities", []),
            "notes": ev.get("notes", ""),
        }
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                if 200 <= r.status < 300:
                    alerts_sent += 1
        except Exception as e:
            print(f"Webhook failed for {ev.get('id')}: {e}")

    return {"statusCode": 200, "body": json.dumps({"alerts_sent": alerts_sent})}
