from typing import Dict, Any, List

class WhatsAppFormatter:
    @staticmethod
    def format_message(recipient_id: str, text: str, suggested_actions: List[str] = []) -> Dict[str, Any]:
        """
        Formats generic text and actions into a Meta WhatsApp payload.
        """
        base_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id
        }
        
        # Intercept specific string to trigger native WhatsApp Location Request button
        if "share your current location" in text.lower():
            base_payload["type"] = "interactive"
            base_payload["interactive"] = {
                "type": "location_request_message",
                "body": {"text": text},
                "action": {"name": "send_location"}
            }
            return base_payload

        if not suggested_actions:
            # Simple Text
            base_payload["type"] = "text"
            base_payload["text"] = {"body": text}
            
        elif len(suggested_actions) <= 3:
            # Buttons
            base_payload["type"] = "interactive"
            
            buttons = []
            for i, action in enumerate(suggested_actions):
                # Meta button ID max length is 256, title max is 20
                safe_title = action[:20]
                action_id = action.replace(' ', '_').lower()[:20]
                buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{i}_{action_id}",
                        "title": safe_title
                    }
                })
                
            base_payload["interactive"] = {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": buttons}
            }
            
        else:
            # List (for > 3 options)
            base_payload["type"] = "interactive"
            
            rows = []
            for i, action in enumerate(suggested_actions):
                safe_title = action[:24]
                action_id = action.replace(' ', '_').lower()[:20]
                rows.append({
                    "id": f"opt_{i}_{action_id}",
                    "title": safe_title
                })
                
            base_payload["interactive"] = {
                "type": "list",
                "body": {"text": text},
                "action": {
                    "button": "Select Option",
                    "sections": [
                        {
                            "title": "Options",
                            "rows": rows
                        }
                    ]
                }
            }
            
        return base_payload

    @staticmethod
    def format_read_receipt(message_id: str) -> Dict[str, Any]:
        return {
          "messaging_product": "whatsapp",
          "status": "read",
          "message_id": message_id,
          "typing_indicator": {
              "type": "text"
          }
        }
    
    @staticmethod
    def format_reaction(recipient_id: str, message_id: str, emoji: str) -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
