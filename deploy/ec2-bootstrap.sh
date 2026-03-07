#!/bin/bash
# Run this ONCE on EC2 (from repo root) to create deploy/ec2-setup.sh and deploy/ec2-run.sh
# Then run: bash deploy/ec2-setup.sh
set -e
cd "$(dirname "$0")/.."
mkdir -p deploy

# Dashboard requirements.txt if missing (repo may not have it)
DASH_REQ="app/Dashboard/requirements.txt"
if [ ! -f "$DASH_REQ" ]; then
  echo "Creating $DASH_REQ..."
  cat > "$DASH_REQ" << 'ENDREQ'
flask>=3.0.0
boto3>=1.34.0
python-dotenv>=1.0.0
rich>=13.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
joblib>=1.3.0
python-docx>=1.0.0
ENDREQ
fi

# ec2-setup.sh
cat > deploy/ec2-setup.sh << 'ENDSETUP'
#!/bin/bash
set -e
INSTALL_DIR="${INSTALL_DIR:-$HOME/ai-sahayak}"
cd "$INSTALL_DIR"

echo "Installing system deps (git, python3, node if missing)..."
sudo dnf install -y git python3 python3-pip 2>/dev/null || sudo yum install -y git python3 python3-pip
if ! command -v node &>/dev/null; then
  curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
  sudo dnf install -y nodejs 2>/dev/null || sudo yum install -y nodejs
fi

echo "Setting up agents backend..."
AGENTS="$INSTALL_DIR/app/backend/agents"
python3 -m venv "$AGENTS/.venv"
"$AGENTS/.venv/bin/pip" install -r "$AGENTS/requirements.txt"

echo "Setting up Dashboard backend..."
DASH="$INSTALL_DIR/app/Dashboard"
python3 -m venv "$DASH/.venv"
"$DASH/.venv/bin/pip" install -r "$DASH/requirements.txt"

echo "Installing frontend deps..."
[ -f "$INSTALL_DIR/app/frontend/package.json" ] && (cd "$INSTALL_DIR/app/frontend" && npm ci 2>/dev/null || npm install)
[ -f "$DASH/package.json" ] && (cd "$DASH" && npm ci 2>/dev/null || npm install)

if [ ! -f "$DASH/.env" ]; then
  cp "$DASH/.env.example" "$DASH/.env"
  echo "Created $DASH/.env – edit and set AWS keys."
else
  echo ".env already exists"
fi
echo ""
echo "Setup done. Next: nano $DASH/.env   then   ./deploy/ec2-run.sh"
ENDSETUP

# ec2-run.sh
cat > deploy/ec2-run.sh << 'ENDRUN'
#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUR_BACKEND="$ROOT/app/backend/agents"
FRIEND_BACKEND="$ROOT/app/Dashboard"
export AI_SAHAYAK_API_HOST="0.0.0.0"
export AI_SAHAYAK_DEEPAR_ENDPOINT_RAJU="ai-sahayak-deepar-raju-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_RAMESH="ai-sahayak-deepar-ramesh-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_SURESH="ai-sahayak-deepar-suresh-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_KANTA="ai-sahayak-deepar-kanta-endpoint"
export AI_SAHAYAK_DEEPAR_ENDPOINT_LAKSHMI="ai-sahayak-deepar-lakshmi-endpoint"
for _f in "$FRIEND_BACKEND/.env" "$FRIEND_BACKEND/.env.local"; do
  [ -f "$_f" ] && set -a && . "$_f" && set +a
done
PIDS=()
cleanup() { for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null; done; wait; exit 0; }
trap cleanup INT TERM
echo "Starting backend :8000..."
(cd "$OUR_BACKEND" && PYTHONPATH="$OUR_BACKEND/src:$PYTHONPATH" .venv/bin/python src/ai_sahayak/main.py 2>&1 | sed 's/^/[8000] /') &
PIDS+=($!)
echo "Starting Dashboard :8001..."
(cd "$FRIEND_BACKEND" && .venv/bin/python app.py --mode api --host 0.0.0.0 --port 8001 2>&1 | sed 's/^/[8001] /') &
PIDS+=($!)
echo "Backends running. Lambda URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'EC2_IP'):8001"
echo "Press Ctrl+C to stop."
wait
ENDRUN

chmod +x deploy/ec2-setup.sh deploy/ec2-run.sh
echo "Created deploy/ec2-setup.sh and deploy/ec2-run.sh. Run: bash deploy/ec2-setup.sh"