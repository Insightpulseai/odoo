#!/usr/bin/env python3
"""
Vendor Backlog Sync - Loop apps.yml and export vendor issues + projectv2.

Exports GitHub Issues and ProjectV2 items for each configured vendor app
into backlog/vendors/<slug>/, then runs validate_and_diff.py to produce
aggregated diff reports.

Usage:
    python3 scripts/integrations/vendor_backlog_sync.py

Env:
    GH_TOKEN (required) - GitHub App installation token
    APPS_CATALOG (default: integrations/apps.yml)
    BACKLOG_EXPORT_VALIDATE_STRICT (default: 1)
    BACKLOG_DIFF_MAX_ITEMS (default: 20)
    BACKLOG_PROJECT_FIELD_ALLOWLIST (optional)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    try:
        import yaml
    except ImportError:
        print("Missing PyYAML. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(path.read_text("utf-8"))


def run_script(script: str, env: Dict[str, str]) -> bool:
    """Run a Python script with given environment."""
    full_env = {**os.environ, **env}
    script_path = REPO_ROOT / script

    if not script_path.exists():
        print(f"Script not found: {script_path}", file=sys.stderr)
        return False

    try:
        subprocess.run(
            ["python3", str(script_path)],
            env=full_env,
            check=True,
            cwd=str(REPO_ROOT)
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed: {script} (exit {e.returncode})", file=sys.stderr)
        return False


def sync_app_backlog(app: Dict[str, Any], token: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Sync backlog for a single app. Returns status dict."""
    slug = app["slug"]
    backlog_cfg = app.get("backlog", {})
    gh_cfg = backlog_cfg.get("github", {})
    p2_cfg = backlog_cfg.get("projectv2", {})

    result = {
        "slug": slug,
        "issues_synced": False,
        "project_synced": False,
        "issues_count": 0,
        "project_count": 0,
        "errors": []
    }

    # Skip if no GitHub config
    if not gh_cfg.get("owner") or not gh_cfg.get("repo"):
        result["errors"].append("No GitHub config")
        return result

    # Create output directory
    export_dir = settings.get("export_dir", "backlog/vendors")
    out_dir = REPO_ROOT / export_dir / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export Issues
    issues_env = {
        "GH_TOKEN": token,
        "GH_OWNER": gh_cfg["owner"],
        "GH_REPO": gh_cfg["repo"],
        "GH_INCLUDE_PRS": "1" if gh_cfg.get("include_prs", False) else "0",
        "GH_STATE": gh_cfg.get("state", "open"),
        "BACKLOG_OUT": str(out_dir / "issues.json"),
    }

    if gh_cfg.get("labels"):
        issues_env["GH_LABELS"] = gh_cfg["labels"]

    if run_script("scripts/backlog_export/github_export_issues.py", issues_env):
        result["issues_synced"] = True
        # Count issues
        issues_file = out_dir / "issues.json"
        if issues_file.exists():
            try:
                data = json.loads(issues_file.read_text("utf-8"))
                result["issues_count"] = len(data.get("issues", []))
            except Exception:
                pass
    else:
        result["errors"].append("Issues export failed")

    # Export ProjectV2 if enabled
    if p2_cfg.get("enabled"):
        project_env = {
            "GH_TOKEN": token,
            "GH_PROJECT_OWNER": p2_cfg.get("owner", ""),
            "GH_PROJECT_OWNER_TYPE": p2_cfg.get("owner_type", "org"),
            "GH_PROJECT_NUMBER": str(p2_cfg.get("number", "")),
            "BACKLOG_PROJECT_OUT": str(out_dir / "project_export.json"),
            "GH_PROJECT_ITEM_LIMIT": str(p2_cfg.get("item_limit", 300)),
        }

        if run_script("scripts/backlog_export/github_export_projectv2.py", project_env):
            result["project_synced"] = True
            # Count project items
            project_file = out_dir / "project_export.json"
            if project_file.exists():
                try:
                    data = json.loads(project_file.read_text("utf-8"))
                    result["project_count"] = len(data.get("items", []))
                except Exception:
                    pass
        else:
            result["errors"].append("ProjectV2 export failed")

    return result


