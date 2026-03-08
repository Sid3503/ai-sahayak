from typing import Literal
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
import re

async def classify_intent_node(state: ConversationState):
    """
    Route conversations to appropriate dashboard workflow based on intent
    """
    llm = get_llm(temperature=0.1)
    
    intent_classifier_prompt = """You are an intent classifier for an Indian Kirana store dashboard assistant.
    Categorize the user query into EXACTLY one of these categories:

    - sales_query: Any question about sales, revenue, KPIs, business pulse, overview, performance, "kaisa chal raha", top items, monthly/weekly/daily figures
    - pricing_query: Price recommendation for a product, margin, market price, competitor pricing, "price kya hoga", "show review", "last price run", price for sugar/atta/oil etc.
    - inventory: Stock levels, low stock, reorder, restocking, inventory, shelf management
    - forecast: Demand forecast, seasonal trends, festival stock prediction, next week/month demand
    - image_analysis: User uploaded a photo of store shelves or products
    - alert_query: "what if" scenarios, competitor drops price, festival impact simulation, what happens if, "kya hoga agar"
    - alert_preferences: User wants to CHANGE alert timing/settings (e.g. "7 din pehle batao", "8 baje bhejo")
    - general_chat: Greetings (hello, hi, namaste), "what can you help", "what can you do", general store advice not covered above

    IMPORTANT RULES:
    - "KPIs", "business pulse", "overview", "how are my sales", "sales kaisi hain" → sales_query
    - "show review", "price review" → pricing_query
    - "what if competitor drops" → alert_query
    - "hello", "hi", "what can you help" → general_chat

    Respond ONLY with the exact category name. No explanations.

    Query: {user_message}
    """
    
    user_message = (state["messages"][-1].content or "").strip().lower() if state["messages"] else ""
    msg_trim = user_message.strip()

    # Fast path: if the payload included an image, force image analysis intent
    if state.get("image_path"):
        return {"next_intent": "image_analysis"}
    # Fast path: greetings only — skip LLM classifier to reduce latency
    greeting_only = msg_trim in (
        "hello", "hi", "hey", "hlw", "hii", "namaste", "namaskar", "haan", "ji", "good morning",
        "good afternoon", "good evening", "good night", "gm", "gn"
    ) or (len(msg_trim) <= 20 and re.match(r"^(hello|hi|hey|namaste|namaskar|haan)\s*!?\.?$", msg_trim))
    if greeting_only:
        return {"next_intent": "general_chat"}
    # Fast path: alert time/days — no LLM needed (works without Bedrock)
    if re.search(r"\d+\s*baje|bhejo|alert\s*(time|chahiye|at)|din\s*pehle\s*batao|\d+\s*(am|pm)|alert\s+at|send\s+(me\s+)?alert", user_message):
        return {"next_intent": "alert_preferences"}
    # Fast paths (English + Hinglish) to avoid LLM misclassification
    if any(w in user_message for w in (
        "what if", "agar kya", "kya hoga agar", "competitor", "price drop", "price gira", "price giraye",
        "competitor ne", "simulate", "impact kya hoga"
    )):
        return {"next_intent": "alert_query"}
    if any(w in user_message for w in (
        "kpi", "business pulse", "overview", "sales kaisi", "how are my sales", "sales kaise",
        "mera overview", "overview batao", "dimaag kya keh raha", "pulse kaisa", "revenue kya",
        "profit kya", "units kya", "sell through", "margin kya"
    )):
        return {"next_intent": "sales_query"}
    if any(w in user_message for w in (
        "show review", "price review", "last price run", "price recommendation",
        "price kya", "atta ka price", "sugar ka price", "chini ka price", "tel ka price", "ghee ka price",
        "recommend kya", "market price", "margin batao"
    )):
        return {"next_intent": "pricing_query"}
    if any(w in user_message for w in ("forecast", "demand kya", "aage demand", "festival demand")):
        return {"next_intent": "forecast"}
    
    response = await llm.ainvoke([SystemMessage(content=intent_classifier_prompt.format(user_message=user_message))])
    
    intent_match = re.search(r"(sales_query|pricing_query|inventory|forecast|image_analysis|alert_query|alert_preferences|general_chat)", response.content)
    intent = intent_match.group(1) if intent_match else "general_chat"
    
    return {"next_intent": intent}
