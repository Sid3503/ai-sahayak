from langchain_aws import ChatBedrock
from ai_sahayak.config.settings import settings

def get_llm(model_id: str = None, temperature: float = 0.0) -> ChatBedrock:
    """Returns a LangChain ChatBedrock instance."""
    return ChatBedrock(
        model_id=model_id or settings.DEFAULT_MODEL_ID,
        region_name=settings.BEDROCK_REGION,
        model_kwargs={"temperature": temperature}
    )
