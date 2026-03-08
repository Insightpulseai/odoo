#!/usr/bin/env python3
"""
Normalize raw SSOT snapshots into committed YAML inventories.

Reads raw snapshot JSON (CI artifacts), classifies repos against
target-state-repos.yaml, normalizes environments, and emits stable
YAML summaries. Flags drift when repos are unclassified or environments
use non-canonical names.

Usage:
    python3 scripts/ssot/normalize_snapshot_inventory.py           # normalize + write
    python3 scripts/ssot/normalize_snapshot_inventory.py --dry-run  # validate only
    python3 scripts/ssot/normalize_snapshot_inventory.py --check    # CI mode, exit 1 on drift
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parent.parent.parent
SSOT_DIR = REPO_ROOT / "ssot"
GITHUB_DIR = SSOT_DIR / "github"
VERCEL_DIR = SSOT_DIR / "vercel"
RUNTIME_DIR = SSOT_DIR / "runtime"
REPO_DETAIL_DIR = GITHUB_DIR / "repo-details"

TARGET_STATE_PATH = GITHUB_DIR / "target-state-repos.yaml"
ORG_INVENTORY_PATH = GITHUB_DIR / "org.inventory.yaml"
REPOS_INVENTORY_PATH = GITHUB_DIR / "repos.inventory.yaml"
ENVS_INVENTORY_PATH = RUNTIME_DIR / "environments.inventory.yaml"

VALID_DOMAINS = {
    "erp", "control-plane", "web", "data-platform", "infrastructure",
    "design-system", "agents", "governance", "templates",
}

VALID_ENV_CLASSES = {"dev", "staging", "prod", "preview"}

# Environment name -> canonical class mapping
ENV_CLASS_MAP = {
    "dev": "dev",
    "development": "dev",
    "odoo-dev": "dev",
    "databricks-dev": "dev",
    "staging": "staging",
    "odoo-staging": "staging",
    "databricks-staging": "staging",
    "prod": "prod",
    "production": "prod",
    "odoo-production": "prod",
    "databricks-production": "prod",
    "github-pages": "prod",
}


def read_json(path: Path) -> dict | list:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def read_yaml(path: Path) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def write_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def classify_environment(env_name: str) -> str:
    """Map environment name to canonical class."""
    lower = env_name.lower().strip()

    # Direct mapping
    if lower in ENV_CLASS_MAP:
        return ENV_CLASS_MAP[lower]

    # Pattern matching
    if "preview" in lower:
        return "preview"
    if "prod" in lower:
        return "prod"
    if "stag" in lower:
        return "staging"
    if "dev" in lower:
        return "dev"

    return "unknown"


def load_target_state() -> dict[str, dict]:
    """Load target-state-repos.yaml into name->config map."""
    ts = read_yaml(TARGET_STATE_PATH)
    repos = ts.get("canonical_repos", [])
    return {r["name"]: r for r in repos}


def normalize_org(repos_snapshot: list, teams_snapshot: list, members_snapshot: list) -> dict:
    """Normalize org-level inventory."""
    active = [r for r in repos_snapshot if not r.get("archived", False)]
    archived = [r for r in repos_snapshot if r.get("archived", False)]

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "org": "Insightpulseai",
        "counts": {
            "total_repos": len(repos_snapshot),
            "active_repos": len(active),
            "archived_repos": len(archived),
            "teams": len(teams_snapshot) if isinstance(teams_snapshot, list) else 0,
            "members": len(members_snapshot) if isinstance(members_snapshot, list) else 0,
        },
        "active_repos": sorted([r["name"] for r in active]),
        "archived_repos": sorted([r["name"] for r in archived]),
        "teams": [t.get("name", t.get("slug", "")) for t in teams_snapshot]
        if isinstance(teams_snapshot, list)
        else [],
    }


def normalize_repos(repos_snapshot: list, target_state: dict[str, dict]) -> tuple[dict, list[str]]:
    """Normalize per-repo inventory. Returns (inventory, drift_warnings)."""
    drift = []
    normalized = []

    for repo in repos_snapshot:
        name = repo["name"]
        ts = target_state.get(name, {})

        if not ts:
            drift.append(f"UNCLASSIFIED: repo '{name}' not in target-state-repos.yaml")

        domain = ts.get("domain", "unclassified")
        if domain not in VALID_DOMAINS and domain != "unclassified":
            drift.append(f"INVALID_DOMAIN: repo '{name}' has domain '{domain}'")

        # Check for duplicate canonical responsibility
        if ts.get("canonical", False):
            existing = [
                r for r in normalized
                if r.get("domain") == domain and r.get("canonical", False)
            ]
            if existing:
                drift.append(
                    f"DUPLICATE_CANONICAL: domain '{domain}' claimed by both "
                    f"'{existing[0]['name']}' and '{name}'"
                )

        # Check archived repos still receiving real updates
        # (skip metadata-only updates within 7 days of archival — those are
        # GitHub's own archival timestamp bumps, not real activity)
        if repo.get("archived", False):
            updated = repo.get("updated_at", "")
            ts_entry = target_state.get(name, {})
            # Only flag if there are recent workflow runs or pushes
            runs_file = REPO_DETAIL_DIR / f"{name}.workflow-runs.json"
            has_recent_runs = False
            if runs_file.exists():
                runs_data = read_json(runs_file)
                run_count = runs_data.get("total_count", 0) if isinstance(runs_data, dict) else 0
                has_recent_runs = run_count > 0

            if has_recent_runs:
                drift.append(
                    f"ARCHIVED_ACTIVE: archived repo '{name}' has recent workflow runs"
                )

        # Read per-repo detail if available
        detail_file = REPO_DETAIL_DIR / f"{name}.workflows.json"
        workflow_count = 0
        if detail_file.exists():
            wf_data = read_json(detail_file)
            if isinstance(wf_data, list):
                workflow_count = sum(
                    len(page.get("workflows", []))
                    for page in wf_data
                    if isinstance(page, dict)
                )
            elif isinstance(wf_data, dict):
                workflow_count = len(wf_data.get("workflows", []))

        normalized.append({
            "name": name,
            "visibility": repo.get("visibility", "unknown"),
            "status": "archived" if repo.get("archived") else "active",
            "domain": domain,
            "canonical": ts.get("canonical", False),
            "source_of_truth": ts.get("canonical", False),
            "default_branch": repo.get("default_branch", "main"),
            "workflows": workflow_count,
            "updated_at": repo.get("updated_at", ""),
        })

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "org": "Insightpulseai",
        "repos": sorted(normalized, key=lambda r: (r["status"] != "active", r["name"])),
    }, drift


def normalize_environments(repos_snapshot: list) -> tuple[dict, list[str]]:
    """Normalize environment inventory across all repos and providers."""
    drift = []
    environments = []
    seen = set()

    for repo in repos_snapshot:
        name = repo["name"]
        env_file = REPO_DETAIL_DIR / f"{name}.environments.json"
        if not env_file.exists():
            continue

        env_data = read_json(env_file)
        env_list = env_data.get("environments", []) if isinstance(env_data, dict) else []

        for env in env_list:
            env_name = env.get("name", "")
            if not env_name:
                continue

            env_class = classify_environment(env_name)
            if env_class == "unknown":
                drift.append(
                    f"UNKNOWN_ENV_CLASS: environment '{env_name}' in repo '{name}' "
                    f"does not map to dev/staging/prod/preview"
                )

            key = f"{name}:{env_name}"
            if key in seen:
                continue
            seen.add(key)

            environments.append({
                "provider": "github",
                "environment": env_name,
                "repo": name,
                "class": env_class,
                "canonical": env_class in VALID_ENV_CLASSES,
            })

    # Add Vercel environments if available
    vercel_projects = read_json(VERCEL_DIR / "projects.snapshot.json")
    if isinstance(vercel_projects, dict) and not vercel_projects.get("skipped"):
        for proj in vercel_projects.get("projects", []):
            proj_name = proj.get("name", "")
            environments.append({
                "provider": "vercel",
                "environment": f"Production – {proj_name}",
                "repo": proj_name,
                "class": "prod",
                "canonical": True,
            })

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environments": sorted(
            environments,
            key=lambda e: (e["provider"], e["repo"], e["class"]),
        ),
    }, drift


def check_staged_snapshots() -> list[str]:
    """Check if any raw snapshot JSON files are staged in git."""
    import subprocess

    drift = []
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            if line.endswith(".snapshot.json") and "ssot/" in line:
                drift.append(f"STAGED_SNAPSHOT: raw snapshot '{line}' staged in git")
            if "ssot/github/repo-details/" in line:
                drift.append(f"STAGED_SNAPSHOT: raw detail '{line}' staged in git")
            if line == "ssot/evidence/snapshot-manifest.json":
                drift.append(f"STAGED_SNAPSHOT: manifest '{line}' staged in git")
    except Exception:
        pass

    return drift


def main():
    parser = argparse.ArgumentParser(description="Normalize SSOT snapshot inventory")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write")
    parser.add_argument("--check", action="store_true", help="CI mode — exit 1 on any drift")
    args = parser.parse_args()

    all_drift: list[str] = []

    # Load raw snapshots
    repos_raw = read_json(GITHUB_DIR / "repos.snapshot.json")
    if isinstance(repos_raw, dict):
        repos_raw = [repos_raw] if "name" in repos_raw else []

    teams_raw = read_json(GITHUB_DIR / "teams.snapshot.json")
    members_raw = read_json(GITHUB_DIR / "members.snapshot.json")

    # Load target state
    target_state = load_target_state()

    # Normalize
    org_inventory = normalize_org(repos_raw, teams_raw, members_raw)
    repos_inventory, repos_drift = normalize_repos(repos_raw, target_state)
    envs_inventory, envs_drift = normalize_environments(repos_raw)

    all_drift.extend(repos_drift)
    all_drift.extend(envs_drift)
    all_drift.extend(check_staged_snapshots())

    # Report
    print(f"Org: {org_inventory['org']}")
    print(f"  Repos: {org_inventory['counts']['total_repos']} "
          f"({org_inventory['counts']['active_repos']} active, "
          f"{org_inventory['counts']['archived_repos']} archived)")
    print(f"  Teams: {org_inventory['counts']['teams']}")
    print(f"  Members: {org_inventory['counts']['members']}")
    print(f"  Environments: {len(envs_inventory['environments'])}")
    print(f"  Drift warnings: {len(all_drift)}")

    if all_drift:
        print("\n--- DRIFT ---")
        for d in all_drift:
            print(f"  ! {d}")

    if not args.dry_run:
        write_yaml(ORG_INVENTORY_PATH, org_inventory)
        write_yaml(REPOS_INVENTORY_PATH, repos_inventory)
        write_yaml(ENVS_INVENTORY_PATH, envs_inventory)
        print(f"\nWrote:")
        print(f"  {ORG_INVENTORY_PATH}")
        print(f"  {REPOS_INVENTORY_PATH}")
        print(f"  {ENVS_INVENTORY_PATH}")
    else:
        print("\n[dry-run] No files written.")

    if args.check and all_drift:
        print(f"\nFAIL: {len(all_drift)} drift warning(s)", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
