from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Sahayak"
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_sahayak"
    
    BEDROCK_REGION: str = "ap-south-1"
    DEFAULT_MODEL_ID: str = "qwen.qwen3-32b-v1:0"
    REASONING_MODEL_ID: str = "qwen.qwen3-32b-v1:0"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AGENTCORE_MEMORY_ID: str = ""
    AWS_REGION: str = "ap-south-1"
    APP_ENV: str = "dev"
    
    WHATSAPP_VERIFY_TOKEN: str = "sahayak_secret"
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""    
    class Config:
        env_file = ".env"

settings = Settings()
