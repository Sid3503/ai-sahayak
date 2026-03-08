#!/usr/bin/env python3
"""
Run on EC2 to find why ai-sahayak-users isn't updated when user sets "alert at 1 pm".
Usage: cd ~/ai-sahayak && python3 deploy/ec2-check-alert-dynamodb.py
"""
import os
import sys

# Load agents .env so we see same env as the service
env_file = os.path.expanduser("~/ai-sahayak/app/backend/agents/.env")
if os.path.exists(env_file):
    for line in open(env_file):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip("'\"")

USERS_TABLE = os.environ.get("USERS_TABLE", "ai_sahayak_user_info")
ALERT_USERS_TABLE = (os.environ.get("ALERT_USERS_TABLE") or "").strip() or USERS_TABLE
REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "ap-south-1"))

print("1. Env (what agents would use):")
print(f"   USERS_TABLE       = {USERS_TABLE}")
print(f"   ALERT_USERS_TABLE = {ALERT_USERS_TABLE}")
print(f"   AWS_REGION        = {REGION}")
if ALERT_USERS_TABLE != "ai-sahayak-users":
    print("   >>> ALERT_USERS_TABLE is NOT ai-sahayak-users, so alert time is written to the WRONG table!")
else:
    print("   >>> ALERT_USERS_TABLE is correct (ai-sahayak-users).")

print("\n2. Testing DynamoDB UpdateItem on ai-sahayak-users for raju...")
try:
    import boto3
    from botocore.exceptions import ClientError
    table = boto3.resource("dynamodb", region_name=REGION).Table("ai-sahayak-users")
    table.update_item(
        Key={"user_id": "raju"},
        UpdateExpression="SET alert_time_hour_ist = :h, alert_time_minute_ist = :m",
        ExpressionAttributeValues={":h": 13, ":m": 0},
    )
    print("   [OK] UpdateItem succeeded. Check DynamoDB console -> raju item -> you should see alert_time_hour_ist=13, alert_time_minute_ist=0.")
except ClientError as e:
    print(f"   [FAIL] {e.response['Error']['Code']}: {e.response['Error']['Message']}")
    print("   >>> Fix IAM (dynamodb:UpdateItem on ai-sahayak-users) or table name.")
except Exception as e:
    print(f"   [FAIL] {type(e).__name__}: {e}")
    sys.exit(1)

print("\n3. Intent router: does 'send me alert at 1 pm' hit alert_preferences?")
import re
user_message = "send me alert at 1 pm"
if re.search(r"\d+\s*baje|bhejo|alert\s*(time|chahiye|at)|din\s*pehle\s*batao|\d+\s*(am|pm)|alert\s+at|send\s+(me\s+)?alert", user_message):
    print("   [OK] Regex matches -> would route to alert_preferences.")
else:
    print("   [MISS] Regex does NOT match -> would NOT route to alert_preferences (LLM might reply instead).")

print("\n4. Agents code: does alert_preferences node exist?")
alert_pref_path = os.path.expanduser("~/ai-sahayak/app/backend/agents/src/ai_sahayak/graphs/workflows/alert_preferences.py")
if os.path.exists(alert_pref_path):
    print(f"   [OK] {alert_pref_path} exists.")
else:
    print(f"   [MISS] {alert_pref_path} NOT FOUND -> pull latest code on EC2.")
print("\nDone. If step 2 passed, DynamoDB is writable; then ensure ALERT_USERS_TABLE=ai-sahayak-users and restart agents.")
