#!/usr/bin/env python3
"""
Parity Auditor for ERP SaaS Clone Suite.

Reads capability scores from equivalence_matrix.csv, compares against
baseline.json for P0 capabilities, and fails if any score regresses.

Exit codes:
- 0: Parity audit passed (no regressions)
- 2: Missing required files
- 3: P0 parity regressions detected
"""

import csv
import json
import os
import sys
from datetime import datetime
from typing import Any

MATRIX_PATH = "catalog/equivalence_matrix.csv"
RUBRIC_PATH = "kb/parity/rubric.json"
BASELINE_PATH = "kb/parity/baseline.json"
OUTPUT_PATH = "parity_report.json"


def load_json(path: str, default: Any) -> Any:
    """Load JSON file or return default if not found."""
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_matrix() -> list:
    """Load capability matrix from CSV."""
    rows = []
    with open(MATRIX_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("capability_id"):
                rows.append(row)
    return rows


def main() -> int:
    # Check required files
    if not os.path.exists(MATRIX_PATH):
        print(f"Missing {MATRIX_PATH}")
        return 2

    # Load configuration
    rubric = load_json(RUBRIC_PATH, {
        "weights": {
            "workflow": 30,
            "ux": 25,
            "data": 15,
            "perm": 15,
            "report": 10,
            "perf": 5
        },
        "thresholds": {
            "p0_minimum": 70,
            "p1_minimum": 50,
            "p2_minimum": 0
        }
    })

    baseline = load_json(BASELINE_PATH, {"p0": {}})

    # Load and process matrix
    rows = load_matrix()

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "rubric": rubric,
        "scores": {
            "p0": {},
            "p1": {},
            "p2": {}
        },
        "regressions": [],
        "below_threshold": [],
        "summary": {}
    }

    # Process each capability
    for row in rows:
        cap_id = row["capability_id"]
        tier = (row.get("tier") or "p1").lower()
        score = int(row.get("manual_score") or 0)

        # Store score by tier
        if tier not in report["scores"]:
            report["scores"][tier] = {}
        report["scores"][tier][cap_id] = score

        # Check for P0 regressions
        if tier == "p0":
            prev_score = int(baseline.get("p0", {}).get(cap_id, 0))
            if score < prev_score:
                report["regressions"].append({
                    "capability_id": cap_id,
                    "previous": prev_score,
                    "current": score,
                    "delta": score - prev_score
                })

            # Check against threshold
            threshold = rubric.get("thresholds", {}).get("p0_minimum", 70)
            if score < threshold:
                report["below_threshold"].append({
                    "capability_id": cap_id,
                    "score": score,
                    "threshold": threshold,
                    "tier": tier
                })

    # Calculate summary
    for tier in ["p0", "p1", "p2"]:
        tier_scores = report["scores"].get(tier, {})
        if tier_scores:
            scores_list = list(tier_scores.values())
            report["summary"][tier] = {
                "count": len(scores_list),
                "average": round(sum(scores_list) / len(scores_list), 1),
                "min": min(scores_list),
                "max": max(scores_list)
            }

    # Write report
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Parity report written to {OUTPUT_PATH}")

    # Output results
    if report["regressions"]:
        print("\n[FAIL] Parity regressions detected:")
        for reg in report["regressions"]:
            print(f"  - {reg['capability_id']}: {reg['previous']} -> {reg['current']} ({reg['delta']:+d})")
        return 3

    if report["below_threshold"]:
        print("\n[WARN] Capabilities below threshold (not blocking):")
        for item in report["below_threshold"]:
            print(f"  - {item['capability_id']}: {item['score']}/{item['threshold']} ({item['tier']})")

    # Print summary
    print("\nParity Summary:")
    for tier, stats in report["summary"].items():
        print(f"  {tier.upper()}: {stats['count']} capabilities, avg={stats['average']}, range=[{stats['min']}-{stats['max']}]")

    print("\n[OK] Parity audit passed (no regressions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
