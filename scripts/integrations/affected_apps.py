#!/usr/bin/env python3
"""
Compute affected apps from git diff + dependency graph.

Rules:
- If files under integrations/apps.yml change => all apps affected
- If a vendored mirror folder changes => that app affected
- If an app depends_on another app and dependency affected => app affected too
- Optional lockfile heuristic: if any lockfile changes, mark all node apps (conservative)
- If supabase/migrations change => apps with shared supabase affected
- If supabase/functions change => config-registry affected

Outputs:
  - prints JSON list to stdout
  - writes to $AFFECTED_OUT if set

Env:
  GIT_BASE (default origin/main)
  GIT_HEAD (default HEAD)
  AFFECTED_OUT (optional)
  APPS_CATALOG (default integrations/apps.yml)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def sh(cmd: List[str]) -> str:
    """Run shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(REPO_ROOT)
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def load_apps(catalog_path: str) -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Load apps from catalog YAML."""
    try:
        import yaml
    except ImportError:
        print("Missing PyYAML. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    path = REPO_ROOT / catalog_path
    if not path.exists():
        print(f"Apps catalog not found: {path}", file=sys.stderr)
        sys.exit(2)

    cfg = yaml.safe_load(path.read_text("utf-8"))
    apps = cfg.get("apps", [])
    by_slug = {a["slug"]: a for a in apps}
    return apps, by_slug


def get_changed_files(base: str, head: str) -> List[str]:
    """Get list of changed files between base and head."""
    diff = sh(["git", "diff", "--name-only", f"{base}..{head}"])
    return [f.strip() for f in diff.splitlines() if f.strip()]


def compute_affected(
    apps: List[Dict[str, Any]],
    by_slug: Dict[str, Dict[str, Any]],
    changed_files: List[str]
) -> Set[str]:
    """Compute set of affected app slugs based on changed files."""
    affected: Set[str] = set()

    # Rule 1: If the catalog changes, all apps are affected
    if any(f == "integrations/apps.yml" for f in changed_files):
        return {a["slug"] for a in apps}

    # Rule 2: Check specific paths for each app
    for f in changed_files:
        parts = f.split("/")

        # Vendor backlog changes
        if len(parts) >= 3 and parts[0] == "backlog" and parts[1] == "vendors":
            affected.add(parts[2])

        # Vendored repos (if you vendor external repos)
        if len(parts) >= 2 and parts[0] == "vendors":
            affected.add(parts[1])

        # Internal apps in apps/ directory
        if len(parts) >= 2 and parts[0] == "apps":
            app_dir = parts[1]
            # Find app by deploy path
            for app in apps:
                deploy = app.get("deploy", {})
                deploy_path = deploy.get("path", "")
                if deploy_path and deploy_path.startswith(f"apps/{app_dir}"):
                    affected.add(app["slug"])

        # Supabase migrations affect shared-supabase apps
        if f.startswith("supabase/migrations/"):
            for app in apps:
                supabase = app.get("supabase", {})
                if supabase.get("shared", False):
                    affected.add(app["slug"])

        # Supabase functions changes
        if f.startswith("supabase/functions/"):
            # Check if it's a specific function
            if len(parts) >= 3:
                func_name = parts[2]
                for app in apps:
                    deploy = app.get("deploy", {})
                    functions = deploy.get("functions", [])
                    if func_name in functions:
                        affected.add(app["slug"])
            # Also mark config-registry
            if "config-registry" in by_slug:
                affected.add("config-registry")

        # Config directory changes affect config-registry
        if f.startswith("config/"):
            if "config-registry" in by_slug:
                affected.add("config-registry")

    # Rule 3: Conservative lockfile heuristic
    lockfiles = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
    if any(Path(f).name in lockfiles for f in changed_files):
        for app in apps:
            if app.get("type") == "node":
                affected.add(app["slug"])

    # Rule 4: Propagate through dependency graph
    changed = True
    iterations = 0
    max_iterations = len(apps) + 1  # Prevent infinite loops

    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        for app in apps:
            slug = app["slug"]
            deps = app.get("depends_on", []) or []
            if any(d in affected for d in deps) and slug not in affected:
                affected.add(slug)
                changed = True

    return affected


def main():
    base = os.environ.get("GIT_BASE", "origin/main")
    head = os.environ.get("GIT_HEAD", "HEAD")
    catalog_path = os.environ.get("APPS_CATALOG", "integrations/apps.yml")
    out_path = os.environ.get("AFFECTED_OUT")

    # Ensure we have the base ref
    sh(["git", "fetch", "origin", "main", "--depth=1"])

    apps, by_slug = load_apps(catalog_path)
    changed_files = get_changed_files(base, head)

    if not changed_files:
        print("[]")
        if out_path:
            Path(out_path).write_text("[]", "utf-8")
        return

    affected = compute_affected(apps, by_slug, changed_files)

    # Filter to only external apps (exclude "internal" repos for deployment matrix)
    # but include all for backlog sync
    external_affected = sorted([
        slug for slug in affected
        if by_slug.get(slug, {}).get("repo") != "internal"
    ])

    # Output all affected for general use
    all_affected = sorted(affected)
    payload = json.dumps(all_affected)
    print(payload)

    if out_path:
        Path(out_path).write_text(payload, "utf-8")

    # Also output external-only to a separate file if needed
    ext_out = os.environ.get("AFFECTED_EXTERNAL_OUT")
    if ext_out:
        Path(ext_out).write_text(json.dumps(external_affected), "utf-8")


if __name__ == "__main__":
    main()
