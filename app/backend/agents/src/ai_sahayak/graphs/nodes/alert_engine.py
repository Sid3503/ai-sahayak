from langchain_core.messages import AIMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.monitoring.alerts import AlertManager

async def alert_engine_node(state: ConversationState):
    """
    Evaluates current business context and dispatches proactive alerts.
    """
    alert_manager = AlertManager()
    user_context = state.get("user_context", {})
    store_id = user_context.get("store_id", "mock_store_123")
    
    # In a full proactive engine, a scheduler would trigger this, or it would run async during a user session.
    # We simulate generating an alert for the user.
    alert = await alert_manager.generate_mock_festival_alert(store_id)
    
    message = f"🚨 **Alert:** {alert.title}\n{alert.message}"
    
    return {
        "messages": [AIMessage(content=message)],
        "current_step": "alert_delivered",
        # Pass the suggested actions back into the state to populate UI chips
        "alert_suggested_actions": alert.suggested_actions
    }
