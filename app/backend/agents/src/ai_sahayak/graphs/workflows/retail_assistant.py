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
from ai_sahayak.utils.validators import validate_onboarding_field
from ai_sahayak.utils.location_resolver import enrich_location
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
    user_context = state.get("user_context", {})
    
    # Pre-seed name from WhatsApp profile only on WhatsApp (not web demo)
    if not onboarding_data.get("name") and user_context.get("whatsapp_push_name") and user_context.get("platform") == "whatsapp":
        onboarding_data["name"] = user_context.get("whatsapp_push_name")

    # On web, don't use persisted name from a previous session when conversation is still early (user hasn't been asked for name yet)
    messages_list = state.get("messages", [])
    name_for_prompt = onboarding_data.get("name") or "Not provided"
    if user_context.get("platform") == "web" and len(messages_list) <= 4:
        name_for_prompt = "Not provided"

    # When user uploads document/photo for Aadhar, treat as Aadhar received so next step is GST (friend's flow)
    if messages_list and not onboarding_data.get("aadhar"):
        last_msg = messages_list[-1]
        last_content = (getattr(last_msg, "content", "") or "").strip().lower()
        if any(x in last_content for x in ("document attached", "photo attached", "[image uploaded", "📄 document")):
            onboarding_data["aadhar"] = "uploaded"

    # Persist preferred language when user clearly chose one (English / Hindi / Hinglish only; Marathi removed)
    last_user_content = ""
    if messages_list:
        last_msg = messages_list[-1]
        if getattr(last_msg, "content", None):
            raw = str(last_msg.content).strip().lower()
            last_user_content = raw
            if raw in ("english", "hindi", "hinglish"):
                onboarding_data["preferred_language"] = raw.title()
            elif raw.startswith("[hi]") or raw.startswith("[hin]"):
                onboarding_data["preferred_language"] = "Hindi"
            elif raw.startswith("[en]"):
                onboarding_data["preferred_language"] = "English"

    # When user just sent a 6-digit pincode, set pincode + location before LLM so it doesn't re-ask for location
    if messages_list and getattr(messages_list[-1], "content", None):
        raw = str(messages_list[-1].content).strip().replace(" ", "")
        if raw.isdigit() and len(raw) == 6 and (not onboarding_data.get("pincode") or not onboarding_data.get("location")):
            onboarding_data["pincode"] = raw
            onboarding_data["location"] = raw

    # Fallback: we have name but no store_name — use user's last reply as store name (stops "What is the official name of your shop?" loop)
    from langchain_core.messages import HumanMessage
    def _has_val(v):
        return v and str(v).strip().lower() not in ["null", "none", "not provided", "", "unknown"]
    if messages_list and len(messages_list) >= 2 and _has_val(onboarding_data.get("name")) and not _has_val(onboarding_data.get("store_name")):
        last_msg = messages_list[-1]
        if isinstance(last_msg, HumanMessage):
            user_reply = (getattr(last_msg, "content", "") or "").strip()
            if user_reply and len(user_reply) < 200 and user_reply.lower() not in ("english", "hindi", "hinglish"):
                if not (user_reply.isdigit() and len(user_reply) == 6):
                    onboarding_data["store_name"] = user_reply

    system_content = system_template.replace("{name}", str(name_for_prompt))\
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
            
        json_str = json_str.strip()
        parsed_data = json.loads(json_str)
        
        reply_text = parsed_data.get("reply", response.content)
        extracted_data = parsed_data.get("data", {})

        if isinstance(extracted_data, dict):
            validation_errors = []
            for k, v in extracted_data.items():
                if not is_valid_value(v):
                    continue
                # Aadhar: we already set "uploaded" from document/photo detection — don't overwrite with LLM extraction (e.g. "4" from filename)
                if k == "aadhar" and str(onboarding_data.get("aadhar", "")).strip().lower() == "uploaded":
                    continue
                # Aadhar "uploaded" from LLM — accept as-is
                if k == "aadhar" and str(v).strip().lower() == "uploaded":
                    onboarding_data[k] = "uploaded"
                    continue
                result = validate_onboarding_field(k, str(v))
                if result.is_valid:
                    onboarding_data[k] = result.normalized if result.normalized is not None else v
                else:
                    validation_errors.append(result.error or f"Invalid {k}")

            if validation_errors:
                reply_text = "Please correct:\n" + "\n".join(f"• {e}" for e in validation_errors)
            else:
                # When user says "no" to GST, LLM often doesn't put gst_number in data — set it so we can complete and show ID/pass
                if not onboarding_data.get("gst_number") and is_valid_value(onboarding_data.get("aadhar")):
                    last_msg = (state.get("messages") or [])[-1] if state.get("messages") else None
                    last_content = (getattr(last_msg, "content", "") or "").strip().lower()
                    no_gst = last_content in ("no", "nope", "nahi", "nhi", "no gst", "no gst number") or (len(last_content) <= 20 and "no" in last_content.split())
                    if no_gst:
                        onboarding_data["gst_number"] = "no"

                # DB Injection - Progressive Upsert
                # Skip progressive upserts during onboarding to avoid duplicate entries
                # We'll do final upsert when onboarding completes with the generated user_id_cred
                if onboarding_data.get("location") or onboarding_data.get("pincode"):
                    raw_location = onboarding_data.get("location") or onboarding_data.get("pincode") or "Unknown Location"
                    resolved_location = await enrich_location(raw_location)
                    onboarding_data["resolved_location"] = resolved_location
                
    except Exception as e:
        # Fallback to raw response if JSON parsing fails
        # This is expected when LLM returns plain text (e.g., asking for Aadhar/GST)
        reply_text = (response.content or "").strip()
        if not reply_text:
            reply_text = "Please share that again; I didn't catch it."
        # Only log if it's not a simple acknowledgment or question
        if not any(keyword in (response.content or "").lower() for keyword in ['aadhar', 'gst', 'verification', 'upload', 'provide']):
            print(f"Failed to parse onboarding JSON: {e}")
            print(f"Raw LLM response: {(response.content or '')[:500]}")

    # When user said "no" to GST but LLM didn't put it in data (e.g. parse failed or empty data), set it so we can complete
    if not is_valid_value(onboarding_data.get("gst_number")) and is_valid_value(onboarding_data.get("aadhar")):
        last_msg = (state.get("messages") or [])[-1] if state.get("messages") else None
        last_content = (getattr(last_msg, "content", "") or "").strip().lower()
        no_gst = last_content in ("no", "nope", "nahi", "nhi", "no gst", "no gst number") or (len(last_content) <= 20 and "no" in last_content.split())
        if no_gst:
            onboarding_data["gst_number"] = "no"

    # If user gave pincode but not location (e.g. only typed 400042), use pincode as location so we can complete and show credentials
    if not is_valid_value(onboarding_data.get("location")) and is_valid_value(onboarding_data.get("pincode")):
        onboarding_data["location"] = str(onboarding_data.get("pincode", ""))

    # Never re-ask the language question: if user just chose language, reply with "Great, we'll continue in X" and ask for name
    if last_user_content in ("english", "hindi", "hinglish") and is_valid_value(onboarding_data.get("preferred_language")) and not is_valid_value(onboarding_data.get("name")):
        lang = onboarding_data.get("preferred_language", "English").strip()
        reply_text = f"Great, we'll continue in {lang}.\n\nWhat is your full name?"
        
    # Deterministic completion check (ignore LLM's flag to avoid premature completion)
    required_keys = ["name", "store_name", "store_type", "pincode", "location", "years_in_business", "aadhar", "gst_number"]
    is_complete = all(is_valid_value(onboarding_data.get(k)) for k in required_keys)
    
    print(f"Onboarding completion check: {is_complete}")
    print(f"Onboarding data: {onboarding_data}")
        
    if is_complete:
        new_step = "completed"
        
        # Credentials: Generate 10-digit user ID (phone-like for consistency)
        # For web users, generate random 10-digit number; for WhatsApp, use actual phone
        user_name = onboarding_data.get("name", "User").strip()
        user_id_from_payload = str(state.get("user_context", {}).get("user_id", "")).strip()
        payload_phone = str(state.get("user_context", {}).get("phone_number", "")).strip().replace(" ", "")
        
        # Generate user_id: if real phone, use it; else generate 10-digit number
        if payload_phone and payload_phone != "0000000000" and len(payload_phone) >= 10 and payload_phone.isdigit():
            user_id_cred = payload_phone[-10:] if len(payload_phone) > 10 else payload_phone
        else:
            # Generate random 10-digit phone-like number for web users
            import random
            user_id_cred = "9" + "".join([str(random.randint(0, 9)) for _ in range(9)])
        
        # Password: firstname + last4digits + ! (Cognito requires uppercase + numbers)
        first_name = user_name.split()[0] if user_name else "User"
        first_name = "".join(c for c in first_name if c.isalpha())[:20] or "User"
        first_name_for_pwd = (first_name or "User").capitalize()
        last4 = user_id_cred[-4:]
        pwd = f"{first_name_for_pwd}{last4}!"
        phone_num = payload_phone if payload_phone and payload_phone != "0000000000" else user_id_cred

        # Credentials must always be in Latin (User ID / Password) so user can sign in; intro can be in Hindi.
        preferred_lang = (onboarding_data.get("preferred_language") or "English").strip().lower()
        if preferred_lang == "hindi":
            final_message = (
                "आप सब तैयार हैं! डैशबोर्ड पर साइन इन करने के लिए नीचे दिए गए आईडी और पासवर्ड का उपयोग करें:\n\n"
                f"User ID: {user_id_cred}\n"
                f"Password: {pwd}\n\n"
                "(बाद के लिए इन्हें सहेजें।)"
            )
        else:
            final_message = (
                "You're all set! Use these to sign in to the Dashboard:\n\n"
                f"User ID: {user_id_cred}\n"
                f"Password: {pwd}\n\n"
                "(Save them for later.)"
            )
        
        # Create/update Cognito user so they can sign in on the Dashboard with this User ID and Password (name = greeting on Dashboard)
        try:
            from ai_sahayak.tools.auth.cognito_user import ensure_cognito_user
            import asyncio
            ok = await asyncio.to_thread(ensure_cognito_user, user_id_cred, pwd, name=user_name)
            if not ok:
                print(f"[Onboarding] Cognito: user '{user_id_cred}' was NOT created. Set COGNITO_USER_POOL_ID in .env and ensure IAM has cognito-idp:AdminCreateUser and AdminSetUserPassword.")
            else:
                print(f"[Onboarding] Cognito: user '{user_id_cred}' ready for Dashboard sign-in.")
        except Exception as e:
            print(f"[Onboarding] Cognito user create/set-password failed for '{user_id_cred}': {e}")
        
        # Finalize and persist user credentials and store (with resolved location) to the database
        try:
            db_tool_final = DynamoDBTool()
            await db_tool_final.upsert_user_profile(
                user_id=user_id_cred,
                name=user_name,
                phone=phone_num,
                password=pwd
            )
            # Persist store with City, District, State when possible
            loc_for_store = onboarding_data.get("resolved_location")
            if not loc_for_store:
                raw = onboarding_data.get("location") or onboarding_data.get("pincode") or "Unknown Location"
                loc_for_store = await enrich_location(raw)
            await db_tool_final.upsert_store_profile(
                user_id=user_id_cred,
                store_name=onboarding_data.get("store_name", "Unknown Store"),
                location=loc_for_store
            )
            print(f"✅ User {user_id_cred} and store persisted to DynamoDB")
        except Exception as e:
            print(f"Failed to upsert user credentials: {e}")

        return {
            "messages": [AIMessage(content=final_message)],
            "current_step": new_step,
            "onboarding_data": onboarding_data
        }

    # Safeguards: if we already have data but LLM re-asked, skip to next question
    r = (reply_text or "").strip().lower()
    if is_valid_value(onboarding_data.get("pincode")) and is_valid_value(onboarding_data.get("location")):
        if "pincode" in r or "6-digit" in r or ("share" in r and "location" in r) or "enter an address" in r:
            reply_text = "How many years have you been running this business?"
    elif is_valid_value(onboarding_data.get("store_name")) and ("official name of your shop" in r or "name of your shop" in r):
        # Have shop name but LLM asked again — ask for store type or pincode
        if is_valid_value(onboarding_data.get("store_type")):
            reply_text = "What is your shop's 6-digit Pincode?\n\nYou can either manually *enter an address* or *share your current location*."
        else:
            reply_text = "What type of store do you run? (e.g., Kirana, General Store, Medical)"

    # Ensure we never return empty reply (robustness)
    out_reply = (reply_text or "").strip() or "Please try again."
    return {
        "messages": [AIMessage(content=out_reply)],
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
        "alert_preferences": "general_chat_node",
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
