from pydantic import BaseModel
from typing import Optional, Any, List
from enum import Enum

class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    WEB = "web"
    SYSTEM = "system"

class AgentRequest(BaseModel):
    message: str
    session_id: str
    channel: Channel
    user_id: str
    store_id: Optional[str] = None
    metadata: dict = {}

class AgentResponse(BaseModel):
    message: str
    session_id: str
    suggestions: List[str] = []
    metadata: dict = {}
