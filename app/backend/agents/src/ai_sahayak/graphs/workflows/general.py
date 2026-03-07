"""
General chat workflow: uses Bedrock Knowledge Base + dashboard data for store advice.
"""
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.bedrock_knowledge_base import retrieve_from_panchang_kb
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def general_chat_node(state: ConversationState):
    """Answer general store questions using Bedrock KB + dashboard (e.g. what to stock, how were sales)."""
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else "How can you help?"
    user_id = (state.get("user_context") or {}).get("user_id", "unknown_user")
    onboarding_data = state.get("onboarding_data", {})

    kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
    dashboard = get_dashboard_data(user_id)

    # Get user's preferred language from onboarding
    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    
    # Language instruction for LLM
    if preferred_lang in ["english", "en"]:
        lang_instruction = "Reply in English."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi (Devanagari script)."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = "Reply in Hinglish (Hindi words in Roman script)."
    elif preferred_lang in ["marathi", "mr"]:
        lang_instruction = "Reply in Marathi."
    else:
        lang_instruction = "Reply in the user's preferred language."

    system_prompt = """You are AI Sahayak, an assistant for Indian Kirana store owners.
Use the context below to answer. {lang_instruction} Be brief and practical.
When listing user profile info (e.g. "what do you know about me"), use plain text only — no markdown like **bold** or asterisks.

## User Profile:
{user_profile}

## Knowledge Base (festivals / events / general):
{kb_context}

## Store / dashboard context:
{store_context}

Answer questions like "what should I stock?", "how were my sales?", "any festival coming?" using this data. If something is not in context, say so and offer a generic tip."""

    # Build user profile context from onboarding data
    user_profile = ""
    if onboarding_data:
        name = onboarding_data.get("name")
        store_name = onboarding_data.get("store_name")
        store_type = onboarding_data.get("store_type")
        location = onboarding_data.get("resolved_location") or onboarding_data.get("location")
        years = onboarding_data.get("years_in_business")
        aadhar = onboarding_data.get("aadhar")
        gst = onboarding_data.get("gst_number")
        
        if name:
            user_profile += f"Owner: {name}. "
        if store_name:
            user_profile += f"Store: {store_name}"
            if store_type:
                user_profile += f" ({store_type})"
            user_profile += ". "
        if location:
            user_profile += f"Location: {location}. "
        if years:
            user_profile += f"Years in business: {years}. "
        if aadhar and str(aadhar).lower() not in ["null", "none", "not provided"]:
            user_profile += f"Aadhar: {aadhar}. "
        if gst and str(gst).lower() not in ["null", "none", "not provided", "no"]:
            user_profile += f"GST: {gst}. "
        elif gst and str(gst).lower() == "no":
            user_profile += "GST: Not registered. "
    
    if not user_profile:
        user_profile = "No user profile available yet."

    # For web users who just completed onboarding, don't include mock sales data
    # Only include dashboard data if user_id is a known retailer (raju, ramesh, etc.)
    store_context = ""
    if user_id in ["raju", "ramesh", "suresh", "kanta", "lakshmi"] and dashboard:
        store_info = dashboard.get("store_info", {})
        sales = dashboard.get("sales_summary", {})
        inv = dashboard.get("inventory_summary", {})
        if store_info:
            store_context += f"Store: {store_info.get('name', '')}, {store_info.get('city', '')}. "
        if sales:
            store_context += f"Sales: today ~{sales.get('today', 'N/A')}, last week ~{sales.get('last_week', 'N/A')}; top items: {sales.get('top_items', [])}. "
        if inv:
            store_context += f"Low stock: {inv.get('low_stock', [])}; total SKUs: {inv.get('total_skus', 'N/A')}."

    if not store_context:
        store_context = "No sales/inventory data available yet. User just completed onboarding."

    try:
        llm = get_llm(temperature=0.3)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
                lang_instruction=lang_instruction,
                user_profile=user_profile,
                kb_context=kb_context or "(No KB results.)",
                store_context=store_context,
            )),
            *[m for m in messages if hasattr(m, "content")][-3:],
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"General chat node error: {e}")
        reply = "🗣️ Abhi response generate karte waqt issue aaya. Thodi der baad try karein."

    return {"messages": [AIMessage(content=reply)]}
