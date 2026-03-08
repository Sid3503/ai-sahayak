#!/usr/bin/env python3
"""Run on EC2 once: fix intent_router.py so 'set alert for 2 pm' / 'send me alert at 2 pm' route to alert_preferences.
Usage: python3 deploy/ec2-fix-intent-router-alert.py   (from repo root on EC2)
"""
import os
path = os.path.expanduser("~/ai-sahayak/app/backend/agents/src/ai_sahayak/graphs/nodes/router/intent_router.py")
with open(path, "r") as f:
    content = f.read()

old_marker = 'return {"next_intent": "alert_preferences"}'
# Full regex: baje|bhejo|alert (time|chahiye|at)|din pehle|am/pm|alert at|send alert|set alert
new_line = '    if re.search(r"\\d+\\s*baje|bhejo|alert\\s*(time|chahiye|at)|din\\s*pehle\\s*batao|\\d+\\s*(am|pm)|alert\\s+at|send\\s+(me\\s+)?alert|set\\s+alert", user_message):'

lines = content.split("\n")
for i, line in enumerate(lines):
    if "alert_preferences" in line and "next_intent" in line and i > 0:
        prev = lines[i - 1]
        if "re.search" in prev and "user_message" in prev and "baje" in prev:
            lines[i - 1] = new_line
            break
with open(path, "w") as f:
    f.write("\n".join(lines))
print("Updated intent_router.py. Restart agents: sudo systemctl restart ai-sahayak-agents")
