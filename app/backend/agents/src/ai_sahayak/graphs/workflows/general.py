from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState

async def general_chat_node(state: ConversationState):
    """Mock node for handling general queries."""
    response = "🗣️ [GENERAL WORKFLOW] I can help you with store operations, advice, or general chat. (Mock Response)"
    return {"messages": [AIMessage(content=response)]}
