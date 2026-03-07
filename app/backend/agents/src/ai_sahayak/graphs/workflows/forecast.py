"""
Forecast workflow: uses Bedrock Knowledge Base (Panchang/festival data) + dashboard data.
"""
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.bedrock_knowledge_base import retrieve_from_panchang_kb
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def forecast_query_node(state: ConversationState):
    """Answer forecast queries using Bedrock KB (festival/seasonal) + dashboard context."""
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else "What is the demand forecast?"
    user_id = (state.get("user_context") or {}).get("user_id", "unknown_user")
    onboarding_data = state.get("onboarding_data", {})

    kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
    
    # Only fetch dashboard data for known retailers (not web demo users)
    dashboard = {}
    if user_id in ["raju", "ramesh", "suresh", "kanta", "lakshmi"]:
        dashboard = get_dashboard_data(user_id)
    
    # Get preferred language
    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    if preferred_lang in ["english", "en"]:
        lang_instruction = "Reply in English."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi only, using Devanagari script."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = "Reply in Hinglish only: Hindi + English in Roman script."
    else:
        lang_instruction = "Reply in English."

    system_prompt = """You are AI Sahayak, helping an Indian Kirana store owner with demand forecasting and seasonal/festival trends.
{lang_instruction} Keep it concise and actionable.

## User Profile:
{user_profile}

## Knowledge Base (festivals / Panchang / seasonal):
{kb_context}

## Store / sales context (for context only):
{store_context}

If the KB has no relevant festival/season info, say so and give general practical tips for the next 2–4 weeks."""

    # Build user profile
    user_profile = ""
    if onboarding_data:
        name = onboarding_data.get("name")
        store_name = onboarding_data.get("store_name")
        location = onboarding_data.get("resolved_location") or onboarding_data.get("location")
        if name:
            user_profile += f"Owner: {name}. "
        if store_name:
            user_profile += f"Store: {store_name}. "
        if location:
            user_profile += f"Location: {location}. "
    if not user_profile:
        user_profile = "No user profile available."

    # For web users who just completed onboarding, don't include mock sales data
    store_context = ""
    if user_id in ["raju", "ramesh", "suresh", "kanta", "lakshmi"] and dashboard:
        store_info = dashboard.get("store_info", {})
        sales = dashboard.get("sales_summary", {})
        inv = dashboard.get("inventory_summary", {})
        if store_info:
            store_context += f"Store: {store_info.get('name', '')}, {store_info.get('city', '')}. "
        if sales:
            store_context += f"Sales: last month ~{sales.get('last_month', 'N/A')}; top items: {sales.get('top_items', [])}. "
        if inv:
            store_context += f"Low stock: {inv.get('low_stock', [])}."

    if not store_context:
        store_context = "No sales/inventory data available yet. User just completed onboarding."

    try:
        llm = get_llm(temperature=0.2)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
                lang_instruction=lang_instruction,
                user_profile=user_profile,
                kb_context=kb_context or "(No festival/season data retrieved.)",
                store_context=store_context,
            )),
            *[m for m in messages if hasattr(m, "content")][-3:],
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"Forecast node error: {e}")
        reply = "🔮 Demand forecast abhi load nahi ho paya. Thodi der baad try karein ya 'Festival forecast' / 'seasonal trend' poochhen."

    return {"messages": [AIMessage(content=reply)]}
