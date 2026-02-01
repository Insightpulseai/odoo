#!/usr/bin/env python3
"""
Aggregate individual audit results into a single report.
"""
import json
import os
import sys
from datetime import datetime, timezone
from glob import glob


def main():
    if len(sys.argv) < 2:
        print("Usage: aggregate_results.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    raw_dir = os.path.join(output_dir, "raw")

    # Collect all result files
    result_files = glob(os.path.join(raw_dir, "*_audit.json"))

    results = []
    missing_inputs = {}
    pass_count = 0
    fail_count = 0
    skip_count = 0

    for filepath in sorted(result_files):
        try:
            with open(filepath) as f:
                data = json.load(f)

            # Collect missing inputs
            if data.get("missing_required"):
                integration_name = data.get("name", os.path.basename(filepath).replace("_audit.json", ""))
                missing_inputs[integration_name] = data["missing_required"]

            # Count status
            status = data.get("status", "UNKNOWN")
            if status == "PASS":
                pass_count += 1
            elif status in ["FAIL", "PARTIAL"]:
                fail_count += 1
            else:
                skip_count += 1

            results.append(data)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            results.append({
                "name": os.path.basename(filepath).replace("_audit.json", ""),
                "status": "SKIP",
                "error": str(e)
            })
            skip_count += 1

    # Create aggregate report
    aggregate = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_integrations": len(results),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "results": results,
        "missing_inputs": missing_inputs
    }

    # Save aggregate
    output_file = os.path.join(output_dir, "integration_results.json")
    with open(output_file, "w") as f:
        json.dump(aggregate, f, indent=2, default=str)

    print(f"Aggregated {len(results)} results to {output_file}")
    print(f"  Pass: {pass_count}, Fail: {fail_count}, Skip: {skip_count}")

    if missing_inputs:
        print("\nMissing inputs by integration:")
        for name, vars in missing_inputs.items():
            print(f"  {name}: {', '.join(vars)}")


if __name__ == "__main__":
    main()
