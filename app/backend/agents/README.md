# AI Sahayak Agents

This is the backend intelligence service for AI Sahayak, powered by LangGraph and FastAPI.

## Quick Start

1. **Activate Virtual Environment**:

   ```bash
   source ../../ai-sahayak-env/bin/activate
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Agent Server**:
   ```bash
   ./start_agent.sh
   ```

## API Endpoints for Frontend UI

The Frontend Chat UI should communicate with:

- **Base URL**: `http://localhost:8000`
- **Webhook Endpoint**: `POST /v1/webhook/incoming`

### Sample Request

```json
{
  "user_id": "test_user_1",
  "text": "Hello Sahayak! Show me sales forecast.",
  "session_id": "session_123"
}
```

## Project Structure

- `src/ai_sahayak/api/routes/chat.py`: Main logic for Frontend UI communication.
- `src/ai_sahayak/graphs/workflows/`: LangGraph definitions.
- `src/ai_sahayak/memory/`: Session and state management.
