from typing import Annotated, List, TypedDict, Union
from langchain_core.messages import BaseMessage
from ai_sahayak.graphs.state.user_context import UserContext

def merge_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]:
    return left + right

class ConversationState(TypedDict):
    messages: Annotated[List[BaseMessage], merge_messages]
    user_context: UserContext
    next_node: str
    confidence: float
    is_complete: bool
    current_step: str  # E.g., 'wait_for_hi', 'onboarding', 'completed'
    onboarding_data: dict  # To store Name, Store, Location fields
    next_intent: str
