#!/usr/bin/env python3
"""
GitHub Infrastructure Discovery

Discovers GitHub repositories, workflows, and related resources.
"""

import logging
import os
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"


def discover_github(orchestrator) -> Dict[str, Any]:
    """
    Discover GitHub infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    token = os.environ.get("GITHUB_TOKEN")
    repos = os.environ.get("GITHUB_REPOS", "jgtolentino/odoo-ce").split(",")

    if not token:
        logger.warning("GITHUB_TOKEN not set, skipping GitHub discovery")
        return {"skipped": True, "reason": "GITHUB_TOKEN not set"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    discovered = {"repos": 0, "workflows": 0, "branches": 0}

    try:
        for repo_full_name in repos:
            repo_full_name = repo_full_name.strip()
            if not repo_full_name:
                continue

            # Get repository info
            repo_resp = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}", headers=headers
            )

            if repo_resp.status_code != 200:
                logger.warning(
                    f"Could not fetch repo {repo_full_name}: {repo_resp.status_code}"
                )
                continue

            repo = repo_resp.json()

            # Create repository node
            repo_node_id = orchestrator.upsert_node(
                kind="github_repo",
                key=f"github:repo:{repo['id']}",
                label=repo["full_name"],
                attrs={
                    "github_id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "owner": repo["owner"]["login"],
                    "private": repo["private"],
                    "default_branch": repo["default_branch"],
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "html_url": repo["html_url"],
                },
            )
            discovered["repos"] += 1

            # Get workflows
            workflows_resp = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}/actions/workflows",
                headers=headers,
            )

            if workflows_resp.status_code == 200:
                workflows = workflows_resp.json().get("workflows", [])

                for workflow in workflows:
                    workflow_node_id = orchestrator.upsert_node(
                        kind="github_workflow",
                        key=f"github:workflow:{workflow['id']}",
                        label=workflow["name"],
                        attrs={
                            "github_id": workflow["id"],
                            "name": workflow["name"],
                            "path": workflow["path"],
                            "state": workflow["state"],
                            "created_at": workflow.get("created_at"),
                            "updated_at": workflow.get("updated_at"),
                        },
                    )
                    discovered["workflows"] += 1

                    # Link workflow to repository
                    orchestrator.upsert_edge(
                        src_node_id=repo_node_id,
                        predicate="CONTAINS",
                        dst_node_id=workflow_node_id,
                        source_type="github",
                        source_ref=f"github:repo:{repo['id']}",
                    )

            # Get branches
            branches_resp = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}/branches",
                headers=headers,
                params={"per_page": 30},
            )

            if branches_resp.status_code == 200:
                branches = branches_resp.json()

                for branch in branches:
                    branch_node_id = orchestrator.upsert_node(
                        kind="github_branch",
                        key=f"github:branch:{repo['id']}:{branch['name']}",
                        label=f"{repo['name']}:{branch['name']}",
                        attrs={
                            "name": branch["name"],
                            "protected": branch.get("protected", False),
                            "sha": branch["commit"]["sha"],
                        },
                    )
                    discovered["branches"] += 1

                    # Link branch to repository
                    orchestrator.upsert_edge(
                        src_node_id=repo_node_id,
                        predicate="CONTAINS",
                        dst_node_id=branch_node_id,
                        source_type="github",
                        source_ref=f"github:repo:{repo['id']}",
                    )

            # Link to known deployment targets
            # If repo deploys to Vercel or Supabase

            # Check for supabase directory
            supabase_check = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}/contents/supabase",
                headers=headers,
            )

            if supabase_check.status_code == 200:
                # This repo has Supabase config, link to Supabase project
                supabase_node_id = orchestrator.upsert_node(
                    kind="supabase_project",
                    key="supabase:spdtwktxdalcfigzeqrz",
                    label="superset",
                    attrs={"project_ref": "spdtwktxdalcfigzeqrz"},
                )

                orchestrator.upsert_edge(
                    src_node_id=repo_node_id,
                    predicate="INTEGRATES_WITH",
                    dst_node_id=supabase_node_id,
                    source_type="github",
                    source_ref=f"github:repo:{repo['id']}:supabase",
                )

            # Check for Dockerfile
            dockerfile_check = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}/contents/Dockerfile",
                headers=headers,
            )

            if dockerfile_check.status_code == 200:
                # This repo builds Docker images
                docker_host_node_id = orchestrator.upsert_node(
                    kind="docker_host",
                    key="docker:host:production",
                    label="Docker Production",
                    attrs={},
                )

                orchestrator.upsert_edge(
                    src_node_id=repo_node_id,
                    predicate="DEPLOYS_TO",
                    dst_node_id=docker_host_node_id,
                    source_type="github",
                    source_ref=f"github:repo:{repo['id']}:dockerfile",
                )

    except requests.RequestException as e:
        logger.error(f"GitHub API error: {e}")
        discovered["error"] = str(e)

    return discovered


if __name__ == "__main__":
    # Standalone test
    class MockOrchestrator:
        def upsert_node(self, kind, key, label, attrs):
            print(f"Node: {kind}/{key} ({label})")
            return key

        def upsert_edge(self, src_node_id, predicate, dst_node_id, **kwargs):
            print(f"Edge: {src_node_id} --{predicate}--> {dst_node_id}")
            return f"{src_node_id}:{predicate}:{dst_node_id}"

    result = discover_github(MockOrchestrator())
    print(f"Result: {result}")
