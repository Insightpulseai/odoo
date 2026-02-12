#!/usr/bin/env python3
import sys
import yaml
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
MATRIX = ROOT / "parity" / "parity-matrix.yaml"


def main():
    if not MATRIX.exists():
        print(f"Error: Matrix file not found at {MATRIX}")
        return 1

    with open(MATRIX, "r") as f:
        data = yaml.safe_load(f)

    thr = data.get("policy", {}).get("thresholds", {})
    fail_below = float(thr.get("fail_below", 0.0))

    bad = []
    print("Parity Matrix Status Check")
    print("=" * 30)
    for p in data.get("platforms", []):
        cov = float(p.get("coverage", 0))
        status = p.get("status", "unknown").upper()
        print(f"{p.get('name'):<20} | {cov:>4.0%} | {status}")
        if cov < fail_below:
            bad.append((p.get("name", p.get("id")), cov))

    print("=" * 30)
    if bad:
        print("Parity validation FAILED:")
        for name, cov in bad:
            print(f" - {name}: {cov:.2f} < fail_below={fail_below:.2f}")
        return 1

    print("Parity validation OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
