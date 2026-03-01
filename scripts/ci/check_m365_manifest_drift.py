#!/usr/bin/env python3
"""
check_m365_manifest_drift.py — M365 Manifest Drift CI Validator

Verifies that dist/m365/agents/insightpulseai_ops_advisor/manifest.json is
in sync with its SSOT YAML sources in ssot/m365/agents/insightpulseai_ops_advisor/.

Also checks that all action IDs in the manifest appear in the allowed_action_ids
allowlist declared in actions.yaml. Unknown action IDs are a policy violation.

Exit 0 = PASS (manifest is current, all action IDs allowlisted).
Exit 1 = FAIL (drift detected or unknown action IDs found).

Usage:
    python scripts/ci/check_m365_manifest_drift.py
    python scripts/ci/check_m365_manifest_drift.py --repo-root /path/to/odoo
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL [setup] pyyaml not installed — run: pip install pyyaml", flush=True)
    sys.exit(1)

ACTIONS_YAML_REL = Path("ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml")
MANIFEST_OUT_REL = Path("dist/m365/agents/insightpulseai_ops_advisor/manifest.json")
GENERATOR_REL = Path("scripts/m365/generate_actions_manifest.py")


def result(tag: str, label: str, ok: bool, detail: str = "") -> bool:
    prefix = "PASS" if ok else "FAIL"
    msg = f"{prefix} [{tag}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg, flush=True)
    return ok


def check_generator_sync(repo_root: Path) -> bool:
    """Check 1: Run generator --validate-only and capture its result."""
    generator = repo_root / GENERATOR_REL
    if not generator.exists():
        return result(
            "drift",
            "generator script exists",
            False,
            f"{GENERATOR_REL} not found",
        )

    proc = subprocess.run(
        [sys.executable, str(generator), "--validate-only", "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
    )

    # Echo generator output so CI logs show the detail
    if proc.stdout:
        for line in proc.stdout.strip().splitlines():
            print(f"  generator> {line}", flush=True)
    if proc.stderr:
        for line in proc.stderr.strip().splitlines():
            print(f"  generator> {line}", flush=True)

    ok = proc.returncode == 0
    return result(
        "drift",
        "manifest.json matches SSOT YAML",
        ok,
        "up to date" if ok else "regenerate with: python scripts/m365/generate_actions_manifest.py",
    )


def check_allowlist(repo_root: Path) -> bool:
    """Check 2: All action IDs in manifest.json are in allowed_action_ids."""
    actions_path = repo_root / ACTIONS_YAML_REL
    manifest_path = repo_root / MANIFEST_OUT_REL

    if not actions_path.exists():
        return result("allowlist", "actions.yaml exists", False, str(ACTIONS_YAML_REL))

    if not manifest_path.exists():
        return result(
            "allowlist",
            "manifest.json exists for allowlist check",
            False,
            str(MANIFEST_OUT_REL),
        )

    with actions_path.open("r", encoding="utf-8") as f:
        actions_data = yaml.safe_load(f)
    allowed: set[str] = set(actions_data.get("allowed_action_ids", []))

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_action_ids: list[str] = [a["id"] for a in manifest.get("actions", [])]

    unknown = [aid for aid in manifest_action_ids if aid not in allowed]
    ok = len(unknown) == 0

    if unknown:
        detail = f"not in allowed_action_ids: {', '.join(unknown)}"
    else:
        detail = f"{len(manifest_action_ids)} action ID(s) all allowlisted"

    return result("allowlist", "all manifest action IDs are allowlisted", ok, detail)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check M365 manifest drift and action ID allowlist"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: .)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    print(f"M365 Manifest Drift Check — repo root: {repo_root}", flush=True)
    print(f"Manifest: {MANIFEST_OUT_REL}", flush=True)
    print("-" * 64, flush=True)

    checks = [check_generator_sync, check_allowlist]
    failures = 0
    for check_fn in checks:
        ok = check_fn(repo_root)
        if not ok:
            failures += 1

    print("-" * 64, flush=True)
    if failures == 0:
        print(f"PASS — all {len(checks)} checks passed", flush=True)
        sys.exit(0)
    else:
        print(f"FAIL — {failures}/{len(checks)} check(s) failed", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
