import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8000/v1/webhook/incoming"

def simulate_flow(name, lang_selection, inputs):
    print(f"\n--- Testing {name} Flow ---")
    session_id = f"test_{lang_selection}_{uuid.uuid4().hex[:4]}"
    user_id = f"9199{uuid.uuid4().hex[:8]}"
    
    # 1. Initial Greeting
    resp = requests.post(BASE_URL, json={
        "user_id": user_id,
        "session_id": session_id,
        "text": "hi",
        "platform": "test"
    }).json()
    print(f"Bot: {resp['reply']}")
    
    # 2. Language Selection
    resp = requests.post(BASE_URL, json={
        "user_id": user_id,
        "session_id": session_id,
        "text": lang_selection,
        "platform": "test"
    }).json()
    print(f"You: {lang_selection}")
    print(f"Bot: {resp['reply']}")
    
    # 3. Follow up inputs
    for inp in inputs:
        resp = requests.post(BASE_URL, json={
            "user_id": user_id,
            "session_id": session_id,
            "text": inp,
            "platform": "test"
        }).json()
        print(f"You: {inp}")
        print(f"Bot: {resp['reply']}")
        
    final_reply = resp['reply']
    print(f"\nFinal Message: {final_reply}")
    return final_reply

# Test Inputs
english_inputs = [
    "I am John, my shop is John's General Store",
    "123456789012",
    "Mumbai, Suburban",
    "ledger.png"
]

hindi_inputs = [
    "मेरा नाम रमेश है और दुकान का नाम रमेश किरना है",
    "987654321098",
    "इंदौर, मध्य प्रदेश",
    "khatabook_photo.jpg"
]

hinglish_inputs = [
    "Siddharth mera naam hai, raju store meri dukaan hai",
    "111222333444",
    "Mira Road, Thane",
    "ok, ledger.png"
]

print("Starting Simulated Tests...")
print("Note: Ensure backend is running at localhost:8000")

try:
    en_final = simulate_flow("English", "English", english_inputs)
    hi_final = simulate_flow("Hindi", "Hindi", hindi_inputs)
    hng_final = simulate_flow("Hinglish", "Hinglish", hinglish_inputs)

    print("\n" + "="*50)
    print("VERIFICATION RESULTS")
    print("="*50)
    print(f"English Final: {en_final[:50]}...")
    print(f"Hindi Final: {hi_final[:50]}...")
    print(f"Hinglish Final: {hng_final[:50]}...")
    
    # Simple check for Hinglish/Hindi
    if "Welcome" in hng_final and "Hinglish" not in hng_final:
        print("❌ HINGLISH TEST FAILED: Welcome message still in English")
    else:
        print("✅ HINGLISH TEST PASSED")
        
    if "Welcome" in hi_final:
        print("❌ HINDI TEST FAILED: Welcome message still in English")
    else:
        print("✅ HINDI TEST PASSED")

except Exception as e:
    print(f"Test failed with error: {e}")
