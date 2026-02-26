from typing import TypedDict, Optional

class UserContext(TypedDict):
    store_id: str
    language: str
    region: str
    channel: str
    owner_name: Optional[str]
    target_language: Optional[str]
    requires_translation: Optional[bool]
    original_content: Optional[str]
