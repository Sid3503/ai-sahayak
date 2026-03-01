from fastapi import APIRouter, Request, Query, BackgroundTasks
from ai_sahayak.schemas.webhook import WebhookAck, WhatsAppWebhookPayload
from ai_sahayak.channels.whatsapp.verifier import verify_webhook as do_verify_webhook
from ai_sahayak.channels.whatsapp.mapper import WhatsAppMapper
from ai_sahayak.channels.whatsapp.outbound import WhatsAppOutbound
from ai_sahayak.api.routes.chat import webhook_incoming

router = APIRouter()
whatsapp_client = WhatsAppOutbound()

@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    return do_verify_webhook(hub_mode, hub_verify_token, hub_challenge)

@router.post("/whatsapp")
async def whatsapp_webhook(payload: WhatsAppWebhookPayload, background_tasks: BackgroundTasks):
    inbound_payload = WhatsAppMapper.to_inbound_payload(payload)
    
    if inbound_payload:
        msg_id_req = None
        # Try to extract the message ID for typing indicators
        try:
            msg_id_req = payload.entry[0].changes[0].value.messages[0].id
        except (IndexError, AttributeError):
            pass

        if msg_id_req:
            import random
            # Mark message as read
            background_tasks.add_task(whatsapp_client.send_read_receipt, msg_id_req)
            
            # Add a processing reaction to acknowledge we received it
            emojis = ['⏳', '💭', '🤔', '👀', '✨', '⚡️', '🔧']
            background_tasks.add_task(
                whatsapp_client.send_reaction, 
                inbound_payload.phone_number, 
                msg_id_req, 
                random.choice(emojis)
            )
            
        # Process message using the core LangGraph agent logic via background task
        background_tasks.add_task(process_whatsapp_message, inbound_payload, msg_id_req)
        
    return WebhookAck(status="received")

async def process_whatsapp_message(payload, msg_id_req=None):
    # Process message through the main AI orchestrator (chat.py)
    # webhook_incoming returns a dictionary with 'ok', 'reply', 'suggested_actions'
    result = await webhook_incoming(payload)
    
    if result and result.get("ok"):
        reply = result.get("reply", "")
        suggested_actions = result.get("suggested_actions", [])
        
        # Dispatch back to WhatsApp
        await whatsapp_client.send_message(
            recipient_id=payload.phone_number,
            text=reply,
            suggested_actions=suggested_actions
        )
