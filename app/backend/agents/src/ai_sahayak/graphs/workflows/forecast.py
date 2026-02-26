from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState

async def forecast_query_node(state: ConversationState):
    """Mock node for handling forecast queries."""
    response = "🔮 [FORECAST WORKFLOW] Based on seasonal trends, expect higher demand next month. (Mock Response)"
    return {"messages": [AIMessage(content=response)]}
