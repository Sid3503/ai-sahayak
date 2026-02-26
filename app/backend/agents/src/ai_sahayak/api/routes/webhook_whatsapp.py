from fastapi import APIRouter, Request, Header
from ai_sahayak.schemas.webhook import WebhookAck

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Header(None, alias="hub.mode"),
    hub_challenge: str = Header(None, alias="hub.challenge"),
    hub_verify_token: str = Header(None, alias="hub.verify_token")
):
    # Logic to verify Meta webhook
    return hub_challenge

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    # Logic to process WhatsApp payload
    return WebhookAck(status="received")
