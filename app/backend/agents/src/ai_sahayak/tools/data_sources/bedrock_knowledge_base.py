"""
Query Bedrock Knowledge Base (Panchang / festival data) for contextual AI reasoning.
"""
import os
from typing import List

import boto3
from ai_sahayak.config.settings import settings

_KB_ID = os.environ.get("BEDROCK_KNOWLEDGE_BASE_ID", settings.BEDROCK_KNOWLEDGE_BASE_ID)
_REGION = os.environ.get("AWS_REGION", settings.BEDROCK_REGION)
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-agent-runtime", region_name=_REGION)
    return _client


def retrieve_from_panchang_kb(query: str, max_results: int = 5) -> str:
    """
    Retrieve relevant chunks from the Panchang Knowledge Base.
    Returns concatenated text from top results for use in LLM context.
    """
    try:
        client = _get_client()
        response = client.retrieve(
            knowledgeBaseId=_KB_ID,
            retrievalQuery={"text": query[:2000]},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": max_results,
                }
            },
        )
        parts: List[str] = []
        for item in response.get("retrievalResults", []):
            raw = item.get("content") or {}
            content = (raw.get("text") if isinstance(raw, dict) else None) or ""
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")
            content = (content or "").strip()
            if content:
                parts.append(content)
        return "\n\n".join(parts) if parts else ""
    except Exception as e:
        print(f"Bedrock KB retrieve error: {e}")
        return ""
