"""
Text-to-Speech (TTS) for AI replies – Amazon Polly (Hindi / Indian English).
"""
import base64
import os
from typing import Optional

import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language_code: Optional[str] = "hi-IN"  # hi-IN (Hindi) or en-IN (Indian English)


# Aditi: bilingual Hindi + Indian English
VOICE_ID = "Aditi"
ENGINE = "neural"  # or "standard"


def _get_polly_client():
    region = os.environ.get("AWS_REGION") or os.environ.get("BEDROCK_REGION") or "ap-south-1"
    return boto3.client("polly", region_name=region)


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
        raise HTTPException(status_code=503, detail=f"TTS failed: {str(e)}")
