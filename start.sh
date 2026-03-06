#!/bin/bash
# ============================================================
#  AI Sahayak – Start Everything
#  Starts all 4 processes with one command:
#    1. Our backend   (FastAPI on :8000)
#    2. Our frontend  (Vite React on :5173)
#    3. Friend's backend (Flask on :8001)
#    4. Friend's frontend (Vite React on :5174)
#
#  Usage:
#    chmod +x start.sh   (first time only)
#    ./start.sh
#
#  For Dashboard Bedrock + SageMaker: in the same terminal, before ./start.sh, run:
#    export AWS_ACCESS_KEY_ID="your_access_key"
#    export AWS_SECRET_ACCESS_KEY="your_secret_key"
#    export AWS_DEFAULT_REGION="ap-south-1"
#  Then check: http://127.0.0.1:8001/api/model-status?dataset_key=ramesh  (bedrock_ready should be true)
#
#  Stop all:  Press Ctrl+C
# ============================================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUR_BACKEND="$ROOT/app/backend/agents"
OUR_FRONTEND="$ROOT/app/frontend"
FRIEND_BACKEND="$ROOT/app/Dashboard"
FRIEND_FRONTEND="$ROOT/app/Dashboard"

PIDS=()

cleanup() {
  echo ""
  echo "Stopping all services..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null
  done
  wait
  echo "All stopped."
  exit 0
}
trap cleanup INT TERM

# ── 1. Our Backend (FastAPI / uvicorn on port 8000) ──────────────────────────
echo "Starting OUR backend (port 8000)..."
(
  cd "$OUR_BACKEND"
  export PYTHONPATH="$OUR_BACKEND/src:$PYTHONPATH"
  if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
  elif [ -f "../../../.venv/bin/python" ]; then
    PYTHON="../../../.venv/bin/python"
  else
    PYTHON="python3"
  fi
  $PYTHON src/ai_sahayak/main.py 2>&1 | sed 's/^/[our-backend] /'
) &
PIDS+=($!)

# ── 2. Our Frontend (Vite on port 5173) ──────────────────────────────────────
echo "Starting OUR frontend (port 5173)..."
(
  cd "$OUR_FRONTEND"
  npm run dev 2>&1 | sed 's/^/[our-frontend] /'
) &
PIDS+=($!)

# ── 3. Friend's Backend (Flask on port 8001) ─────────────────────────────────
# Free port 8001 if something from a previous run is still using it
if command -v lsof >/dev/null 2>&1; then
  (lsof -ti :8001 | xargs kill -9 2>/dev/null) || true
  sleep 1
fi
echo "Starting FRIEND'S backend (port 8001)..."
(
  cd "$FRIEND_BACKEND"
  # SageMaker DeepAR endpoints per retailer (must already exist in ap-south-1).
  # These env vars are read by app.py via get_deepar_endpoint().
  export AI_SAHAYAK_DEEPAR_ENDPOINT_RAJU="ai-sahayak-deepar-raju-endpoint"
  export AI_SAHAYAK_DEEPAR_ENDPOINT_RAMESH="ai-sahayak-deepar-ramesh-endpoint"
  export AI_SAHAYAK_DEEPAR_ENDPOINT_SURESH="ai-sahayak-deepar-suresh-endpoint"
  export AI_SAHAYAK_DEEPAR_ENDPOINT_KANTA="ai-sahayak-deepar-kanta-endpoint"
  export AI_SAHAYAK_DEEPAR_ENDPOINT_LAKSHMI="ai-sahayak-deepar-lakshmi-endpoint"
  if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
  else
    PYTHON="python3"
  fi
  $PYTHON app.py --mode api --port 8001 2>&1 | sed 's/^/[friend-backend] /'
) &
PIDS+=($!)

# ── 4. Friend's Frontend (Vite on port 5174) ─────────────────────────────────
echo "Starting FRIEND'S frontend (port 5174)..."
(
  cd "$FRIEND_FRONTEND"
  npm run dev 2>&1 | sed 's/^/[friend-frontend] /'
) &
PIDS+=($!)

echo ""
echo "============================================================"
echo "  All services started!"
echo "  Our frontend  →  http://localhost:5173   (sign in here)"
echo "  Friend's dash →  http://localhost:5174   (embedded after sign in)"
echo "  Our backend   →  http://localhost:8000"
echo "  Friend's API  →  http://localhost:8001"
echo "============================================================"
echo "  Press Ctrl+C to stop everything."
echo ""

wait
