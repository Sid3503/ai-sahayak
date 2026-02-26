from typing import Generator
from ai_sahayak.config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient

def get_mongodb_client() -> Generator:
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    try:
        yield client
    finally:
        client.close()

def get_database(client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    return client[settings.DATABASE_NAME]
