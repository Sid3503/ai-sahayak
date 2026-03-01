import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"
USER_ID = f"sim_test_{uuid.uuid4().hex[:6]}"
SESSION_ID = f"session_{USER_ID}"

def send_message(text):
    print(f"🧑 You: {text}")
    payload = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "text": text,
        "platform": "web"
    }
    response = requests.post(f"{BASE_URL}/v1/webhook/incoming", json=payload)
    if response.status_code == 200:
        reply = response.json().get("reply")
        print(f"🤖 Bot: {reply}\n")
        return reply
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def run_simulation_test():
    print(f"🚀 Starting What-If Simulation Test for User: {USER_ID}\n")
    
    # 1. Start onboarding
    send_message("hi")
    send_message("English")
    
    # 2. Complete onboarding quickly
    send_message("My name is Sim Boy, my shop is Sim Store")
    send_message("General Store")
    send_message("Pincode 400001, location Mumbai")
    send_message("5 years")
    send_message("123456789012")
    send_message("No GST")
    
    print("✅ Onboarding should be complete now. Testing What-If Simulator...")
    time.sleep(2)
    
    # 3. Test What-If Simulator
    send_message("What if I increase the price of milk by 10 rupees?")

if __name__ == "__main__":
    run_simulation_test()
