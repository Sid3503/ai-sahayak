from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState

async def sales_query_node(state: ConversationState):
    """Mock node for handling sales queries."""
    response = "📈 [SALES WORKFLOW] I can help you analyze your past sales and total revenue. (Mock Response)"
    return {"messages": [AIMessage(content=response)]}
