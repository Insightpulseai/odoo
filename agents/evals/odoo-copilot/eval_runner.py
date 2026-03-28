"""
Odoo Copilot Eval Runner
Validates that the copilot routes prompts to correct tools
and returns expected content.

Usage:
    python eval_runner.py --endpoint https://ipai-odoo-connector.<domain>/mcp
    python eval_runner.py --local  # uses localhost:3100
"""

import json
import sys
import argparse
from pathlib import Path

EVAL_FILE = Path(__file__).parent / "eval_dataset.jsonl"


def load_evals():
    evals = []
    with open(EVAL_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                evals.append(json.loads(line))
    return evals


def run_eval(endpoint: str):
    """Placeholder — in production, this would:
    1. Send each input to the copilot/agent endpoint
    2. Check which tool was called
    3. Check if response contains expected strings
    4. Score pass/fail per eval case
    """
    evals = load_evals()

    print(f"Loaded {len(evals)} eval cases from {EVAL_FILE}")
    print(f"Endpoint: {endpoint}")
    print()

    categories = {}
    types = {}
    for e in evals:
        cat = e["category"]
        typ = e["type"]
        categories[cat] = categories.get(cat, 0) + 1
        types[typ] = types.get(typ, 0) + 1

    print("Coverage by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print(f"\nCoverage by type:")
    for typ, count in sorted(types.items()):
        print(f"  {typ}: {count}")

    print(f"\nTotal: {len(evals)} cases")
    print(f"Informational: {types.get('informational', 0)}")
    print(f"Transactional: {types.get('transactional', 0)}")

    # Tool coverage
    tools = set(e["expected_tool"] for e in evals)
    print(f"\nTools covered: {len(tools)}")
    for t in sorted(tools):
        print(f"  {t}")

    print("\n[PLACEHOLDER] Full eval execution requires MCP client integration.")
    print("Run with --execute to send real requests (not implemented yet).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:3100/mcp")
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    endpoint = "http://localhost:3100/mcp" if args.local else args.endpoint
    run_eval(endpoint)
