from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.prompts.registry import PromptRegistry
from ai_sahayak.tools.data_sources.mongodb_tool import MongoDBTool
from ai_sahayak.graphs.nodes.router.intent_router import classify_intent_node
from ai_sahayak.graphs.workflows.sales import sales_query_node
from ai_sahayak.graphs.workflows.pricing import pricing_query_node
from ai_sahayak.graphs.workflows.inventory import inventory_query_node
from ai_sahayak.graphs.workflows.forecast import forecast_query_node
from ai_sahayak.graphs.workflows.general import general_chat_node
from ai_sahayak.graphs.nodes.router.language_router import language_detection_node
import os
import json
import re

# Initialize Prompt Registry
prompt_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts", "system")
registry = PromptRegistry(prompt_dir)

async def onboarding_node(state: ConversationState):
    """Handles the onboarding flow by asking questions sequentially."""
    llm = get_llm(temperature=0.3)
    
    # Load prompt and format with current data
    prompt_data = registry.load_prompt("onboarding_agent")
    system_template = prompt_data.get("system_prompt", "")
    
    onboarding_data = state.get("onboarding_data", {})
    system_content = system_template.replace("{name}", onboarding_data.get("name", "Not provided"))\
                                    .replace("{store_name}", onboarding_data.get("store_name", "Not provided"))\
                                    .replace("{location}", onboarding_data.get("location", "Not provided"))\
                                    .replace("{aadhar}", onboarding_data.get("aadhar", "Not provided"))\
                                    .replace("{ledger}", onboarding_data.get("ledger", "Not provided"))
    
    messages = [SystemMessage(content=system_content)] + state["messages"]
    
    # Invoke the LLM
    response = llm.invoke(messages)
    
    # Check if onboarding is complete (Look for JSON)
    if "ONBOARDING_COMPLETE" in response.content:
        new_step = "completed"
        final_message = "🎉 Welcome to AI Sahayak! Your store is successfully set up. I can now help you with Sales Forecasts, Pricing, and Inventory."
        
        try:
            # Try finding a markdown json block first
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            json_str = json_match.group(1) if json_match else response.content

            # Clean up the string to ensure it's parseable JSON
            json_str = json_str.strip()
            if json_str.startswith('{') and json_str.endswith('}'):
                extracted_data = json.loads(json_str)
                onboarding_data = extracted_data.get("data", {})
                
                # Get user context to know who to save it under
                user_id = state.get("user_context", {}).get("user_id", "unknown_user")
                phone = state.get("user_context", {}).get("phone_number")
                
                # DB Injection - Optimal Upsert
                db_tool = MongoDBTool()
                await db_tool.upsert_user_profile(
                    user_id=user_id, 
                    name=onboarding_data.get("name", ""),
                    phone=phone
                )
                await db_tool.upsert_store_profile(
                    user_id=user_id,
                    store_name=onboarding_data.get("store_name", ""),
                    location=onboarding_data.get("location", "")
                )
            else:
                print(f"Could not find valid JSON object in response: {response.content}")
        except Exception as e:
            print(f"Failed to parse onboarding JSON or save to DB: {e}")
            
        return {
            "messages": [AIMessage(content=final_message)],
            "current_step": new_step
        }
        
    return {
        "messages": [response],
        "current_step": "onboarding",
        # For simplicity in Phase 1, we let the LLM extract next time or parse via another node. 
        # (A true implementation would use Tool Calling to extract state).
    }

def route_step(state: ConversationState) -> Literal["onboarding_node", "intent_classifier"]:
    if state.get("current_step") == "completed":
        return "intent_classifier"
    return "onboarding_node"

# Define Graph
workflow = StateGraph(ConversationState)

workflow.add_node("language_detection_node", language_detection_node)
workflow.add_node("onboarding_node", onboarding_node)
workflow.add_node("intent_classifier", classify_intent_node)
workflow.add_node("sales_query_node", sales_query_node)
workflow.add_node("pricing_query_node", pricing_query_node)
workflow.add_node("inventory_query_node", inventory_query_node)
workflow.add_node("forecast_query_node", forecast_query_node)
workflow.add_node("general_chat_node", general_chat_node)

workflow.set_entry_point("language_detection_node")

workflow.add_conditional_edges(
    "language_detection_node",
    route_step,
    {
        "onboarding_node": "onboarding_node",
        "intent_classifier": "intent_classifier"
    }
)

workflow.add_conditional_edges(
    "intent_classifier",
    lambda state: state.get("next_intent", "general_chat"),
    {
        "sales_query": "sales_query_node",
        "pricing_query": "pricing_query_node",
        "inventory": "inventory_query_node",
        "forecast": "forecast_query_node",
        "general_chat": "general_chat_node"
    }
)

workflow.add_edge("onboarding_node", END)
workflow.add_edge("sales_query_node", END)
workflow.add_edge("pricing_query_node", END)
workflow.add_edge("inventory_query_node", END)
workflow.add_edge("forecast_query_node", END)
workflow.add_edge("general_chat_node", END)

graph = workflow.compile()
