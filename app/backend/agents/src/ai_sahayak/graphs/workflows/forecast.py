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

    kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
    dashboard = get_dashboard_data(user_id)

    system_prompt = """You are AI Sahayak, helping an Indian Kirana store owner with demand forecasting and seasonal/festival trends.
Use the following context to answer. Reply in Hinglish or the user's language; keep it concise and actionable.

## Knowledge Base (festivals / Panchang / seasonal):
{kb_context}

## Store / sales context (for context only):
{store_context}

If the KB has no relevant festival/season info, say so and give general practical tips for the next 2–4 weeks."""

    store_context = ""
    if dashboard:
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
        store_context = "No store data available yet."

    try:
        llm = get_llm(temperature=0.2)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
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
