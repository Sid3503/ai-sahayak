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
    - sales_query: Questions about sales performance, revenue, trends, daily/monthly sales
    - pricing_query: Competitor pricing, market rates, margin analysis, price changes
    - inventory: Stock levels, inventory management, restocking needs, shelf space
    - forecast: Demand forecasting, seasonal trends, festival predictions
    - general_chat: General business advice, store operations, greetings, non-specific queries
    
    Respond ONLY with the exact category name. No explanations.
    
    Query: {user_message}
    """
    
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    response = await llm.ainvoke([SystemMessage(content=intent_classifier_prompt.format(user_message=user_message))])
    
    intent_match = re.search(r"(sales_query|pricing_query|inventory|forecast|general_chat)", response.content)
    intent = intent_match.group(1) if intent_match else "general_chat"
    
    return {"next_intent": intent}
