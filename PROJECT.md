# AI Sahayak – Project Overview

Proactive intelligence platform for Indian kirana & MSME stores (AWS AI for Bharat Hackathon). One place: what the project does, what works, which code and tech stack do what, and how to run it.

---

## What It Does

- **Proactive alerts:** EventBridge + AWS Change Calendar (festivals) → Lambda / backend → demand insight → WhatsApp or in-app.
- **Reactive chat:** Shopkeeper asks in English/Hinglish (e.g. “sales?”, “low stock?”) → agent uses live dashboard KPIs + Bedrock → answer in same language.
- **Dashboard (Control Centre):** Pricing, forecast, what‑if, KPIs per retailer (Raju, Ramesh, Suresh, Kanta, Lakshmi). Forecast uses SageMaker DeepAR when endpoints are configured; otherwise local proxy.
- **My day (Live Alerts):** Post–sign-in chat scoped to the logged-in retailer; same agent + live data; alerts polled from backend.

---

## Tech Stack and Who Does What

| Layer | Tech | Role |
|-------|------|------|
| **Our website** | React, Vite, Tailwind, Lucide, Cognito | Landing, onboarding flow, sign-in, embed of friend’s Dashboard, “My day” chat UI. |
| **Our backend (agents)** | FastAPI, LangGraph, Bedrock, MongoDB (state), DynamoDB (profiles) | Chat logic, session, tools (dashboard data, etc.). Serves `/v1/webhook/incoming`, `/v1/alerts/for-user`, `/v1/profile`. |
| **Friend’s Dashboard backend** | Flask, Python, pandas, boto3 | `/api/meta`, `/api/kpis`, `/api/forecast`, `/api/price`, `/api/whatif`, `/api/model-status`. Uses Bedrock for explanations, SageMaker DeepAR for demand forecast when endpoints are set. |
| **Friend’s Dashboard frontend** | React, Vite | Control Centre UI (pricing, forecast charts, what‑if). Shown in iframe; can be locked to retailer via `?retailer=raju`. |
| **Lambdas** | Python, boto3 | (1) Festival orchestrator: EventBridge → calls Dashboard API for forecast/SKUs; (2) Alerts: panchang/calendar → webhook to backend. |
| **AWS** | Bedrock, SageMaker (DeepAR), DynamoDB, S3, EventBridge, Cognito, SSM (Change Calendar) | Models, forecast endpoints, store/user data, calendar, auth, scheduling. |

- **Bedrock:** Used by our agents (LangGraph) and by friend’s Dashboard (explanations, NL). Requires `bedrock:InvokeModel` and `bedrock:ListFoundationModels`.
- **SageMaker DeepAR:** Used only in friend’s Dashboard backend for `/api/forecast` when env vars point to your endpoints (e.g. `ai-sahayak-deepar-raju-endpoint`).
- **DynamoDB:** Our agents use `ai_sahayak_stores` (store profile) and `ai-sahayak-users` (user profile). Friend’s app may use other tables for its own data.

---

## Repo Layout (What Code Lives Where)

```
ai-sahayak/
├── start.sh                    # Start all 4 processes (our backend 8000, our frontend 5173, friend backend 8001, friend frontend 5174)
├── PROJECT.md                  # This file – single project doc
├── app/
│   ├── frontend/                # Our website (React, Vite). Sign-in, Dashboard embed, My day chat.
│   │   ├── src/App.tsx         # Main app, views (landing, chat, dashboard, day), chat handlers
│   │   ├── src/dashboard/      # Dashboard wrapper, welcome card, iframe to Control Centre
│   │   └── .env                # VITE_AGENT_API_BASE (our backend, e.g. http://localhost:8000)
│   ├── backend/
│   │   ├── agents/             # Our backend (FastAPI, LangGraph). Chat, alerts API, profile.
│   │   │   ├── src/ai_sahayak/
│   │   │   │   ├── api/        # Routes: chat, alerts, profile, webhook
│   │   │   │   ├── graphs/     # LangGraph retail assistant
│   │   │   │   ├── tools/      # dashboard_data_tool (calls friend’s /api/kpis), DynamoDB, etc.
│   │   │   │   └── config/     # settings (env vars)
│   │   │   └── .env            # AWS keys, MONGODB_URI, AI_SAHAYAK_API_BASE_URL (friend’s Dashboard API for live KPIs)
│   │   └── lambda/             # Alerts Lambda (panchang → webhook)
│   └── Dashboard/              # Friend’s app: backend + frontend
│       ├── app.py              # Flask API: /api/meta, /api/kpis, /api/forecast, /api/price, /api/whatif, Bedrock, DeepAR
│       ├── src/                # Friend’s Control Centre React app (iframe)
│       ├── aws/lambda/         # Festival orchestrator Lambda code + env reference
│       └── .env.local           # VITE_API_PROXY_TARGET for friend’s frontend
└── docs/                       # (Optional) extra setup notes; only PROJECT.md is the main doc now
```

- **Our frontend** talks to **our backend** (`VITE_AGENT_API_BASE`) for chat and alerts.
- **Our backend** talks to **friend’s Dashboard API** (`AI_SAHAYAK_API_BASE_URL`, e.g. `http://127.0.0.1:8001/api`) for live KPIs in “My day”.
- **Friend’s frontend** (iframe) talks to **friend’s backend** (same host, proxy or same origin).

