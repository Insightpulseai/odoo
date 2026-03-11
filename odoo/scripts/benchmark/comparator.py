#!/usr/bin/env python3
"""Cross-release benchmark comparison.

Usage:
    python scripts/benchmark/comparator.py --current 20260311-1430 --previous 20260310-0900
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reporter import generate_comparison_report

EVIDENCE_ROOT = Path(__file__).resolve().parent.parent.parent / "docs" / "evidence"


def load_scores(timestamp: str) -> dict:
    """Load scores from an evidence directory."""
    scores_path = EVIDENCE_ROOT / timestamp / "copilot-benchmark" / "scores.json"
    if not scores_path.exists():
        # Try summary.json
        summary_path = EVIDENCE_ROOT / timestamp / "copilot-benchmark" / "summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                data = json.load(f)
            return data.get("scores", data)
        raise FileNotFoundError(f"No scores found at {scores_path} or {summary_path}")

    with open(scores_path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Compare benchmark runs")
    parser.add_argument("--current", required=True, help="Current run timestamp (e.g. 20260311-1430)")
    parser.add_argument("--previous", required=True, help="Previous run timestamp")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        current_scores = load_scores(args.current)
        previous_scores = load_scores(args.previous)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = generate_comparison_report(current_scores, previous_scores)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Comparison report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
