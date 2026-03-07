from langchain_aws import ChatBedrock
from ai_sahayak.config.settings import settings

# Nova Lite with Converse requires an inference profile (not raw model ID) for on-demand.
# Map region -> inference profile ID per Bedrock docs (APAC / US / EU / etc.).
_NOVA_LITE_INFERENCE_PROFILE_BY_REGION = {
    "ap-south-1": "apac.amazon.nova-lite-v1:0",
    "ap-south-2": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-1": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-2": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-3": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-4": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-5": "apac.amazon.nova-lite-v1:0",
    "ap-southeast-7": "apac.amazon.nova-lite-v1:0",
    "ap-northeast-1": "apac.amazon.nova-lite-v1:0",
    "ap-northeast-2": "apac.amazon.nova-lite-v1:0",
    "ap-northeast-3": "apac.amazon.nova-lite-v1:0",
    "ap-east-2": "apac.amazon.nova-lite-v1:0",
    "me-central-1": "apac.amazon.nova-lite-v1:0",
    "us-east-1": "us.amazon.nova-lite-v1:0",
    "us-east-2": "us.amazon.nova-lite-v1:0",
    "us-west-1": "us.amazon.nova-lite-v1:0",
    "us-west-2": "us.amazon.nova-lite-v1:0",
    "eu-central-1": "eu.amazon.nova-lite-v1:0",
    "eu-west-1": "eu.amazon.nova-lite-v1:0",
    "eu-west-2": "eu.amazon.nova-lite-v1:0",
    "eu-west-3": "eu.amazon.nova-lite-v1:0",
    "eu-north-1": "eu.amazon.nova-lite-v1:0",
    "eu-south-1": "eu.amazon.nova-lite-v1:0",
    "eu-south-2": "eu.amazon.nova-lite-v1:0",
    "ca-central-1": "ca.amazon.nova-lite-v1:0",
    "ca-west-1": "ca.amazon.nova-lite-v1:0",
}


def get_llm(model_id: str = None, temperature: float = 0.0) -> ChatBedrock:
    """Returns a LangChain ChatBedrock instance. Uses AWS creds from settings/.env."""
    mid = model_id or settings.DEFAULT_MODEL_ID
    # Nova models use Converse API; Converse requires inference profile ID for on-demand (not raw model ID).
    use_converse = "nova" in (mid or "").lower()
    if use_converse and (mid or "").strip().lower() == "amazon.nova-lite-v1:0":
        region = (getattr(settings, "BEDROCK_REGION", None) or "").strip() or "ap-south-1"
        profile = _NOVA_LITE_INFERENCE_PROFILE_BY_REGION.get(region)
        if profile:
            mid = profile
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
