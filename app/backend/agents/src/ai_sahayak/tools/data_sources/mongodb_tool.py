from motor.motor_asyncio import AsyncIOMotorClient
from ai_sahayak.config.settings import settings

class MongoDBTool:
    def __init__(self, db_name: str = settings.DATABASE_NAME):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[db_name]

    async def get_store_profile(self, store_id: str):
        return await self.db.stores.find_one({"store_id": store_id})

    async def upsert_user_profile(self, user_id: str, name: str, phone: str = None):
        """Optimally insert or update a user profile."""
        update_data = {"name": name}
        if phone:
            update_data["phone_number"] = phone
            
        await self.db.user_info.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )

    async def upsert_store_profile(self, user_id: str, store_name: str, location: str):
        """Optimally insert or update a store profile, linking to the user."""
        # Using a deterministic store_id based on user_id for 1:1 relationship in MVP
        store_id = f"store_{user_id}"
        
        await self.db.stores.update_one(
            {"store_id": store_id},
            {"$set": {
                "owner_id": user_id,
                "name": store_name,
                "location": location
            }},
            upsert=True
        )
