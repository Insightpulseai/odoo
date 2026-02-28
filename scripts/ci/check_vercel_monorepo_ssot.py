#!/usr/bin/env python3
"""
check_vercel_monorepo_ssot.py — Vercel Monorepo SSOT CI Validator

Validates that ssot/vercel/projects.yaml is internally consistent and
satisfies monorepo contract invariants defined in
docs/architecture/VERCEL_MONOREPO_CONTRACT.md.

Exit 0 = all checks pass.
Exit 1 = one or more checks fail.

Usage:
    python scripts/ci/check_vercel_monorepo_ssot.py
    python scripts/ci/check_vercel_monorepo_ssot.py --repo-root /path/to/repo
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL [setup] pyyaml not installed — run: pip install pyyaml", flush=True)
    sys.exit(1)

SSOT_PATH = Path("ssot/vercel/projects.yaml")
PNPM_WORKSPACE_PATH = Path("pnpm-workspace.yaml")
TURBO_JSON_PATH = Path("turbo.json")

PASS = "PASS"
FAIL = "FAIL"


def result(tag: str, label: str, ok: bool, detail: str = "") -> bool:
    prefix = PASS if ok else FAIL
    msg = f"{prefix} [{tag}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg, flush=True)
    return ok


def check_ssot_exists_and_valid(repo_root: Path):
    """Check 1: ssot/vercel/projects.yaml exists and is valid YAML."""
    path = repo_root / SSOT_PATH
    if not path.exists():
        return result("check1", "ssot/vercel/projects.yaml exists", False,
                      f"file not found at {SSOT_PATH}"), None

    try:
        with path.open() as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return result("check1", "ssot/vercel/projects.yaml is valid YAML", False,
                      str(exc)), None

    if data is None:
        return result("check1", "ssot/vercel/projects.yaml exists and is valid YAML", False,
                      "file is empty"), None

    return result("check1", "ssot/vercel/projects.yaml exists and is valid YAML", True), data


def check_root_directories_under_apps(data: dict):
    """Check 2: Every project root_directory starts with 'apps/'."""
    projects = data.get("projects", [])
    if not projects:
        return result("check2", "projects[].root_directory all start with apps/", True,
                      "no projects defined (vacuously true)")

    bad = []
    for p in projects:
        name = p.get("name", "<unnamed>")
        root = p.get("root_directory", "")
        if not root.startswith("apps/"):
            bad.append(f"{name!r}: root_directory={root!r}")

    ok = len(bad) == 0
    detail = "; ".join(bad) if bad else f"checked {len(projects)} project(s)"
    return result("check2", "projects[].root_directory all start with apps/", ok, detail)


def check_packages_require_include_files(data: dict):
    """Check 3: If uses_packages is true, include_files_outside_root must be true."""
    projects = data.get("projects", [])
    bad = []
    for p in projects:
        name = p.get("name", "<unnamed>")
        if p.get("uses_packages") is True:
            if p.get("include_files_outside_root") is not True:
                bad.append(f"{name!r}: uses_packages=true but include_files_outside_root is not true")

    ok = len(bad) == 0
    detail = "; ".join(bad) if bad else f"checked {len(projects)} project(s)"
    return result("check3",
                  "uses_packages=true implies include_files_outside_root=true",
                  ok, detail)


def check_turborepo_turbo_json(repo_root: Path, data: dict):
    """Check 4: If monorepo-level turborepo is true, turbo.json must exist at repo root."""
    turborepo_enabled = data.get("turborepo", False)
    if not turborepo_enabled:
        return result("check4", "turborepo flag implies turbo.json at repo root", True,
                      "turborepo: false — skipped")

    turbo_path = repo_root / TURBO_JSON_PATH
    exists = turbo_path.exists()
    detail = str(TURBO_JSON_PATH) if exists else f"{TURBO_JSON_PATH} not found"
    return result("check4", "turborepo: true => turbo.json exists at repo root", exists, detail)


def check_pnpm_workspace(repo_root: Path):
    """Check 5: pnpm-workspace.yaml exists and contains patterns for apps/* and packages/*."""
    path = repo_root / PNPM_WORKSPACE_PATH
    if not path.exists():
        return result("check5",
                      "pnpm-workspace.yaml exists with apps/* and packages/* patterns",
                      False, f"{PNPM_WORKSPACE_PATH} not found")

    try:
        with path.open() as f:
            ws = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return result("check5",
                      "pnpm-workspace.yaml exists with apps/* and packages/* patterns",
                      False, str(exc))

    packages_list = ws.get("packages", []) if ws else []
    has_apps = any("apps/" in p or p == "apps/*" for p in packages_list)
    has_packages = any("packages/" in p or p == "packages/*" for p in packages_list)

    missing = []
    if not has_apps:
        missing.append("apps/* pattern missing")
    if not has_packages:
        missing.append("packages/* pattern missing")

    ok = len(missing) == 0
    detail = "; ".join(missing) if missing else f"patterns found: {packages_list}"
    return result("check5",
                  "pnpm-workspace.yaml has apps/* and packages/* patterns",
                  ok, detail)


def check_all_projects_declare_ignored_build(data: dict):
    """Check 6: Every project declares ignored_build (no project missing it)."""
    projects = data.get("projects", [])
    if not projects:
        return result("check6", "all projects declare ignored_build", True,
                      "no projects defined (vacuously true)")

    bad = []
    for p in projects:
        name = p.get("name", "<unnamed>")
        if "ignored_build" not in p:
            bad.append(name)

    ok = len(bad) == 0
    if bad:
        detail = f"missing ignored_build: {', '.join(repr(n) for n in bad)}"
    else:
        detail = f"{len(projects)} project(s) all declare ignored_build"
    return result("check6", "all projects declare ignored_build", ok, detail)


def main():
    parser = argparse.ArgumentParser(description="Validate ssot/vercel/projects.yaml")
    parser.add_argument("--repo-root", default=".", help="Path to repo root (default: .)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    print(f"Vercel Monorepo SSOT Validator — repo root: {repo_root}", flush=True)
    print("-" * 60, flush=True)

    failures = 0

    # Check 1: file exists + valid YAML — also loads data for subsequent checks
    ok1, data = check_ssot_exists_and_valid(repo_root)
    if not ok1:
        failures += 1

    if data is not None:
        # Check 2
        if not check_root_directories_under_apps(data):
            failures += 1

        # Check 3
        if not check_packages_require_include_files(data):
            failures += 1

        # Check 4
        if not check_turborepo_turbo_json(repo_root, data):
            failures += 1
    else:
        # Data unavailable — mark remaining data-dependent checks as failed
        for n, label in [
            ("check2", "projects[].root_directory all start with apps/"),
            ("check3", "uses_packages=true implies include_files_outside_root=true"),
            ("check4", "turborepo: true => turbo.json exists at repo root"),
        ]:
            result(n, label, False, "skipped — SSOT file unreadable")
            failures += 1

    # Check 5 (independent of SSOT data)
    if not check_pnpm_workspace(repo_root):
        failures += 1

    # Check 6 (needs data)
    if data is not None:
        if not check_all_projects_declare_ignored_build(data):
            failures += 1
    else:
        result("check6", "all projects declare ignored_build", False,
               "skipped — SSOT file unreadable")
        failures += 1

    print("-" * 60, flush=True)
    if failures == 0:
        print(f"PASS — all 6 checks passed", flush=True)
        sys.exit(0)
    else:
        print(f"FAIL — {failures} check(s) failed", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
