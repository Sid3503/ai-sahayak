#!/usr/bin/env bash
# Run on EC2 to debug why 12:30 PM alert didn't fire.
# Usage: bash deploy/ec2-check-alerts.sh

set -e
REGION="${AWS_REGION:-ap-south-1}"
USERS_TABLE="${USERS_TABLE:-ai-sahayak-users}"
EC2_IP="${EC2_IP:-$(curl -s -m 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_IP')}"

echo "=== 1. Raju's alert preference in DynamoDB (Lambda reads this) ==="
echo "    Table: $USERS_TABLE | Region: $REGION"
if command -v aws &>/dev/null; then
  OUT=$(aws dynamodb get-item --table-name "$USERS_TABLE" --key '{"user_id":{"S":"raju"}}' --region "$REGION" 2>&1) || true
  if echo "$OUT" | grep -q "alert_time_hour_ist"; then
    echo "$OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('Item') or {}
h = d.get('alert_time_hour_ist', {}).get('N', '?')
m = d.get('alert_time_minute_ist', {}).get('N', '')
print(f'  raju: alert_time_hour_ist={h}, alert_time_minute_ist={m or \"(not set => top of hour)\"}')
" 2>/dev/null || echo "$OUT"
  elif echo "$OUT" | grep -q "ResourceNotFoundException"; then
    echo "  [ERROR] Table $USERS_TABLE not found in $REGION"
  else
    echo "  $OUT"
  fi
else
  echo "  [SKIP] aws CLI not found. In AWS Console: DynamoDB -> Tables -> $USERS_TABLE -> Explore items -> key user_id=raju, check alert_time_hour_ist, alert_time_minute_ist"
fi

echo ""
echo "=== 2. Agents backend (Lambda posts alerts here) ==="
AGENTS_URL="http://127.0.0.1:8000"
if curl -sf -m 3 "$AGENTS_URL/health" >/dev/null 2>&1; then
  echo "  $AGENTS_URL/health [OK]"
else
  echo "  $AGENTS_URL/health [FAIL or not reachable]"
fi
echo "  Lambda must have BACKEND_WEBHOOK_URL=http://${EC2_IP}:8000 (or this server's public IP)"

echo ""
echo "=== 3. Test: POST one alert to agents (should appear in My day for raju) ==="
TEST_PAYLOAD="{\"user_id\":\"raju\",\"phone\":\"\",\"text\":\"[Test] EC2 check-alerts script. Agar ye dikh raha hai to webhook kaam kar raha hai.\",\"platform\":\"web\",\"is_alert\":true}"
if curl -sf -m 5 -X POST "$AGENTS_URL/v1/alerts/incoming" -H "Content-Type: application/json" -d "$TEST_PAYLOAD" >/dev/null 2>&1; then
  echo "  POST /v1/alerts/incoming [OK] — check My day for raju for the test message"
else
  echo "  POST /v1/alerts/incoming [FAIL] — Lambda alerts won't show in My day until this works"
fi

echo ""
echo "=== 4. Why 12:30 might not have run ==="
echo "  - EventBridge must invoke the ALERTS Lambda every 30 minutes (e.g. rate(30 minutes) or cron at :00 and :30)."
echo "    If the rule runs only once per day (e.g. 9 AM IST), 12:30 will never run."
echo "  - In AWS Console: EventBridge -> Rules -> find the rule that targets ai-sahayak-alerts-handler -> check Schedule."
echo "    Change to: rate(30 minutes) so it runs at :00 and :30 every hour."
echo "  - Lambda env: BACKEND_WEBHOOK_URL must be this EC2 (e.g. http://${EC2_IP}:8000)."
echo ""
echo "=== 5. Quick Lambda test (ignore time = send now to all users) ==="
echo "  In AWS Console: Lambda -> ai-sahayak-alerts-handler -> Test -> Create event: {\"test_ignore_time\": true}"
echo "  Then run Test. Alerts should appear in My day for raju (if webhook and backend are OK)."
echo ""
echo "=== 6. Festival orchestrator (optional) ==="
echo "  Lambda -> ai-sahayak-festival-orchestrator: needs AI_SAHAYAK_API_BASE_URL pointing to Dashboard (e.g. http://${EC2_IP}:8001)."
echo "  EventBridge: separate rule if you use it; check it runs when you expect."
