# Optional MongoDB deps (deprecated – we use DynamoDB for conversation and profiles).
# Kept for backward compatibility if any script still needs them.
from typing import Generator, Any

def get_mongodb_client() -> Generator[Any, None, None]:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from ai_sahayak.config.settings import settings
        if getattr(settings, "MONGODB_URI", ""):
            client = AsyncIOMotorClient(settings.MONGODB_URI)
            try:
                yield client
            finally:
                client.close()
            return
    except Exception:
        pass
    yield None

def get_database(client: Any = None):
    if client is None:
        return None
    from ai_sahayak.config.settings import settings
    return client[getattr(settings, "DATABASE_NAME", "ai_sahayak")]
