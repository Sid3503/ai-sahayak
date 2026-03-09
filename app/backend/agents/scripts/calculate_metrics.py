"""
Calculate performance metrics for AI Sahayak (chat response time, forecast time, error rate).

Prerequisites:
  - Agents API running: uvicorn (e.g. ./start_agent.sh or python -m uvicorn ai_sahayak.main:app --host 0.0.0.0 --port 8000)
  - Dashboard API running (for forecast): python app.py --mode api --port 8001  (from app/Dashboard)

Usage:
  cd app/backend/agents && python scripts/calculate_metrics.py
  python scripts/calculate_metrics.py --agents-base http://localhost:8000 --dashboard-base http://localhost:8001 --chat-samples 5 --forecast-samples 3
  python scripts/calculate_metrics.py --output metrics_results.json
"""
import argparse
import json
import statistics
import sys
import time
import urllib.request
import urllib.error
import uuid

def _post_json(url: str, payload: dict, timeout: int = 60):
    """POST JSON; returns (parsed_body_or_None, elapsed_seconds, status_code)."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            elapsed = time.perf_counter() - start
            raw = r.read().decode("utf-8")
            body = json.loads(raw) if raw else None
            return body, elapsed, getattr(r, "status", 200)
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start
        try:
            body = json.loads(e.read().decode("utf-8")) if e.fp else None
        except Exception:
            body = None
        return body, elapsed, e.code
    except Exception as e:
        elapsed = time.perf_counter() - start
        return None, elapsed, 0  # 0 = connection/timeout error

def _get(url: str, timeout: int = 10):
    """GET; returns (parsed_json_or_None, elapsed_seconds, status_code)."""
    req = urllib.request.Request(url, method="GET")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            elapsed = time.perf_counter() - start
            raw = r.read().decode("utf-8")
            body = json.loads(raw) if raw else None
            return body, elapsed, getattr(r, "status", 200)
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start
        return None, elapsed, e.code
    except Exception:
        elapsed = time.perf_counter() - start
        return None, elapsed, 0

def measure_chat(agents_base: str, session_id: str, samples: int) -> dict:
    url = f"{agents_base.rstrip('/')}/v1/webhook/incoming"
    payload_base = {
        "user_id": "metrics_tester",
        "session_id": session_id,
        "platform": "cli",
    }
    times = []
    errors = 0
    for i in range(samples):
        payload = {**payload_base, "text": f"Hello, test message {i+1}."}
        body, elapsed, status = _post_json(url, payload, timeout=90)
        if 200 <= status < 300 and body and body.get("ok"):
            times.append(elapsed)
        else:
            errors += 1
    return {
        "samples": samples,
        "success_count": len(times),
        "error_count": errors,
        "response_times_s": times,
        "avg_s": round(statistics.mean(times), 3) if times else None,
        "p95_s": round(sorted(times)[int(len(times) * 0.95) - 1], 3) if len(times) >= 2 else (times[0] if times else None),
    }

def measure_forecast(dashboard_base: str, samples: int) -> dict:
    url = f"{dashboard_base.rstrip('/')}/api/forecast"
    payload = {"dataset_key": "raju", "days": 14}
    times = []
    errors = 0
    for _ in range(samples):
        body, elapsed, status = _post_json(url, payload, timeout=60)
        if 200 <= status < 300 and body:
            times.append(elapsed)
        else:
            errors += 1
    return {
        "samples": samples,
        "success_count": len(times),
        "error_count": errors,
        "response_times_s": times,
        "avg_s": round(statistics.mean(times), 3) if times else None,
        "p95_s": round(sorted(times)[int(len(times) * 0.95) - 1], 3) if len(times) >= 2 else (round(times[0], 3) if times else None),
    }

def measure_health(agents_base: str, dashboard_base: str) -> dict:
    out = {}
    url_agents = f"{agents_base.rstrip('/')}/health"
    body, elapsed, status = _get(url_agents, timeout=5)
    out["agents"] = {"ok": 200 <= status < 300, "status": status, "elapsed_s": round(elapsed, 3)}
    url_dash = f"{dashboard_base.rstrip('/')}/api/meta"
    body2, elapsed2, status2 = _get(url_dash, timeout=10)
    out["dashboard"] = {"ok": 200 <= status2 < 300, "status": status2, "elapsed_s": round(elapsed2, 3)}
    return out

def main():
    ap = argparse.ArgumentParser(description="Calculate AI Sahayak performance metrics")
    ap.add_argument("--agents-base", default="http://localhost:8000", help="Agents API base URL")
    ap.add_argument("--dashboard-base", default="http://localhost:8001", help="Dashboard API base URL")
    ap.add_argument("--chat-samples", type=int, default=5, help="Number of chat requests to sample")
    ap.add_argument("--forecast-samples", type=int, default=3, help="Number of forecast requests to sample")
    ap.add_argument("--output", default="", help="Write results JSON to this file")
    ap.add_argument("--skip-forecast", action="store_true", help="Skip forecast (Dashboard not running)")
    args = ap.parse_args()

    session_id = f"metrics_{uuid.uuid4().hex[:8]}"
    results = {
        "chat_response": None,
        "forecast": None,
        "health": None,
        "summary": {},
    }

    # Health
    print("Checking health...")
    results["health"] = measure_health(args.agents_base, args.dashboard_base)
    print(f"  Agents:   {'OK' if results['health']['agents']['ok'] else 'FAIL'} (status={results['health']['agents']['status']})")
    print(f"  Dashboard: {'OK' if results['health']['dashboard']['ok'] else 'FAIL'} (status={results['health']['dashboard']['status']})")

    if not results["health"]["agents"]["ok"]:
        print("Agents API not reachable. Start it with: uvicorn ai_sahayak.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Chat response time
    print(f"\nMeasuring chat response time ({args.chat_samples} samples)...")
    results["chat_response"] = measure_chat(args.agents_base, session_id, args.chat_samples)
    total_chat = results["chat_response"]["samples"]
    err_chat = results["chat_response"]["error_count"]
    if results["chat_response"]["avg_s"] is not None:
        print(f"  Avg: {results['chat_response']['avg_s']}s  P95: {results['chat_response']['p95_s']}s  Errors: {err_chat}/{total_chat}")
        results["summary"]["chat_response_time_avg_s"] = results["chat_response"]["avg_s"]
        results["summary"]["chat_response_time_p95_s"] = results["chat_response"]["p95_s"]
    else:
        print("  No successful responses.")
    results["summary"]["chat_error_rate_pct"] = round(100 * err_chat / total_chat, 2) if total_chat else None

    # Forecast (optional)
    if not args.skip_forecast and results["health"]["dashboard"]["ok"]:
        print(f"\nMeasuring forecast time ({args.forecast_samples} samples)...")
        results["forecast"] = measure_forecast(args.dashboard_base, args.forecast_samples)
        total_f = results["forecast"]["samples"]
        err_f = results["forecast"]["error_count"]
        if results["forecast"]["avg_s"] is not None:
            print(f"  Avg: {results['forecast']['avg_s']}s  P95: {results['forecast']['p95_s']}s  Errors: {err_f}/{total_f}")
            results["summary"]["forecast_time_avg_s"] = results["forecast"]["avg_s"]
            results["summary"]["forecast_time_p95_s"] = results["forecast"]["p95_s"]
        else:
            print("  No successful responses.")
        results["summary"]["forecast_error_rate_pct"] = round(100 * err_f / total_f, 2) if total_f else None
    else:
        if args.skip_forecast:
            print("\nSkipping forecast (--skip-forecast).")
        else:
            print("\nDashboard not reachable; skipping forecast. Start Dashboard with: python app.py --mode api --port 8001")
        results["summary"]["forecast_time_avg_s"] = None
        results["summary"]["forecast_time_p95_s"] = None
        results["summary"]["forecast_error_rate_pct"] = None

    # Overall error rate (from this run)
    total_requests = total_chat + (results["forecast"]["samples"] if results.get("forecast") else 0)
    total_errors = err_chat + (results["forecast"]["error_count"] if results.get("forecast") else 0)
    results["summary"]["overall_error_rate_pct"] = round(100 * total_errors / total_requests, 2) if total_requests else None

    print("\n--- Summary (use these in performance-benchmarking.md) ---")
    print(json.dumps(results["summary"], indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults written to {args.output}")

if __name__ == "__main__":
    main()
