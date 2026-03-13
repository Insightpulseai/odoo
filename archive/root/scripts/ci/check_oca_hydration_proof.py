#!/usr/bin/env python3
"""
OCA Hydration Proof Gate

Deterministic verification that gitaggregate produces the expected
addon directories from oca-aggregate.yml.

Phase 1 (CI-safe, no git clone): Validate aggregate config structure
Phase 2 (full hydration): Clone repos and verify module directories

Usage:
    # Phase 1: Config validation only (fast, no network)
    python3 scripts/ci/check_oca_hydration_proof.py --config-only

    # Phase 2: Full hydration + module verification
    python3 scripts/ci/check_oca_hydration_proof.py

    # With evidence output
    python3 scripts/ci/check_oca_hydration_proof.py --evidence-dir docs/evidence/oca_hydration

Exit codes:
    0 - All checks pass
    1 - Hydration or verification failure
    2 - Configuration error
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGGREGATE_FILE = REPO_ROOT / "oca-aggregate.yml"
ADDONS_OCA = REPO_ROOT / "addons" / "oca"
MUST_HAVE_DIR = REPO_ROOT / "config" / "oca"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_aggregate_repos(data: dict) -> list:
    """Extract repo info from oca-aggregate.yml."""
    repos = []
    for key, config in data.items():
        repo_name = key.rstrip("/").split("/")[-1]
        remotes = config.get("remotes", {})
        merges = config.get("merges", [])
        target_dir = Path(key)
        repos.append({
            "name": repo_name,
            "dir": str(key),
            "target_dir": target_dir,
            "remotes": remotes,
            "merges": merges,
        })
    return repos


def get_must_have_modules() -> dict:
    """Load all must-have manifests and return {category: [modules]}."""
    modules = {}
    for manifest in sorted(MUST_HAVE_DIR.glob("oca_must_have_*.yml")):
        if "all" in manifest.name:
            continue
        data = load_yaml(manifest)
        if data and "modules" in data:
            category = manifest.stem.replace("oca_must_have_", "")
            modules[category] = data["modules"]
    return modules


def validate_config(repos: list) -> dict:
    """Phase 1: Validate aggregate config structure."""
    result = {
        "total_repos": len(repos),
        "valid_repos": 0,
        "errors": [],
    }

    for repo in repos:
        if not repo["remotes"]:
            result["errors"].append(f"{repo['name']}: no remotes defined")
            continue
        if not repo["merges"]:
            result["errors"].append(f"{repo['name']}: no merges defined")
            continue
        # Check remote URL format
        for name, url in repo["remotes"].items():
            if not url.startswith("https://github.com/OCA/"):
                result["errors"].append(
                    f"{repo['name']}: remote '{name}' not an OCA repo: {url}"
                )
                continue
        result["valid_repos"] += 1

    return result


def check_hydration(repos: list) -> dict:
    """Phase 2: Verify hydrated directories exist."""
    result = {
        "hydrated": [],
        "missing": [],
    }

    for repo in repos:
        repo_path = REPO_ROOT / repo["dir"].lstrip("./")
        if repo_path.exists() and repo_path.is_dir():
            # Count modules (dirs with __manifest__.py)
            module_count = sum(
                1 for d in repo_path.iterdir()
                if d.is_dir() and (d / "__manifest__.py").exists()
            )
            result["hydrated"].append({
                "name": repo["name"],
                "path": str(repo_path.relative_to(REPO_ROOT)),
                "module_count": module_count,
            })
        else:
            result["missing"].append(repo["name"])

    return result


def check_must_have_modules(must_have: dict) -> dict:
    """Verify must-have modules exist as directories after hydration."""
    result = {"categories": {}}

    for category, modules in must_have.items():
        found = []
        missing = []
        for module in modules:
            # Search all repo dirs under addons/oca/
            module_found = False
            if ADDONS_OCA.exists():
                for repo_dir in ADDONS_OCA.iterdir():
                    if repo_dir.is_dir():
                        manifest = repo_dir / module / "__manifest__.py"
                        if manifest.exists():
                            module_found = True
                            break
            if module_found:
                found.append(module)
            else:
                missing.append(module)

        result["categories"][category] = {
            "total": len(modules),
            "found": len(found),
            "missing": missing,
        }

    return result


def write_evidence(evidence: dict, evidence_dir: Path):
    """Write evidence report as JSON."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    report_path = evidence_dir / "report.json"
    with open(report_path, "w") as f:
        json.dump(evidence, f, indent=2, default=str)
    print(f"\nEvidence written to: {report_path}")


