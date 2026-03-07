"""
Text-to-Speech (TTS) for AI replies – Amazon Polly (Hindi / Indian English).
Model-agnostic: does not use Bedrock (Nova/Qwen); works the same with any chat model.
Runs Polly in a thread so the async server does not block.
"""
import asyncio
import base64
import logging
from typing import Optional

import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai_sahayak.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class TTSRequest(BaseModel):
    text: str
    language_code: Optional[str] = "hi-IN"  # hi-IN (Hindi) or en-IN (Indian English)


VOICE_ID = "Aditi"
ENGINE = "standard"


def _get_polly_client():
    region = getattr(settings, "AWS_REGION", None) or "ap-south-1"
    kwargs = {"region_name": region}
    if getattr(settings, "AWS_ACCESS_KEY_ID", None) and getattr(settings, "AWS_SECRET_ACCESS_KEY", None):
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client("polly", **kwargs)


def _synthesize_sync(text: str, lang: str) -> bytes:
    """Blocking Polly call – run from thread."""
    client = _get_polly_client()
    response = client.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=VOICE_ID,
        LanguageCode=lang,
        Engine=ENGINE,
    )
    return response["AudioStream"].read()


@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    """
    Convert reply text to speech (Hindi or Indian English) using Amazon Polly.
    Returns base64-encoded MP3 so the frontend can play it.
    """
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    if len(text) > 3000:
        raise HTTPException(status_code=400, detail="text too long (max 3000 chars)")

    lang = (req.language_code or "hi-IN").strip()
    if lang not in ("hi-IN", "en-IN"):
        lang = "hi-IN"

    try:
        audio_bytes = await asyncio.to_thread(_synthesize_sync, text, lang)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio_base64": audio_b64, "content_type": "audio/mpeg"}
    except Exception as e:
        err_msg = str(e)
        logger.exception("Polly TTS failed: %s", err_msg)
        raise HTTPException(status_code=503, detail=f"TTS failed: {err_msg}")
