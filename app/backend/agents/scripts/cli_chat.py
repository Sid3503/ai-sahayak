import requests
import json
import uuid
import sys
import os
import uuid

# Base Configuration
API_URL = "http://localhost:8000/v1/webhook/incoming"
PLATFORM = "cli"

USER_ID = "cli_tester_001"
SESSION_ID = sys.argv[1] if len(sys.argv) > 1 else f"cli_session_{uuid.uuid4().hex[:8]}"

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*50)
    print("🤖 AI Sahayak - Terminal Chat Client")
    print("="*50)
    print(f"User ID: {USER_ID}")
    print(f"Session ID: {SESSION_ID}")
    print("Type 'quit' or 'exit' to stop.")
    print("="*50 + "\n")

def send_message(text: str):
    payload = {
        "user_id": USER_ID,
        "text": text,
        "session_id": SESSION_ID,
        "platform": PLATFORM
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the server.")
        print("   Make sure the FastAPI server is running (./start_agent.sh)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        return None

def main():
    print_header()
    
    while True:
        try:
            # User input
            user_input = input("\n🧑 You: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit']:
                print("\nGoodbye! 👋")
                break
                
            # Send to API
            print("⏳ Sahayak is thinking...", end="\r")
            result = send_message(user_input)
            
            # Clear thinking line
            print(" " * 30, end="\r")
            
            if result and result.get("ok"):
                reply = result.get("reply", "")
                suggested_actions = result.get("suggested_actions", [])
                
                print(f"🤖 Sahayak: {reply}")
                
                if suggested_actions:
                    print("\n   [Suggested Actions]:")
                    for action in suggested_actions:
                        print(f"   👉 {action}")
            else:
                print("⚠️ Received an invalid response from the server.")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break

if __name__ == "__main__":
    # Ensure requests is installed
    try:
        import requests
    except ImportError:
        print("Required package 'requests' is missing. Installing it now...")
        os.system("pip install requests")
        print("\n---")
    
    main()
