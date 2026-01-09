#!/usr/bin/env python3
"""
whats_deployed.py - Generate deterministic "What's Deployed" inventory from GitHub APIs

Uses GitHub REST + GraphQL APIs exclusively. No local git history.
All API responses saved as proof files for reproducibility.

Usage:
    export GITHUB_TOKEN=ghp_...
    python scripts/whats_deployed.py

Environment Variables:
    GITHUB_TOKEN (required): GitHub PAT or App token with repo + actions:read
    GITHUB_OWNER (default: jgtolentino): Repository owner
    GITHUB_REPO (default: odoo-ce): Repository name
    PROD_ENV (default: production): Deployment environment name
    RELEASE_TAG_PREFIX (default: prod-): Release tag prefix to match
    WORKFLOW_NAME_HINT (default: Deploy to Production): Workflow name pattern
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configuration from environment
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "jgtolentino")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "odoo-ce")
PROD_ENV = os.environ.get("PROD_ENV", "production")
RELEASE_TAG_PREFIX = os.environ.get("RELEASE_TAG_PREFIX", "prod-")
WORKFLOW_NAME_HINT = os.environ.get("WORKFLOW_NAME_HINT", "Deploy to Production")

# API endpoints
REST_API = "https://api.github.com"
GRAPHQL_API = "https://api.github.com/graphql"

# Output paths
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
RELEASES_DIR = REPO_ROOT / "docs" / "releases"
PROOFS_DIR = RELEASES_DIR / "DEPLOYMENT_PROOFS"


def make_request(
    url: str,
    method: str = "GET",
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> tuple[int, dict | list | str]:
    """Make HTTP request to GitHub API."""
    default_headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "whats_deployed.py",
    }
    if GITHUB_TOKEN:
        default_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    if headers:
        default_headers.update(headers)

    request_data = None
    if data:
        request_data = json.dumps(data).encode("utf-8")
        default_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=request_data, headers=default_headers, method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            try:
                return response.status, json.loads(body)
            except json.JSONDecodeError:
                return response.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": str(e), "body": body}
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}


def rest_get(endpoint: str) -> tuple[int, Any]:
    """GET request to GitHub REST API."""
    url = f"{REST_API}{endpoint}"
    return make_request(url)


def graphql_query(query: str, variables: Optional[dict] = None) -> tuple[int, Any]:
    """Execute GraphQL query."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return make_request(GRAPHQL_API, method="POST", data=payload)


def save_proof(filename: str, data: Any) -> Path:
    """Save API response as proof file."""
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PROOFS_DIR / filename
    with open(filepath, "w") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, indent=2, sort_keys=True)
        else:
            f.write(str(data))
    return filepath


