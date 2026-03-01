from pydantic import BaseModel, Field
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

# Meta WhatsApp Webhook Schemas
class WhatsAppText(BaseModel):
    body: str

class WhatsAppInteractiveReply(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None

class WhatsAppInteractive(BaseModel):
    type: str
    button_reply: Optional[WhatsAppInteractiveReply] = None
    list_reply: Optional[WhatsAppInteractiveReply] = None

class WhatsAppStatus(BaseModel):
    id: str
    status: str
    recipient_id: str
    timestamp: str
    errors: Optional[List[dict]] = None

class WhatsAppLocation(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    name: Optional[str] = None

class WhatsAppMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppText] = None
    interactive: Optional[WhatsAppInteractive] = None
    location: Optional[WhatsAppLocation] = None

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[dict]] = None
    messages: Optional[List[WhatsAppMessage]] = None
    statuses: Optional[List[WhatsAppStatus]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]
