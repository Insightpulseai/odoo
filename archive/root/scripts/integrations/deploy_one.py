#!/usr/bin/env python3
"""
Deploy One App - Dispatcher for vendor app deployments.

Supports multiple providers:
- fly: Fly.io deployment
- vercel: Vercel deployment
- supabase: Supabase Edge Functions deployment
- docker: Docker build and push (future)

Usage:
    python3 scripts/integrations/deploy_one.py --slug <app-slug>

Env:
    APPS_CATALOG (default: integrations/apps.yml)
    VERCEL_TOKEN - Required for Vercel deployments
    FLY_API_TOKEN - Required for Fly.io deployments
    SUPABASE_ACCESS_TOKEN - Required for Supabase deployments
    SUPABASE_PROJECT_REF - Required for Supabase deployments
    DRY_RUN (0|1) - If 1, print commands without executing
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORK_DIR = REPO_ROOT / ".work" / "vendors"


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    try:
        import yaml
    except ImportError:
        print("Missing PyYAML. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(path.read_text("utf-8"))


def sh(cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None, dry_run: bool = False) -> bool:
    """Run shell command."""
    full_env = {**os.environ, **(env or {})}

    if dry_run:
        print(f"[DRY RUN] {' '.join(cmd)}")
        if cwd:
            print(f"  cwd: {cwd}")
        return True

    try:
        subprocess.run(cmd, cwd=cwd, env=full_env, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)} (exit {e.returncode})", file=sys.stderr)
        return False


def clone_or_update_repo(app: Dict[str, Any], dry_run: bool = False) -> Optional[Path]:
    """Clone or update the vendor repo."""
    repo_url = app.get("repo")
    ref = app.get("ref", "main")
    slug = app["slug"]

    if repo_url == "internal":
        # Internal app - use monorepo path
        deploy_path = app.get("deploy", {}).get("path", "")
        if deploy_path:
            return REPO_ROOT / deploy_path
        return REPO_ROOT

    work_path = WORK_DIR / slug
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    if not (work_path / ".git").exists():
        print(f"Cloning {repo_url} -> {work_path}")
        if not sh(["git", "clone", "--depth=1", "--branch", ref, repo_url, str(work_path)], dry_run=dry_run):
            return None
    else:
        print(f"Updating {work_path}")
        if not sh(["git", "fetch", "origin", ref, "--depth=1"], cwd=str(work_path), dry_run=dry_run):
            return None
        if not sh(["git", "checkout", ref], cwd=str(work_path), dry_run=dry_run):
            return None
        if not sh(["git", "reset", "--hard", f"origin/{ref}"], cwd=str(work_path), dry_run=dry_run):
            return None

    deploy_path = app.get("deploy", {}).get("path", ".")
    return work_path / deploy_path


def deploy_vercel(app: Dict[str, Any], cwd: str, dry_run: bool = False) -> bool:
    """Deploy to Vercel."""
    token = os.environ.get("VERCEL_TOKEN")
    if not token:
        print("Missing VERCEL_TOKEN", file=sys.stderr)
        return False

    deploy_cfg = app.get("deploy", {})
    runtime = app.get("runtime", {})
    package_manager = runtime.get("package_manager", "npm")

    print(f"Deploying {app['slug']} to Vercel...")

    # Install dependencies
    if package_manager == "pnpm":
        if not sh(["pnpm", "install", "--frozen-lockfile"], cwd=cwd, dry_run=dry_run):
            return False
    elif package_manager == "yarn":
        if not sh(["yarn", "install", "--frozen-lockfile"], cwd=cwd, dry_run=dry_run):
            return False
    else:
        if not sh(["npm", "ci"], cwd=cwd, dry_run=dry_run):
            return False

    # Build
    if not sh(["npm", "run", "build"], cwd=cwd, dry_run=dry_run):
        print("Build failed or no build script", file=sys.stderr)
        # Continue anyway - Vercel might handle build

    # Deploy
    cmd = ["vercel", "deploy", "--prod", "--token", token]
    project_name = deploy_cfg.get("project_name")
    if project_name:
        cmd.extend(["--name", project_name])

    return sh(cmd, cwd=cwd, dry_run=dry_run)


def deploy_fly(app: Dict[str, Any], cwd: str, dry_run: bool = False) -> bool:
    """Deploy to Fly.io."""
    token = os.environ.get("FLY_API_TOKEN")
    if not token:
        print("Missing FLY_API_TOKEN", file=sys.stderr)
        return False

    deploy_cfg = app.get("deploy", {})
    runtime = app.get("runtime", {})
    package_manager = runtime.get("package_manager", "npm")

    print(f"Deploying {app['slug']} to Fly.io...")

    # Install dependencies
    if package_manager == "pnpm":
        if not sh(["pnpm", "install", "--frozen-lockfile"], cwd=cwd, dry_run=dry_run):
            return False
    elif package_manager == "yarn":
        if not sh(["yarn", "install", "--frozen-lockfile"], cwd=cwd, dry_run=dry_run):
            return False
    else:
        if not sh(["npm", "ci"], cwd=cwd, dry_run=dry_run):
            return False

    # Build
    sh(["npm", "run", "build"], cwd=cwd, dry_run=dry_run)  # May fail if no build script

    # Deploy
    env = {"FLY_API_TOKEN": token}
    cmd = ["flyctl", "deploy", "--remote-only"]

    app_name = deploy_cfg.get("app_name")
    if app_name:
        cmd.extend(["--app", app_name])

    region = deploy_cfg.get("region")
    if region:
        cmd.extend(["--region", region])

    return sh(cmd, cwd=cwd, env=env, dry_run=dry_run)


def deploy_supabase(app: Dict[str, Any], cwd: str, dry_run: bool = False) -> bool:
    """Deploy Supabase Edge Functions."""
    token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    project_ref = os.environ.get("SUPABASE_PROJECT_REF") or app.get("supabase", {}).get("project_ref")

    if not token:
        print("Missing SUPABASE_ACCESS_TOKEN", file=sys.stderr)
        return False

    if not project_ref:
        print("Missing SUPABASE_PROJECT_REF", file=sys.stderr)
        return False

    deploy_cfg = app.get("deploy", {})
    functions = deploy_cfg.get("functions", [])

    if not functions:
        print("No functions specified in deploy config", file=sys.stderr)
        return False

    print(f"Deploying {len(functions)} Supabase functions for {app['slug']}...")

    # Link project (if not already linked)
    sh(["supabase", "link", "--project-ref", project_ref], cwd=str(REPO_ROOT), dry_run=dry_run)

    # Deploy each function
    for func in functions:
        print(f"  Deploying function: {func}")
        if not sh(["supabase", "functions", "deploy", func], cwd=str(REPO_ROOT), dry_run=dry_run):
            print(f"  Failed to deploy function: {func}", file=sys.stderr)
            return False

    return True


def deploy_docker(app: Dict[str, Any], cwd: str, dry_run: bool = False) -> bool:
    """Deploy via Docker (build and push)."""
    deploy_cfg = app.get("deploy", {})
    image = deploy_cfg.get("image")
    registry = deploy_cfg.get("registry", "")

    if not image:
        print("Missing docker image name in deploy config", file=sys.stderr)
        return False

    print(f"Building Docker image for {app['slug']}...")

    tag = f"{registry}/{image}" if registry else image

    # Build
    if not sh(["docker", "build", "-t", tag, "."], cwd=cwd, dry_run=dry_run):
        return False

    # Push
    if not sh(["docker", "push", tag], cwd=cwd, dry_run=dry_run):
        return False

    return True


def write_deploy_evidence(app: Dict[str, Any], success: bool, provider: str) -> None:
    """Write deployment evidence to docs/evidence/."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    evidence_dir = REPO_ROOT / "docs" / "evidence" / timestamp / "deploy"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence = {
        "deployed_at_utc": datetime.now(timezone.utc).isoformat(),
        "app_slug": app["slug"],
        "app_name": app.get("name", app["slug"]),
        "provider": provider,
        "success": success,
        "repo": app.get("repo", "internal"),
        "ref": app.get("ref", "main"),
    }

    evidence_file = evidence_dir / f"{app['slug']}_deploy.json"
    evidence_file.write_text(json.dumps(evidence, indent=2) + "\n", "utf-8")
    print(f"Wrote deploy evidence to {evidence_file}")


