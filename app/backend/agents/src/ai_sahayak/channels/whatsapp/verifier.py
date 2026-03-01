from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from ai_sahayak.config.settings import settings

def verify_webhook(hub_mode: str, hub_verify_token: str, hub_challenge: str):
    """
    Verifies the Meta Webhook handshake.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")
