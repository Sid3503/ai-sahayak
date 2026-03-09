#!/bin/bash
# Run on EC2 to rebuild the main frontend (no pricing page) and reload nginx.
# Usage: cd ~/ai-sahayak && ./deploy/ec2-rebuild-frontend-no-pricing.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 1) Check source has no Pricing page (optional)
if grep -q "Pricing for MSME\|MSME_PLANS\|id: 'pricing'" app/frontend/src/App.tsx 2>/dev/null; then
  echo "WARN: App.tsx still has pricing page code. Pull latest: git pull origin main"
else
  echo "OK: Source has no pricing page."
fi

# 2) EC2 public IP for build
BASE_URL="${BASE_URL:-http://13.126.200.157}"
export VITE_AGENT_API_BASE="${BASE_URL}:8000"
export VITE_CONTROL_CENTRE_URL="${BASE_URL}/control-centre/"
export VITE_COGNITO_REDIRECT_URI="${BASE_URL}"
echo "Building main frontend with BASE_URL=$BASE_URL ..."

cd "$ROOT/app/frontend"
npm ci 2>/dev/null || npm install --no-audit --no-fund
npm run build

echo "Build done. app/frontend/dist updated."

# 3) Copy to nginx docroot (nginx serves from /var/www/ai-sahayak/frontend)
WWW_FRONTEND="/var/www/ai-sahayak/frontend"
if [ -d "$ROOT/app/frontend/dist" ]; then
  sudo mkdir -p "$WWW_FRONTEND"
  sudo cp -a "$ROOT/app/frontend/dist"/. "$WWW_FRONTEND"/
  echo "Copied dist to $WWW_FRONTEND"
fi

# 4) Reload nginx if present
if command -v nginx &>/dev/null && sudo systemctl is-active --quiet nginx 2>/dev/null; then
  sudo nginx -t && sudo systemctl reload nginx
  echo "Nginx reloaded. Hard-refresh the browser (Ctrl+Shift+R)."
else
  echo "Nginx not running or not found. If you serve static files another way, point them to: $ROOT/app/frontend/dist"
fi
