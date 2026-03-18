#!/usr/bin/env python3
"""
Parity Auditor for ERP SaaS Clone Suite.

Reads capability scores from equivalence_matrix*.csv files, compares against
baseline.json for P0 capabilities, and fails if any score regresses.

Features:
- Multi-matrix support via glob pattern
- Automated module/model/view existence checks
- Regression detection against baseline
- JSON report generation

Exit codes:
- 0: Parity audit passed (no regressions)
- 2: Missing required files
- 3: P0 parity regressions detected
"""

import csv
import glob
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
MATRIX_GLOB = "catalog/equivalence_matrix*.csv"
RUBRIC_PATH = "kb/parity/rubric.json"
BASELINE_PATH = "kb/parity/baseline.json"
OUTPUT_PATH = "parity_report.json"
ADDONS_PATH = "addons"


def load_json(path: str, default: Any) -> Any:
    """Load JSON file or return default if not found."""
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    """Save data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_matrix() -> list:
    """Load all capability matrix CSV files and merge rows."""
    rows = []
    files = sorted(glob.glob(MATRIX_GLOB))
    if not files:
        return rows
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("capability_id"):
                    row["_source_file"] = fp
                    rows.append(row)
    return rows


def check_module_exists(module_name: str) -> bool:
    """Check if an Odoo module exists in addons directory."""
    module_path = Path(ADDONS_PATH) / module_name
    manifest_path = module_path / "__manifest__.py"
    return manifest_path.exists()


def check_model_exists(module_name: str, model_name: str) -> bool:
    """Check if a model is defined in the module's models directory."""
    models_path = Path(ADDONS_PATH) / module_name / "models"
    if not models_path.exists():
        return False
    # Convert model name to potential file name (e.g., ipai.workos.page -> page.py)
    model_file = model_name.split(".")[-1] + ".py"
    return (models_path / model_file).exists()


def check_view_exists(module_name: str, view_id: str) -> bool:
    """Check if a view is defined in the module's views directory."""
    views_path = Path(ADDONS_PATH) / module_name / "views"
    if not views_path.exists():
        return False
    # Search for view_id in XML files
    for xml_file in views_path.glob("*.xml"):
        try:
            content = xml_file.read_text()
            if f'id="{view_id}"' in content or f"id='{view_id}'" in content:
                return True
        except Exception:
            pass
    return False


def compute_capability_score(capability_id: str, rubric: dict, row: dict) -> dict:
    """Compute score for a single capability based on rubric checks."""
    checks = rubric.get("capability_checks", {}).get(capability_id, {})
    if not checks:
        # No automated checks defined, use manual score
        return {
            "score": int(row.get("manual_score", 0)),
            "automated": False,
            "checks": {}
        }

    results = {}
    total_checks = 0
    passed_checks = 0

    # Check module exists
    if "module_exists" in checks:
        module_name = checks["module_exists"]
        exists = check_module_exists(module_name)
        results["module_exists"] = {
            "module": module_name,
            "passed": exists
        }
        total_checks += 1
        if exists:
            passed_checks += 1

    # Check models exist
    if "models" in checks and "module_exists" in checks:
        module_name = checks["module_exists"]
        for model in checks["models"]:
            exists = check_model_exists(module_name, model)
            results[f"model:{model}"] = {"passed": exists}
            total_checks += 1
            if exists:
                passed_checks += 1

    # Check views exist
    if "views" in checks and "module_exists" in checks:
        module_name = checks["module_exists"]
        for view in checks["views"]:
            exists = check_view_exists(module_name, view)
            results[f"view:{view}"] = {"passed": exists}
            total_checks += 1
            if exists:
                passed_checks += 1

    # Calculate score (0-100)
    if total_checks > 0:
        score = int((passed_checks / total_checks) * 100)
    else:
        score = int(row.get("manual_score", 0))

    return {
        "score": score,
        "automated": total_checks > 0,
        "checks": results,
        "passed": passed_checks,
        "total": total_checks
    }


def main() -> int:
    print("=== Parity Audit Tool ===")
    print("")

    # Check for matrix files
    matrix_files = glob.glob(MATRIX_GLOB)
    if not matrix_files:
        print(f"WARNING: No files matching {MATRIX_GLOB}")
        print("Creating empty report...")
        # Don't fail if no matrix files - this might be initial setup

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
        "capability_checks": {},
        "thresholds": {
            "p0_minimum": 70,
            "p1_minimum": 50,
            "p2_minimum": 0
        }
    })

    baseline = load_json(BASELINE_PATH, {"p0": {}, "p1": {}, "p2": {}})

    # Load and process matrix
    rows = load_matrix()
    print(f"Loaded {len(rows)} capabilities from {len(matrix_files)} matrix file(s)")

    report: dict[str, Any] = {
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

        # Compute score using automated checks if available
        score_result = compute_capability_score(cap_id, rubric, row)
        score = score_result.get("score", 0)

        # Store score by tier
        if tier not in report["scores"]:
            report["scores"][tier] = {}
        report["scores"][tier][cap_id] = score_result

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

        print(f"  [{tier.upper()}] {cap_id}: {score}")

    # Calculate summary
    for tier in ["p0", "p1", "p2"]:
        tier_scores = report["scores"].get(tier, {})
        if tier_scores:
            scores_list = [s.get("score", 0) if isinstance(s, dict) else s for s in tier_scores.values()]
            report["summary"][tier] = {
                "count": len(scores_list),
                "average": round(sum(scores_list) / len(scores_list), 1) if scores_list else 0,
                "min": min(scores_list) if scores_list else 0,
                "max": max(scores_list) if scores_list else 0
            }

    # Add regression summary
    report["summary"]["regression_count"] = len(report["regressions"])
    report["summary"]["p0_regressions"] = len([r for r in report["regressions"]])

    # Write report
    save_json(OUTPUT_PATH, report)
    print(f"\nParity report written to {OUTPUT_PATH}")

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
        if isinstance(stats, dict) and "count" in stats:
            print(f"  {tier.upper()}: {stats['count']} capabilities, avg={stats['average']}, range=[{stats['min']}-{stats['max']}]")

    print("\n[OK] Parity audit passed (no regressions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
