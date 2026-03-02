from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.prompts.registry import PromptRegistry
from ai_sahayak.config.settings import settings
from ai_sahayak.tools.data_sources.dynamodb_tool import DynamoDBTool
from ai_sahayak.graphs.nodes.router.intent_router import classify_intent_node
from ai_sahayak.graphs.workflows.sales import sales_query_node
from ai_sahayak.graphs.workflows.pricing import pricing_query_node
from ai_sahayak.graphs.workflows.inventory import inventory_query_node
from ai_sahayak.graphs.workflows.forecast import forecast_query_node
from ai_sahayak.graphs.workflows.general import general_chat_node
from ai_sahayak.graphs.nodes.router.language_router import language_detection_node
from ai_sahayak.graphs.workflows.alert import handle_alert_query_node
from ai_sahayak.graphs.nodes.vision_node import image_analysis_node
from ai_sahayak.graphs.nodes.system.memory_hooks import pre_model_hook, post_model_hook, memory_store
import os
import json
import re
from ai_sahayak.utils.validators import validate_onboarding_field
from ai_sahayak.utils.location_resolver import enrich_location

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
    user_context = state.get("user_context", {})
    
    # Pre-seed name from WhatsApp profile if available and not set
    if not onboarding_data.get("name") and user_context.get("whatsapp_push_name"):
        onboarding_data["name"] = user_context.get("whatsapp_push_name")
        
    system_content = system_template.replace("{name}", str(onboarding_data.get("name", "Not provided")))\
                                    .replace("{store_name}", str(onboarding_data.get("store_name", "Not provided")))\
                                    .replace("{store_type}", str(onboarding_data.get("store_type", "Not provided")))\
                                    .replace("{pincode}", str(onboarding_data.get("pincode", "Not provided")))\
                                    .replace("{location}", str(onboarding_data.get("location", "Not provided")))\
                                    .replace("{years_in_business}", str(onboarding_data.get("years_in_business", "Not provided")))\
                                    .replace("{aadhar}", str(onboarding_data.get("aadhar", "Not provided")))\
                                    .replace("{gst_number}", str(onboarding_data.get("gst_number", "Not provided")))
    
    messages = [SystemMessage(content=system_content)] + state["messages"]
    
    # Invoke the LLM
    response = llm.invoke(messages)
    
    reply_text = response.content
    is_complete = False
    new_step = "onboarding"
    
    def is_valid_value(val):
        if not val:
            return False
        val_str = str(val).strip().lower()
        return val_str not in ["null", "none", "not provided", "", "unknown"]
    
    try:
        # Check if response content exists
        if not response.content.strip():
            raise ValueError("Empty LLM response")
            
        json_str = response.content
        
        # Try finding a markdown json block first
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            
        # regardless of markdown, ALWAYS strictly clamp to the outermost { and }
        # this handles " json { ... }  " and other bizarre hidden characters the LLM spits out
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = json_str[start_idx:end_idx+1]
            
        # Clean up any rogue string concatenations the LLM might have generated
        # e.g., "Hello" + "\n\n" + "World" -> "Hello\n\nWorld"
        json_str = re.sub(r'"\s*\+\s*"', '', json_str)
        
        json_str = json_str.strip()
        parsed_data = json.loads(json_str)
        
        reply_text = parsed_data.get("reply", response.content)
        extracted_data = parsed_data.get("data", {})

        if isinstance(extracted_data, dict):
            validation_errors: list[str] = []

            for k, v in extracted_data.items():
                if not is_valid_value(v):
                    continue
                result = validate_onboarding_field(k, str(v))
                if result.is_valid:
                    # Store the normalized canonical value
                    onboarding_data[k] = result.normalized if result.normalized else v
                else:
                    validation_errors.append(result.error)

            # If any identifier failed validation, override the LLM reply with the error
            if validation_errors:
                error_summary = "\n".join(f"⚠️ {err}" for err in validation_errors)
                reply_text = f"{error_summary}\n\nPlease correct the above and try again."

            # DB Injection - Progressive Upsert (only when no validation errors)
            if not validation_errors:
                user_id = state.get("user_context", {}).get("user_id", "unknown_user")
                phone = state.get("user_context", {}).get("phone_number")

                db_tool = DynamoDBTool()
                if onboarding_data.get("name") or phone:
                    await db_tool.upsert_user_profile(
                        user_id=user_id,
                        name=onboarding_data.get("name", "Unknown"),
                        phone=phone
                    )

                if onboarding_data.get("store_name") or onboarding_data.get("location") or onboarding_data.get("pincode"):
                    # Resolve the best available location signal to a human-readable string
                    raw_location = (
                        onboarding_data.get("location")
                        or onboarding_data.get("pincode")
                        or "Unknown Location"
                    )
                    resolved_location = await enrich_location(raw_location)
                    onboarding_data["resolved_location"] = resolved_location

                    await db_tool.upsert_store_profile(
                        user_id=user_id,
                        store_name=onboarding_data.get("store_name", "Unknown Store"),
                        location=resolved_location,
                        pincode=onboarding_data.get("pincode")
                    )
                
    except Exception as e:
        print(f"Failed to parse onboarding JSON: {e}")
        # Fallback to raw response if JSON parsing fails
        reply_text = response.content
        
    # Deterministic completion check (ignore LLM's flag to avoid premature completion)
    required_keys_base = ["name", "store_name", "store_type", "years_in_business", "aadhar", "gst_number"]
    base_complete = all(is_valid_value(onboarding_data.get(k)) for k in required_keys_base)
    location_complete = is_valid_value(onboarding_data.get("pincode")) or is_valid_value(onboarding_data.get("location"))
    is_complete = base_complete and location_complete
        
    if is_complete:
        new_step = "completed"
        
        # The LLM generates the final message in its 'reply' JSON field
        # We use that instead of hardcoding, as it will be in the correct language natively.
        final_message = reply_text if reply_text else "🎉 Welcome to AI Sahayak! Your store is successfully set up. I can now help you with Sales Forecasts, Pricing, and Inventory."
        
        # Generate strict/rigid Login Credentials
        user_name = onboarding_data.get("name", "User").strip()
        phone_num = str(state.get("user_context", {}).get("phone_number", ""))
        
        # User ID
        user_id_cred = phone_num if phone_num else state.get("user_context", {}).get("user_id", "UnknownID")
        
        # Password
        name_clean = user_name.replace(" ", "")
        name_part = name_clean[:4] if len(name_clean) >= 4 else name_clean
        phone_part = phone_num[-4:] if len(phone_num) >= 4 else phone_num
        pwd = f"{name_part}{phone_part}"
        
        credentials_msg = f"\n\n🔐 *Your Sahayak Analytics Dashboard Login*\n*User ID:* {user_id_cred}\n*Password:* {pwd}\n(Please save these for future access)"
        final_message += credentials_msg
        
        # Finalize and persist user credentials to the database
        try:
            db_tool_final = DynamoDBTool()
            import asyncio
            # Running asynchronously or awaiting if possible.
            # This is an async func so we can await it directly.
            asyncio.create_task(db_tool_final.upsert_user_profile(
                user_id=state.get("user_context", {}).get("user_id", "UnknownID"),
                name=user_name,
                phone=phone_num,
                password=pwd
            ))
        except Exception as e:
            print(f"Failed to upsert user credentials: {e}")
            
        return {
            "messages": [AIMessage(content=final_message)],
            "current_step": new_step,
            "onboarding_data": onboarding_data
        }
        
    return {
        "messages": [AIMessage(content=reply_text)],
        "current_step": new_step,
        "onboarding_data": onboarding_data
    }

