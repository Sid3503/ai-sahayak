#!/bin/bash
# ============================================================
#  AI Sahayak – Run on EC2 (backends only, reachable by Lambda)
#  Bind to 0.0.0.0 so Lambda / external callers can reach APIs.
#  Run from repo root: ./deploy/ec2-run.sh
#  For long-running: nohup ./deploy/ec2-run.sh > ec2.log 2>&1 &
#  Or run inside screen/tmux and detach.
# ============================================================

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUR_BACKEND="$ROOT/app/backend/agents"
FRIEND_BACKEND="$ROOT/app/Dashboard"

# So Lambda can call Dashboard API
export AI_SAHAYAK_API_HOST="0.0.0.0"
export AI_SAHAYAK_API_PORT="8001"

# DeepAR endpoints (adjust names if different in your account)
export AI_SAHAYAK_DEEPAR_ENDPOINT_RAJU="ai-sahayak-deepar-raju-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_RAMESH="ai-sahayak-deepar-ramesh-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_SURESH="ai-sahayak-deepar-suresh-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_KANTA="ai-sahayak-deepar-kanta-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_LAKSHMI="ai-sahayak-deepar-lakshmi-endpoint"

# Load Dashboard .env for AWS_* if present
for _f in "$FRIEND_BACKEND/.env" "$FRIEND_BACKEND/.env.local"; do
  [ -f "$_f" ] && set -a && . "$_f" && set +a
done

# Load agents .env (Bedrock, DynamoDB, etc.) so bot works on EC2
for _f in "$OUR_BACKEND/.env" "$OUR_BACKEND/.env.local"; do
  [ -f "$_f" ] && set -a && . "$_f" && set +a
done

# Agents call Dashboard API for pricing/KPIs; on EC2 both run on same host
export DASHBOARD_API_BASE_URL="${DASHBOARD_API_BASE_URL:-http://127.0.0.1:8001}"

PIDS=()
cleanup() {
  echo "Stopping services..."
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null; done
  wait
  exit 0
}
trap cleanup INT TERM

# 1. Our backend (FastAPI :8000)
echo "Starting our backend on 0.0.0.0:8000..."
(cd "$OUR_BACKEND" && export PYTHONPATH="$OUR_BACKEND/src:$PYTHONPATH" && .venv/bin/python src/ai_sahayak/main.py 2>&1 | sed 's/^/[backend:8000] /') &
PIDS+=($!)

# 2. Friend's backend (Flask :8001)
echo "Starting Dashboard API on 0.0.0.0:8001..."
(cd "$FRIEND_BACKEND" && .venv/bin/python app.py --mode api --host 0.0.0.0 --port 8001 2>&1 | sed 's/^/[dashboard:8001] /') &
PIDS+=($!)

echo ""
echo "Backends running. Lambda can use: http://<this-server-ip>:8001"
echo "Press Ctrl+C to stop."
wait
