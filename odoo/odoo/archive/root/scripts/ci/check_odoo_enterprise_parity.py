#!/usr/bin/env python3
"""
check_odoo_enterprise_parity.py
CI gate: fails if any required=true feature has status=missing and no evidence pointer.
Also warns on partial features without evidence.
"""
import sys
import pathlib
import yaml

SSOT_PATH = pathlib.Path("ssot/parity/odoo_enterprise.yaml")
EXIT_CODE = 0


def main():
    global EXIT_CODE
    if not SSOT_PATH.exists():
        print(f"ERROR: {SSOT_PATH} not found -- parity SSOT is required")
        sys.exit(1)

    data = yaml.safe_load(SSOT_PATH.read_text())
    features = data.get("features", [])

    print(f"Odoo Enterprise Parity Check -- {len(features)} features")
    print("=" * 60)

    errors = []
    warnings = []

    for f in features:
        fid = f.get("id", "UNKNOWN")
        required = f.get("required", False)
        status = f.get("status", "missing")
        evidence = f.get("evidence")

        if required and status == "missing":
            errors.append(f"FAIL [required+missing]: {fid} -- no implementation defined")
            EXIT_CODE = 1

        if required and status in ("met", "partial") and not evidence:
            warnings.append(f"WARN [no evidence]: {fid} (status={status}) -- add evidence pointer")

        if required and status == "partial":
            warnings.append(f"WARN [partial]: {fid} -- implementation incomplete, track in backlog")

        status_icon = {"met": "OK  ", "partial": "WARN", "missing": "FAIL", "waived": "SKIP"}.get(status, "?   ")
        req_flag = "[required]" if required else "[optional]"
        print(f"  {status_icon} {fid} {req_flag} -- {status}")

    print()
    for w in warnings:
        print(f"  {w}")
    for e in errors:
        print(f"  {e}")

    fail_count = len(errors)
    warn_count = len(warnings)
    if EXIT_CODE != 0:
        print(f"\nParity gate FAILED: {fail_count} required feature(s) are missing.")
        print("Fix: update ssot/parity/odoo_enterprise.yaml -- set status or mark as waived.")
    else:
        print(f"\nParity gate PASSED: {fail_count} failures, {warn_count} warnings.")

    sys.exit(EXIT_CODE)


if __name__ == "__main__":
    main()
