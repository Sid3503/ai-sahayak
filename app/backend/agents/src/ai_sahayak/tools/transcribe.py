"""
Speech-to-text for voice messages using Amazon Transcribe.
Audio is uploaded to S3, then a transcription job is run; the transcript is returned.
If TRANSCRIBE_MEDIA_BUCKET is not set, returns None (caller should use placeholder text).
"""
import base64
import json
import time
import uuid
from typing import Optional
from urllib.parse import urlparse

import boto3

from ai_sahayak.config.settings import settings

# MediaFormat for Transcribe: webm, mp3, wav, etc.
MEDIA_FORMAT_MAP = {
    "webm": "webm",
    "audio/webm": "webm",
    "mp3": "mp3",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "wav": "wav",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "ogg": "ogg",
    "audio/ogg": "ogg",
    "mp4": "mp4",
    "audio/mp4": "mp4",
}


def _get_media_format(media_type: str) -> str:
    if not media_type:
        return "webm"
    mt = (media_type or "").strip().lower()
    return MEDIA_FORMAT_MAP.get(mt, "webm")


def transcribe_audio(audio_base64: str, media_type: str = "audio/webm", language_code: str = "hi-IN") -> Optional[str]:
    """
    Transcribe audio (base64) to text using Amazon Transcribe.
    Requires TRANSCRIBE_MEDIA_BUCKET to be set in .env. Returns None if not configured or on error.
    """
    bucket = (getattr(settings, "TRANSCRIBE_MEDIA_BUCKET", None) or "").strip()
    if not bucket:
        print("Transcribe: TRANSCRIBE_MEDIA_BUCKET not set — skipping transcription.")
        return None

    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        print(f"Transcribe: base64 decode failed: {e}")
        return None

    if not audio_bytes:
        return None

    media_format = _get_media_format(media_type)
    ext = f".{media_format}" if media_format else ".webm"
    key = f"transcribe-in/{uuid.uuid4().hex}{ext}"
    region = getattr(settings, "AWS_REGION", "ap-south-1")

    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )
    transcribe = boto3.client(
        "transcribe",
        region_name=region,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
    )

    try:
        s3.put_object(Bucket=bucket, Key=key, Body=audio_bytes, ContentType=media_type or "audio/webm")
    except Exception as e:
        print(f"Transcribe: S3 upload failed: {e}")
        return None

    media_uri = f"s3://{bucket}/{key}"
    job_name = f"sahayak-{uuid.uuid4().hex}"[:200]

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat=media_format,
            LanguageCode=language_code,
            OutputBucketName=bucket,
        )
    except Exception as e:
        print(f"Transcribe: start_transcription_job failed: {e}")
        try:
            s3.delete_object(Bucket=bucket, Key=key)
        except Exception:
            pass
        return None

    # Poll until COMPLETED or FAILED (max ~60 s)
    for _ in range(30):
        time.sleep(2)
        try:
            job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        except Exception as e:
            print(f"Transcribe: get_transcription_job failed: {e}")
            break
        status = job.get("TranscriptionJob", {}).get("TranscriptionJobStatus", "")
        if status == "COMPLETED":
            transcript_uri = job.get("TranscriptionJob", {}).get("Transcript", {}).get("TranscriptFileUri")
            if not transcript_uri:
                break
            try:
                parsed = urlparse(transcript_uri)
                path_parts = parsed.path.lstrip("/").split("/")
                if parsed.netloc.startswith("s3.") and "amazonaws.com" in parsed.netloc and len(path_parts) >= 2:
                    out_bucket, out_key = path_parts[0], "/".join(path_parts[1:])
                else:
                    out_bucket = parsed.netloc.split(".")[0]
                    out_key = parsed.path.lstrip("/")
                out_obj = s3.get_object(Bucket=out_bucket, Key=out_key)
                data = json.loads(out_obj["Body"].read().decode("utf-8"))
                transcript = (data.get("results") or {}).get("transcripts") or []
                text = (transcript[0].get("transcript") or "").strip() if transcript else ""
            except Exception as e:
                print(f"Transcribe: read transcript JSON failed: {e}")
                text = ""
            try:
                s3.delete_object(Bucket=bucket, Key=key)
            except Exception:
                pass
            return text if text else None
        if status == "FAILED":
            print(f"Transcribe: job failed: {job.get('TranscriptionJob', {}).get('FailureReason', '')}")
            break

    try:
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    except Exception:
        pass
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception:
        pass
    return None
