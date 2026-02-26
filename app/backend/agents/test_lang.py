import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # Send a Hindi message
        payload = {
            "user_id": "test_user_hi",
            "platform": "whatsapp",
            "text": "क्या मेरे पास बिस्कुट खत्म हो गए हैं?",
            "session_id": "test_lang_session_hi"
        }
        response = await client.post("http://localhost:8000/api/v1/webhook/incoming", json=payload)
        print("Response:", response.json())

# Assuming the server is already running with start_agent.sh that the user kicked off
asyncio.run(test_api())