def write_sync_summary(results: List[Dict[str, Any]], settings: Dict[str, Any]) -> None:
    """Write sync summary to docs/."""
    from datetime import datetime, timezone

    summary = {
        "synced_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_apps": len(results),
        "successful": sum(1 for r in results if r["issues_synced"]),
        "failed": sum(1 for r in results if r["errors"]),
        "total_issues": sum(r["issues_count"] for r in results),
        "total_project_items": sum(r["project_count"] for r in results),
        "apps": results,
    }

    # Write JSON
    summary_path = REPO_ROOT / "docs" / "VENDOR_BACKLOG_SYNC_SUMMARY.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", "utf-8")

    # Write Markdown
    md_path = REPO_ROOT / "docs" / "VENDOR_BACKLOG_SYNC_SUMMARY.md"
    lines = [
        "# Vendor Backlog Sync Summary\n",
        f"**Synced at (UTC):** {summary['synced_at_utc']}\n\n",
        "## Overview\n",
        f"- Total apps: **{summary['total_apps']}**\n",
        f"- Successful: **{summary['successful']}**\n",
        f"- Failed: **{summary['failed']}**\n",
        f"- Total issues synced: **{summary['total_issues']}**\n",
        f"- Total project items: **{summary['total_project_items']}**\n\n",
        "## Per-App Status\n\n",
        "| App | Issues | Project Items | Status | Errors |\n",
        "|-----|--------|---------------|--------|--------|\n",
    ]

    for r in results:
        status = "OK" if r["issues_synced"] and not r["errors"] else "FAILED"
        errors = "; ".join(r["errors"]) if r["errors"] else "-"
        lines.append(
            f"| {r['slug']} | {r['issues_count']} | {r['project_count']} | {status} | {errors} |\n"
        )

    md_path.write_text("".join(lines), "utf-8")
    print(f"Wrote sync summary to {summary_path} and {md_path}")


def main():
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        print("Missing GH_TOKEN environment variable", file=sys.stderr)
        sys.exit(2)

    catalog_path = REPO_ROOT / os.environ.get("APPS_CATALOG", "integrations/apps.yml")
    if not catalog_path.exists():
        print(f"Apps catalog not found: {catalog_path}", file=sys.stderr)
        sys.exit(2)

    cfg = load_yaml(catalog_path)
    apps = cfg.get("apps", [])
    settings = cfg.get("settings", {}).get("backlog", {})

    print(f"Found {len(apps)} apps in catalog")

    # Sync each app
    results = []
    for app in apps:
        slug = app["slug"]
        print(f"\n=== Syncing {slug} ===")
        result = sync_app_backlog(app, token, settings)
        results.append(result)

        if result["issues_synced"]:
            print(f"  Issues: {result['issues_count']} items")
        if result["project_synced"]:
            print(f"  Project: {result['project_count']} items")
        if result["errors"]:
            print(f"  Errors: {', '.join(result['errors'])}")

    # Write sync summary
    write_sync_summary(results, settings)

    # Run aggregate validation and diff
    print("\n=== Running aggregate validation ===")

    # Set up environment for validate_and_diff
    validate_env = {
        "BACKLOG_EXPORT_VALIDATE_STRICT": os.environ.get("BACKLOG_EXPORT_VALIDATE_STRICT", "1"),
        "BACKLOG_DIFF_MAX_ITEMS": os.environ.get("BACKLOG_DIFF_MAX_ITEMS", "20"),
    }

    allowlist = settings.get("project_field_allowlist", [])
    if allowlist:
        validate_env["BACKLOG_PROJECT_FIELD_ALLOWLIST"] = ",".join(allowlist)

    # Check if validate script exists
    validate_script = REPO_ROOT / "scripts/backlog_export/validate_and_diff.py"
    if validate_script.exists():
        run_script("scripts/backlog_export/validate_and_diff.py", validate_env)
    else:
        print("Skipping validate_and_diff.py (script not found)")

    # Report final status
    failed = sum(1 for r in results if r["errors"])
    if failed > 0:
        print(f"\n{failed} app(s) had sync errors")
        sys.exit(1)

    print(f"\nSync complete: {len(results)} apps processed")


if __name__ == "__main__":
    main()
