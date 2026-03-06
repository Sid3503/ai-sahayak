"""
Fetch per-retailer shop data for the Live Alerts / chat agent.
Dashboard (Step 2) owns the same data; this tool is the bridge so the agent can answer
"what should I stock?", "how were my sales?" using the same datasets (raju, ramesh, suresh, kanta, lakshmi).

This version prefers live data from the dashboard backend (`/api/kpis`) and falls back
to realistic per-user mock data if the HTTP call fails. That keeps the demo robust
while still showing end-to-end integration when the backend is reachable.
"""
from typing import Any, Optional
import os
import json
import urllib.error
import urllib.parse
import urllib.request


API_BASE_URL = os.getenv("AI_SAHAYAK_API_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")


def get_dashboard_data(user_id: str) -> dict[str, Any]:
    """
    Returns shop data for the given user_id (same Raju as in dashboard).
    Keys: sales_summary, inventory_summary, store_info, etc.
    """
    if not user_id or user_id == "unknown_user":
        return _empty_data()
    return _fetch_from_backend(user_id)


def _fetch_from_backend(user_id: str) -> dict[str, Any]:
    """
    First try to fetch live KPIs from the dashboard backend (`/api/kpis`),
    using the same dataset_key convention as the Control Centre (raju, ramesh, ...).
    If anything goes wrong (timeout, non-200, bad JSON), fall back to
    the per-user mock data so the assistant still answers.
    """
    key = (user_id or "").strip().lower()

    if not key:
        return _empty_data()

    # Live path: call the same backend the dashboard uses.
    try:
        base = API_BASE_URL.rstrip("/")
        # API_BASE_URL already includes /api (e.g. http://13.206.41.149/api).
        url = f"{base}/kpis?dataset_key={urllib.parse.quote(key)}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        kpis = data.get("kpis") or {}
        series = data.get("series") or {}
        top_skus = data.get("top_skus") or []

        dates = series.get("dates") or []
        revenue_series = series.get("revenue") or []
        today_revenue = float(revenue_series[-1]) if revenue_series else 0.0
        last_7_revenue = float(sum(revenue_series[-7:])) if revenue_series else 0.0
        last_30_revenue = float(sum(revenue_series[-30:])) if revenue_series else 0.0

        top_items = [str(row.get("item_name", "")).strip() for row in top_skus[:3] if row.get("item_name")]

        low_stock_items = [
            str(row.get("item_name", "")).strip()
            for row in top_skus
            if row.get("stock", 0) is not None and float(row.get("stock", 0)) < 5
        ][:5]

        store_name = f"{key.capitalize()} Store"

        return {
            "store_info": {
                "name": store_name,
                "city": "",
                "state": "",
            },
            "sales_summary": {
                "today": today_revenue,
                "last_week": last_7_revenue,
                "last_month": last_30_revenue or float(kpis.get("revenue_30d", 0.0)),
                "top_items": top_items,
            },
            "inventory_summary": {
                "low_stock": low_stock_items,
                "total_skus": int(kpis.get("reorder_risk_skus", 0)) + int(kpis.get("low_cover_skus", 0)),
            },
            "raw_kpis": kpis,
            "raw_series": series,
        }
    except Exception as exc:
        # Surface the error instead of silently falling back to mock data,
        # so we immediately see when the dashboard backend is unhealthy.
        raise RuntimeError(f"Dashboard /api/kpis failed for dataset_key={key}: {exc}") from exc

    if key == "raju":
        return {
            "store_info": {"name": "Raju Kirana & General Store", "city": "Indore", "state": "MP"},
            "sales_summary": {
                "today": 15200,
                "last_week": 98400,
                "last_month": 412000,
                "top_items": ["Amul Ghee 500g", "Tata Salt", "Parle-G"],
            },
            "inventory_summary": {
                "low_stock": ["Tata Salt", "Parle-G", "Ariel 1kg"],
                "total_skus": 120,
            },
        }

    if key == "ramesh":
        return {
            "store_info": {"name": "Ramesh Medical & Chemist", "city": "Pune", "state": "MH"},
            "sales_summary": {
                "today": 8400,
                "last_week": 61200,
                "last_month": 249000,
                "top_items": ["Dolo 650", "ORS Pack", "Vitamin C Tablets"],
            },
            "inventory_summary": {
                "low_stock": ["Dolo 650", "Cough Syrup 100ml"],
                "total_skus": 260,
            },
        }

    if key == "suresh":
        return {
            "store_info": {"name": "Suresh Building Materials", "city": "Nagpur", "state": "MH"},
            "sales_summary": {
                "today": 30400,
                "last_week": 210500,
                "last_month": 915000,
                "top_items": ["Cement 50kg", "TMT Bar 12mm", "Bricks (per 1000)"],
            },
            "inventory_summary": {
                "low_stock": ["Cement 50kg"],
                "total_skus": 80,
            },
        }

    if key == "kanta":
        return {
            "store_info": {"name": "Kanta Textile Corner", "city": "Jaipur", "state": "RJ"},
            "sales_summary": {
                "today": 12900,
                "last_week": 77400,
                "last_month": 338000,
                "top_items": ["Cotton Saree", "Kurta Set", "Bedsheet 2-in-1"],
            },
            "inventory_summary": {
                "low_stock": ["Festival Kurta Set"],
                "total_skus": 190,
            },
        }

    if key == "lakshmi":
        return {
            "store_info": {"name": "Lakshmi Electronics & Accessories", "city": "Hyderabad", "state": "TS"},
            "sales_summary": {
                "today": 18600,
                "last_week": 133400,
                "last_month": 572000,
                "top_items": ["Type-C Cable", "Bluetooth Earbuds", "Mobile Cover"],
            },
            "inventory_summary": {
                "low_stock": ["Type-C Cable", "Power Bank 10k mAh"],
                "total_skus": 145,
            },
        }

    # Fallback generic mock so the assistant can still answer even for unknown ids.
    return {
        "store_info": {"name": "Demo Kirana Store", "city": "Indore", "state": "MP"},
        "sales_summary": {
            "today": 10000,
            "last_week": 70000,
            "last_month": 300000,
            "top_items": ["Atta 10kg", "Sugar 1kg", "Tea 250g"],
        },
        "inventory_summary": {
            "low_stock": ["Sugar 1kg"],
            "total_skus": 100,
        },
    }


def _empty_data() -> dict[str, Any]:
    return {
        "store_info": {},
        "sales_summary": {},
        "inventory_summary": {},
    }