def redact_sensitive(data: dict) -> dict:
    """Redact sensitive URLs from data for output."""
    result = json.loads(json.dumps(data))  # Deep copy

    def redact_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "REDACTED"
                if k in ("archive_download_url", "upload_url") and v
                else redact_recursive(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [redact_recursive(item) for item in obj]
        return obj

    return redact_recursive(result)


def classify_area(filepath: str) -> str:
    """Classify file path into area category."""
    if filepath.startswith("supabase/"):
        return "supabase"
    if filepath.startswith(("addons/", "odoo/")):
        return "odoo"
    if filepath.startswith(("infra/", "services/", "docker/", "deploy/")):
        return "infra"
    if filepath.startswith(".github/workflows/"):
        return "ci"
    if filepath.startswith("docs/"):
        return "docs"
    return "unknown"


def get_latest_release() -> tuple[Optional[dict], list[str]]:
    """Fetch latest release from GitHub API."""
    unverified = []
    status, data = rest_get(f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest")

    if status != 200:
        unverified.append(f"latest_release: API returned {status}")
        return None, unverified

    save_proof("api_release_latest.json", data)
    return data, unverified


def get_previous_release(current_tag: str) -> tuple[Optional[str], list[str]]:
    """Find previous release with same prefix."""
    unverified = []
    status, data = rest_get(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases?per_page=100"
    )

    if status != 200:
        unverified.append(f"releases_list: API returned {status}")
        return None, unverified

    # Find releases matching prefix, excluding current
    matching = [
        r
        for r in data
        if r.get("tag_name", "").startswith(RELEASE_TAG_PREFIX)
        and r.get("tag_name") != current_tag
    ]

    if not matching:
        unverified.append("previous_release: No matching releases found")
        return None, unverified

    # Sort by published_at descending
    matching.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    return matching[0].get("tag_name"), unverified


def get_compare(base: str, head: str) -> tuple[Optional[dict], list[str]]:
    """Get comparison between two refs."""
    unverified = []
    status, data = rest_get(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/compare/{base}...{head}"
    )

    if status != 200:
        unverified.append(f"compare: API returned {status} for {base}...{head}")
        return None, unverified

    save_proof("api_compare.json", data)

    # Check for truncation
    if data.get("total_commits", 0) > 250:
        unverified.append(
            f"compare: Commits truncated ({data.get('total_commits')} total, showing 250)"
        )

    return data, unverified


def get_workflow_runs(head_sha: str, published_at: str) -> tuple[Optional[dict], list[str]]:
    """Find deployment workflow run matching the release."""
    unverified = []
    status, data = rest_get(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs?per_page=50"
    )

    if status != 200:
        unverified.append(f"workflow_runs: API returned {status}")
        return None, unverified

    save_proof("api_workflow_runs.json", data)

    runs = data.get("workflow_runs", [])
    workflow_hints = [
        WORKFLOW_NAME_HINT.lower(),
        "deploy",
        "production",
        "release",
    ]

    # Find matching run by head_sha first
    for run in runs:
        run_name = (run.get("name") or "").lower()
        workflow_name = (run.get("workflow", {}).get("name") or run.get("path") or "").lower()
        if run.get("head_sha") == head_sha:
            if any(hint in run_name or hint in workflow_name for hint in workflow_hints):
                save_proof(f"api_workflow_run_{run['id']}.json", run)
                return run, unverified

    # Fallback: find by time proximity to published_at
    if published_at:
        try:
            pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            for run in runs:
                run_time_str = run.get("created_at", "")
                if run_time_str:
                    run_time = datetime.fromisoformat(run_time_str.replace("Z", "+00:00"))
                    time_diff = abs((pub_time - run_time).total_seconds())
                    # Within 30 minutes
                    if time_diff < 1800:
                        run_name = (run.get("name") or "").lower()
                        if any(hint in run_name for hint in workflow_hints):
                            save_proof(f"api_workflow_run_{run['id']}.json", run)
                            unverified.append(
                                f"workflow_run: Matched by time proximity ({int(time_diff)}s diff)"
                            )
                            return run, unverified
        except (ValueError, TypeError):
            pass

    unverified.append("workflow_run: No matching deployment workflow found")
    return None, unverified


def get_artifacts(run_id: int) -> tuple[list[dict], list[str]]:
    """Get artifacts for a workflow run."""
    unverified = []
    status, data = rest_get(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}/artifacts"
    )

    if status != 200:
        unverified.append(f"artifacts: API returned {status}")
        return [], unverified

    save_proof("artifacts_index.json", data)
    return data.get("artifacts", []), unverified


def get_deployments() -> tuple[list[dict], list[str]]:
    """Get deployments for production environment."""
    unverified = []
    status, data = rest_get(
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/deployments?environment={PROD_ENV}&per_page=50"
    )

    if status == 200 and isinstance(data, list):
        save_proof("api_deployments.json", data)
        return data, unverified
    else:
        # Deployments API may not be enabled
        unverified.append(f"deployments: API returned {status} (may not be enabled)")
        save_proof("api_deployments.json", {"error": f"API returned {status}", "data": data})
        return [], unverified


def get_commits_prs_graphql(commit_shas: list[str]) -> tuple[list[dict], list[str]]:
    """Use GraphQL to map commits to associated PRs."""
    unverified = []

    if not commit_shas:
        return [], unverified

    # Limit to 100 commits per query to avoid complexity limits
    shas_to_query = commit_shas[:100]
    if len(commit_shas) > 100:
        unverified.append(f"graphql_commits: Truncated to 100 of {len(commit_shas)} commits")

    # Build GraphQL query with aliases for each commit
    commit_fragments = []
    for i, sha in enumerate(shas_to_query):
        commit_fragments.append(f"""
        commit{i}: object(oid: "{sha}") {{
          ... on Commit {{
            oid
            messageHeadline
            committedDate
            author {{
              name
              user {{
                login
              }}
            }}
            associatedPullRequests(first: 5) {{
              nodes {{
                number
                title
                url
                mergedAt
                labels(first: 10) {{
                  nodes {{
                    name
                  }}
                }}
                author {{
                  login
                }}
                changedFiles
                additions
                deletions
                mergeCommit {{
                  oid
                }}
              }}
            }}
          }}
        }}
        """)

    query = f"""
    query {{
      repository(owner: "{GITHUB_OWNER}", name: "{GITHUB_REPO}") {{
        {"".join(commit_fragments)}
      }}
    }}
    """

    status, data = graphql_query(query)

    if status != 200:
        unverified.append(f"graphql: API returned {status}")
        save_proof("graphql_commits_prs.json", {"error": status, "data": data})
        return [], unverified

    if "errors" in data:
        unverified.append(f"graphql: Query errors - {data['errors']}")
        save_proof("graphql_commits_prs.json", data)
        return [], unverified

    save_proof("graphql_commits_prs.json", data)

    # Parse results
    commits_data = []
    repo_data = data.get("data", {}).get("repository", {})
    for i, sha in enumerate(shas_to_query):
        commit_obj = repo_data.get(f"commit{i}")
        if commit_obj:
            author_name = commit_obj.get("author", {}).get("name", "")
            author_login = (
                commit_obj.get("author", {}).get("user", {}) or {}
            ).get("login", "")

            prs = []
            for pr_node in (
                commit_obj.get("associatedPullRequests", {}).get("nodes", []) or []
            ):
                if pr_node and pr_node.get("mergedAt"):
                    prs.append({
                        "number": pr_node.get("number"),
                        "title": pr_node.get("title"),
                        "url": pr_node.get("url"),
                        "merged_at": pr_node.get("mergedAt"),
                        "labels": [
                            l.get("name")
                            for l in (pr_node.get("labels", {}).get("nodes", []) or [])
                            if l
                        ],
                        "author": (pr_node.get("author") or {}).get("login", ""),
                        "changed_files": pr_node.get("changedFiles"),
                        "additions": pr_node.get("additions"),
                        "deletions": pr_node.get("deletions"),
                        "merge_commit_sha": (pr_node.get("mergeCommit") or {}).get("oid"),
                    })

            commits_data.append({
                "sha": commit_obj.get("oid"),
                "message_headline": commit_obj.get("messageHeadline"),
                "author": author_login or author_name or "UNVERIFIED",
                "committer_date": commit_obj.get("committedDate"),
                "associated_prs": prs,
            })

    return commits_data, unverified


def build_output(
    release: Optional[dict],
    prev_tag: Optional[str],
    compare: Optional[dict],
    workflow_run: Optional[dict],
    artifacts: list[dict],
    commits_prs: list[dict],
    all_unverified: list[str],
) -> dict:
    """Build the final WHAT_DEPLOYED.json structure."""
    generated_at = datetime.now(timezone.utc).isoformat()

    # Build production section
    production = {}
    if release:
        production["release"] = {
            "tag": release.get("tag_name"),
            "name": release.get("name"),
            "published_at": release.get("published_at"),
            "target_commitish": release.get("target_commitish"),
            "html_url": release.get("html_url"),
            "evidence": "DEPLOYMENT_PROOFS/api_release_latest.json",
        }
        production["head_sha"] = release.get("target_commitish")
    else:
        production["release"] = None
        production["head_sha"] = "UNVERIFIED"

    production["previous_release_tag"] = prev_tag or "UNVERIFIED"

    if compare:
        production["compare"] = {
            "base": compare.get("base_commit", {}).get("sha", "")[:7],
            "head": compare.get("merge_base_commit", {}).get("sha", "")[:7],
            "commits": len(compare.get("commits", [])),
            "files": len(compare.get("files", [])),
            "html_url": compare.get("html_url"),
            "evidence": "DEPLOYMENT_PROOFS/api_compare.json",
        }
    else:
        production["compare"] = None

    if workflow_run:
        production["workflow_run"] = {
            "id": workflow_run.get("id"),
            "name": workflow_run.get("name"),
            "status": workflow_run.get("status"),
            "conclusion": workflow_run.get("conclusion"),
            "created_at": workflow_run.get("created_at"),
            "updated_at": workflow_run.get("updated_at"),
            "html_url": workflow_run.get("html_url"),
            "evidence": f"DEPLOYMENT_PROOFS/api_workflow_run_{workflow_run.get('id')}.json",
        }
    else:
        production["workflow_run"] = None

    production["artifacts"] = [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "size_in_bytes": a.get("size_in_bytes"),
            "expired": a.get("expired"),
            "archive_download_url": "REDACTED",
            "evidence": "DEPLOYMENT_PROOFS/artifacts_index.json",
        }
        for a in artifacts
    ]

    # Build changes section
    # Get unique PRs from commits
    seen_pr_numbers = set()
    unique_prs = []
    for commit in commits_prs:
        for pr in commit.get("associated_prs", []):
            if pr.get("number") not in seen_pr_numbers:
                seen_pr_numbers.add(pr.get("number"))
                unique_prs.append(pr)

    # Sort PRs by number descending
    unique_prs.sort(key=lambda p: p.get("number", 0), reverse=True)

    # Sort commits by date ascending
    commits_sorted = sorted(
        commits_prs, key=lambda c: c.get("committer_date", "")
    )

    # Classify PR areas based on compare files
    files_by_area = {}
    if compare:
        for f in compare.get("files", []):
            area = classify_area(f.get("filename", ""))
            if area not in files_by_area:
                files_by_area[area] = []
            files_by_area[area].append(f.get("filename"))

    # Attach areas to PRs (inferred from file changes)
    for pr in unique_prs:
        pr["areas"] = list(files_by_area.keys()) if files_by_area else ["unknown"]
        pr["files_changed"] = pr.get("changed_files", 0)

    changes = {
        "commits": commits_sorted,
        "prs": unique_prs,
    }

    return {
        "generated_at": generated_at,
        "repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "production": production,
        "changes": changes,
        "unverified": all_unverified,
    }