def route_step(state: ConversationState) -> Literal["onboarding_node", "intent_classifier"]:
    current_step = state.get("current_step")
    # If the user has completed onboarding, or is in any subsequent dashboard step
    if current_step and current_step not in ["wait_for_hi", "onboarding"]:
        return "intent_classifier"
    return "onboarding_node"

from ai_sahayak.memory.profile_store import load_profile_into_state
from functools import partial

# Define Graph
workflow = StateGraph(ConversationState)

workflow.add_node("load_profile", load_profile_into_state)
workflow.add_node("language_detection_node", language_detection_node)
workflow.add_node("onboarding_node", onboarding_node)
workflow.add_node("intent_classifier", classify_intent_node)
workflow.add_node("sales_query_node", sales_query_node)
workflow.add_node("pricing_query_node", pricing_query_node)
workflow.add_node("inventory_query_node", inventory_query_node)
workflow.add_node("forecast_query_node", forecast_query_node)
workflow.add_node("general_chat_node", general_chat_node)
workflow.add_node("alert_query_node", handle_alert_query_node)
workflow.add_node("image_analysis_node", image_analysis_node)

workflow.add_node("pre_memory_hook", partial(pre_model_hook, store=memory_store))
workflow.add_node("post_memory_hook", partial(post_model_hook, store=memory_store))

workflow.set_entry_point("load_profile")
workflow.add_edge("load_profile", "language_detection_node")
workflow.add_edge("language_detection_node", "pre_memory_hook")

workflow.add_conditional_edges(
    "pre_memory_hook",
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
        "image_analysis": "image_analysis_node",
        "alert_query": "alert_query_node",
        "general_chat": "general_chat_node"
    }
)

# Connect all handlers to post_memory_hook instead of END
workflow.add_edge("onboarding_node", "post_memory_hook")
workflow.add_edge("sales_query_node", "post_memory_hook")
workflow.add_edge("pricing_query_node", "post_memory_hook")
workflow.add_edge("inventory_query_node", "post_memory_hook")
workflow.add_edge("forecast_query_node", "post_memory_hook")
workflow.add_edge("general_chat_node", "post_memory_hook")
workflow.add_edge("image_analysis_node", "post_memory_hook")
workflow.add_edge("alert_query_node", "post_memory_hook")

workflow.add_edge("post_memory_hook", END)

graph = workflow.compile()
