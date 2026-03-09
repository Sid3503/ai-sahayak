"""
Compute intent classification accuracy using the same classifier as the chat pipeline.

Uses a local test set (scripts/test_data/intent_test_set.json). Run from agents dir
with PYTHONPATH so ai_sahayak is importable. Requires Bedrock/LLM for non-fast-path queries.

  cd app/backend/agents && PYTHONPATH=src python scripts/calculate_intent_accuracy.py
  python scripts/calculate_intent_accuracy.py --test-data scripts/test_data/intent_test_set.json
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

# Add agents src so we can import ai_sahayak
def _ensure_path():
    script_dir = Path(__file__).resolve().parent
    agents_root = script_dir.parent
    src = agents_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
_ensure_path()

from ai_sahayak.graphs.nodes.router.intent_router import classify_intent_node


def build_state(query: str):
    return {
        "messages": [HumanMessage(content=query)],
        "user_context": {},
        "next_node": "",
        "confidence": 0.0,
        "is_complete": False,
        "current_step": "",
        "onboarding_data": {},
        "next_intent": "",
    }


async def run_one(query: str, expected: str) -> tuple[str, str, bool]:
    state = build_state(query)
    out = await classify_intent_node(state)
    actual = out.get("next_intent") or "general_chat"
    return actual, expected, actual == expected


async def main_async(test_data_path: str, verbose: bool):
    with open(test_data_path, "r") as f:
        cases = json.load(f)
    correct = 0
    results = []
    for i, row in enumerate(cases):
        query = row.get("query", "").strip()
        expected = row.get("expected_intent", "general_chat").strip()
        if not query:
            continue
        actual, exp, ok = await run_one(query, expected)
        if ok:
            correct += 1
        results.append({"query": query[:50], "expected": exp, "actual": actual, "ok": ok})
        if verbose:
            print(f"  {'✓' if ok else '✗'} {query[:45]:45} -> {actual} (expected {exp})")
    total = len(results)
    pct = round(100 * correct / total, 1) if total else 0
    print(f"\nIntent accuracy: {correct}/{total} = {pct}%")
    return {"total": total, "correct": correct, "accuracy_pct": pct, "results": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-data", default=None, help="Path to intent_test_set.json")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    path = args.test_data
    if not path:
        path = str(Path(__file__).parent / "test_data" / "intent_test_set.json")
    if not os.path.isfile(path):
        print(f"Test data not found: {path}")
        sys.exit(1)
    metrics = asyncio.run(main_async(path, args.verbose))
    # Write summary for use in performance report
    out_path = Path(__file__).parent.parent / "intent_accuracy_result.json"
    with open(out_path, "w") as f:
        json.dump({"intent_accuracy_pct": metrics["accuracy_pct"], "total": metrics["total"], "correct": metrics["correct"]}, f, indent=2)
    print(f"Summary written to {out_path}")


if __name__ == "__main__":
    main()
