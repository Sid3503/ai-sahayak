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

    kb_context = retrieve_from_panchang_kb(user_message, max_results=5)
    dashboard = get_dashboard_data(user_id)

    system_prompt = """You are AI Sahayak, an assistant for Indian Kirana store owners.
Use the context below to answer. Reply in Hinglish or the user's language; be brief and practical.

## Knowledge Base (festivals / events / general):
{kb_context}

## Store / dashboard context:
{store_context}

Answer questions like "what should I stock?", "how were my sales?", "any festival coming?" using this data. If something is not in context, say so and offer a generic tip."""

    store_context = ""
    if dashboard:
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
        store_context = "No store data available yet."

    try:
        llm = get_llm(temperature=0.3)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt.format(
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
