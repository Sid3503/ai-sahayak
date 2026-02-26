import asyncio
from ai_sahayak.graphs.workflows.retail_assistant import graph
from ai_sahayak.memory.conversation import get_conversation_state
from langchain_core.messages import HumanMessage

async def main():
    print("Testing Retail Assistant Graph (Onboarding Phase 1)\n---")
    
    session_id = "test_onboarding_001"
    state = await get_conversation_state(session_id)
    
    # Simulate a user saying hi
    user_input = "Hi Sahayak"
    print(f"User: {user_input}")
    
    state["messages"].append(HumanMessage(content=user_input))
    
    # Run graph
    result = await graph.ainvoke(state)
    
    print(f"AI: {result['messages'][-1].content}")
    print(f"Current Step: {result['current_step']}")

if __name__ == "__main__":
    asyncio.run(main())
