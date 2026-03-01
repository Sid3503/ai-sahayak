from langchain_core.messages import AIMessage
from langgraph.graph import END

# We can import the nodes
from ai_sahayak.graphs.nodes.alert_engine import alert_engine_node
from ai_sahayak.graphs.nodes.whatif_simulator import whatif_simulator_node

async def handle_alert_query_node(state):
    """
    Dispatcher node for alert-related queries.
    If the user asks "What if...", route to whatif_simulator_node.
    If the system needs to proactively alert, route to alert_engine_node.
    """
    messages = state.get("messages", [])
    last_query = messages[-1].content.lower() if messages else ""
    
    if "what if" in last_query or "agar" in last_query or "kya hoga" in last_query:
        return await whatif_simulator_node(state)
        
    # Default to fetching active alerts if they ask about alerts
    from ai_sahayak.monitoring.alerts import AlertManager
    manager = AlertManager()
    user_context = state.get("user_context", {})
    store_id = user_context.get("store_id", "mock_store_123")
    
    alerts = await manager.get_active_alerts(store_id)
    if not alerts:
        return {
            "messages": [AIMessage(content="You have no active alerts right now. Your business is running smoothly!")],
            "current_step": "alerts_checked"
        }
    
    alert_msgs = ["Here are your active alerts:"]
    for idx, alert in enumerate(alerts, 1):
        alert_msgs.append(f"{idx}. [{alert.severity}] {alert.title} - {alert.message}")
        
    return {
        "messages": [AIMessage(content="\n\n".join(alert_msgs))],
        "current_step": "alerts_checked"
    }
