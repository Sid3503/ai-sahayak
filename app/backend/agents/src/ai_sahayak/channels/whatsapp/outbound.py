import httpx
from typing import Dict, Any, List
from ai_sahayak.config.settings import settings
from ai_sahayak.channels.whatsapp.formatter import WhatsAppFormatter

class WhatsAppOutbound:
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def send_message(self, recipient_id: str, text: str, suggested_actions: List[str] = []) -> Dict[str, Any]:
        """
        Formats and sends a message (text, buttons, or list) via WhatsApp API.
        """
        if not self.api_token or not self.phone_id:
            print("Warning: WhatsApp credentials not configured. Skipping outbound message.")
            return {"status": "skipped_no_credentials"}

        payload = WhatsAppFormatter.format_message(recipient_id, text, suggested_actions)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"WhatsApp API HTTP Error: {e.response.text}")
            return {"error": str(e), "details": e.response.text}
        except Exception as e:
            print(f"WhatsApp Output Error: {e}")
            return {"error": str(e)}

    async def send_read_receipt(self, message_id: str) -> Dict[str, Any]:
        """
        Marks an incoming message as read.
        """
        if not self.api_token or not self.phone_id:
            return {"status": "skipped"}
            
        payload = WhatsAppFormatter.format_read_receipt(message_id)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                return response.json()
        except Exception as e:
            print(f"WhatsApp Read Receipt Error: {e}")
            return {"error": str(e)}
            
    async def send_reaction(self, recipient_id: str, message_id: str, emoji: str) -> Dict[str, Any]:
        """
        Sends an emoji reaction to a specific message.
        """
        if not self.api_token or not self.phone_id:
            return {"status": "skipped"}
            
        payload = WhatsAppFormatter.format_reaction(recipient_id, message_id, emoji)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                return response.json()
        except Exception as e:
            print(f"WhatsApp Reaction Error: {e}")
            return {"error": str(e)}
