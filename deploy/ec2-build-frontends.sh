#!/bin/bash
# Build both frontends for production on EC2. Set BASE_URL before running, or pass as first arg.
# Example: BASE_URL=http://13.232.40.210 ./deploy/ec2-build-frontends.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="${1:-$BASE_URL}"
if [ -z "$BASE_URL" ]; then
  BASE_URL="http://$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'localhost')"
fi
echo "Building frontends with BASE_URL=$BASE_URL"

# Main frontend: agent API, control centre, and Cognito redirect for EC2
export VITE_AGENT_API_BASE="${BASE_URL}:8000"
export VITE_CONTROL_CENTRE_URL="${BASE_URL}/control-centre/"
export VITE_COGNITO_REDIRECT_URI="${BASE_URL}"
# Load Cognito vars from .env if present (so "Cognito is not configured" goes away)
if [ -f "$ROOT/app/frontend/.env" ]; then
  set -a
  . "$ROOT/app/frontend/.env"
  set +a
fi
# BASE_URL must win for API base (avoid .env overriding with old IP)
export VITE_AGENT_API_BASE="${BASE_URL}:8000"
export VITE_CONTROL_CENTRE_URL="${BASE_URL}/control-centre/"
export VITE_COGNITO_REDIRECT_URI="${BASE_URL}"
cd "$ROOT/app/frontend"
npm ci 2>/dev/null || npm install --no-audit --no-fund
npm run build

# Dashboard (control centre): API will be proxied by nginx at /api
export VITE_API_PROXY_TARGET="${BASE_URL}"
cd "$ROOT/app/Dashboard"
npm ci 2>/dev/null || npm install --no-audit --no-fund
npm run build

echo "Done. Static files: app/frontend/dist and app/Dashboard/dist"
echo "Next: install nginx, copy deploy/nginx-ai-sahayak.conf, reload nginx."
