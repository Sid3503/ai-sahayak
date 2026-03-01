#!/bin/bash
# Script to start the ngrok tunnel for Meta WhatsApp webhooks

echo "========================================================="
echo "🌍 Starting ngrok tunnel for AI Sahayak WhatsApp Webhook"
echo "========================================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null
then
    echo "❌ Error: ngrok is not installed or not in PATH."
    echo "Please install ngrok first: https://ngrok.com/download"
    echo "On Mac: brew install ngrok/ngrok/ngrok"
    exit 1
fi

echo "Starting ngrok on port 8000..."
echo "Wait a few seconds for the tunnel to initialize..."

# Start ngrok in the background non-interactively
ngrok http 8000 --log=stdout > /dev/null 2>&1 &
NGROK_PID=$!

sleep 3

# Fetch the public URL from ngrok's local API (trying port 4040 then 4041)
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[a-zA-Z0-9.-]*\.ngrok[^"]*' | head -n 1)

if [ -z "$NGROK_URL" ]; then
    NGROK_URL=$(curl -s http://localhost:4041/api/tunnels | grep -o 'https://[a-zA-Z0-9.-]*\.ngrok[^"]*' | head -n 1)
fi

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to retrieve ngrok URL. Make sure ngrok started correctly."
    kill $NGROK_PID
    exit 1
fi

echo ""
echo "✅ TUNNEL ACTIVE!"
echo "Your secure Meta Webhook URL is:"
echo "👉  ${NGROK_URL}/v1/webhooks/whatsapp"
echo ""
echo "Go to the Meta Business Dashboard:"
echo "1. WhatsApp > Configuration > Edit Webhook"
echo "2. Callback URL: ${NGROK_URL}/v1/webhooks/whatsapp"
echo "3. Verify Token: sahayak_secret"
echo "========================================================="

# Keep script running to keep ngrok alive
wait $NGROK_PID
