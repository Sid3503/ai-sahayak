# Phase-Based Development Plan for LangGraph Agent

## Phase 1: Core Agent Framework Setup (Ready to Run)

### Changes to start_agent.sh

```bash
#!/bin/bash
# Script to start the AI Sahayak Agents API

# Set PYTHONPATH to include the src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "🚀 Starting AI Sahayak Agents API..."
echo "🔧 Environment: $(python3 --version)"
echo "📦 Dependencies: $(pip list | grep -E 'langgraph|fastapi|pydantic|boto3' | head -5)"

# Check if requirements are installed
if ! pip list | grep -q "langgraph"; then
    echo "⚠️  Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Start the application
python3 src/ai_sahayak/main.py
```

### Key Files for Phase 1 Implementation:

#### 1. backend/agents/src/ai_sahayak/main.py

```python
import uvicorn
from fastapi import FastAPI
from .api.server import create_app

# Create the FastAPI app
app = create_app()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. backend/agents/src/ai_sahayak/api/server.py

```python
from fastapi import FastAPI
from .routes import health, chat, webhook_whatsapp
from .middleware import logging, tracing, auth

def create_app():
    app = FastAPI(
        title="AI Sahayak Agents API",
        version="1.0.0",
        description="LangGraph-based AI agents for kirana store owners"
    )

    # Middleware
    app.add_middleware(logging.LoggingMiddleware)
    app.add_middleware(tracing.TracingMiddleware)
    app.add_middleware(auth.AuthMiddleware)

    # Routes
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(chat.router, prefix="/v1", tags=["Chat"])
    app.include_router(webhook_whatsapp.router, prefix="/v1/webhooks", tags=["Webhooks"])

    return app
```

#### 3. backend/agents/src/ai_sahayak/api/routes/chat.py

```python
from fastapi import APIRouter, HTTPException
from ..schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # For Phase 1: Minimal implementation
        response = ChatResponse(
            response="Hello! I'm your AI Sahayak assistant. How can I help you today?",
            session_id=request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 4. backend/agents/src/ai_sahayak/api/routes/health.py

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "healthy", "service": "agents-api"}
```

#### 5. backend/agents/src/ai_sahayak/channels/base.py

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseChannelAdapter(ABC):
    """Abstract base class for channel adapters"""

    @abstractmethod
    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate incoming payload"""
        pass

    @abstractmethod
    def to_agent_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert channel payload to AgentRequest format"""
        pass
```

#### 6. backend/agents/src/ai_sahayak/channels/models.py

```python
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    WEB = "web"
    MOBILE = "mobile"

class AgentRequest(BaseModel):
    session_id: str
    store_id: str
    channel: Channel
    raw_input: str
    message_type: str
    timestamp: str
    language: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    session_id: str
    language: Optional[str] = None
    buttons: Optional[list] = None
```

#### 7. backend/agents/src/ai_sahayak/graphs/workflows/retail_assistant.py

```python
from langgraph.graph import StateGraph, END
from ..state.conversation import ConversationState

# Placeholder for Phase 1 - minimal workflow
def create_retail_assistant_graph():
    """Create a basic retail assistant workflow"""
    workflow = StateGraph(ConversationState)

    # For Phase 1: Just return a simple response
    def simple_response(state):
        return {"response": "Hello! I'm your AI Sahayak assistant."}

    workflow.add_node("simple_response", simple_response)
    workflow.set_entry_point("simple_response")
    workflow.add_edge("simple_response", END)

    return workflow.compile()
```

#### 8. backend/agents/src/ai_sahayak/runtime/executor.py

```python
from .registry import GraphRegistry
from ..graphs.workflows.retail_assistant import create_retail_assistant_graph

class GraphExecutor:
    def __init__(self):
        self.registry = GraphRegistry()
        self.graph = create_retail_assistant_graph()

    async def run_graph(self, agent_request):
        """Run the LangGraph agent"""
        # For Phase 1: Just return a simple response
        return {"response": "Hello! I'm your AI Sahayak assistant."}
```

## Phase 2: Basic LangGraph Integration with State (Completed ✓)

### Key Achievements:

1. **Implemented LangGraph state management:** Tracked `onboarding` step and intermediate user data within `ConversationState`.
2. **Onboarding Flow:** Configured the Qwen LLM via AWS Bedrock to systematically gather store and user details.
3. **DB Integration:** Updated the prompt to return a structured JSON response to securely capture Name, Store, and City. Implemented async `MongoDBTool` `upsert` queries.
4. **Session Persistence (MongoDB):** Converted the volatile in-memory dictionary to an async MongoDB manager over the `conversation_history` collection to retain thread context.

## Phase 3: The Main Dashboard Chat Router (Next Step 🚀)

### Key Features to Build Next:

1. **The Core Router Node:** Once onboarding is `"completed"`, user messages should be directed to an intent classification router (e.g., `"sales_query"`, `"pricing_query"`, `"inventory"`, `"general_chat"`).
2. **Specific Graph Nodes:** Create placeholder nodes for these specialized domains.
3. **Advanced Tool Calling:** Give the LLM access to "Fake/Mock" databases for finding inventory prices and recent sales to simulate the dashboard experience.
4. **Suggesting Next Actions:** Make the chat endpoint return smart contextual suggestions to power the UI.

## Phase 4: Full Multilingual Support (Bhashini/LLM)

### Key Features:

1. Language detection and normalization.
2. Real-time translation to/from English using translation tools or pure LLM capabilities.
3. Localization of responses (e.g., maintaining Hindi idioms).
4. Multi-language prompt support.

## Phase 5: Deep Integrations & Advanced Alert Workflows

### Key Components:

1. **Shelf Eye (Image Recognition):** Accept base64 imagery to assess shelf stock leveraging Qwen Vision (or similar pipeline).
2. **"What-if" Simulator Engine:** Create a specific workflow node capable of answering hypothetical business scenarios.
3. **Proactive Alert Engine:** Generate simulated alerts (e.g., "Holi coming up").

## Phase 6: Production Ready Deployment

### Final Enhancements:

1. Comprehensive error handling.
2. Performance monitoring and tracing (LangSmith setup).
3. Security enhancements (API Key management, robust auth).
4. Comprehensive testing suite.
5. Documentation and observability.

## Testing Strategy

### Unit Tests (Phase 1):

```python
# tests/unit/test_chat_endpoint.py
import pytest
from fastapi.testclient import TestClient
from src.ai_sahayak.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post("/v1/chat", json={
        "session_id": "test_session",
        "store_id": "STORE_001",
        "channel": "web",
        "raw_input": "Hello",
        "message_type": "text"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### Integration Tests:

- Test the complete flow from chat endpoint → LangGraph agent → response
- Test session persistence
- Test error scenarios

### End-to-End Tests:

- Simulate complete WhatsApp webhook flow
- Test multilingual translation
- Test proactive alert flow

## Docker Deployment (Phase 5)

### Dockerfile.agents

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY start_agent.sh .

EXPOSE 8000

CMD ["./start_agent.sh"]
```

## Running Phase 1

1. Install dependencies: `pip install -r requirements.txt`
2. Run the agent: `./start_agent.sh`
3. Test endpoints:
   - `curl http://localhost:8000/health`
   - `curl -X POST http://localhost:8000/v1/chat -H "Content-Type: application/json" -d '{"session_id":"test","store_id":"STORE_001","channel":"web","raw_input":"Hello","message_type":"text"}'`
