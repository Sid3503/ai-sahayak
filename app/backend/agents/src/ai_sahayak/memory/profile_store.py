"""
Load store owner profile into conversation state at graph start.
"""
from ai_sahayak.tools.data_sources.dynamodb_tool import DynamoDBTool
from ai_sahayak.graphs.state.conversation import ConversationState
from langchain_core.runnables import RunnableConfig

_db_tool = None


def _get_db():
    global _db_tool
    if _db_tool is None:
        _db_tool = DynamoDBTool()
    return _db_tool


async def load_profile_into_state(state: ConversationState, config: RunnableConfig = None) -> dict:
    """
    Node that runs at START to load store owner's profile into state.
    Runs before language_detection so planners have full context.
    """
    config = config or {}
    configurable = config.get("configurable", {})
    store_id = configurable.get("actor_id") or configurable.get("thread_id")
    if not store_id:
        return {}

    try:
        db_tool = _get_db()
        profile = await db_tool.get_store_profile(f"store_{store_id}")
        if not profile:
            return {}
        current_context = state.get("user_context", {}) or {}
        return {
            "user_context": {
                **current_context,
                "store_id": store_id,
                "language": profile.get("preferred_lang", "hi"),
                "store_type": profile.get("store_type", "grocery"),
                "city": profile.get("location", ""),
                "pincode": profile.get("pincode", ""),
                "owner_name": profile.get("name", ""),
                "onboarding": profile.get("onboarding_done", False),
            }
        }
    except Exception as e:
        print(f"[load_profile_into_state] {e}")
        return {}
