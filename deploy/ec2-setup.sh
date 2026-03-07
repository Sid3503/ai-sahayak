#!/bin/bash
# ============================================================
#  AI Sahayak – EC2 one-time setup (Amazon Linux 2023)
#  Run on EC2 after SSH: bash ec2-setup.sh
#  Then fill app/Dashboard/.env with AWS keys and run ec2-run.sh
# ============================================================

set -e
REPO_URL="${REPO_URL:-https://github.com/Sid3503/ai-sahayak.git}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/ai-sahayak}"

echo "Installing system deps (git, python3, node if missing)..."
sudo dnf install -y git python3 python3-pip 2>/dev/null || sudo yum install -y git python3 python3-pip
if ! command -v node &>/dev/null; then
  curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
  sudo dnf install -y nodejs 2>/dev/null || sudo yum install -y nodejs
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Repo already at $INSTALL_DIR – pulling latest..."
  cd "$INSTALL_DIR" && git pull
  cd - >/dev/null
  cd "$INSTALL_DIR"
else
  echo "Cloning repo into $INSTALL_DIR..."
  git clone "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

# —— Agents backend (port 8000) ——
echo "Setting up agents backend..."
AGENTS="$INSTALL_DIR/app/backend/agents"
python3 -m venv "$AGENTS/.venv"
"$AGENTS/.venv/bin/pip" install -r "$AGENTS/requirements.txt"

# —— Dashboard backend (port 8001) ——
echo "Setting up Dashboard backend..."
DASH="$INSTALL_DIR/app/Dashboard"
python3 -m venv "$DASH/.venv"
"$DASH/.venv/bin/pip" install -r "$DASH/requirements.txt"

# —— Frontends (optional, for full UI on EC2) ——
echo "Installing frontend deps..."
if [ -f "$INSTALL_DIR/app/frontend/package.json" ]; then
  (cd "$INSTALL_DIR/app/frontend" && npm ci 2>/dev/null || npm install)
fi
if [ -f "$DASH/package.json" ]; then
  (cd "$DASH" && npm ci 2>/dev/null || npm install)
fi

# —— Env file ——
if [ ! -f "$DASH/.env" ]; then
  cp "$DASH/.env.example" "$DASH/.env"
  echo "Created $DASH/.env – please edit and set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION"
else
  echo ".env already exists in Dashboard"
fi

echo ""
echo "Setup done. Next:"
echo "  1. Edit: nano $DASH/.env   (set AWS keys, region=ap-south-1)"
echo "  2. Start: cd $INSTALL_DIR && ./deploy/ec2-run.sh"
echo "  3. Lambda: set AI_SAHAYAK_API_BASE_URL / BACKEND_ALERTS_URL to http://<EC2_PUBLIC_IP>:8001"
