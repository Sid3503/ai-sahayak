import requests
import uuid
import time
import base64
import os

BASE_URL = "http://localhost:8000/v1/webhook/incoming"

def create_dummy_image():
    """Creates a tiny 1x1 base64 encoded jpeg for testing"""
    # 1x1 pixel white jpeg
    img_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfd\xfc\x7f\xff\xd9'
    return base64.b64encode(img_data).decode('utf-8')

def send_message(session_id, user_id, text, image_b64=None):
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "text": text,
        "platform": "test"
    }
    if image_b64:
        payload["image"] = image_b64
        payload["image_media_type"] = "image/jpeg"
        
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        print(f"You: {text}")
        if image_b64:
            print(f"[Attached Image to Payload]")
        print(f"Bot: {data['reply']}\n")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_e2e_test():
    print("="*60)
    print("AI SAHAYAK - E2E INTEGRATION TEST SUITE")
    print("="*60)
    
    session_id = f"e2e_{uuid.uuid4().hex[:6]}"
    user_id = f"9198{uuid.uuid4().hex[:8]}"
    
    print("\n--- Phase 1: Onboarding Flow ---")
    send_message(session_id, user_id, "hi")
    send_message(session_id, user_id, "English")
    send_message(session_id, user_id, "My name is Admin, my shop is Demo Store")
    send_message(session_id, user_id, "123456789012")
    send_message(session_id, user_id, "Delhi")
    send_message(session_id, user_id, "ledger.png") # Triggers completion
    
    print("\n--- Phase 2: Core Dashboard Routing ---")
    # Sales
    send_message(session_id, user_id, "What were my sales today?")
    
    # Pricing
    send_message(session_id, user_id, "Should I change the price of milk?")
    
    # Inventory
    send_message(session_id, user_id, "Are we running out of biscuits?")
    
    # Forecast
    send_message(session_id, user_id, "What should I stock up on for next week?")
    
    # General Chat
    send_message(session_id, user_id, "Can you remind me again how this app works?")
    
    print("\n--- Phase 3: Shelf Eye (Vision) Integration ---")
    tiny_img = create_dummy_image()
    # Sending an image payload should explicitly route to image_analysis_node
    send_message(session_id, user_id, "Please check this photo of my shelf", image_b64=tiny_img)
    
    print("\n--- Phase 4: What-If Simulator & Alerts ---")
    send_message(session_id, user_id, "What if I drop the price of Maggi by 10% next month?")
    
    print("\n================ E2E TEST COMPLETE =================\n")

if __name__ == "__main__":
    run_e2e_test()