def generate_markdown(data: dict, compare: Optional[dict]) -> str:
    """Generate WHAT_DEPLOYED.md from data."""
    lines = []
    prod = data.get("production", {})
    changes = data.get("changes", {})

    # Header
    lines.append("# What's Deployed")
    lines.append("")
    lines.append(f"**Generated:** {data.get('generated_at')}")
    lines.append(f"**Repository:** [{data.get('repo')}](https://github.com/{data.get('repo')})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Production Release Summary
    lines.append("## Production Release")
    lines.append("")
    release = prod.get("release")
    if release:
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| **Tag** | `{release.get('tag')}` |")
        lines.append(f"| **Name** | {release.get('name')} |")
        lines.append(f"| **Published** | {release.get('published_at')} |")
        lines.append(f"| **Commit** | `{release.get('target_commitish')}` |")
        lines.append(f"| **URL** | [{release.get('tag')}]({release.get('html_url')}) |")
        lines.append(f"| **Previous Tag** | `{prod.get('previous_release_tag')}` |")
    else:
        lines.append("*No release data available*")
    lines.append("")

    # Workflow Run
    lines.append("### Deployment Workflow")
    lines.append("")
    wf = prod.get("workflow_run")
    if wf:
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| **Run ID** | [{wf.get('id')}]({wf.get('html_url')}) |")
        lines.append(f"| **Name** | {wf.get('name')} |")
        lines.append(f"| **Status** | {wf.get('status')} |")
        lines.append(f"| **Conclusion** | {wf.get('conclusion')} |")
        lines.append(f"| **Created** | {wf.get('created_at')} |")
    else:
        lines.append("*No deployment workflow found*")
    lines.append("")

    # Evidence
    lines.append("---")
    lines.append("")
    lines.append("## Evidence Files")
    lines.append("")
    lines.append("All API responses saved in `DEPLOYMENT_PROOFS/`:")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `api_release_latest.json` | Latest release metadata |")
    lines.append("| `api_compare.json` | Commit comparison between tags |")
    lines.append("| `api_workflow_runs.json` | Recent workflow runs |")
    if wf:
        lines.append(f"| `api_workflow_run_{wf.get('id')}.json` | Deployment workflow details |")
    lines.append("| `artifacts_index.json` | Workflow artifacts list |")
    lines.append("| `graphql_commits_prs.json` | Commit-to-PR mapping |")
    lines.append("| `api_deployments.json` | Environment deployments |")
    lines.append("")

    # Changes Summary
    lines.append("---")
    lines.append("")
    lines.append("## What Changed Since Previous Tag")
    lines.append("")
    comp = prod.get("compare")
    if comp:
        lines.append(
            f"**Comparing:** `{comp.get('base')}` → `{comp.get('head')}` "
            f"([view diff]({comp.get('html_url')}))"
        )
        lines.append(f"- **Commits:** {comp.get('commits')}")
        lines.append(f"- **Files Changed:** {comp.get('files')}")
    lines.append("")

    # PRs by Area
    prs = changes.get("prs", [])
    if prs:
        # Group by area
        prs_by_area = {}
        for pr in prs:
            for area in pr.get("areas", ["unknown"]):
                if area not in prs_by_area:
                    prs_by_area[area] = []
                prs_by_area[area].append(pr)

        for area in ["odoo", "supabase", "infra", "ci", "docs", "unknown"]:
            if area in prs_by_area:
                lines.append(f"### {area.title()} Changes")
                lines.append("")
                for pr in prs_by_area[area]:
                    labels = ", ".join(pr.get("labels", [])) or "none"
                    lines.append(
                        f"- **[#{pr.get('number')}]({pr.get('url')})** {pr.get('title')} "
                        f"(by @{pr.get('author')}, labels: {labels})"
                    )
                lines.append("")
    else:
        lines.append("*No PRs found in this release*")
        lines.append("")

    # Supabase Impact
    lines.append("---")
    lines.append("")
    lines.append("## Supabase Impact")
    lines.append("")
    supabase_files = []
    if compare:
        supabase_files = [
            f.get("filename")
            for f in compare.get("files", [])
            if f.get("filename", "").startswith("supabase/")
        ]
    if supabase_files:
        lines.append(f"**{len(supabase_files)} file(s) changed:**")
        lines.append("")
        for f in supabase_files[:20]:
            lines.append(f"- `{f}`")
        if len(supabase_files) > 20:
            lines.append(f"- ... and {len(supabase_files) - 20} more")
    else:
        lines.append("*No Supabase changes detected (proven by compare file list)*")
    lines.append("")

    # Odoo Impact
    lines.append("---")
    lines.append("")
    lines.append("## Odoo Impact")
    lines.append("")
    odoo_files = []
    if compare:
        odoo_files = [
            f.get("filename")
            for f in compare.get("files", [])
            if f.get("filename", "").startswith(("addons/", "odoo/", "deploy/"))
        ]
    if odoo_files:
        # Group by module
        modules = set()
        for f in odoo_files:
            parts = f.split("/")
            if len(parts) >= 3 and parts[0] == "addons":
                modules.add(f"{parts[1]}/{parts[2]}")
            elif len(parts) >= 2:
                modules.add(parts[1])

        lines.append(f"**{len(odoo_files)} file(s) changed across {len(modules)} module(s):**")
        lines.append("")
        for m in sorted(modules)[:30]:
            lines.append(f"- `{m}`")
        if len(modules) > 30:
            lines.append(f"- ... and {len(modules) - 30} more modules")
    else:
        lines.append("*No Odoo changes detected*")
    lines.append("")

    # Infra Impact
    lines.append("---")
    lines.append("")
    lines.append("## Infra Impact")
    lines.append("")
    infra_files = []
    if compare:
        infra_files = [
            f.get("filename")
            for f in compare.get("files", [])
            if f.get("filename", "").startswith(("infra/", "docker/", "services/"))
        ]
    if infra_files:
        lines.append(f"**{len(infra_files)} file(s) changed:**")
        lines.append("")
        for f in infra_files[:15]:
            lines.append(f"- `{f}`")
        if len(infra_files) > 15:
            lines.append(f"- ... and {len(infra_files) - 15} more")
    else:
        lines.append("*No infra changes detected*")
    lines.append("")

    # Unverified
    lines.append("---")
    lines.append("")
    lines.append("## UNVERIFIED Items")
    lines.append("")
    unverified = data.get("unverified", [])
    if unverified:
        lines.append("The following items could not be proven from API responses:")
        lines.append("")
        for item in unverified:
            lines.append(f"- {item}")
    else:
        lines.append("*All items verified from GitHub API responses*")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `scripts/whats_deployed.py` using GitHub REST + GraphQL APIs*")

    return "\n".join(lines)


def main():
    """Main entry point."""
    print("=" * 60)
    print("What's Deployed - GitHub API Inventory Generator")
    print("=" * 60)
    print(f"Repository: {GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"Tag Prefix: {RELEASE_TAG_PREFIX}")
    print(f"Workflow Hint: {WORKFLOW_NAME_HINT}")
    print("")

    if not GITHUB_TOKEN:
        print("WARNING: GITHUB_TOKEN not set - API rate limits will apply")
        print("")

    all_unverified = []

    # Ensure output directories exist
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Get latest release
    print("[1/7] Fetching latest release...")
    release, unv = get_latest_release()
    all_unverified.extend(unv)
    if release:
        print(f"      Found: {release.get('tag_name')} ({release.get('published_at')})")
    else:
        print("      ERROR: Could not fetch latest release")
        # Create minimal output
        data = build_output(None, None, None, None, [], [], all_unverified)
        save_proof("api_release_latest.json", {"error": "Not found"})

    # 2. Find previous release
    print("[2/7] Finding previous release...")
    prev_tag = None
    if release:
        prev_tag, unv = get_previous_release(release.get("tag_name", ""))
        all_unverified.extend(unv)
        if prev_tag:
            print(f"      Found: {prev_tag}")
        else:
            print("      Not found (may be first release)")

    # 3. Get comparison
    print("[3/7] Fetching commit comparison...")
    compare = None
    if release and prev_tag:
        compare, unv = get_compare(prev_tag, release.get("tag_name", ""))
        all_unverified.extend(unv)
        if compare:
            print(
                f"      {len(compare.get('commits', []))} commits, "
                f"{len(compare.get('files', []))} files changed"
            )
    elif release:
        # Compare with default branch
        compare, unv = get_compare("main", release.get("tag_name", ""))
        all_unverified.extend(unv)
        all_unverified.append("compare: Using main as base (no previous release tag)")

    # 4. Get workflow runs
    print("[4/7] Finding deployment workflow run...")
    workflow_run = None
    if release:
        workflow_run, unv = get_workflow_runs(
            release.get("target_commitish", ""),
            release.get("published_at", ""),
        )
        all_unverified.extend(unv)
        if workflow_run:
            print(f"      Found: Run #{workflow_run.get('id')} ({workflow_run.get('conclusion')})")
        else:
            print("      Not found")

    # 5. Get artifacts
    print("[5/7] Fetching workflow artifacts...")
    artifacts = []
    if workflow_run:
        artifacts, unv = get_artifacts(workflow_run.get("id"))
        all_unverified.extend(unv)
        print(f"      Found: {len(artifacts)} artifact(s)")
    else:
        save_proof("artifacts_index.json", {"artifacts": [], "total_count": 0})

    # 6. Get deployments (optional)
    print("[6/7] Fetching deployments...")
    deployments, unv = get_deployments()
    all_unverified.extend(unv)
    print(f"      Found: {len(deployments)} deployment(s)")

    # 7. Get commits->PRs via GraphQL
    print("[7/7] Mapping commits to PRs via GraphQL...")
    commits_prs = []
    if compare:
        commit_shas = [c.get("sha") for c in compare.get("commits", []) if c.get("sha")]
        commits_prs, unv = get_commits_prs_graphql(commit_shas)
        all_unverified.extend(unv)
        print(f"      Mapped: {len(commits_prs)} commits")
    else:
        save_proof("graphql_commits_prs.json", {"data": None, "note": "No compare data"})

    # Build output
    print("")
    print("Building output files...")
    data = build_output(
        release, prev_tag, compare, workflow_run, artifacts, commits_prs, all_unverified
    )

    # Write JSON
    json_path = RELEASES_DIR / "WHAT_DEPLOYED.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    print(f"  Wrote: {json_path}")

    # Write Markdown
    md_content = generate_markdown(data, compare)
    md_path = RELEASES_DIR / "WHAT_DEPLOYED.md"
    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"  Wrote: {md_path}")

    # Summary
    print("")
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("")
    print("Output files:")
    print(f"  - {RELEASES_DIR / 'WHAT_DEPLOYED.md'}")
    print(f"  - {RELEASES_DIR / 'WHAT_DEPLOYED.json'}")
    print(f"  - {PROOFS_DIR}/ (proof files)")
    print("")

    if all_unverified:
        print(f"UNVERIFIED items ({len(all_unverified)}):")
        for item in all_unverified:
            print(f"  - {item}")
    else:
        print("All items verified from API responses.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
