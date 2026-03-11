#!/usr/bin/env python3
"""
Build snapshot manifest from collected SSOT inventory data.

Generates ssot/evidence/snapshot-manifest.json tying together
all GitHub and Vercel snapshots into one provenance record.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
GITHUB_DIR = REPO_ROOT / "ssot" / "github"
VERCEL_DIR = REPO_ROOT / "ssot" / "vercel"
REPO_DETAIL_DIR = GITHUB_DIR / "repo-details"


def count_files(directory: Path, pattern: str) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def read_json_safe(path: Path) -> dict | list:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def extract_repo_summary(repo_dir: Path) -> list[dict]:
    """Extract per-repo summary from detail files."""
    summaries = []
    for meta_file in sorted(repo_dir.glob("*.json")):
        # Only process the base repo metadata files (not .workflows.json etc)
        name = meta_file.stem
        if "." in name:
            continue

        meta = read_json_safe(meta_file)
        if not isinstance(meta, dict) or "name" not in meta:
            continue

        repo_name = meta["name"]

        # Count workflows
        wf_file = repo_dir / f"{repo_name}.workflows.json"
        wf_data = read_json_safe(wf_file)
        wf_count = len(wf_data.get("workflows", [])) if isinstance(wf_data, dict) else 0

        # Count recent runs
        runs_file = repo_dir / f"{repo_name}.workflow-runs.json"
        runs_data = read_json_safe(runs_file)
        runs_count = runs_data.get("total_count", 0) if isinstance(runs_data, dict) else 0

        # Count deployments
        deploy_file = repo_dir / f"{repo_name}.deployments.json"
        deploy_data = read_json_safe(deploy_file)
        deploy_count = len(deploy_data) if isinstance(deploy_data, list) else 0

        # Count environments
        env_file = repo_dir / f"{repo_name}.environments.json"
        env_data = read_json_safe(env_file)
        env_count = len(env_data.get("environments", [])) if isinstance(env_data, dict) else 0

        summaries.append({
            "name": repo_name,
            "default_branch": meta.get("default_branch", "main"),
            "visibility": meta.get("visibility", "unknown"),
            "workflows": wf_count,
            "recent_runs": runs_count,
            "deployments": deploy_count,
            "environments": env_count,
            "archived": meta.get("archived", False),
            "updated_at": meta.get("updated_at", ""),
        })

    return summaries


def extract_vercel_summary(vercel_dir: Path) -> dict:
    """Extract Vercel deployment summary."""
    projects = read_json_safe(vercel_dir / "projects.snapshot.json")
    deployments = read_json_safe(vercel_dir / "deployments.snapshot.json")
    aliases = read_json_safe(vercel_dir / "aliases.snapshot.json")

    if isinstance(projects, dict) and projects.get("skipped"):
        return {"skipped": True, "reason": projects.get("reason", "unknown")}

    proj_list = projects.get("projects", []) if isinstance(projects, dict) else []
    deploy_list = deployments.get("deployments", []) if isinstance(deployments, dict) else []
    alias_list = aliases if isinstance(aliases, list) else []

    return {
        "project_count": len(proj_list),
        "deployment_count": len(deploy_list),
        "alias_count": len(alias_list),
        "projects": [
            {
                "name": p.get("name", ""),
                "framework": p.get("framework", ""),
                "updated_at": p.get("updatedAt", ""),
            }
            for p in proj_list
        ],
    }


def build_manifest(
    timestamp: str,
    org: str,
    repo_count: int,
    workflow_count: int,
    vercel_projects: int,
    vercel_deployments: int,
) -> dict:
    """Build the complete snapshot manifest."""
    repo_summaries = extract_repo_summary(REPO_DETAIL_DIR)
    vercel_summary = extract_vercel_summary(VERCEL_DIR)

    # Compute aggregate stats
    total_workflows = sum(r.get("workflows", 0) for r in repo_summaries) or workflow_count
    total_deployments = sum(r.get("deployments", 0) for r in repo_summaries)
    total_environments = sum(r.get("environments", 0) for r in repo_summaries)
    archived_repos = sum(1 for r in repo_summaries if r.get("archived"))

    manifest = {
        "generated_at": timestamp,
        "generator": "scripts/ssot/snapshot_github_and_vercel.sh",
        "github_org": org,
        "summary": {
            "repo_count": repo_count or len(repo_summaries),
            "active_repos": (repo_count or len(repo_summaries)) - archived_repos,
            "archived_repos": archived_repos,
            "total_workflows": total_workflows,
            "total_github_deployments": total_deployments,
            "total_environments": total_environments,
            "vercel_project_count": vercel_summary.get("project_count", vercel_projects),
            "vercel_deployment_count": vercel_summary.get("deployment_count", vercel_deployments),
            "vercel_alias_count": vercel_summary.get("alias_count", 0),
        },
        "sources": {
            "github": [
                "org metadata",
                "org teams",
                "org members",
                "org repos",
                "repo metadata",
                "branch protection",
                "actions workflows",
                "actions workflow runs",
                "repo deployments",
                "repo environments",
                "repo releases",
                "repo tags",
            ],
            "vercel": [
                "projects",
                "deployments",
                "aliases",
            ],
        },
        "artifacts": {
            "github": {
                "org.snapshot.json": "org metadata",
                "repos.snapshot.json": "all repos in org",
                "teams.snapshot.json": "org teams",
                "members.snapshot.json": "org members",
                "repo-details/<repo>.json": "per-repo metadata",
                "repo-details/<repo>.branch-protection.json": "default branch protection",
                "repo-details/<repo>.workflows.json": "actions workflows",
                "repo-details/<repo>.workflow-runs.json": "recent workflow runs",
                "repo-details/<repo>.deployments.json": "deployment records",
                "repo-details/<repo>.environments.json": "deployment environments",
                "repo-details/<repo>.releases.json": "releases",
                "repo-details/<repo>.tags.json": "tags",
            },
            "vercel": {
                "projects.snapshot.json": "all Vercel projects",
                "deployments.snapshot.json": "recent deployments",
                "aliases.snapshot.json": "all aliases/custom domains",
            },
        },
        "repos": repo_summaries,
        "vercel": vercel_summary,
    }

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Build SSOT snapshot manifest")
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--org", required=True)
    parser.add_argument("--repo-count", type=int, default=0)
    parser.add_argument("--workflow-count", type=int, default=0)
    parser.add_argument("--vercel-projects", type=int, default=0)
    parser.add_argument("--vercel-deployments", type=int, default=0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest = build_manifest(
        timestamp=args.timestamp,
        org=args.org,
        repo_count=args.repo_count,
        workflow_count=args.workflow_count,
        vercel_projects=args.vercel_projects,
        vercel_deployments=args.vercel_deployments,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"Manifest: {output_path}")
    print(f"  Repos: {manifest['summary']['repo_count']}")
    print(f"  Workflows: {manifest['summary']['total_workflows']}")
    print(f"  GitHub Deployments: {manifest['summary']['total_github_deployments']}")
    print(f"  Vercel Projects: {manifest['summary']['vercel_project_count']}")


if __name__ == "__main__":
    main()
