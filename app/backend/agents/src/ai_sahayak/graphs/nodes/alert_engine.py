from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def alert_engine_node(state: ConversationState):
    """
    Proactive alerts from Dashboard only — no mock. Shows first alert from Dashboard /api/kpis if any.
    """
    user_context = state.get("user_context", {})
    user_id = (user_context.get("user_id") or "raju").strip().lower()
    data = get_dashboard_data(user_id)

    if not data.get("from_dashboard") or not data.get("alerts"):
        return {
            "messages": [AIMessage(content="Abhi koi naya alert nahi hai. Dashboard se data aate hi bataunga.")],
            "current_step": "alert_delivered",
            "alert_suggested_actions": [],
        }
    alerts = data.get("alerts", [])
    first = alerts[0]
    if isinstance(first, dict):
        title = first.get("title") or first.get("message", "Alert")
        message = first.get("message") or first.get("title", "")
    else:
        title, message = "Alert", str(first)
    msg_text = f"**{title}**\n{message}" if message else f"**{title}**"
    return {
        "messages": [AIMessage(content=msg_text)],
        "current_step": "alert_delivered",
        "alert_suggested_actions": first.get("actions", []) if isinstance(first, dict) else [],
    }
