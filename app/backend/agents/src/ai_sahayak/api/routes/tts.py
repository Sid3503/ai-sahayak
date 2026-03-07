"""
Text-to-Speech (TTS) for AI replies – Amazon Polly (Hindi / Indian English).
Model-agnostic: does not use Bedrock (Nova/Qwen); works the same with any chat model.
"""
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


# Aditi: bilingual Hindi + Indian English (standard engine; neural not supported for Aditi in ap-south-1)
VOICE_ID = "Aditi"
ENGINE = "standard"


def _get_polly_client():
    region = getattr(settings, "AWS_REGION", None) or "ap-south-1"
    kwargs = {"region_name": region}
    if getattr(settings, "AWS_ACCESS_KEY_ID", None) and getattr(settings, "AWS_SECRET_ACCESS_KEY", None):
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client("polly", **kwargs)


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
        client = _get_polly_client()
        response = client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=VOICE_ID,
            LanguageCode=lang,
            Engine=ENGINE,
        )
        audio_bytes = response["AudioStream"].read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {
            "audio_base64": audio_b64,
            "content_type": "audio/mpeg",
        }
    except Exception as e:
        err_msg = str(e)
        print(f"[TTS] Polly failed: {err_msg}")
        logger.exception("Polly TTS failed: %s", err_msg)
        if "neural" in err_msg.lower() or "Engine" in err_msg:
            try:
                client = _get_polly_client()
                response = client.synthesize_speech(
                    Text=text,
                    OutputFormat="mp3",
                    VoiceId=VOICE_ID,
                    LanguageCode=lang,
                    Engine="standard",
                )
                audio_bytes = response["AudioStream"].read()
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                return {"audio_base64": audio_b64, "content_type": "audio/mpeg"}
            except Exception as e2:
                logger.exception("Polly TTS (standard engine) failed: %s", e2)
                raise HTTPException(status_code=503, detail=f"TTS failed: {str(e2)}")
        raise HTTPException(status_code=503, detail=f"TTS failed: {err_msg}")
