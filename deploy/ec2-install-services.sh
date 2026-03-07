#!/bin/bash
# Install systemd services so AI Sahayak backends start on boot.
# Run once on EC2 (with sudo):  sudo ./deploy/ec2-install-services.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SVC_AGENTS="$ROOT/deploy/ai-sahayak-agents.service"
SVC_DASHBOARD="$ROOT/deploy/ai-sahayak-dashboard.service"

if [ ! -f "$SVC_AGENTS" ] || [ ! -f "$SVC_DASHBOARD" ]; then
  echo "Run this from the ai-sahayak repo root on EC2 (e.g. ~/ai-sahayak)."
  exit 1
fi

sudo cp "$SVC_AGENTS" /etc/systemd/system/
sudo cp "$SVC_DASHBOARD" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-sahayak-agents ai-sahayak-dashboard
sudo systemctl start ai-sahayak-agents ai-sahayak-dashboard
echo "Services enabled and started. Check: sudo systemctl status ai-sahayak-agents ai-sahayak-dashboard"
echo "After reboot they will start automatically."
