#!/usr/bin/env python3
"""
Databricks GitHub Org Catalog Crawler

Recursively catalogs all repositories from the Databricks GitHub organization
for ingestion into the RAG system (Bronze layer).

Usage:
    python tools/catalog/databricks_org_catalog.py > bronze/databricks_org.json
    python tools/catalog/databricks_org_catalog.py --org OCA > bronze/oca_org.json

Output:
    JSON with repo metadata + README content for each repository.
    Feed this to the Bronze → Silver → Gold pipeline.

Environment:
    GITHUB_TOKEN - GitHub personal access token (optional, increases rate limit)
"""

import argparse
import hashlib
import json
import os
import sys
import time
from typing import Any, Generator, Optional

import requests

GITHUB_API = "https://api.github.com"
DEFAULT_ORG = "databricks"
REQUEST_TIMEOUT = 60
RATE_LIMIT_DELAY = 0.2  # seconds between requests


def get_headers() -> dict:
    """Get request headers with optional auth token."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def gh_get(url: str, params: Optional[dict] = None) -> requests.Response:
    """Make authenticated GET request to GitHub API."""
    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response


def iter_repos(org: str) -> Generator[dict, None, None]:
    """Iterate through all repositories in an organization."""
    page = 1
    while True:
        try:
            response = gh_get(
                f"{GITHUB_API}/orgs/{org}/repos",
                params={"per_page": 100, "page": page, "type": "all"},
            )
            items = response.json()
            if not items:
                break
            for item in items:
                yield item
            page += 1
            time.sleep(RATE_LIMIT_DELAY)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # Rate limited - wait and retry
                reset_time = int(e.response.headers.get("X-RateLimit-Reset", 0))
                wait_time = max(reset_time - int(time.time()), 60)
                print(f"Rate limited, waiting {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            raise


def get_readme(owner: str, repo: str) -> Optional[str]:
    """Fetch README content for a repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    headers = {**get_headers(), "Accept": "application/vnd.github.raw"}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return None


def get_docs_tree(owner: str, repo: str, default_branch: str) -> list[dict]:
    """Get list of files in /docs and /examples directories."""
    docs_files = []
    for path in ["docs", "examples"]:
        try:
            response = gh_get(
                f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": default_branch},
            )
            items = response.json()
            if isinstance(items, list):
                for item in items:
                    if item.get("type") == "file" and item.get("name", "").endswith(
                        (".md", ".rst", ".txt", ".ipynb")
                    ):
                        docs_files.append(
                            {
                                "path": item["path"],
                                "name": item["name"],
                                "size": item.get("size", 0),
                                "download_url": item.get("download_url"),
                            }
                        )
        except requests.exceptions.HTTPError:
            continue
    return docs_files


def stable_hash(data: str) -> str:
    """Generate stable SHA-256 hash of content."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def catalog_org(org: str, include_docs: bool = False) -> dict:
    """Catalog all repositories in an organization."""
    repos = []
    skipped = 0

    for repo in iter_repos(org):
        name = repo["name"]
        default_branch = repo.get("default_branch") or "main"

        # Skip archived/disabled repos
        if repo.get("archived") or repo.get("disabled"):
            skipped += 1
            continue

        # Fetch README
        readme = get_readme(org, name)

        # Build payload
        payload = {
            "source": "github_org",
            "source_org": org,
            "repo": name,
            "full_name": repo["full_name"],
            "html_url": repo["html_url"],
            "description": repo.get("description") or "",
            "topics": repo.get("topics") or [],
            "language": repo.get("language") or "",
            "stargazers_count": repo.get("stargazers_count") or 0,
            "forks_count": repo.get("forks_count") or 0,
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "default_branch": default_branch,
            "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
            "readme_md": readme or "",
        }

        # Optionally include docs tree
        if include_docs:
            payload["docs_files"] = get_docs_tree(org, name, default_branch)

        # Compute content hash for deduplication
        payload["content_hash"] = stable_hash(json.dumps(payload, sort_keys=True))

        repos.append(payload)
        print(f"Cataloged: {org}/{name}", file=sys.stderr)
        time.sleep(RATE_LIMIT_DELAY)

    return {
        "org": org,
        "count": len(repos),
        "skipped": skipped,
        "cataloged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repos": repos,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Catalog GitHub org repositories for RAG ingestion"
    )
    parser.add_argument(
        "--org",
        default=DEFAULT_ORG,
        help=f"GitHub organization to catalog (default: {DEFAULT_ORG})",
    )
    parser.add_argument(
        "--include-docs",
        action="store_true",
        help="Include docs/examples file listings (slower)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    # Catalog the org
    result = catalog_org(args.org, include_docs=args.include_docs)

    # Output
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Wrote {result['count']} repos to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
