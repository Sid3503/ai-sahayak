from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data
from ai_sahayak.tools.llm.bedrock_client import get_llm


async def sales_query_node(state: ConversationState):
    """
    Answer sales questions using dashboard data for the current retailer.
    Uses the same user_id as Dashboard / My day: raju, ramesh, suresh, kanta, lakshmi.
    """
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "unknown_user").strip().lower()
    onboarding_data = state.get("onboarding_data", {})
    messages = state.get("messages", [])
    
    # Only fetch dashboard data for known retailers (not web demo users)
    data = {}
    if user_id in ["raju", "ramesh", "suresh", "kanta", "lakshmi"]:
        data = get_dashboard_data(user_id)
    
    store = data.get("store_info", {}) or {}
    sales = data.get("sales_summary", {}) or {}

    # Prefer user's actual store name from onboarding over dashboard data
    store_name = onboarding_data.get("store_name") or store.get("name", "your store")
    city = onboarding_data.get("resolved_location") or store.get("city")
    
    # Get preferred language
    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    if preferred_lang in ["english", "en"]:
        lang_instruction = "Reply in English."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi (Devanagari script)."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = "Reply in Hinglish (Hindi words in Roman script)."
    else:
        lang_instruction = "Reply in the user's preferred language."

    if not sales:
        text = (
            "📈 Sales data is not available yet. "
            "Once you start using the Dashboard, I'll be able to help with sales insights. "
            "For now, I can answer general questions about your store."
        )
        return {"messages": [AIMessage(content=text)]}

    # Build sales context for LLM
    sales_context = f"Store: {store_name}"
    if city:
        if "," in str(city):
            city_short = str(city).split(",")[0].strip()
            sales_context += f" ({city_short})"
        else:
            sales_context += f" ({city})"
    sales_context += "\n\n"
    
    if sales.get("today") is not None:
        sales_context += f"Today's sales: ₹{sales['today']:,.0f}\n"
    if sales.get("last_week") is not None:
        sales_context += f"Last 7 days total: ₹{sales['last_week']:,.0f}\n"
    if sales.get("last_month") is not None:
        sales_context += f"Last month total: ₹{sales['last_month']:,.0f}\n"
    
    top_items = sales.get("top_items") or []
    if top_items:
        sales_context += f"Top selling items: {', '.join(top_items[:3])}\n"

    system_prompt = f"""You are AI Sahayak, an assistant for Indian Kirana store owners.
{lang_instruction}

## Sales Data:
{sales_context}

Provide a brief sales summary and offer to help with margin analysis, slow-movers, or festival planning."""

    try:
        llm = get_llm(temperature=0.3)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            *[m for m in messages if hasattr(m, "content")][-3:],
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"Sales query node error: {e}")
        reply = "Unable to fetch sales data right now. Please try again."

    return {"messages": [AIMessage(content=reply)]}
