"""
Alert preferences node: when user says "7 din pehle batao" or "subah 8 baje bhejo",
extract days_before and/or time_hour and update DynamoDB. Reply in Hinglish.
"""
import json
import re
from langchain_core.messages import AIMessage, SystemMessage

from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.tools.data_sources.user_preferences_dynamodb import update_alert_preferences

EXTRACT_PROMPT = """You extract alert preferences from a store owner's message.
Output a JSON object with exactly two optional keys:
- "alert_days_before": integer 1-30 (how many days before a festival to get the alert), or omit if not mentioned
- "alert_time_hour_ist": integer 0-23 (hour in 24h IST when they want daily alert, e.g. 8 for 8 AM, 9 for 9 AM), or omit if not mentioned

Examples:
"7 din pehle batao" -> {"alert_days_before": 7}
"subah 8 baje bhejo" -> {"alert_time_hour_ist": 8}
"9 baje alert chahiye" -> {"alert_time_hour_ist": 9}
"5 days before and 8 AM" -> {"alert_days_before": 5, "alert_time_hour_ist": 8}
"only change time to 10" -> {"alert_time_hour_ist": 10}
"nothing" or "what's the weather" -> {}

User message: {user_message}

Respond with ONLY the JSON object, no other text."""


async def alert_preferences_node(state: ConversationState):
    user_message = (state["messages"][-1].content or "").strip() if state.get("messages") else ""
    user_context = state.get("user_context") or {}
    user_id = user_context.get("user_id") or "demo-user"
    phone = user_context.get("phone_number")

    # Extract preferences via LLM
    llm = get_llm(temperature=0)
    response = await llm.ainvoke([
        SystemMessage(content=EXTRACT_PROMPT.format(user_message=user_message))
    ])
    text = (response.content or "").strip()
    days_before = None
    time_hour = None
    try:
        # Allow JSON inside markdown code block
        json_match = re.search(r"\{[^{}]*\}", text)
        if json_match:
            data = json.loads(json_match.group(0))
            days_before = data.get("alert_days_before")
            time_hour = data.get("alert_time_hour_ist")
        if days_before is not None and not isinstance(days_before, int):
            days_before = int(days_before) if str(days_before).isdigit() else None
        if time_hour is not None and not isinstance(time_hour, int):
            time_hour = int(time_hour) if str(time_hour).isdigit() else None
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    if days_before is None and time_hour is None:
        reply = (
            "Aap batao: festival se kitne din pehle alert chahiye (jaise 3, 5, 7)? "
            "Aur din mein kis time pe bhejna hai (jaise subah 8 baje ya 9 baje)? Dono set kar sakte ho."
        )
        return {"messages": [AIMessage(content=reply)]}

    ok = update_alert_preferences(
        user_id=user_id,
        alert_days_before=days_before,
        alert_time_hour_ist=time_hour,
        phone=phone,
    )
    if not ok:
        reply = "Settings save karte waqt issue aaya. Thodi der baad try karein ya support se baat karein."
        return {"messages": [AIMessage(content=reply)]}

    parts = []
    if days_before is not None:
        parts.append(f"Festival alert ab **{days_before} din pehle** bhejunga.")
    if time_hour is not None:
        parts.append(f"Daily alert **{time_hour}:00 IST** pe bhejunga.")
    reply = "✅ Ho gaya! " + " ".join(parts) + " Kuch aur change karna ho to bolo."
    return {"messages": [AIMessage(content=reply)]}
