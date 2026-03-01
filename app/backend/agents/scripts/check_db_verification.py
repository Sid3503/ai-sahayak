import asyncio
import os
import sys

# Add src to path to import settings
sys.path.append(os.path.join(os.getcwd(), 'src'))

from ai_sahayak.tools.data_sources.mongodb_tool import MongoDBTool
from ai_sahayak.config.settings import settings

async def check_db():
    print(f"Connecting to: {settings.MONGODB_URI}")
    db_tool = MongoDBTool()
    db = db_tool.db
    
    print("\n--- User Profiles ---")
    users = await db.user_info.find().sort("_id", -1).to_list(length=10)
    for user in users:
        print(user)
        
    print("\n--- Store Profiles ---")
    stores = await db.stores.find().sort("_id", -1).to_list(length=10)
    for store in stores:
        print(store)

if __name__ == "__main__":
    asyncio.run(check_db())
