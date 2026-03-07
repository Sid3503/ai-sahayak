"""Pydantic models for Calendar Events API (dynamic events.json)."""
from typing import Optional

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    id: str
    name: str
    type: str = "festival"
    date: str
    regions: list[str] = Field(default_factory=lambda: ["IN"])
    days_advance_alert: list[int] = Field(default_factory=lambda: [30, 14, 7, 3, 1])
    cities: Optional[list[str]] = None
    notes: Optional[str] = None


class CalendarEventsPayload(BaseModel):
    events: list[CalendarEvent]


class CalendarEventCreate(BaseModel):
    id: Optional[str] = None
    name: str
    type: str = "festival"
    date: str
    regions: list[str] = Field(default_factory=lambda: ["IN"])
    days_advance_alert: list[int] = Field(default_factory=lambda: [30, 14, 7, 3, 1])
    cities: Optional[list[str]] = None
    notes: Optional[str] = None
