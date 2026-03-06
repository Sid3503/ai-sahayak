from langchain_aws import ChatBedrock
from ai_sahayak.config.settings import settings

def get_llm(model_id: str = None, temperature: float = 0.0) -> ChatBedrock:
    """Returns a LangChain ChatBedrock instance. Uses AWS creds from settings/.env."""
    kwargs = {
        "model_id": model_id or settings.DEFAULT_MODEL_ID,
        "region_name": settings.BEDROCK_REGION,
        "model_kwargs": {"temperature": temperature},
    }
    aid = getattr(settings, "AWS_ACCESS_KEY_ID", "") or ""
    secret = getattr(settings, "AWS_SECRET_ACCESS_KEY", "") or ""
    if aid and secret:
        kwargs["aws_access_key_id"] = aid
        kwargs["aws_secret_access_key"] = secret
    return ChatBedrock(**kwargs)
