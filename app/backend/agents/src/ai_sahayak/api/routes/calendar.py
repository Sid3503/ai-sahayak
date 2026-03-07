"""Calendar Events API: dynamic read/write of events (stored in S3)."""
import json
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException

from ai_sahayak.schemas.calendar import (
    CalendarEvent,
    CalendarEventCreate,
    CalendarEventsPayload,
)

router = APIRouter()

S3 = boto3.client("s3")


def _get_bucket_key():
    bucket = os.environ.get("CALENDAR_S3_BUCKET")
    key = os.environ.get("CALENDAR_S3_KEY", "panchang/events.json")
    return bucket, key


def _read_events() -> list[dict]:
    bucket, key = _get_bucket_key()
    if not bucket:
        raise HTTPException(
            status_code=503,
            detail="CALENDAR_S3_BUCKET not configured. Set it in .env to use the calendar API.",
        )
    try:
        resp = S3.get_object(Bucket=bucket, Key=key)
        data = json.loads(resp["Body"].read().decode())
        return data.get("events", [])
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=502, detail=f"Failed to read calendar from S3: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to read calendar from S3: {e}")


def _write_events(events: list[dict]) -> None:
    bucket, key = _get_bucket_key()
    if not bucket:
        raise HTTPException(status_code=503, detail="CALENDAR_S3_BUCKET not configured.")
    body = json.dumps({"events": events}, indent=2)
    try:
        S3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to write calendar to S3: {e}")


@router.get("/calendar/events", response_model=CalendarEventsPayload)
def list_events(city: Optional[str] = None, type_filter: Optional[str] = None):
    """List all calendar events. Optionally filter by city or type (festival/local)."""
    events = _read_events()
    if city:
        events = [e for e in events if e.get("cities") and city in e["cities"]]
    if type_filter:
        events = [e for e in events if e.get("type") == type_filter]
    return CalendarEventsPayload(events=[CalendarEvent(**e) for e in events])


@router.get("/calendar/events/{event_id}", response_model=CalendarEvent)
def get_event(event_id: str):
    """Get a single event by id."""
    events = _read_events()
    for e in events:
        if e.get("id") == event_id:
            return CalendarEvent(**e)
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@router.post("/calendar/events", response_model=CalendarEvent, status_code=201)
def create_event(payload: CalendarEventCreate):
    """Add a new event. Id is optional; generated from name and date if not provided."""
    events = _read_events()
    raw = payload.model_dump(exclude_none=True)
    event_id = raw.get("id") or f"{raw['name'].lower().replace(' ', '-')}-{raw['date']}"
    raw["id"] = event_id
    if any(e.get("id") == event_id for e in events):
        raise HTTPException(status_code=409, detail=f"Event id {event_id} already exists")
    events.append(raw)
    _write_events(events)
    return CalendarEvent(**raw)


@router.put("/calendar/events/{event_id}", response_model=CalendarEvent)
def update_event(event_id: str, payload: CalendarEventCreate):
    """Update an existing event by id."""
    events = _read_events()
    raw = payload.model_dump(exclude_none=True)
    raw["id"] = event_id
    for i, e in enumerate(events):
        if e.get("id") == event_id:
            events[i] = raw
            _write_events(events)
            return CalendarEvent(**raw)
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@router.delete("/calendar/events/{event_id}", status_code=204)
def delete_event(event_id: str):
    """Delete an event by id."""
    events = _read_events()
    new_events = [e for e in events if e.get("id") != event_id]
    if len(new_events) == len(events):
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    _write_events(new_events)
