from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from motor.motor_asyncio import AsyncIOMotorClient
from ai_sahayak.config.settings import settings

class MongoConversationManager:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db.conversation_history

    async def get_conversation_state(self, session_id: str) -> Dict[str, Any]:
        doc = await self.collection.find_one({"session_id": session_id})
        if not doc:
            return {
                "messages": [],
                "current_step": "onboarding",
                "onboarding_data": {},
                "metadata": {}
            }
        
        # We strip out _id and session_id as they aren't part of Langchain state
        doc.pop("_id", None)
        doc.pop("session_id", None)
        return doc

    async def save_conversation_state(self, session_id: str, state: Dict[str, Any]):
        # Serialize messages if they are LangChain objects
        if "messages" in state:
            serializable_messages = []
            for m in state["messages"]:
                if isinstance(m, BaseMessage):
                    # Standard LangChain serialization format
                    serializable_messages.append({
                        "type": m.type,
                        "content": m.content,
                        "additional_kwargs": m.additional_kwargs,
                        "name": getattr(m, "name", None)
                    })
                else:
                    serializable_messages.append(m)
            state["messages"] = serializable_messages
        
        # Upsert the state document
        upsert_doc = state.copy()
        upsert_doc["session_id"] = session_id
        await self.collection.update_one(
            {"session_id": session_id},
            {"$set": upsert_doc},
            upsert=True
        )

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
memory_manager = MongoConversationManager()
get_conversation_state = memory_manager.get_conversation_state
save_conversation_state = memory_manager.save_conversation_state
