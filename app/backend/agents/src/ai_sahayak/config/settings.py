from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Sahayak"
    # Deprecated: use DynamoDB (USERS_TABLE, STORES_TABLE, CONVERSATIONS_TABLE). Left for legacy scripts.
    MONGODB_URI: str = ""
    DATABASE_NAME: str = "ai_sahayak"

    BEDROCK_REGION: str = "ap-south-1"
    DEFAULT_MODEL_ID: str = "amazon.nova-lite-v1:0"
    REASONING_MODEL_ID: str = "amazon.nova-lite-v1:0"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    APP_ENV: str = "dev"

    WHATSAPP_VERIFY_TOKEN: str = "sahayak_secret"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    AGENTCORE_MEMORY_ID: str = ""
    AGENTCORE_GATEWAY_ENDPOINT: str = ""

    CALENDAR_S3_BUCKET: str = ""
    CALENDAR_S3_KEY: str = "panchang/events.json"
    USERS_TABLE: str = "ai_sahayak_user_info"
    STORES_TABLE: str = "ai_sahayak_stores"
    CONVERSATIONS_TABLE: str = "ai_sahayak_conversation_history"
    ALERTS_TABLE: str = ""
    BEDROCK_KNOWLEDGE_BASE_ID: str = "PF0KY6SM7W"

    # Cognito: create user when onboarding generates ID/pass so they can sign in on Dashboard
    COGNITO_USER_POOL_ID: str = ""

    # Transcribe: S3 bucket for voice message audio (required for speech-to-text in onboarding)
    TRANSCRIBE_MEDIA_BUCKET: str = ""

    # Dashboard API base URL for live KPIs (/api/kpis, /api/meta, etc.).
    # Env var: AI_SAHAYAK_API_BASE_URL
    ai_sahayak_api_base_url: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignore extra env vars (e.g. AWS_DEFAULT_REGION) so .env is flexible

settings = Settings()
