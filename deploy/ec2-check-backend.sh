#!/bin/bash
# Run on EC2 to check why the bot/Polly might not be reachable from the browser.
echo "=== 1. Agents service (port 8000) ==="
systemctl is-active ai-sahayak-agents 2>/dev/null || echo "Service not found"
echo ""
echo "=== 2. Is anything listening on 8000? ==="
ss -tlnp | grep 8000 || echo "Nothing on 8000"
echo ""
echo "=== 3. Curl backend health (localhost) ==="
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health
echo " (expect 200)"
echo ""
echo "=== 4. Last 15 lines of agents log ==="
journalctl -u ai-sahayak-agents -n 15 --no-pager 2>/dev/null || echo "No journalctl"
echo ""
echo "=== 5. If port 8000 is not open in Security Group, the browser cannot reach the bot. Open inbound TCP 8000 from 0.0.0.0/0 in EC2 Security Group. ==="
