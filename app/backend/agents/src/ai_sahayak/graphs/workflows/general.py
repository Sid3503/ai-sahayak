"""
General chat workflow: uses Bedrock Knowledge Base + dashboard data for store advice.
"""
import re
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.bedrock_knowledge_base import retrieve_from_panchang_kb
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


def _is_greeting_only(text: str) -> bool:
    """True if message is just a greeting (hello, hi, etc.) — skip KB and dashboard for fast reply."""
    t = (text or "").strip().lower()
    if not t or len(t) > 50:
        return False
    greetings = ("hello", "hi", "hey", "hlw", "hii", "namaste", "namaskar", "haan", "ji", "good morning", "good afternoon", "good evening", "good night", "gm", "gn")
    if t in greetings:
        return True
    return bool(re.match(r"^(hello|hi|hey|namaste|namaskar|haan)\s*[!?\.]*$", t))


async def general_chat_node(state: ConversationState):
    """Answer general store questions using Bedrock KB + dashboard (e.g. what to stock, how were sales)."""
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else "How can you help?"
    user_id = (state.get("user_context") or {}).get("user_id", "unknown_user")
    onboarding_data = state.get("onboarding_data", {})

    greeting_only = _is_greeting_only(user_message)
    # Skip KB and dashboard for greeting-only to reduce latency (no blocking HTTP/KB calls)
    if greeting_only:
        kb_context = ""
        dashboard = {}
    else:
        kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
        dashboard = get_dashboard_data(user_id)

    # Get user's preferred language from onboarding
    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    
    # Language instruction for LLM (English / Hindi / Hinglish only)
    owner_name = onboarding_data.get("name", "").split()[0] if onboarding_data.get("name") else ""
    name_suffix = f" {owner_name} bhai" if owner_name else " bhai"

    if preferred_lang in ["english", "en"]:
        lang_instruction = "Reply in English. Be brief, friendly, max 2-3 sentences. No bullet points."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi only, using Devanagari script (e.g. नमस्ते, धन्यवाद). Max 2-3 sentences. No bullet points."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = (
            f"You MUST reply ONLY in Hinglish (Hindi + English in Roman script), like a local dost talking to{name_suffix}. "
            "Rules: max 2-3 SHORT sentences, no bullet lists, no markdown (no ** or ---), no numbered lists, no long English paragraphs. "
            "Sound natural and warm — like a helpful neighbourhood friend, not a formal AI. "
            "Vary your phrasing each time. "
            "For greetings/hello: give a short warm welcome and mention 1-2 things you can help with naturally. "
            "For 'what can you help': mention sales, stock, price in ONE casual sentence. "
            "Good example: 'Haan{name_suffix}, bol! Sales, stock, price — sab dekh sakte hain. Kya chahiye?'"
        )
    else:
        lang_instruction = "Reply in English. Be brief, friendly, max 2-3 sentences."

    system_prompt = """You are AI Sahayak, a smart assistant for Indian Kirana store owners.
{lang_instruction}

## User Profile:
{user_profile}

## Store / Dashboard Data:
{store_context}

## Knowledge Base (festivals / events / seasonal tips):
{kb_context}

Use ONLY the data above (Dashboard + KB — do not invent numbers). Answer in simple, easy-to-understand language. If greeting or asked what you can help with, be brief and warm. When you include numbers, put them in a **markdown table** (Metric | Value) or **bold labels**. No long paragraphs, no fancy AI English — sound like a local friend. If data is not available, say so briefly and offer to help differently."""

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

    # Real dashboard data only (no mock). Include overview KPIs and alerts for suggestions.
    store_context = ""
    if dashboard.get("from_dashboard") and dashboard:
        store_info = dashboard.get("store_info", {})
        sales = dashboard.get("sales_summary", {})
        inv = dashboard.get("inventory_summary", {})
        overview_kpis = dashboard.get("overview_kpis") or {}
        alerts = dashboard.get("alerts") or []
        if store_info:
            store_context += f"Store: {store_info.get('name', '')}, {store_info.get('city', '')}. "
        if sales:
            store_context += f"Sales: today ₹{sales.get('today', 0):,.0f}, last week ₹{sales.get('last_week', 0):,.0f}, last month ₹{sales.get('last_month', 0):,.0f}; top items: {sales.get('top_items', [])}. "
        if inv:
            store_context += f"Low stock / reorder risk: {inv.get('low_stock', [])}; reorder_risk_skus: {inv.get('reorder_risk_skus', 0)}; low_cover_skus: {inv.get('low_cover_skus', 0)}. "
        if overview_kpis:
            store_context += f"Overview: revenue_30d ₹{overview_kpis.get('revenue_30d', 0):,.0f}, profit_30d ₹{overview_kpis.get('profit_30d', 0):,.0f}, sell_through {overview_kpis.get('sell_through_pct', 0):.1f}%, avg_margin {overview_kpis.get('avg_margin_pct', 0):.1f}%, festival_days_last30 {overview_kpis.get('festival_days_last30', 0)}. "
        if alerts:
            store_context += "Alerts (suggest these when relevant): " + "; ".join(alerts[:3]) + "."
    if not store_context:
        store_context = "Dashboard abhi connect nahi hai — real data tabhi milega jab Control Centre open hoga. User ko batao: Dashboard khol ke try karein, phir main real numbers bata paunga."
    if greeting_only:
        store_context = "(User just said hello — reply with a short warm welcome only.)"

    # For greeting-only: use only last message to keep prompt small and response fast
    recent = [m for m in messages if hasattr(m, "content")][-1:] if greeting_only else [m for m in messages if hasattr(m, "content")][-3:]
    try:
        llm = get_llm(temperature=0.7)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
                lang_instruction=lang_instruction,
                user_profile=user_profile,
                kb_context=kb_context or "(No KB results.)",
                store_context=store_context,
            )),
            *recent,
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"General chat node error: {e}")
        reply = "🗣️ Abhi response generate karte waqt issue aaya. Thodi der baad try karein."

    return {"messages": [AIMessage(content=reply)]}
