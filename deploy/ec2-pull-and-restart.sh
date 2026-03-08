#!/bin/bash
# Run on EC2 after SSH (or run the one-liner below from your Mac).
# Pulls latest from GitHub and restarts backend services so the live site (13.126.200.157) is updated.

set -e
INSTALL_DIR="${INSTALL_DIR:-$HOME/ai-sahayak}"
cd "$INSTALL_DIR"

echo "Pulling latest from origin main..."
git fetch origin main
git pull origin main

echo "Updating Python deps (agents)..."
(cd app/backend/agents && .venv/bin/pip install -q -r requirements.txt 2>/dev/null || true)

echo "Updating Python deps (Dashboard)..."
(cd app/Dashboard && .venv/bin/pip install -q -r requirements.txt 2>/dev/null || true)

echo "Updating frontend deps (optional)..."
(cd app/frontend && npm ci 2>/dev/null || npm install --no-audit --no-fund) || true

# Restart services if systemd is used
if systemctl is-active --quiet ai-sahayak-agents 2>/dev/null; then
  echo "Restarting ai-sahayak-agents and ai-sahayak-dashboard..."
  sudo systemctl restart ai-sahayak-agents ai-sahayak-dashboard
  echo "Done. Check: sudo systemctl status ai-sahayak-agents ai-sahayak-dashboard"
else
  echo "Systemd services not found. If you run with ./deploy/ec2-run.sh, stop it (Ctrl+C) and run it again from $INSTALL_DIR."
fi