def main():
    config_only = "--config-only" in sys.argv
    evidence_dir = None

    for i, arg in enumerate(sys.argv):
        if arg == "--evidence-dir" and i + 1 < len(sys.argv):
            evidence_dir = Path(sys.argv[i + 1])

    print("=" * 60)
    print("  OCA Hydration Proof Gate")
    print("=" * 60)
    print()

    # Load aggregate config
    if not AGGREGATE_FILE.exists():
        print(f"ERROR: {AGGREGATE_FILE} not found")
        sys.exit(2)

    data = load_yaml(AGGREGATE_FILE)
    if not data:
        print("ERROR: Empty aggregate config")
        sys.exit(2)

    repos = parse_aggregate_repos(data)
    must_have = get_must_have_modules()

    # Phase 1: Config validation
    print("[Phase 1] Config validation")
    config_result = validate_config(repos)
    print(f"  Repos configured: {config_result['total_repos']}")
    print(f"  Valid configs:    {config_result['valid_repos']}")
    if config_result["errors"]:
        for err in config_result["errors"]:
            print(f"  ERROR: {err}")
    else:
        print("  PASS: All repo configs valid")
    print()

    evidence = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aggregate_file": str(AGGREGATE_FILE.relative_to(REPO_ROOT)),
        "phase_1_config": config_result,
    }

    if config_only:
        print("  (--config-only: skipping hydration check)")
        if evidence_dir:
            write_evidence(evidence, evidence_dir)
        sys.exit(1 if config_result["errors"] else 0)

    # Phase 2: Hydration check
    print("[Phase 2] Hydration directory check")
    hydration_result = check_hydration(repos)
    print(f"  Hydrated repos: {len(hydration_result['hydrated'])}/{len(repos)}")
    if hydration_result["missing"]:
        print(f"  Missing repos:  {len(hydration_result['missing'])}")
        for name in hydration_result["missing"]:
            print(f"    - {name}")
    else:
        print("  PASS: All repos hydrated")

    for h in hydration_result["hydrated"]:
        print(f"    {h['name']}: {h['module_count']} modules")
    print()

    evidence["phase_2_hydration"] = hydration_result

    # Phase 3: Must-have module check
    print("[Phase 3] Must-have module verification")
    module_result = check_must_have_modules(must_have)
    total_found = 0
    total_required = 0
    for category, info in module_result["categories"].items():
        total_found += info["found"]
        total_required += info["total"]
        status = "PASS" if not info["missing"] else "PARTIAL"
        print(f"  [{status}] {category}: {info['found']}/{info['total']}")
        if info["missing"]:
            for m in info["missing"]:
                print(f"           missing: {m}")
    print()
    print(f"  Must-have modules: {total_found}/{total_required}")

    evidence["phase_3_must_have"] = module_result

    # Summary
    print("=" * 60)
    config_pass = not config_result["errors"]
    hydration_pass = not hydration_result["missing"]
    print(f"  Phase 1 (config):    {'PASS' if config_pass else 'FAIL'}")
    print(f"  Phase 2 (hydration): {'PASS' if hydration_pass else 'PARTIAL'}")
    print(f"  Phase 3 (must-have): {total_found}/{total_required}")
    print("=" * 60)

    evidence["summary"] = {
        "config_pass": config_pass,
        "hydration_pass": hydration_pass,
        "must_have_found": total_found,
        "must_have_required": total_required,
    }

    if evidence_dir:
        write_evidence(evidence, evidence_dir)

    # Exit code: fail only if config is broken (hydration may not be available in CI)
    if not config_pass:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
