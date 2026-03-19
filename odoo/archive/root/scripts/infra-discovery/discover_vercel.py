#!/usr/bin/env python3
"""
Vercel Infrastructure Discovery

Discovers Vercel projects, deployments, and domains.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

VERCEL_API_URL = "https://api.vercel.com"


def discover_vercel(orchestrator) -> Dict[str, Any]:
    """
    Discover Vercel infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    token = os.environ.get("VERCEL_TOKEN")
    team_id = os.environ.get("VERCEL_TEAM_ID")

    if not token:
        logger.warning("VERCEL_TOKEN not set, skipping Vercel discovery")
        return {"skipped": True, "reason": "VERCEL_TOKEN not set"}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    params = {}
    if team_id:
        params["teamId"] = team_id

    discovered = {"projects": 0, "domains": 0, "deployments": 0}

    try:
        # Discover projects
        projects_resp = requests.get(
            f"{VERCEL_API_URL}/v9/projects", headers=headers, params=params
        )
        projects_resp.raise_for_status()
        projects = projects_resp.json().get("projects", [])

        project_nodes = {}

        for project in projects:
            # Create project node
            node_id = orchestrator.upsert_node(
                kind="vercel_project",
                key=f"vercel:{project['id']}",
                label=project["name"],
                attrs={
                    "vercel_id": project["id"],
                    "framework": project.get("framework"),
                    "node_version": project.get("nodeVersion"),
                    "root_directory": project.get("rootDirectory"),
                    "created_at": project.get("createdAt"),
                    "updated_at": project.get("updatedAt"),
                },
            )
            project_nodes[project["id"]] = node_id
            discovered["projects"] += 1

            # Get project domains
            domains_resp = requests.get(
                f'{VERCEL_API_URL}/v9/projects/{project["id"]}/domains',
                headers=headers,
                params=params,
            )
            if domains_resp.status_code == 200:
                domains = domains_resp.json().get("domains", [])

                for domain in domains:
                    domain_node_id = orchestrator.upsert_node(
                        kind="domain",
                        key=f"domain:{domain['name']}",
                        label=domain["name"],
                        attrs={
                            "verified": domain.get("verified"),
                            "redirect": domain.get("redirect"),
                            "git_branch": domain.get("gitBranch"),
                        },
                    )
                    discovered["domains"] += 1

                    # Link domain to project
                    orchestrator.upsert_edge(
                        src_node_id=node_id,
                        predicate="EXPOSES_API",
                        dst_node_id=domain_node_id,
                        source_type="vercel",
                        source_ref=f"vercel:project:{project['id']}",
                    )

            # Get latest deployment
            deployments_resp = requests.get(
                f"{VERCEL_API_URL}/v6/deployments",
                headers=headers,
                params={**params, "projectId": project["id"], "limit": 1},
            )
            if deployments_resp.status_code == 200:
                deployments = deployments_resp.json().get("deployments", [])

                for deployment in deployments[:1]:  # Just latest
                    deploy_node_id = orchestrator.upsert_node(
                        kind="deployment",
                        key=f"vercel:deployment:{deployment['uid']}",
                        label=f"{project['name']}@{deployment.get('meta', {}).get('githubCommitSha', 'latest')[:7]}",
                        attrs={
                            "uid": deployment["uid"],
                            "url": deployment.get("url"),
                            "state": deployment.get("state"),
                            "ready_state": deployment.get("readyState"),
                            "created_at": deployment.get("createdAt"),
                        },
                    )
                    discovered["deployments"] += 1

                    # Link deployment to project
                    orchestrator.upsert_edge(
                        src_node_id=deploy_node_id,
                        predicate="DEPLOYED_FROM",
                        dst_node_id=node_id,
                        source_type="vercel",
                        source_ref=f"vercel:deployment:{deployment['uid']}",
                    )

        # Create Supabase integration edges if Supabase project exists
        supabase_node = orchestrator.upsert_node(
            kind="supabase_project",
            key="supabase:spdtwktxdalcfigzeqrz",
            label="superset",
            attrs={"project_ref": "spdtwktxdalcfigzeqrz"},
        )

        for project_id, node_id in project_nodes.items():
            orchestrator.upsert_edge(
                src_node_id=node_id,
                predicate="USES_DB",
                dst_node_id=supabase_node,
                source_type="vercel",
                source_ref=f"vercel:project:{project_id}:env",
            )

    except requests.RequestException as e:
        logger.error(f"Vercel API error: {e}")
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

    result = discover_vercel(MockOrchestrator())
    print(f"Result: {result}")
