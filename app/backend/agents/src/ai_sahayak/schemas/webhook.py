from pydantic import BaseModel
from typing import Optional, List, Any

class InboundPayload(BaseModel):
    user_id: str
    text: Optional[str] = None
    image: Optional[str] = None  # Base64 encoded
    image_media_type: Optional[str] = None
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
