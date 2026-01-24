#!/usr/bin/env python3
"""
FigJam Feature Map Sync

Syncs feature cards from FigJam to GitHub Issues.
Creates/updates issues based on standardized naming convention: FM-###: Feature Name

Usage:
    FIGMA_TOKEN=xxx FIGMA_FILE_KEY=xxx GITHUB_TOKEN=xxx GITHUB_OWNER=xxx GITHUB_REPO=xxx \
    python scripts/figma/figma_featuremap_sync.py

Environment Variables:
    FIGMA_TOKEN     - Figma personal access token
    FIGMA_FILE_KEY  - FigJam file key (from URL)
    GITHUB_TOKEN    - GitHub personal access token
    GITHUB_OWNER    - GitHub repository owner
    GITHUB_REPO     - GitHub repository name
"""

import os
import re
import json
import time
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(2)

# ============================================================================
# CONFIGURATION
# ============================================================================

FIGMA_TOKEN = os.environ.get("FIGMA_TOKEN")
FIGMA_FILE_KEY = os.environ.get("FIGMA_FILE_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER")
GITHUB_REPO = os.environ.get("GITHUB_REPO")

# Feature card naming pattern: FM-001: Feature Title
FEATURE_RE = re.compile(r"^(FM-\d+)\s*:\s*(.+)$", re.IGNORECASE)

# ============================================================================
# VALIDATION
# ============================================================================

def validate_env():
    """Validate required environment variables."""
    missing = []
    if not FIGMA_TOKEN:
        missing.append("FIGMA_TOKEN")
    if not FIGMA_FILE_KEY:
        missing.append("FIGMA_FILE_KEY")
    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not GITHUB_OWNER:
        missing.append("GITHUB_OWNER")
    if not GITHUB_REPO:
        missing.append("GITHUB_REPO")

    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(2)

# ============================================================================
# FIGMA API
# ============================================================================

def figma_get_file() -> dict[str, Any]:
    """Fetch the Figma/FigJam file."""
    url = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}"
    headers = {"X-Figma-Token": FIGMA_TOKEN}

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()

def walk_nodes(node: dict[str, Any], results: list[dict[str, Any]]) -> None:
    """Recursively walk Figma document tree and collect nodes."""
    if isinstance(node, dict):
        name = node.get("name", "")
        if name:
            results.append({
                "id": node.get("id"),
                "name": name,
                "type": node.get("type"),
            })

        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                walk_nodes(child, results)

# ============================================================================
# GITHUB API
# ============================================================================

def gh_headers() -> dict[str, str]:
    """Get GitHub API headers."""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def gh_search_issue(key: str) -> dict[str, Any] | None:
    """Search for existing issue by feature key."""
    query = f'repo:{GITHUB_OWNER}/{GITHUB_REPO} "{key}" in:title'
    url = "https://api.github.com/search/issues"

    response = requests.get(
        url,
        headers=gh_headers(),
        params={"q": query},
        timeout=60,
    )
    response.raise_for_status()

    items = response.json().get("items", [])
    return items[0] if items else None

def gh_create_issue(title: str, body: str, labels: list[str]) -> dict[str, Any]:
    """Create a new GitHub issue."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"

    response = requests.post(
        url,
        headers=gh_headers(),
        json={"title": title, "body": body, "labels": labels},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

def gh_update_issue(
    number: int, title: str, body: str, labels: list[str]
) -> dict[str, Any]:
    """Update an existing GitHub issue."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues/{number}"

    response = requests.patch(
        url,
        headers=gh_headers(),
        json={"title": title, "body": body, "labels": labels},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main sync function."""
    validate_env()

    print(f"Fetching FigJam file: {FIGMA_FILE_KEY}")
    file_data = figma_get_file()
    file_name = file_data.get("name", "Unknown")
    print(f"File name: {file_name}")

    # Walk document tree
    nodes: list[dict[str, Any]] = []
    walk_nodes(file_data.get("document", {}), nodes)
    print(f"Found {len(nodes)} nodes")

    # Extract features
    features: list[dict[str, Any]] = []
    for node in nodes:
        match = FEATURE_RE.match(node["name"].strip())
        if match:
            key = match.group(1).upper()
            title = match.group(2).strip()
            features.append({
                "key": key,
                "title": title,
                "figma_node_id": node["id"],
                "figma_type": node["type"],
            })

    print(f"Found {len(features)} feature cards")

    if not features:
        print("No features found matching pattern 'FM-###: Title'")
        print(json.dumps({"synced": [], "message": "No features found"}, indent=2))
        return

    # Sync to GitHub
    results: list[dict[str, Any]] = []

    for feature in sorted(features, key=lambda x: x["key"]):
        key = feature["key"]
        issue_title = f"{key}: {feature['title']}"

        body = f"""## Source: FigJam Feature Map

- **Figma file:** https://www.figma.com/file/{FIGMA_FILE_KEY}
- **Node ID:** {feature['figma_node_id']}
- **Node type:** {feature['figma_type']}

---

## Release Evidence

- [ ] Spec bundle created (`spec/{key.lower()}/`)
- [ ] Design contract exported
- [ ] Implementation complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Deployed to production

## Notes

_Synced automatically from FigJam feature map._
"""

        labels = ["type:feature", "source:figma"]

        # Check if issue exists
        existing = gh_search_issue(key)

        try:
            if existing:
                number = existing["number"]
                result = gh_update_issue(number, issue_title, body, labels)
                results.append({
                    "key": key,
                    "action": "updated",
                    "issue_number": number,
                    "issue_url": result["html_url"],
                })
                print(f"  Updated: {key} -> #{number}")
            else:
                result = gh_create_issue(issue_title, body, labels)
                results.append({
                    "key": key,
                    "action": "created",
                    "issue_number": result["number"],
                    "issue_url": result["html_url"],
                })
                print(f"  Created: {key} -> #{result['number']}")

            # Rate limit protection
            time.sleep(0.5)

        except requests.HTTPError as e:
            results.append({
                "key": key,
                "action": "error",
                "error": str(e),
            })
            print(f"  Error: {key} - {e}")

    # Output report
    report = {
        "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "figma_file": FIGMA_FILE_KEY,
        "github_repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "features_found": len(features),
        "synced": results,
    }

    print("\n" + json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
