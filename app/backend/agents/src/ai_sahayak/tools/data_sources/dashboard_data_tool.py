"""
Fetch per-retailer shop data for the Live Alerts / chat agent from the Dashboard (Control Centre) API.
Uses ONLY real data from /api/kpis; no mock data. When the API is unreachable, returns empty
so the agent can say "Dashboard abhi connect nahi ho pa raha."
"""
from typing import Any, Optional
import os
import json
import urllib.error
import urllib.parse
import urllib.request


DASHBOARD_API_BASE = (os.getenv("DASHBOARD_API_BASE_URL") or os.getenv("AI_SAHAYAK_DASHBOARD_API") or "http://127.0.0.1:8001").rstrip("/")


def get_dashboard_data(user_id: str) -> dict[str, Any]:
    """
    Returns shop data for the given user_id from the Dashboard backend only.
    Keys: sales_summary, inventory_summary, store_info, overview_kpis, alerts, payment_mix, from_dashboard (bool).
    If API fails, returns empty data and from_dashboard=False so agent can say data is not available.
    """
    if not user_id or user_id == "unknown_user":
        return _empty_data()
    key = (user_id or "").strip().lower()
    if key.startswith("web_"):
        key = "raju"  # Web Live Alerts user: use raju dataset for demo
    return _fetch_from_backend(key)


def _fetch_from_backend(user_id: str) -> dict[str, Any]:
    """
    Fetch live KPIs from Dashboard /api/kpis. No mock fallback — real data only.
    Enriches response with overview_kpis, alerts, payment_mix for agent suggestions.
    """
    try:
        url = f"{DASHBOARD_API_BASE}/api/kpis?dataset_key={urllib.parse.quote(user_id)}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
    except Exception as exc:
        print(f"Dashboard /api/kpis failed for dataset_key={user_id}: {exc}. Returning no data (no mock).")
        return _empty_data(from_dashboard=False)

    kpis = data.get("kpis") or {}
    series = data.get("series") or {}
    top_skus = data.get("top_skus") or []
    alerts = data.get("alerts") or []
    payment_mix = data.get("payment_mix") or []

    revenue_series = series.get("revenue") or []
    today_revenue = float(revenue_series[-1]) if revenue_series else 0.0
    last_7_revenue = float(sum(revenue_series[-7:])) if revenue_series else 0.0
    last_30_revenue = float(kpis.get("revenue_30d", 0.0)) or (float(sum(revenue_series[-30:])) if revenue_series else 0.0)

    top_items = [str(row.get("item_name", "")).strip() for row in top_skus[:6] if row.get("item_name")]
    low_stock_items = [
        str(row.get("item_name", "")).strip()
        for row in top_skus
        if row.get("stock") is not None and float(row.get("stock", 0)) < 5
    ][:5]

    reorder_risk = int(kpis.get("reorder_risk_skus", 0))
    low_cover = int(kpis.get("low_cover_skus", 0))
    sku_count = len(top_skus) if top_skus else 0
    store_name = f"{user_id.capitalize()} Store"

    overview_kpis = {
        "revenue_30d": float(kpis.get("revenue_30d", 0.0)),
        "profit_30d": float(kpis.get("profit_30d", 0.0)),
        "net_profit_30d": float(kpis.get("net_profit_30d", 0.0)),
        "units_30d": float(kpis.get("units_30d", 0.0)),
        "sell_through_pct": float(kpis.get("sell_through_pct", 0.0)),
        "avg_margin_pct": float(kpis.get("avg_margin_pct", 0.0)),
        "price_vs_market_pct": float(kpis.get("avg_price_gap_pct", 0.0)),
        "reorder_risk_skus": reorder_risk,
        "low_cover_skus": low_cover,
        "festival_days_last30": int(kpis.get("festival_days_last30", 0)),
        "revenue_growth_pct": float(kpis.get("revenue_growth_pct", 0.0)),
        "profit_growth_pct": float(kpis.get("profit_growth_pct", 0.0)),
    }

    return {
        "from_dashboard": True,
        "store_info": {
            "name": store_name,
            "city": "",
            "state": "",
        },
        "sales_summary": {
            "today": today_revenue,
            "last_week": last_7_revenue,
            "last_month": last_30_revenue,
            "top_items": top_items,
        },
        "inventory_summary": {
            "low_stock": low_stock_items,
            "total_skus": sku_count,
            "reorder_risk_skus": reorder_risk,
            "low_cover_skus": low_cover,
        },
        "overview_kpis": overview_kpis,
        "alerts": alerts,
        "payment_mix": payment_mix,
        "raw_kpis": kpis,
        "raw_series": series,
        "top_skus": top_skus,
    }


def _empty_data(from_dashboard: bool = False) -> dict[str, Any]:
    return {
        "from_dashboard": from_dashboard,
        "store_info": {},
        "sales_summary": {},
        "inventory_summary": {},
        "overview_kpis": {},
        "alerts": [],
        "payment_mix": [],
        "top_skus": [],
    }
