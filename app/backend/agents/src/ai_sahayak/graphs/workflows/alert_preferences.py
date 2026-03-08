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


def _extract_alert_preferences_regex(message: str) -> tuple:
    """Extract (days_before, time_hour 0-23, time_minute 0|30|None) from Hinglish. AM default; shaam/raat/pm -> PM."""
    message = (message or "").strip().lower()
    days_before = None
    time_hour = None
    time_minute = None  # 0 = top of hour, 30 = half past, None = not set
    is_pm = "shaam" in message or "raat" in message or "pm" in message or "evening" in message or "night" in message
    # e.g. "7:30 bhejo", "sade saat", "8:30 baje"
    m = re.search(r"(?:subah\s+)?(\d{1,2})\s*:\s*30|sade\s+(\d{1,2})|(\d{1,2})\s*baje\s*(\d{1,2})", message)
    if m:
        h = int(m.group(1) or m.group(2) or m.group(3) or 7)
        if m.group(4):
            try:
                mn = int(m.group(4))
                if mn == 30:
                    time_minute = 30
            except (TypeError, ValueError):
                pass
        else:
            time_minute = 30
        if is_pm and h != 12:
            h += 12
        elif not is_pm and h == 12:
            h = 0
        if 0 <= h <= 23:
            time_hour = h
    if time_hour is None:
        # e.g. "8 baje bhejo", "9 baje", "subah 8 baje", "8:00 bhejo" (top of hour)
        m = re.search(r"(?:subah\s+)?(\d{1,2})\s*baje|(\d{1,2})\s*:\s*00", message)
        if m:
            h = int(m.group(1) or m.group(2) or 9)
            if is_pm and h != 12:
                h += 12
            elif not is_pm and h == 12:
                h = 0
            if 0 <= h <= 23:
                time_hour = h
                time_minute = 0  # top of hour
    if time_hour is None:
        m = re.search(r"(\d{1,2})\s*(am|pm)", message)
        if m:
            h = int(m.group(1))
            if m.group(2).lower() == "pm" and h != 12:
                h += 12
            elif m.group(2).lower() == "am" and h == 12:
                h = 0
            if 0 <= h <= 23:
                time_hour = h
                time_minute = 0
    # e.g. "7 din pehle batao"
    m = re.search(r"(\d{1,2})\s*din\s*pehle", message)
    if m:
        d = int(m.group(1))
        if 1 <= d <= 30:
            days_before = d
    return (days_before, time_hour, time_minute)


async def alert_preferences_node(state: ConversationState):
    user_message = (state["messages"][-1].content or "").strip() if state.get("messages") else ""
    user_context = state.get("user_context") or {}
    # Normalize to lowercase so we always update same item as Lambda (raju, ramesh, etc.)
    user_id = ((user_context.get("user_id") or "demo-user").strip() or "raju").lower()
    phone = user_context.get("phone_number")

    # 1) Regex first — no Bedrock needed for "8 baje bhejo" / "7:30 bhejo" / "7 din pehle"
    days_before, time_hour, time_minute = _extract_alert_preferences_regex(user_message)

    # 2) If regex found nothing, try LLM (may fail if Bedrock not configured)
    if days_before is None and time_hour is None:
        try:
            llm = get_llm(temperature=0)
            response = await llm.ainvoke([
                SystemMessage(content=EXTRACT_PROMPT.format(user_message=user_message))
            ])
            text = (response.content or "").strip()
            try:
                json_match = re.search(r"\{[^{}]*\}", text)
                if json_match:
                    data = json.loads(json_match.group(0))
                    days_before = data.get("alert_days_before")
                    time_hour = data.get("alert_time_hour_ist")
                    if days_before is not None and not isinstance(days_before, int):
                        days_before = int(days_before) if str(days_before).isdigit() else None
                    if time_hour is not None and not isinstance(time_hour, int):
                        time_hour = int(time_hour) if str(time_hour).isdigit() else None
                    time_minute = 0  # LLM only extracts hour
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        except Exception as e:
            print(f"alert_preferences LLM fallback failed: {e}")
        if days_before is None and time_hour is None:
            reply = (
                "Aap batao: festival se kitne din pehle alert chahiye (jaise 3, 5, 7)? "
                "Aur din mein kis time pe bhejna hai (jaise 8 baje, 7:30, shaam 7 baje)? Dono set kar sakte ho."
            )
            return {"messages": [AIMessage(content=reply)]}

    ok = update_alert_preferences(
        user_id=user_id,
        alert_days_before=days_before,
        alert_time_hour_ist=time_hour,
        alert_time_minute_ist=time_minute if time_minute is not None else 0,
        phone=phone,
    )
    if not ok:
        parts = []
        if time_hour is not None:
            mm = (time_minute if time_minute is not None else 0)
            parts.append(f"Daily alert {time_hour}:{mm:02d} IST pe bhejunga.")
        if days_before is not None:
            parts.append(f"Festival {days_before} din pehle bataunga.")
        reply = "✅ " + " ".join(parts) + " (Backend storage connect nahi hai — demo ke liye yahin se kaam karega.)"
        return {"messages": [AIMessage(content=reply)]}

    parts = []
    if days_before is not None:
        parts.append(f"Festival alert ab **{days_before} din pehle** bhejunga.")
    if time_hour is not None:
        mm = (time_minute if time_minute is not None else 0)
        time_str = f"{time_hour}:{mm:02d}" if mm else f"{time_hour}:00"
        parts.append(f"Daily alert **{time_str} IST** pe bhejunga.")
    reply = "✅ Ho gaya! " + " ".join(parts) + " Kuch aur change karna ho to bolo."
    return {"messages": [AIMessage(content=reply)]}
