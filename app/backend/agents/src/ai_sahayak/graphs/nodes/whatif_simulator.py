from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def whatif_simulator_node(state: ConversationState):
    """
    Evaluates what-if business scenarios using the project LLM (Nova Lite).
    No Code Interpreter — uses real store data and a single LLM call for Hinglish what-if answers.
    """
    llm = get_llm(temperature=0.7)

    messages = state.get("messages", [])
    last_query = messages[-1].content if messages else "No query provided."
    onboarding = state.get("onboarding_data", {})
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "raju").strip().lower()

    dashboard = get_dashboard_data(user_id) if user_id not in ("unknown_user",) else {}
    if not dashboard.get("from_dashboard"):
        name_ref = f"{onboarding.get('name', '').split()[0]} bhai" if onboarding.get("name") else "bhai"
        return {
            "messages": [AIMessage(content=f"What-if ke liye Dashboard se data chahiye {name_ref}. Control Centre connect karein, phir poochhen.")],
            "current_step": "simulator_complete",
        }
    sales = dashboard.get("sales_summary", {}) or {}
    owner_name = onboarding.get("name", "").split()[0] if onboarding.get("name") else ""
    name_ref = f"{owner_name} bhai" if owner_name else "bhai"
    store_context = ""
    if sales.get("today"):
        store_context += f"Today's sales: ₹{sales['today']:,.0f}. "
    if sales.get("top_items"):
        store_context += f"Top items: {', '.join(sales['top_items'][:3])}. "
    if not store_context.strip():
        return {
            "messages": [AIMessage(content=f"What-if ke liye Dashboard pe sales data chahiye {name_ref}. Control Centre se data aane do, phir poochhen.")],
            "current_step": "simulator_complete",
        }

    prompt = (
        f"You are AI Sahayak helping {name_ref}, a Kirana store owner.\n"
        f"Store data (from Dashboard only — use ONLY this): {store_context.strip()}\n"
        f"User asks: '{last_query}'\n\n"
        "Use ONLY the data above. Reply in simple Hinglish, easy to understand. Put key numbers in a **markdown table** (e.g. | Scenario | Impact |) or **bold labels**. One short sentence after. No code, no long paragraph, no fancy AI English — sound like a local friend."
    )
    try:
        response = await llm.ainvoke([SystemMessage(content=prompt)])
        reply_message = (response.content or "").strip()
    except Exception as e:
        print(f"[WhatIf] LLM failed: {e}")
        reply_message = "Abhi what-if run nahi ho paya. Thodi der baad try karein."
    if not reply_message:
        reply_message = "Abhi what-if run nahi ho paya. Thodi der baad try karein."

    return {
        "messages": [AIMessage(content=reply_message)],
        "current_step": "simulator_complete",
    }
