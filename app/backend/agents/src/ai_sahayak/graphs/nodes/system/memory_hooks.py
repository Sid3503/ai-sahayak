import uuid
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph_checkpoint_aws import AgentCoreMemoryStore
from ai_sahayak.graphs.state.conversation import ConversationState

MEMORY_ID  = os.getenv("AGENTCORE_MEMORY_ID")
REGION     = os.getenv("AWS_REGION", "ap-south-1")

if MEMORY_ID:
    # Single shared store instance — re-used across all hooks
    memory_store = AgentCoreMemoryStore(memory_id=MEMORY_ID, region_name=REGION)
else:
    memory_store = None

def pre_model_hook(state: ConversationState, config: RunnableConfig, *, store: BaseStore) -> dict:
    """
    Runs before each LLM call.
    1. Saves latest human message → AgentCore extracts preferences in background
    2. Retrieves relevant long-term memories → injected into state as context
    """
    if not store:
        return {}
        
    actor_id  = config["configurable"].get("actor_id", "default_actor")
    thread_id = config["configurable"].get("thread_id", "default_thread")

    messages  = state.get("messages", [])

    # ── Step 1: Save latest human message ─────────────────────────────────
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            # namespace = (actor_id, thread_id) → ties message to this session
            store.put(
                (actor_id, thread_id),
                str(uuid.uuid4()),
                {"message": msg.model_dump()}        # AgentCore auto-extracts preferences from this
            )

            # ── Step 2: Retrieve cross-session memories for this actor ─────
            try:
                preferences = store.search(
                    ("preferences", actor_id),   # cross-session namespace
                    query=msg.content,
                    limit=5
                )

                if preferences:
                    memory_lines = "\n".join([
                        f"- {item.value.get('message', {}).get('content', '')}"
                        for item in preferences
                        if item.value.get("message")
                    ])
                    return {"memory_context": memory_lines}

            except Exception as e:
                # Never let memory failure break the main agent flow
                print(f"[Memory] Long-term retrieval skipped: {e}")
            break

    return {}   # no-op if no human message found


def post_model_hook(state: ConversationState, config: RunnableConfig, *, store: BaseStore) -> dict:
    """
    OPTIONAL — runs after each LLM call.
    Saves AI responses so AgentCore can extract summaries and facts.
    """
    if not store:
        return {}
        
    actor_id  = config["configurable"].get("actor_id", "default_actor")

    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage):
            store.put(
                ("preferences", actor_id),   # cross-session: available in future sessions
                str(uuid.uuid4()),
                {"message": msg.model_dump()}
            )
            break

    return {}
