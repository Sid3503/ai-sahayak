import os
import boto3
import json
import asyncio
import datetime
from decimal import Decimal
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from ai_sahayak.config.settings import settings

class DynamoDBConversationManager:
    def __init__(self):
        self.env = os.getenv("APP_ENV", "prod")
        self._dynamodb = None
        self._table = None
    
    @property
    def dynamodb(self):
        if self._dynamodb is None:
            self._dynamodb = boto3.resource(
                "dynamodb",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        return self._dynamodb
    
    @property
    def table(self):
        if self._table is None:
            table_name = settings.CONVERSATIONS_TABLE
            self._table = self.dynamodb.Table(table_name)
        return self._table

    async def get_conversation_state(self, session_id: str) -> Dict[str, Any]:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key={"session_id": session_id}
        )
        
        if "Item" not in response:
            return {
                "messages": [],
                "current_step": "onboarding",
                "onboarding_data": {},
                "metadata": {}
            }
        
        doc = response["Item"]
        # remove Dynamo keys from Langchain state
        doc.pop("session_id", None)
        return doc
        
    async def save_conversation_state(self, session_id: str, state: Dict[str, Any]):
        # Serialize messages
        if "messages" in state:
            serializable_messages = []
            for m in state["messages"]:
                if isinstance(m, BaseMessage):
                    serializable_messages.append({
                        "type": m.type,
                        "content": m.content,
                        "additional_kwargs": m.additional_kwargs,
                        "name": getattr(m, "name", None)
                    })
                else:
                    serializable_messages.append(m)
        # Trim to last 20 messages to stay within DynamoDB's 400KB item limit
        state["messages"] = serializable_messages[-20:]
            
        # Dynamodb float -> Decimal
        state_json = json.dumps(state)
        upsert_doc = json.loads(state_json, parse_float=Decimal)
        
        upsert_doc["session_id"] = session_id
        
        import asyncio
        await asyncio.to_thread(self.table.put_item, Item=upsert_doc)

def restore_messages(messages: List[Dict[str, Any]]) -> List[BaseMessage]:
    restored = []
    for m in messages:
        m_type = m.get("type", "human")
        content = m.get("content", "")
        name = m.get("name")
        if m_type == "human":
            restored.append(HumanMessage(content=content, name=name))
        elif m_type == "ai":
            restored.append(AIMessage(content=content, name=name))
    return restored

# Singleton instance
memory_manager = DynamoDBConversationManager()
get_conversation_state = memory_manager.get_conversation_state
save_conversation_state = memory_manager.save_conversation_state
