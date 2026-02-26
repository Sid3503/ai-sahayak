from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState

async def pricing_query_node(state: ConversationState):
    """Mock node for handling pricing queries."""
    response = "💰 [PRICING WORKFLOW] Let's analyze competitor prices and your profit margins. (Mock Response)"
    return {"messages": [AIMessage(content=response)]}
