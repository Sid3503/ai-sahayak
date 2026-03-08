#!/usr/bin/env python3
"""
Run on EC2 to check why Cognito user is not created after onboarding.
Usage (from repo root or from app/backend/agents):
  cd ~/ai-sahayak/app/backend/agents && .venv/bin/python scripts/check_cognito_onboarding.py
"""
import os
import sys

# Ensure we load .env and src is on path
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from ai_sahayak.config.settings import settings
from ai_sahayak.tools.auth.cognito_user import ensure_cognito_user

def main():
    print("=== 1. Config (no secrets printed) ===")
    pool_id = (settings.COGNITO_USER_POOL_ID or "").strip()
    print(f"  COGNITO_USER_POOL_ID set: {bool(pool_id)} (length {len(pool_id)})")
    print(f"  AWS_REGION: {getattr(settings, 'AWS_REGION', 'ap-south-1')}")
    print(f"  AWS_ACCESS_KEY_ID set: {bool((settings.AWS_ACCESS_KEY_ID or '').strip())}")
    print(f"  AWS_SECRET_ACCESS_KEY set: {bool((settings.AWS_SECRET_ACCESS_KEY or '').strip())}")

    if not pool_id:
        print("\n>>> FIX: Add COGNITO_USER_POOL_ID to app/backend/agents/.env (same as VITE_COGNITO_USER_POOL_ID in frontend). Then: sudo systemctl restart ai-sahayak-agents")
        return 1

    print("\n=== 2. Try creating a test user (test_diag_001 — safe to delete from Cognito later) ===")
    test_username = "test_diag_001"
    test_password = "Test1234!"
    ok = ensure_cognito_user(test_username, test_password, name="Diagnostic")
    print(f"  ensure_cognito_user returned: {ok}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
