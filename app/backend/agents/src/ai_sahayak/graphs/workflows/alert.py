"""
Alert query handler: what-if simulations vs active alerts list.
All data from Dashboard only — no mock. Alerts list comes from Dashboard /api/kpis.
"""
from langchain_core.messages import AIMessage
from ai_sahayak.graphs.nodes.whatif_simulator import whatif_simulator_node
from ai_sahayak.tools.data_sources.dashboard_data_tool import get_dashboard_data


async def handle_alert_query_node(state):
    """
    Dispatcher for alert-related queries.
    "What if..." -> whatif_simulator. Otherwise show alerts from Dashboard only.
    """
    messages = state.get("messages", [])
    last_query = (messages[-1].content or "").lower() if messages else ""

    whatif_triggers = (
        "what if", "agar", "kya hoga", "competitor", "price drop", "price girae",
        "price giraye", "simulate", "simulation", "what happens if", "impact"
    )
    if any(t in last_query for t in whatif_triggers):
        return await whatif_simulator_node(state)

    user_context = state.get("user_context", {})
    user_id = (user_context.get("user_id") or "raju").strip().lower()
    onboarding = state.get("onboarding_data", {})
    owner_name = onboarding.get("name", "").split()[0] if onboarding.get("name") else ""
    name_ref = f"{owner_name} bhai" if owner_name else "bhai"

    data = get_dashboard_data(user_id)
    if not data.get("from_dashboard"):
        return {
            "messages": [AIMessage(content=f"Alerts Dashboard se aate hain {name_ref}. Control Centre connect karein, phir poochhen.")],
            "current_step": "alerts_checked",
        }

    alerts = data.get("alerts") or []
    if not alerts:
        return {
            "messages": [AIMessage(content=f"Abhi koi active alert nahi hai {name_ref}. Sab theek chal raha hai!")],
            "current_step": "alerts_checked",
        }

    alert_msgs = [f"Active alerts (Dashboard se):"]
    for idx, item in enumerate(alerts[:5], 1):
        if isinstance(item, dict):
            title = item.get("title") or item.get("message", "Alert")
            msg = item.get("message") or item.get("title", "")
            alert_msgs.append(f"{idx}. {title}" + (f" — {msg}" if msg and msg != title else ""))
        else:
            alert_msgs.append(f"{idx}. {item}")
    return {
        "messages": [AIMessage(content="\n".join(alert_msgs))],
        "current_step": "alerts_checked",
    }
