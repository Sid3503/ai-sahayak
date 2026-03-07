from langchain_aws import ChatBedrock
from ai_sahayak.config.settings import settings

def get_llm(model_id: str = None, temperature: float = 0.0) -> ChatBedrock:
    """Returns a LangChain ChatBedrock instance. Uses AWS creds from settings/.env."""
    mid = model_id or settings.DEFAULT_MODEL_ID
    # Nova models use Converse API; Qwen/others use legacy InvokeModel
    use_converse = "nova" in (mid or "").lower()
    kwargs = {
        "model_id": mid,
        "region_name": settings.BEDROCK_REGION,
        "model_kwargs": {"temperature": temperature},
        "beta_use_converse_api": use_converse,
    }
    aid = getattr(settings, "AWS_ACCESS_KEY_ID", "") or ""
    secret = getattr(settings, "AWS_SECRET_ACCESS_KEY", "") or ""
    if aid and secret:
        kwargs["aws_access_key_id"] = aid
        kwargs["aws_secret_access_key"] = secret
    return ChatBedrock(**kwargs)
