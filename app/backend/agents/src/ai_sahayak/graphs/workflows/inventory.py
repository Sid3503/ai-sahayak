from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState

async def inventory_query_node(state: ConversationState):
    """Mock node for handling inventory queries."""
    response = "📦 [INVENTORY WORKFLOW] Here is your current stock availability. (Mock Response)"
    return {"messages": [AIMessage(content=response)]}
