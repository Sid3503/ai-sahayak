"""
Test Lambda -> Chat integration: POST to /v1/alerts/incoming then GET /v1/alerts/for-user.
Run with agents backend up (e.g. uvicorn). Use this to verify alerts show in My day chat.

  python scripts/test_alerts_incoming.py
  python scripts/test_alerts_incoming.py --base http://localhost:8000 --user ramesh
"""
import argparse
import json
import urllib.request

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:8000", help="Agents API base URL")
    p.add_argument("--user", default="raju", help="user_id (raju, ramesh, suresh, kanta, lakshmi)")
    args = p.parse_args()
    base = args.base.rstrip("/")
    user_id = args.user.strip().lower()

    # 1) POST one alert (same payload Lambda sends)
    payload = {
        "user_id": user_id,
        "text": "Test: Aaj ka daily forecast — Holi aa rahi hai! Gulal aur Ghee ka stock check karo.",
        "alert_type": "daily_forecast",
        "platform": "whatsapp",
        "is_alert": True,
        "event_confidence_score": 85,
    }
    url_post = f"{base}/v1/alerts/incoming"
    req = urllib.request.Request(
        url_post,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            out = json.loads(body) if body else {}
            print(f"POST {url_post} -> {r.status} {out}")
    except Exception as e:
        print(f"POST failed: {e}")
        return

    # 2) GET alerts for user (what My day chat polls)
    url_get = f"{base}/v1/alerts/for-user?user_id={user_id}"
    req2 = urllib.request.Request(url_get, method="GET")
    try:
        with urllib.request.urlopen(req2, timeout=5) as r:
            body = r.read().decode("utf-8")
            data = json.loads(body) if body else {}
            alerts = data.get("alerts", [])
            print(f"GET {url_get} -> {len(alerts)} alert(s)")
            for a in alerts[:3]:
                print(f"  - {a.get('id', '')[:8]}... | {a.get('text', '')[:60]}...")
    except Exception as e:
        print(f"GET failed: {e}")
        return

    print("\nDone. Open My day (Live Alerts), select user", user_id, "— you should see the test alert within 30s (poll interval).")


if __name__ == "__main__":
    main()
