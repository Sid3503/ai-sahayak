#!/bin/bash
# Run on EC2 to diagnose why "12 pm bhejo" doesn't trigger alert preferences.
# Usage: bash deploy/ec2-diagnose-alert-preferences.sh

set -e
cd "$(dirname "$0")/.."
AGENTS="app/backend/agents"

echo "=== 1. Code present? (alert_preferences_node, ALERT_USERS_TABLE, intent fast path) ==="
grep -l "alert_preferences_node" app/backend/agents/src/ai_sahayak/graphs/workflows/retail_assistant.py 2>/dev/null && echo "  [OK] retail_assistant has alert_preferences_node" || echo "  [MISSING] retail_assistant.py - pull latest"
grep -l "ALERT_USERS_TABLE" "$AGENTS/src/ai_sahayak/tools/data_sources/user_preferences_dynamodb.py" 2>/dev/null && echo "  [OK] user_preferences_dynamodb has ALERT_USERS_TABLE" || echo "  [MISSING] user_preferences_dynamodb.py - pull latest"
grep "alert_preferences|send.*alert" "$AGENTS/src/ai_sahayak/graphs/nodes/router/intent_router.py" 2>/dev/null | head -1 && echo "  [OK] intent_router has alert_preferences fast path" || echo "  [MISSING] intent_router.py - pull latest"

echo ""
echo "=== 2. Env: ALERT_USERS_TABLE set? ==="
grep "ALERT_USERS_TABLE" "$AGENTS/.env" 2>/dev/null && echo "  [OK]" || echo "  [NOT SET] Run: echo 'ALERT_USERS_TABLE=ai-sahayak-users' >> $AGENTS/.env"

echo ""
echo "=== 3. Last 15 lines of agents log (look for next_intent or alert_preferences or errors) ==="
sudo journalctl -u ai-sahayak-agents -n 15 --no-pager 2>/dev/null || true

echo ""
echo "=== 4. Test DynamoDB update (raju, 12 PM) — requires AWS creds + ALERT_USERS_TABLE in .env ==="
(cd "$AGENTS" && { [ -f .env ] && set -a && . ./.env && set +a; } 2>/dev/null; export PYTHONPATH="$(pwd)/src:$PYTHONPATH"; .venv/bin/python -c "
from ai_sahayak.tools.data_sources.user_preferences_dynamodb import update_alert_preferences
ok = update_alert_preferences('raju', alert_time_hour_ist=12, alert_time_minute_ist=0)
print('  update_alert_preferences(raju, 12:00) ->', ok)
" 2>&1) || echo "  (run failed - check .env and ALERT_USERS_TABLE)"

echo ""
echo "=== Next: Send '12 pm bhejo' in My day, then run: sudo journalctl -u ai-sahayak-agents -n 30 --no-pager ==="
