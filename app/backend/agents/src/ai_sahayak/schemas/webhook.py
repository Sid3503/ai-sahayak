from pydantic import BaseModel
from typing import Optional, List, Any

class InboundPayload(BaseModel):
    user_id: str
    text: Optional[str] = None
    image: Optional[str] = None  # Base64 encoded
    image_media_type: Optional[str] = None
    audio: Optional[str] = None  # Base64 encoded voice message (for Transcribe)
    audio_media_type: Optional[str] = None  # e.g. audio/webm
    session_id: Optional[str] = None
    platform: str = "web"
    phone_number: Optional[str] = None
    metadata: Optional[dict] = None
    callback_url: Optional[str] = None

class OutboundPayload(BaseModel):
    user_id: str
    reply: str
    session_id: str
    metadata: Optional[dict] = None
    platform: str = "web"
    requires_input: bool = True
    suggested_actions: List[str] = []

class WebhookAck(BaseModel):
    status: str
    session_id: Optional[str] = None
    reply: Optional[str] = None
    metadata: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    user_id: Optional[str] = None


# Lambda -> backend: when alerts_handler POSTs to BACKEND_WEBHOOK_URL
class AlertIncomingPayload(BaseModel):
    user_id: str
    phone: Optional[str] = None
    text: str
    platform: str = "whatsapp"
    is_alert: Optional[bool] = True
    alert_type: Optional[str] = None
    event_name: Optional[str] = None
    days_until: Optional[int] = None
    event_confidence_score: Optional[int] = None  # 0-100 from Lambda
