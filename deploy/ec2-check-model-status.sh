#!/usr/bin/env bash
# Run on EC2 to see why Model Status shows "Local Proxy" / "Fallback" instead of "Endpoint Active" / "Loaded".
# Usage: bash deploy/ec2-check-model-status.sh   (from repo root, e.g. ~/ai-sahayak)

INSTALL_DIR="${INSTALL_DIR:-$HOME/ai-sahayak}"
DASH="$INSTALL_DIR/app/Dashboard"
ENV_FILE="$DASH/.env"

echo "=== 1. Model Status API (what the UI reads) ==="
curl -s "http://127.0.0.1:8001/api/model-status?dataset_key=raju" 2>/dev/null | python3 -m json.tool 2>/dev/null || curl -s "http://127.0.0.1:8001/api/model-status?dataset_key=raju" || echo "  [Dashboard not reachable on :8001]"
echo ""

echo "=== 2. DeepAR env vars (Dashboard must see these for 'Endpoint Active') ==="
[ -f "$ENV_FILE" ] || echo "  (No $ENV_FILE found)"
for key in AI_SAHAYAK_DEEPAR_ENDPOINT AI_SAHAYAK_DEEPAR_ENDPOINT_RAJU AI_SAHAYAK_DEEPAR_ENDPOINT_RAMESH; do
  val=""
  [ -f "$ENV_FILE" ] && val=$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' | head -1)
  if [ -n "$val" ]; then
    echo "  $key = $val"
  else
    echo "  $key = [NOT SET in .env]"
  fi
done
# What systemd actually passes is only from EnvironmentFile; ec2-run.sh exports are NOT used by systemd
echo "  (If all NOT SET: add them to $ENV_FILE and restart: sudo systemctl restart ai-sahayak-dashboard)"

echo ""
echo "=== 3. DNN model files (must exist in Dashboard dir for 'Loaded') ==="
for f in nn_demand_model.pt nn_scaler.npz; do
  if [ -f "$DASH/$f" ]; then
    echo "  $DASH/$f  [OK]"
  else
    echo "  $DASH/$f  [MISSING]"
  fi
done
echo "  (If MISSING: copy or train nn_demand_model.pt and nn_scaler.npz into app/Dashboard, then restart dashboard)"

echo ""
echo "=== 4. Dashboard service status ==="
systemctl is-active ai-sahayak-dashboard 2>/dev/null && echo "  ai-sahayak-dashboard: active" || echo "  ai-sahayak-dashboard: not active"
echo ""
echo "=== 5. Last Dashboard log (errors loading NN or DeepAR?) ==="
sudo journalctl -u ai-sahayak-dashboard -n 25 --no-pager 2>/dev/null | tail -20 || true