def main():
    parser = argparse.ArgumentParser(description="Deploy a single vendor app")
    parser.add_argument("--slug", required=True, help="App slug from apps.yml")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "0") == "1"

    catalog_path = REPO_ROOT / os.environ.get("APPS_CATALOG", "integrations/apps.yml")
    if not catalog_path.exists():
        print(f"Apps catalog not found: {catalog_path}", file=sys.stderr)
        sys.exit(2)

    cfg = load_yaml(catalog_path)
    apps = cfg.get("apps", [])

    app = next((a for a in apps if a.get("slug") == args.slug), None)
    if not app:
        print(f"Unknown app slug: {args.slug}", file=sys.stderr)
        print(f"Available: {', '.join(a['slug'] for a in apps)}", file=sys.stderr)
        sys.exit(2)

    deploy_cfg = app.get("deploy", {})
    provider = deploy_cfg.get("provider")

    if not provider:
        print(f"No deploy provider configured for {args.slug}", file=sys.stderr)
        sys.exit(2)

    print(f"=== Deploying {app['name']} ({args.slug}) via {provider} ===")

    # Clone/update repo
    cwd = clone_or_update_repo(app, dry_run=dry_run)
    if not cwd:
        print("Failed to prepare repository", file=sys.stderr)
        sys.exit(1)

    print(f"Working directory: {cwd}")

    # Dispatch to provider
    success = False
    if provider == "vercel":
        success = deploy_vercel(app, str(cwd), dry_run=dry_run)
    elif provider == "fly":
        success = deploy_fly(app, str(cwd), dry_run=dry_run)
    elif provider == "supabase":
        success = deploy_supabase(app, str(cwd), dry_run=dry_run)
    elif provider == "docker":
        success = deploy_docker(app, str(cwd), dry_run=dry_run)
    else:
        print(f"Unknown provider: {provider}", file=sys.stderr)
        sys.exit(2)

    # Write evidence
    if not dry_run:
        write_deploy_evidence(app, success, provider)

    if success:
        print(f"\n=== Deploy successful: {args.slug} ===")
        sys.exit(0)
    else:
        print(f"\n=== Deploy FAILED: {args.slug} ===", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