---

## What Works End-to-End

1. **Landing → Onboarding (chat) → Dashboard (sign-in) → Control Centre (iframe)**  
   Demo users: Raju, Ramesh, Suresh, Kanta, Lakshmi (credentials in UI). Iframe gets `?retailer=raju` etc. so data is scoped.

2. **Dashboard (Model Status)**  
   Bedrock: Connected when AWS credentials are exported before `./start.sh`.  
   Forecast: DeepAR (SageMaker) when SageMaker endpoint env vars are set in `start.sh` for that retailer.

3. **My day (Live Alerts)**  
   Chat uses `user_id` = retailer key (raju, ramesh, …). Backend calls friend’s `/api/kpis?dataset_key=raju` for live sales/inventory. No mock fallback if you set “show error” behaviour.

4. **Festival orchestrator Lambda**  
   EventBridge (or manual invoke) → Lambda → friend’s `/api/meta`, `/api/forecast`. Needs `AI_SAHAYAK_API_BASE_URL` and optional calendar env vars. Optional: `run_all_retailers` to run for all five retailers in one invocation.

5. **Alerts Lambda**  
   Reads panchang from S3, posts to backend webhook; backend stores/serves alerts per `user_id` (retailer key).

---

## How to Run Locally

1. **Terminal – export AWS (for Bedrock + SageMaker in friend’s backend):**
   ```bash
   export AWS_ACCESS_KEY_ID="your_key"
   export AWS_SECRET_ACCESS_KEY="your_secret"
   export AWS_DEFAULT_REGION="ap-south-1"
   ```

2. **Start everything:**
   ```bash
   cd ai-sahayak
   ./start.sh
   ```

3. **URLs:**  
   - Our site: http://localhost:5173  
   - Friend’s Control Centre (standalone): http://localhost:5174/control-centre/  
   - Our backend: http://localhost:8000  
   - Friend’s API: http://localhost:8001  

4. **Check Bedrock / DeepAR:**  
   After starting the stack, open: **http://127.0.0.1:8001/api/model-status?dataset_key=ramesh**  
   Expect `bedrock_ready: true` and `forecast_primary: "DeepAR (SageMaker)"` when configured.  
   **If Bedrock shows "Not Ready":** (1) Put `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` in `app/Dashboard/.env.local` (or export them in the same terminal before `./start.sh`). (2) Ensure IAM has **bedrock:InvokeModel** and **bedrock:ListFoundationModels** for the region (e.g. `ap-south-1`).

---

## Where are all the env files? (for your friend)

| Location | File | Purpose |
|----------|------|--------|
| **Our website (React)** | `app/frontend/.env` | Create from `app/frontend/.env.example`. Backend URL, Cognito, Control Centre URL. |
| **Our backend (agents)** | `app/backend/agents/.env` | Create from `app/backend/agents/.env.example`. AWS keys, Bedrock region, MongoDB, Cognito pool ID. |
| **Friend’s Dashboard** | `app/Dashboard/.env.local` | Optional. Used by friend’s Control Centre frontend (e.g. `VITE_API_PROXY_TARGET`). |

**Copy-paste setup for your friend:**

1. **Frontend (our site)**  
   ```bash
   cp app/frontend/.env.example app/frontend/.env
   # Edit app/frontend/.env: set VITE_AGENT_API_BASE, VITE_COGNITO_*, VITE_CONTROL_CENTRE_URL
   ```

2. **Backend (our agents)**  
   ```bash
   cp app/backend/agents/.env.example app/backend/agents/.env
   # Edit app/backend/agents/.env: set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, COGNITO_USER_POOL_ID, MONGODB_URI
   ```

3. **Friend’s Dashboard**  
   Uses shell env (e.g. `export AWS_ACCESS_KEY_ID=...`) and optional `app/Dashboard/.env.local` for the Control Centre frontend.

**Note:** `.env` files are gitignored; only `.env.example` is in the repo. Your friend creates `.env` from the example and fills in real values.

---

## Env Vars (Summary)

- **Our backend (agents) `.env`:**  
  `AWS_*`, `MONGODB_URI`, `AI_SAHAYAK_API_BASE_URL` (friend’s API, e.g. `http://127.0.0.1:8001/api`), `STORES_TABLE`, `USERS_TABLE`, `COGNITO_*`, etc.

- **Our frontend `.env`:**  
  `VITE_AGENT_API_BASE` (e.g. `http://localhost:8000` for local), `VITE_CONTROL_CENTRE_URL`, Cognito vars.

- **Friend’s backend:**  
  Uses same shell env for AWS. DeepAR endpoints set in `start.sh` (`AI_SAHAYAK_DEEPAR_ENDPOINT_RAJU`, etc.). Bedrock model via `AI_SAHAYAK_BEDROCK_MODEL_ID` if needed.

- **Lambdas (in AWS Console):**  
  Festival: `AI_SAHAYAK_API_BASE_URL`, `AI_SAHAYAK_DATASET_KEY`, calendar/SNS as needed.  
  Alerts: `CALENDAR_S3_BUCKET`, `BACKEND_WEBHOOK_URL`, `USERS_TABLE`, etc.

---

## Single Doc Policy

This file (`PROJECT.md`) is the one project-wide doc. All other `.md` / `.pdf` / extra docs in the repo have been removed or are legacy; for “what works, which code, which tech” use this file only.
