"""Profile API: get display name by user_id (Cognito username) for Dashboard greeting."""
from fastapi import APIRouter, Query

from ai_sahayak.tools.data_sources.dynamodb_tool import DynamoDBTool

router = APIRouter()


@router.get("/profile")
async def get_profile(user_id: str = Query(..., description="Cognito username / User ID (e.g. 9004755498)")):
    """Return display name for the given user_id so the Dashboard can show 'Namaste, {name}!'.
    Used when Cognito does not have the name attribute (e.g. existing users)."""
    try:
        db = DynamoDBTool()
        profile = await db.get_user_profile(user_id)
        if not profile:
            return {"name": None}
        return {"name": profile.get("name")}
    except Exception:
        return {"name": None}
