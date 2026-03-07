"""
Notify the Dashboard (Flask) to drive UI from chat: switch tab, select SKU, show same data.
Used by pricing_query_node, sales_query_node, etc.
"""
import json
import os
import urllib.request


DASHBOARD_API_BASE = (
    os.getenv("DASHBOARD_API_BASE_URL") or os.getenv("AI_SAHAYAK_DASHBOARD_API") or "http://127.0.0.1:8001"
).rstrip("/")


def notify_dashboard_drive_ui(action: str, payload: dict) -> None:
    """
    Tell the dashboard to navigate to the given tab and optionally set SKU/dataset.
    action: "price" | "review" | "insights" | "overview"
    payload: can include sku_id, dataset_key, and tab-specific data (e.g. price result, kpis).
    """
    url = f"{DASHBOARD_API_BASE}/api/drive-ui"
    try:
        body = {"action": action, "payload": payload or {}}
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[drive_ui] notify failed (non-fatal): {e}")
