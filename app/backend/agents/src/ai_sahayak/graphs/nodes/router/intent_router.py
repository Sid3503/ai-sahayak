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
    
    intent_classifier_prompt = """You are an intent classifier for a retail store owner dashboard assistant.
    Categorize the user query into one of these categories:
    - sales_query: Questions about sales performance, revenue, trends, daily/monthly sales, business insights, overview summary
    - pricing_query: Competitor pricing, market rates, margin analysis, price changes, price recommendation, last price run review, "review chahiye"
    - inventory: Stock levels, inventory management, restocking needs, shelf space
    - forecast: Demand forecasting, seasonal trends, festival predictions
    - image_analysis: User uploading a photo of their store shelves or stock for analysis
    - alert_query: Questions starting with 'what if', or asking about alerts, simulations, festivals, active alerts
    - alert_preferences: User wants to change alert settings (e.g. "7 din pehle batao", "subah 8 baje bhejo", "9 baje alert chahiye")
    - general_chat: General business advice, store operations, greetings, non-specific queries
    
    Respond ONLY with the exact category name. No explanations.
    
    Query: {user_message}
    """
    
    user_message = (state["messages"][-1].content or "").strip().lower() if state["messages"] else ""
    
    # Fast path: if the payload included an image, force image analysis intent
    if state.get("image_path"):
        return {"next_intent": "image_analysis"}
    # Fast path: alert time/days — no LLM needed (works without Bedrock)
    if re.search(r"\d+\s*baje|bhejo|alert\s*(time|chahiye)|din\s*pehle\s*batao", user_message):
        return {"next_intent": "alert_preferences"}
    
    response = await llm.ainvoke([SystemMessage(content=intent_classifier_prompt.format(user_message=user_message))])
    
    intent_match = re.search(r"(sales_query|pricing_query|inventory|forecast|image_analysis|alert_query|alert_preferences|general_chat)", response.content)
    intent = intent_match.group(1) if intent_match else "general_chat"
    
    return {"next_intent": intent}
