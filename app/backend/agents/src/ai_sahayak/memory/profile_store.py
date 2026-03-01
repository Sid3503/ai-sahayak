from ai_sahayak.tools.data_sources.dynamodb_tool import DynamoDBTool
from ai_sahayak.graphs.state.conversation import ConversationState
from langchain_core.runnables import RunnableConfig

db_tool = DynamoDBTool()

async def load_profile_into_state(state: ConversationState, config: RunnableConfig) -> dict:
    """
    Node that runs at START to load store owner's profile into state.
    Runs before pre_memory so planners have full context.
    """
    store_id = config["configurable"].get("actor_id")
    if not store_id:
        return {}

    profile = await db_tool.get_store_profile(f"store_{store_id}")
    if profile:
        current_context = state.get("user_context", {})
        return {
            "user_context": {
                **current_context,
                "store_id":     store_id,
                "language":     profile.get("preferred_lang", "hi"),
                "store_type":   profile.get("store_type", "grocery"),
                "city":         profile.get("location", ""),
                "pincode":      profile.get("pincode", ""),
                "owner_name":   profile.get("name", ""),
                "onboarding":   profile.get("onboarding_done", False),
            }
        }
    return {}
