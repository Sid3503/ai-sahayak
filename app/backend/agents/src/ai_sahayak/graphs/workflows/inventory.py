from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data
from ai_sahayak.tools.llm.bedrock_client import get_llm


async def inventory_query_node(state: ConversationState):
    """Answer inventory/stock questions using real Dashboard data (no mock)."""
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "raju").strip().lower()
    if user_id in ("unknown_user", "demo", "web_demo"):
        user_id = "raju"
    onboarding_data = state.get("onboarding_data", {})
    messages = state.get("messages", [])

    data = get_dashboard_data(user_id)
    from_dashboard = data.get("from_dashboard", False)
    inv = data.get("inventory_summary") or {}
    alerts = data.get("alerts") or []
    low_stock = inv.get("low_stock") or []
    reorder_risk = inv.get("reorder_risk_skus") or 0
    low_cover = inv.get("low_cover_skus") or 0

    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    owner_name = onboarding_data.get("name", "").split()[0] if onboarding_data.get("name") else ""
    name_ref = f"{owner_name} bhai" if owner_name else "bhai"

    if not from_dashboard:
        text = (
            "Haan bhai, abhi Dashboard se stock data aa nahi raha. Control Centre khol ke try karein."
        ) if preferred_lang in ["hinglish"] else "Dashboard not connected. Open Control Centre and try again."
        return {"messages": [AIMessage(content=text)]}

    lang_instruction = (
        f"Reply ONLY in Hinglish, 2-3 short sentences. Address as {name_ref}. No bullets."
    ) if preferred_lang in ["hinglish"] else "Reply in English, 2-3 short sentences. No bullets."

    context = f"Reorder risk SKUs: {reorder_risk}. Low cover SKUs: {low_cover}. Low stock items: {', '.join(low_stock[:5]) or 'None'}. Alerts: {'; '.join(alerts[:2]) or 'None'}."
    prompt = f"""You are AI Sahayak. {lang_instruction}
Inventory data from Dashboard (use ONLY this — do not invent): {context}
Reply with data in a **markdown table** (Metric | Value) so it's easy to read. Example:
| Reorder risk SKUs | 1 |
| Low cover SKUs | 1 |
| Low stock | Wheat Atta 5kg |
Then one short line suggesting action if needed. Simple language — like a local friend, not fancy AI English."""

    try:
        llm = get_llm(temperature=0.5)
        resp = await llm.ainvoke([
            SystemMessage(content=prompt),
            *[m for m in messages if hasattr(m, "content")][-3:],
        ])
        reply = (resp.content or "").strip() if hasattr(resp, "content") else str(resp)
    except Exception as e:
        print(f"Inventory node error: {e}")
        reply = "Stock data abhi nahi aa paya. Thodi der baad try karein." if preferred_lang in ["hinglish"] else "Could not fetch stock data. Try again."

    return {"messages": [AIMessage(content=reply)]}
