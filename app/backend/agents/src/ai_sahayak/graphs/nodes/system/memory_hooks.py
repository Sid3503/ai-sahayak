import uuid
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from ai_sahayak.graphs.state.conversation import ConversationState

MEMORY_ID = os.getenv("AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION", "ap-south-1")

try:
    from langgraph_checkpoint_aws import AgentCoreMemoryStore
    memory_store = AgentCoreMemoryStore(memory_id=MEMORY_ID, region_name=REGION) if MEMORY_ID else None
except Exception:
    memory_store = None


def pre_model_hook(state: ConversationState, config: RunnableConfig, *, store: BaseStore) -> dict:
    """
    Runs before each LLM call.
    1. Saves latest human message → AgentCore extracts preferences in background
    2. Retrieves relevant long-term memories → injected into state as context
    """
    if not store:
        return {}

    actor_id = config["configurable"].get("actor_id", "default_actor")
    thread_id = config["configurable"].get("thread_id", "default_thread")
    messages = state.get("messages", [])

    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            store.put(
                (actor_id, thread_id),
                str(uuid.uuid4()),
                {"message": msg.model_dump()},
            )
            try:
                preferences = store.search(
                    ("preferences", actor_id),
                    query=msg.content,
                    limit=5,
                )
                if preferences:
                    memory_lines = "\n".join([
                        f"- {item.value.get('message', {}).get('content', '')}"
                        for item in preferences
                        if item.value.get("message")
                    ])
                    return {"memory_context": memory_lines}
            except Exception as e:
                print(f"[Memory] Long-term retrieval skipped: {e}")
            break
    return {}


def post_model_hook(state: ConversationState, config: RunnableConfig, *, store: BaseStore) -> dict:
    """Runs after each LLM call. Saves AI responses so AgentCore can extract summaries and facts."""
    if not store:
        return {}

    actor_id = config["configurable"].get("actor_id", "default_actor")
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage):
            store.put(
                ("preferences", actor_id),
                str(uuid.uuid4()),
                {"message": msg.model_dump()},
            )
            break
    return {}
