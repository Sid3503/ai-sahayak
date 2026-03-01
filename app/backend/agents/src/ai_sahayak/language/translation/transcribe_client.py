"""
Amazon Transcribe ASR – use when Bhashini isn't available (e.g. hackathon not in their list).
Uploads audio to S3, runs a transcription job, returns text. Supports Hindi (hi-IN) and webm.
"""
import base64
import os
import time
import uuid

import boto3
import httpx


def _get_region():
    return os.environ.get("AWS_REGION") or os.environ.get("BEDROCK_REGION") or "ap-south-1"


def _get_bucket():
    return os.environ.get("TRANSCRIBE_INPUT_BUCKET") or os.environ.get("CALENDAR_S3_BUCKET")


def speech_to_text(
    audio_base64: str,
    language_code: str = "hi-IN",
    media_format: str = "webm",
) -> str:
    """
    Transcribe audio using Amazon Transcribe (batch job with S3).
    Uses TRANSCRIBE_INPUT_BUCKET or CALENDAR_S3_BUCKET for temporary upload.
    """
    bucket = _get_bucket()
    if not bucket:
        raise ValueError(
            "TRANSCRIBE_INPUT_BUCKET (or CALENDAR_S3_BUCKET) must be set for Amazon Transcribe ASR."
        )

    region = _get_region()
    key = f"transcribe-input/{uuid.uuid4().hex}.{media_format}"

    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError(f"Invalid base64 audio: {e}")

    s3 = boto3.client("s3", region_name=region)
    transcribe = boto3.client("transcribe", region_name=region)

    s3.put_object(Bucket=bucket, Key=key, Body=audio_bytes, ContentType=f"audio/{media_format}")
    media_uri = f"s3://{bucket}/{key}"
    job_name = f"sahayak-{uuid.uuid4().hex}"[:200]

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode=language_code,
            MediaFormat=media_format,
            Media={"MediaFileUri": media_uri},
        )

        for _ in range(60):
            job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = job["TranscriptionJob"]["TranscriptionJobStatus"]
            if status == "COMPLETED":
                transcript_uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                with httpx.Client() as client:
                    resp = client.get(transcript_uri)
                    resp.raise_for_status()
                    data = resp.json()
                transcript = (data.get("results", {}).get("transcripts") or [{}])[0].get("transcript", "")
                return (transcript or "").strip()
            if status == "FAILED":
                reason = job["TranscriptionJob"].get("FailureReason", "Unknown")
                raise RuntimeError(f"Transcribe job failed: {reason}")
            time.sleep(1)

        raise RuntimeError("Transcribe job timed out")
    finally:
        try:
            s3.delete_object(Bucket=bucket, Key=key)
        except Exception:
            pass
        try:
            transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        except Exception:
            pass