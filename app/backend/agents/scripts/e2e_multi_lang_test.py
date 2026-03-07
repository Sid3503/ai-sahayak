import requests
import uuid
import time
import base64
import os
import concurrent.futures

BASE_URL = "http://localhost:8000/v1/webhook/incoming"

def create_dummy_image():
    """Creates a tiny 1x1 base64 encoded jpeg for testing"""
    img_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfd\xfc\x7f\xff\xd9'
    return base64.b64encode(img_data).decode('utf-8')

def send_message(session_id, user_id, text, language, image_b64=None):
    payload = {
        "user_id": user_id,
        "phone_number": user_id,
        "session_id": session_id,
        "text": text,
        "platform": "test"
    }
    if image_b64:
        payload["image"] = image_b64
        payload["image_media_type"] = "image/jpeg"
        
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"[{language.upper()}] You: {text}")
        if image_b64:
            print(f"[{language.upper()}] [Attached Dummy Image]")
        print(f"[{language.upper()}] Bot: {data['reply']}\n")
        return data
    except Exception as e:
        print(f"[{language.upper()}] Error: {e}")
        return None

def run_user_flow(language, prompts):
    session_id = f"e2e_{language}_{uuid.uuid4().hex[:4]}"
    user_id = f"9198{uuid.uuid4().hex[:8]}"
    
    print(f"\n--- Starting Flow for {language.upper()} User ---")
    
    for prompt in prompts:
        if isinstance(prompt, dict):
            send_message(session_id, user_id, prompt["text"], language, image_b64=create_dummy_image())
        else:
            send_message(session_id, user_id, prompt, language)
        time.sleep(1) # Small delay to avoid hammering server too hard
        
    print(f"\n--- Completed Flow for {language.upper()} User ---\n")

def run_multi_lang_test():
    print("="*60)
    print("AI SAHAYAK - MULTI-LINGUAL E2E TEST SUITE")
    print("="*60)
    
    english_prompts = [
        "hi",
        "English",
        "My name is John, my shop is Demo Store",
        "It's a General Store",
        "Pincode is 110001, here is my location",
        "I've been running it for 10 years",
        "123456789012",
        "No GST number",
        "What were my sales today?",
        "Should I change the price of milk?",
        {"text": "Please check this photo of my shelf"}
    ]
    
    hindi_prompts = [
        "नमस्ते",
        "Hindi",
        "मेरा नाम राहुल है, मेरी दुकान का नाम राहुल स्टोर है",
        "किराना स्टोर",
        "पिनकोड 400001, ये रही लोकेशन",
        "पिछले 5 साल से",
        "987654321098",
        "GST नंबर नहीं है",
        "आज मेरी बिक्री कितनी हुई?",
        "क्या मुझे दूध की कीमत बदलनी चाहिए?",
        {"text": "कृपया मेरी शेल्फ की इस फोटो की जाँच करें"}
    ]
    
    hinglish_prompts = [
        "hello",
        "Hinglish",
        "Mera naam Amit hai, mera dukan Amit Kirana hai",
        "Medical store hai mera",
        "Pincode 560001, location bhej diya",
        "2 years se chala raha hu",
        "456789123456",
        "GST: 29ABCDE1234F1Z5",
        "Aaj ka sales kaisa raha?",
        "Milk ka price change karu kya?",
        {"text": "Mera shelf ka photo check karo"}
    ]
    
    # Validator error-path: wrong Aadhar/PIN first, then corrected
    validation_error_prompts = [
        "hi",
        "English",
        "My name is Validation Tester, my shop is Test Mart",
        "General Store",
        "PIN 000000",          # invalid: starts with 0
        "560001",              # corrected PIN
        "3 years",
        "ABC123",              # invalid Aadhar: not 12 digits
        "5 2 8 9 1 2 0 4 8 6 2 3",  # with spaces - should normalize to 528912048623
        "BADGSTXX",           # invalid GST: not 15 chars
        "29AABCT1332L1ZN",    # valid GST format
        "What is my stock?"
    ]

    flows = [
        ("English", english_prompts),
        ("Hindi", hindi_prompts),
        ("Hinglish", hinglish_prompts),
        ("Validation-Error-Path", validation_error_prompts),
    ]
    
    # Run sequentially for clearer output tracking in terminal
    for lang, prompts in flows:
        run_user_flow(lang, prompts)
        
    print("\n================ E2E TESTS COMPLETE =================\n")

if __name__ == "__main__":
    run_multi_lang_test()
