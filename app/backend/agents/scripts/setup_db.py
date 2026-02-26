import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_sahayak")

async def setup_database():
    print(f"🚀 Connecting to MongoDB: {DATABASE_NAME}")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    collections = {
        "user_info": {
            "indexes": [
                [ [("user_id", 1)], {"unique": True} ],
                [ [("phone_number", 1)], {"sparse": True} ]
            ]
        },
        "conversation_history": {
            "indexes": [
                [ [("session_id", 1)], {} ],
                [ [("user_id", 1)], {} ],
                [ [("timestamp", -1)], {} ]
            ]
        },
        "stores": {
            "indexes": [
                [ [("store_id", 1)], {"unique": True} ],
                [ [("owner_id", 1)], {} ]
            ]
        },
        "inventory": {
            "indexes": [
                [ [("store_id", 1)], {} ],
                [ [("sku_id", 1)], {} ],
                [ [("store_id", 1), ("sku_id", 1)], {"unique": True} ]
            ]
        },
        "sales": {
            "indexes": [
                [ [("store_id", 1)], {} ],
                [ [("timestamp", -1)], {} ]
            ]
        },
        "audit_logs": {
            "indexes": [
                [ [("timestamp", -1)], {"expireAfterSeconds": 7776000} ]
            ]
        }
    }

    for coll_name, config in collections.items():
        print(f"📦 Setting up collection: {coll_name}")
        if coll_name not in await db.list_collection_names():
            await db.create_collection(coll_name)
        
        for index_spec in config["indexes"]:
            keys = index_spec[0]
            options = index_spec[1]
            idx_name = await db[coll_name].create_index(keys, **options)
            print(f"  ✅ Created index: {idx_name}")

    print("\n✨ Database setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_database())
