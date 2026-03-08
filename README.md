# AI Sahayak

**Proactive intelligence for Indian Kirana stores** — one place for demand forecast, pricing, and Hinglish chat. Built for the **AWS AI for Bharat** hackathon.

---

## What it does

| Feature | Description |
|--------|-------------|
| **My day (Live Alerts)** | Post–login chat for the retailer. Real KPIs from the dashboard, Hinglish replies, voice in/out. Lambda-pushed alerts (festival, news, daily forecast) show up here. |
| **Control Centre (Dashboard)** | Pricing, demand forecast, what-if, KPIs per retailer. SageMaker DeepAR when configured; Bedrock for explanations. |
| **Proactive pipeline** | EventBridge → Lambda (alerts + festival orchestrator) → backend webhook → same chat. “Digital Panchang” via AWS Change Calendar. |
| **Reactive chat** | “Sales kaisa hai?”, “low stock?”, “atta ka price?” — agent uses **only** dashboard data and answers in simple Hinglish (tables, bold, no mock). |

---

## Tech stack

| Layer | Tech |
|-------|------|
| **Frontend** | React, Vite, Tailwind, Lucide, Cognito — landing, onboarding, Dashboard embed, My day chat. |
| **Agents backend** | FastAPI, LangGraph, **Bedrock (Nova Lite)**, dashboard data tool. `/v1/webhook/incoming`, `/v1/alerts/incoming`, `/v1/alerts/for-user`. |
| **Dashboard** | Flask API + React UI — `/api/kpis`, `/api/forecast`, `/api/price`, Bedrock, optional SageMaker DeepAR. |
| **Lambdas** | **alerts-handler** (DynamoDB users + S3 calendar + RSS → webhook). **festival-orchestrator** (Dashboard forecast + calendar → webhook). |
| **AWS** | Lambda, EventBridge, DynamoDB, S3, Bedrock, Cognito, Transcribe, Polly, SSM (Change Calendar). |

---

## Quick start

```bash
# Clone and enter repo
git clone https://github.com/Sid3503/ai-sahayak.git && cd ai-sahayak

# Env (see .env.example in each app)
cp app/backend/agents/.env.example app/backend/agents/.env
cp app/frontend/.env.example app/frontend/.env
# … set VITE_AGENT_API_BASE, backend AWS/MongoDB/Dashboard URL as needed

# One command to run backend (8000), frontend (5173), Dashboard API (8001), Dashboard UI (5174)
./start.sh
```

Open **http://localhost:5173** → Onboarding → sign in as **Raju** (or Ramesh, Suresh, Kanta, Lakshmi) → Dashboard → **My day** for chat and alerts.

---

## Repo layout

```
ai-sahayak/
├── start.sh                 # Run all 4 services
├── app/
│   ├── frontend/            # Our site: landing, onboarding, Dashboard embed, My day
│   ├── backend/
│   │   ├── agents/          # FastAPI + LangGraph (chat, alerts API, profile)
│   │   └── lambda/          # Alerts-handler Lambda (calendar + webhook)
│   └── Dashboard/           # Friend’s Flask API + Control Centre React
├── infra/                   # EventBridge, Lambdas, etc.
└── PROJECT.md               # Detailed project doc
```

---

## Test alerts locally

Backend and frontend running (e.g. via `./start.sh`):

```bash
cd app/backend/agents && python scripts/test_alerts_incoming.py
```

Then open **My day**, select **Raju** — the test alert appears in chat within ~30s.

---

## License

See repository settings. For hackathon use and collaboration with the team.
