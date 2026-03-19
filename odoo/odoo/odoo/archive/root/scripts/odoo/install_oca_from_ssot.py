#!/usr/bin/env python3
"""Deterministic OCA module installation from SSOT.

Reads:
  - ssot/odoo/oca_repos.yaml  (registry: lifecycle, branch, source)
  - ssot/odoo/oca_lock.yaml   (lock: pinned SHA refs)

Outputs:
  - Deterministic install plan (human or JSON)
  - Clones/updates OCA repos into addons/oca/<name>/

Usage:
  python scripts/odoo/install_oca_from_ssot.py [--dry-run] [--json] [--strict]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "ssot" / "odoo" / "oca_repos.yaml"
DEFAULT_LOCK = REPO_ROOT / "ssot" / "odoo" / "oca_lock.yaml"
DEFAULT_TARGET = REPO_ROOT / "addons" / "oca"

INSTALLABLE_STATES = frozenset({"pinned", "ok"})
SKIP_STATES = frozenset({"blocked", "empty", "pending_vendor"})
ALL_KNOWN_STATES = INSTALLABLE_STATES | SKIP_STATES

SKIP_REASONS = {
    "blocked": "on 18.0 branch — must port to 19.0 before activation",
    "empty": "0 modules — forbidden in addons_path",
    "pending_vendor": "not yet vendored as submodule/clone",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class RepoEntry:
    """A single OCA repo from the registry."""

    name: str
    source: str
    branch: str
    status: str
    modules: int = 0
    notes: str = ""


@dataclass
class LockEntry:
    """A pinned ref from the lock file."""

    name: str
    source: str
    target_path: str
    branch: str
    ref: str
    shallow: bool = False
    lifecycle: str = "active"


@dataclass
class PlanItem:
    """One line of the resolved install plan."""

    repo: str
    status: str
    decision: str  # "install" | "skip"
    reason: str
    source: str = ""
    branch: str = ""
    ref: str = ""  # empty = unpinned
    target_path: str = ""
    modules: int = 0


@dataclass
class InstallPlan:
    """The full resolved plan."""

    items: list[PlanItem] = field(default_factory=list)
    installable: int = 0
    skipped: int = 0
    pinned: int = 0
    unpinned: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "installable": self.installable,
                "skipped": self.skipped,
                "pinned": self.pinned,
                "unpinned": self.unpinned,
                "errors": len(self.errors),
            },
            "items": [asdict(i) for i in self.items],
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_registry(path: Path) -> list[RepoEntry]:
    """Load oca_repos.yaml and return list of RepoEntry."""
    with open(path) as f:
        data = yaml.safe_load(f)

    if not data or "repos" not in data:
        raise ValueError(f"Invalid registry: {path} — missing 'repos' key")

    entries = []
    for r in data["repos"]:
        entries.append(
            RepoEntry(
                name=r["name"],
                source=r["source"],
                branch=r["branch"],
                status=r["status"],
                modules=r.get("modules", 0),
                notes=r.get("notes", ""),
            )
        )
    return entries


def load_lock(path: Path) -> dict[str, LockEntry]:
    """Load oca_lock.yaml and return dict keyed by repo name."""
    if not path.exists():
        return {}

    with open(path) as f:
        data = yaml.safe_load(f)

    if not data or "repos" not in data:
        return {}

    lock = {}
    for r in data["repos"]:
        lock[r["name"]] = LockEntry(
            name=r["name"],
            source=r["source"],
            target_path=r["target_path"],
            branch=r["branch"],
            ref=r["ref"],
            shallow=r.get("shallow", False),
            lifecycle=r.get("lifecycle", "active"),
        )
    return lock


# ---------------------------------------------------------------------------
# Plan resolution
# ---------------------------------------------------------------------------
def resolve_plan(
    registry: list[RepoEntry],
    lock: dict[str, LockEntry],
    target_dir: Path,
    strict: bool = False,
) -> InstallPlan:
    """Resolve a deterministic install plan from registry + lock."""
    plan = InstallPlan()

    # Sort by name for determinism
    for repo in sorted(registry, key=lambda r: r.name):
        # Unknown state → error
        if repo.status not in ALL_KNOWN_STATES:
            plan.errors.append(
                f"{repo.name}: unknown lifecycle state '{repo.status}'"
            )
            continue

        # Skip states
        if repo.status in SKIP_STATES:
            plan.items.append(
                PlanItem(
                    repo=repo.name,
                    status=repo.status,
                    decision="skip",
                    reason=SKIP_REASONS.get(repo.status, repo.status),
                    source=repo.source,
                    branch=repo.branch,
                    modules=repo.modules,
                )
            )
            plan.skipped += 1
            continue

        # Installable — resolve ref
        lock_entry = lock.get(repo.name)
        if lock_entry:
            ref = lock_entry.ref
            target = str(target_dir / repo.name)
            plan.pinned += 1
        else:
            ref = ""
            target = str(target_dir / repo.name)
            plan.unpinned += 1
            if strict:
                plan.errors.append(
                    f"{repo.name}: installable (status={repo.status}) "
                    f"but no lock entry — strict mode requires pinned ref"
                )

        plan.items.append(
            PlanItem(
                repo=repo.name,
                status=repo.status,
                decision="install",
                reason="pinned ref" if ref else "branch (unpinned)",
                source=repo.source,
                branch=repo.branch,
                ref=ref,
                target_path=target,
                modules=repo.modules,
            )
        )
        plan.installable += 1

    return plan


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
def execute_plan(plan: InstallPlan) -> bool:
    """Clone/update repos per the resolved plan. Returns True on success."""
    ok = True
    for item in plan.items:
        if item.decision != "install":
            continue

        target = Path(item.target_path)

        if target.exists() and (target / ".git").exists():
            # Update existing clone
            print(f"  UPDATE: {item.repo} → {target}")
            try:
                subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=target,
                    check=True,
                    capture_output=True,
                )
                if item.ref:
                    subprocess.run(
                        ["git", "checkout", item.ref],
                        cwd=target,
                        check=True,
                        capture_output=True,
                    )
                else:
                    subprocess.run(
                        ["git", "checkout", f"origin/{item.branch}"],
                        cwd=target,
                        check=True,
                        capture_output=True,
                    )
            except subprocess.CalledProcessError as e:
                print(f"  FAIL: {item.repo} — {e}", file=sys.stderr)
                ok = False
        else:
            # Fresh clone
            target.parent.mkdir(parents=True, exist_ok=True)
            print(f"  CLONE: {item.repo} → {target}")
            try:
                cmd = [
                    "git",
                    "clone",
                    "--branch",
                    item.branch,
                    "--single-branch",
                    item.source,
                    str(target),
                ]
                subprocess.run(cmd, check=True, capture_output=True)

                # Checkout pinned ref if available
                if item.ref:
                    subprocess.run(
                        ["git", "checkout", item.ref],
                        cwd=target,
                        check=True,
                        capture_output=True,
                    )
            except subprocess.CalledProcessError as e:
                print(f"  FAIL: {item.repo} — {e}", file=sys.stderr)
                ok = False

    return ok


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_plan_table(plan: InstallPlan) -> None:
    """Print the install plan as a human-readable table."""
    print(f"\n{'='*78}")
    print("  OCA Install Plan (from SSOT)")
    print(f"{'='*78}\n")

    # Header
    print(f"  {'Repo':<32} {'Status':<16} {'Decision':<10} {'Ref/Branch'}")
    print(f"  {'-'*32} {'-'*16} {'-'*10} {'-'*20}")

    for item in plan.items:
        ref_display = item.ref[:12] if item.ref else item.branch
        marker = "" if item.decision == "install" else "  "
        print(
            f"  {item.repo:<32} {item.status:<16} {item.decision:<10} {ref_display}"
        )

    print(f"\n  Summary:")
    print(f"    Installable: {plan.installable}")
    print(f"    Skipped:     {plan.skipped}")
    print(f"    Pinned:      {plan.pinned}")
    print(f"    Unpinned:    {plan.unpinned}")

    if plan.errors:
        print(f"\n  Errors ({len(plan.errors)}):")
        for err in plan.errors:
            print(f"    - {err}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic OCA module installation from SSOT"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve plan and print it without cloning",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output plan as JSON",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"Clone target directory (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any installable repo lacks a lock entry",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=f"Path to oca_repos.yaml (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK,
        help=f"Path to oca_lock.yaml (default: {DEFAULT_LOCK})",
    )
    args = parser.parse_args()

    # Load SSOT
    try:
        registry = load_registry(args.registry)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    lock = load_lock(args.lock)

    # Resolve plan
    plan = resolve_plan(registry, lock, args.target_dir, strict=args.strict)

    # Output
    if args.json:
        print(json.dumps(plan.to_dict(), indent=2))
    else:
        print_plan_table(plan)

    # Check errors
    if plan.errors:
        if not args.json:
            print(
                f"FAIL: {len(plan.errors)} error(s) in install plan",
                file=sys.stderr,
            )
        return 1

    # Dry run stops here
    if args.dry_run:
        if plan.unpinned > 0:
            if not args.json:
                print(
                    f"WARN: {plan.unpinned} repo(s) without pinned ref",
                    file=sys.stderr,
                )
            return 2
        return 0

    # Execute
    print("Executing install plan...")
    if not execute_plan(plan):
        return 1

    print(
        f"Done: {plan.installable} repos installed, "
        f"{plan.skipped} skipped"
    )

    return 2 if plan.unpinned > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
