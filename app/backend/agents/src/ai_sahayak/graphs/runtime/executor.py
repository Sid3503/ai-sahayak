from ai_sahayak.graphs.workflows.retail_assistant import graph
from ai_sahayak.graphs.state.conversation import ConversationState

async def run_retail_assistant(state: ConversationState):
    return await graph.ainvoke(state)
