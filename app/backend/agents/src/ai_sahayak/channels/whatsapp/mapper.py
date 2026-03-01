from typing import Optional
from ai_sahayak.schemas.webhook import InboundPayload, WhatsAppWebhookPayload

class WhatsAppMapper:
    @staticmethod
    def to_inbound_payload(payload: WhatsAppWebhookPayload) -> Optional[InboundPayload]:
        """
        Extracts the first user message from the Meta WhatsApp payload
        and converts it into our internal InboundPayload format.
        """
        try:
            for entry in payload.entry:
                for change in entry.changes:
                    value = change.value
                    
                    # Ignore status updates (delivered, read) for routing purposes
                    if value.statuses:
                        return None
                        
                    if value.messages:
                        msg = value.messages[0]
                        user_id = msg.from_  # Phone number
                        msg_type = msg.type
                        
                        text = ""
                        if msg_type == "text" and msg.text:
                            text = msg.text.body
                        elif msg_type == "interactive" and msg.interactive:
                            inter = msg.interactive
                            if inter.type == "button_reply" and inter.button_reply:
                                text = inter.button_reply.id
                            elif inter.type == "list_reply" and inter.list_reply:
                                text = inter.list_reply.id
                        elif msg_type == "location" and msg.location:
                            loc = msg.location
                            parts = [f"Lat/Lng: {loc.latitude}, {loc.longitude}"]
                            
                            address_str = loc.address
                            name_str = loc.name
                            
                            # If WhatsApp doesn't provide the textual address, reverse geocode it
                            if not address_str and not name_str:
                                try:
                                    import requests
                                    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={loc.latitude}&lon={loc.longitude}"
                                    headers = {"User-Agent": "AI-Sahayak-Bot/1.0"}
                                    resp = requests.get(url, headers=headers, timeout=5)
                                    if resp.status_code == 200:
                                        data = resp.json()
                                        if data and "display_name" in data:
                                            address_str = data["display_name"]
                                except Exception as e:
                                    print(f"Reverse geocoding failed: {e}")
                            
                            if address_str:
                                parts.append(f"Address: {address_str}")
                            if name_str:
                                parts.append(f"Name: {name_str}")
                                
                            text = "[Location Shared] " + " | ".join(parts)
                                
                        if not text:
                            # Unsupported message type mapping (or image placeholder)
                            text = f"[Received unsupported message type: {msg_type}]"
                            
                        push_name = None
                        if value.contacts and isinstance(value.contacts, list):
                            profile = value.contacts[0].get("profile", {})
                            push_name = profile.get("name")
                            
                        metadata = {}
                        if push_name:
                            metadata["whatsapp_push_name"] = push_name
                            
                        return InboundPayload(
                            user_id=user_id,
                            text=text,
                            session_id=f"wa_{user_id}",
                            platform="whatsapp",
                            phone_number=user_id,
                            metadata=metadata
                        )
        except Exception as e:
            print(f"Error mapping WhatsApp payload: {e}")
            
        return None
