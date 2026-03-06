from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def sales_query_node(state: ConversationState):
    """
    Answer sales questions using dashboard data for the current retailer.
    Uses the same user_id as Dashboard / My day: raju, ramesh, suresh, kanta, lakshmi.
    """
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "unknown_user").strip().lower()
    data = get_dashboard_data(user_id)
    store = data.get("store_info", {}) or {}
    sales = data.get("sales_summary", {}) or {}

    store_name = store.get("name", "aapki dukaan")
    city = store.get("city")

    if not sales:
        text = (
            "📈 Abhi detailed sales data backend se connected nahi hai, "
            "par main fir bhi generic tips de sakta hoon. "
            "Boliyega — daily sales, weekly trend ya festival ke time ka plan dekhna hai?"
        )
        return {"messages": [AIMessage(content=text)]}

    today = sales.get("today")
    last_week = sales.get("last_week")
    last_month = sales.get("last_month")
    top_items = sales.get("top_items") or []

    def fmt_amt(v):
        try:
            n = float(v or 0)
        except Exception:
            return str(v)
        # Rough INR-style short format for chat
        if n >= 1_00_000:
            return f"₹{n/1_00_000:.1f}L"
        if n >= 1_000:
            return f"₹{n/1_000:.1f}k"
        return f"₹{int(n):,}"

    today_txt = fmt_amt(today) if today is not None else "N/A"
    week_txt = fmt_amt(last_week) if last_week is not None else "N/A"
    month_txt = fmt_amt(last_month) if last_month is not None else "N/A"
    top_str = ", ".join(top_items[:3]) if top_items else "top items data nahi mila"

    location_tag = f" ({city})" if city else ""

    text = (
        f"📊 Sales snapshot — **{store_name}{location_tag}** ke liye:\n\n"
        f"- Aaj ki approximate bikri: {today_txt}\n"
        f"- Last 7 din ka total: {week_txt}\n"
        f"- Pichhle mahine ka total: {month_txt}\n"
        f"- Sabse zyada bikne waale items: {top_str}\n\n"
        "Aap chaho toh main is data se margin, slow-movers ya festival planning pe "
        "bhi detail mein baat kar sakta hoon. Kya dekhna hai next — pricing, inventory ya demand forecast?"
    )

    return {"messages": [AIMessage(content=text)]}
