from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    session_id: str
    store_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    suggestions: List[str] = []
