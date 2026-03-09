from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.dashboard_drive_ui import notify_dashboard_drive_ui


async def sales_query_node(state: ConversationState):
    """
    Answer sales questions using dashboard data for the current retailer.
    Uses the same user_id as Dashboard / My day: raju, ramesh, suresh, kanta, lakshmi.
    """
    user_context = state.get("user_context") or {}
    user_id = (user_context.get("user_id") or "unknown_user").strip().lower()
    onboarding_data = state.get("onboarding_data", {})
    messages = state.get("messages", [])
    
    # Real data only from Dashboard API (no mock)
        data = get_dashboard_data(user_id)
    from_dashboard = data.get("from_dashboard", False)
    store = data.get("store_info", {}) or {}
    sales = data.get("sales_summary", {}) or {}
    overview_kpis = data.get("overview_kpis") or {}
    alerts = data.get("alerts") or []
    inv = data.get("inventory_summary") or {}

    store_name = onboarding_data.get("store_name") or store.get("name", "your store")
    city = onboarding_data.get("resolved_location") or store.get("city")
    
    preferred_lang = onboarding_data.get("preferred_language", "English").lower()
    owner_name = onboarding_data.get("name", "").split()[0] if onboarding_data.get("name") else ""
    name_ref = f"{owner_name} bhai" if owner_name else "bhai"

    if preferred_lang in ["english", "en"]:
        lang_instruction = f"Reply in English, friendly and brief. Address the owner as {name_ref if owner_name else 'friend'}."
    elif preferred_lang in ["hindi", "hi"]:
        lang_instruction = "Reply in Hindi only, using Devanagari script. Max 2-3 sentences."
    elif preferred_lang in ["hinglish"]:
        lang_instruction = (
            f"You MUST reply ONLY in Hinglish (Hindi + English Roman script), like a dost talking to {name_ref}. "
            "Max 2-3 SHORT sentences. No bullet lists, no markdown, no numbered points. "
            "Use varied casual openers each time — e.g. 'Bilkul bhai', 'Haan', 'Dekho', 'Aaj ki baat karein', 'Kal se compare karein toh'. "
            "Include the actual numbers from data. Keep it warm and human, not robotic."
        )
    else:
        lang_instruction = "Reply in English, brief and friendly."

    if not from_dashboard or not sales:
        text = (
            "Haan bhai, abhi Dashboard se data connect nahi ho pa raha. Control Centre (Dashboard) open karke thodi der baad phir poochhen — tab real numbers bata paunga."
        ) if preferred_lang in ["hinglish"] else (
            "Dashboard is not connected right now. Open the Control Centre and try again in a moment — I'll use your real data then."
        )
        return {"messages": [AIMessage(content=text)]}

    # Build sales + overview context from real dashboard data
    sales_context = f"Store: {store_name}"
    if city:
        city_short = str(city).split(",")[0].strip() if "," in str(city) else str(city)
            sales_context += f" ({city_short})"
    sales_context += "\n\n"
    
    if sales.get("today") is not None:
        sales_context += f"Today's sales: ₹{sales['today']:,.0f}\n"
    if sales.get("last_week") is not None:
        sales_context += f"Last 7 days total: ₹{sales['last_week']:,.0f}\n"
    if sales.get("last_month") is not None:
        sales_context += f"Last month total: ₹{sales['last_month']:,.0f}\n"
    
    top_items = sales.get("top_items") or []
    if top_items:
        sales_context += f"Top selling items: {', '.join(top_items[:5])}\n"

    if overview_kpis:
        sales_context += "\nOverview (from Dashboard):\n"
        if overview_kpis.get("revenue_30d") is not None:
            sales_context += f"Revenue (30d): ₹{overview_kpis['revenue_30d']:,.0f}\n"
        if overview_kpis.get("profit_30d") is not None:
            sales_context += f"Profit (30d): ₹{overview_kpis.get('profit_30d', 0):,.0f}\n"
        if overview_kpis.get("units_30d") is not None:
            sales_context += f"Units (30d): {overview_kpis.get('units_30d', 0):,.0f}\n"
        if overview_kpis.get("sell_through_pct") is not None:
            sales_context += f"Sell through: {overview_kpis.get('sell_through_pct', 0):.1f}%\n"
        if overview_kpis.get("avg_margin_pct") is not None:
            sales_context += f"Avg margin: {overview_kpis.get('avg_margin_pct', 0):.1f}%\n"
        if overview_kpis.get("reorder_risk_skus") is not None and overview_kpis["reorder_risk_skus"] > 0:
            sales_context += f"Reorder risk: {overview_kpis['reorder_risk_skus']} SKU(s) below reorder point.\n"
        if overview_kpis.get("low_cover_skus") is not None and overview_kpis["low_cover_skus"] > 0:
            sales_context += f"Low cover: {overview_kpis['low_cover_skus']} SKU(s).\n"
        if overview_kpis.get("festival_days_last30") is not None and overview_kpis["festival_days_last30"] > 0:
            sales_context += f"Festival days (last 30d): {overview_kpis['festival_days_last30']}.\n"
    if alerts:
        sales_context += "\nAlerts (use for suggestions): " + "; ".join(alerts[:3]) + "\n"
    low_stock = inv.get("low_stock") or []
    if low_stock:
        sales_context += f"Low stock / reorder items: {', '.join(low_stock[:5])}\n"

    # Extract what the user actually asked about so LLM can tailor the reply
    last_user_q = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage) and hasattr(m, "content"):
            last_user_q = (m.content or "").strip()
            break

    system_prompt = f"""You are AI Sahayak, a smart assistant for Indian Kirana store owners.
{lang_instruction}

## Sales Data:
{sales_context}

## User's question: "{last_user_q}"

Use ONLY the numbers above (real Dashboard data — do not invent any). Format in an EASY-TO-READ way:
- Put key numbers in a **markdown table** with 2 columns (Metric | Value). Example:
  | Revenue (30d) | ₹4,97,863 |
  | Profit (30d) | ₹9,782 |
  | Top items | Wheat Atta, Refined Oil, Ghee |
- Or use **bold labels** on one line each: **Revenue (30d):** ₹X  **Profit (30d):** ₹Y
- After the table/labels, add 1-2 SHORT sentences in Hinglish (e.g. suggestion if reorder risk or alerts exist).
- Simple language only — like a local friend. No fancy or AI-generated English. Tables or bold for data; then brief comment."""

    try:
        llm = get_llm(temperature=0.75)
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            *[m for m in messages if hasattr(m, "content")][-5:],
        ])
        reply = (response.content or "").strip() if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"Sales query node error: {e}")
        reply = "Abhi sales data nahi aa paaya. Thodi der baad try karein." if preferred_lang in ["hinglish"] else "Unable to fetch sales data right now. Please try again."

    # Drive dashboard to Insights or Overview tab so judges see chat → dashboard movement
    last_user_text = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage) and hasattr(m, "content"):
            last_user_text = (m.content or "").strip().lower()
            break
    drive_action = "overview" if any(k in last_user_text for k in ("overview", "summary", "dashboard", "kpi", "pulse", "business pulse")) else "insights"
    notify_dashboard_drive_ui(drive_action, {"dataset_key": user_id, "sales_summary": sales, "store_info": store})

    return {"messages": [AIMessage(content=reply)]}
