"""
MCP Server: oca-docs
OCA (Odoo Community Association) module documentation server.

Provides three tools:
  - search_oca_modules: search OCA modules by keyword
  - get_oca_module_info: fetch README + manifest for a specific module
  - list_oca_repos: list all tracked OCA repositories

Two modes:
  1. Azure AI Search mode (production): queries srch-ipai-copilot index
  2. GitHub API mode (fallback): queries GitHub search + raw content API

Pattern follows: learn_mcp (Microsoft Learn) + pg-odoo (local MCP server).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("mcp.oca-docs")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_ORG = "OCA"
BRANCH = os.getenv("OCA_BRANCH", "18.0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE", "srch-ipai-copilot")
SEARCH_INDEX = os.getenv("OCA_DOCS_INDEX", "oca-docs-18")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
SEARCH_API_VERSION = "2024-07-01"
MAX_RESULTS = int(os.getenv("OCA_DOCS_MAX_RESULTS", "20"))

TRACKED_REPOS = {
    "account-financial-reporting": "Financial reports (MIS Builder, trial balance, aged partner)",
    "account-financial-tools": "Accounting tools (reconcile, lock dates, asset management)",
    "account-invoicing": "Invoice enhancements (blocking, refund links)",
    "account-payment": "Payment partner, modes, orders",
    "bank-statement-import": "Bank statement import (OFX, CAMT, CSV)",
    "sale-workflow": "Sale order enhancements (cancel reason, approval)",
    "sale-reporting": "Sale reporting and analytics",
    "purchase-workflow": "Purchase order enhancements (request, approval)",
    "hr": "HR modules (attendance, leave, expense)",
    "payroll": "Payroll modules",
    "project": "Project management (timeline, templates, milestones)",
    "server-tools": "Server tools (auditlog, queue_job, sentry)",
    "server-ux": "UX improvements (responsive, dialog size, ribbon)",
    "server-auth": "Authentication (TOTP, OAuth, LDAP)",
    "web": "Web UI modules (responsive, widget enhancements)",
    "rest-framework": "REST framework (FastAPI endpoints for Odoo)",
}


def _github_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


# ---------------------------------------------------------------------------
# Search backends
# ---------------------------------------------------------------------------


async def _search_azure(query: str, repo: str | None, limit: int) -> list[dict]:
    """Query Azure AI Search index for OCA docs."""
    if not SEARCH_API_KEY:
        return []

    url = (
        f"https://{SEARCH_SERVICE}.search.windows.net"
        f"/indexes/{SEARCH_INDEX}/docs/search"
        f"?api-version={SEARCH_API_VERSION}"
    )

    body: dict[str, Any] = {
        "search": query,
        "top": min(limit, MAX_RESULTS),
        "queryType": "semantic",
        "semanticConfiguration": "default",
    }
    if repo:
        body["filter"] = f"repo eq '{repo}'"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "api-key": SEARCH_API_KEY,
            },
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for doc in data.get("value", []):
        results.append(
            {
                "module": doc.get("module", ""),
                "repo": doc.get("repo", ""),
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "snippet": doc.get("content", "")[:400],
                "url": doc.get("url", ""),
                "score": doc.get("@search.score", 0),
            }
        )
    return results


async def _search_github(query: str, repo: str | None, limit: int) -> list[dict]:
    """Fallback: search OCA repos via GitHub code search."""
    results = []

    if repo:
        repos_to_search = [repo] if repo in TRACKED_REPOS else []
    else:
        repos_to_search = list(TRACKED_REPOS.keys())

    # GitHub code search across OCA org
    search_query = f"{query} org:{GITHUB_ORG}"
    if repo:
        search_query = f"{query} repo:{GITHUB_ORG}/{repo}"

    search_url = "https://api.github.com/search/code"
    params = {
        "q": f"{search_query} filename:__manifest__.py OR filename:README.rst",
        "per_page": min(limit, 30),
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            search_url, headers=_github_headers(), params=params
        )
        if resp.status_code == 403:
            # Rate limited — fall back to listing known modules
            return _list_known_modules(query, repos_to_search, limit)
        if resp.status_code != 200:
            return []

        data = resp.json()
        for item in data.get("items", [])[:limit]:
            repo_name = item.get("repository", {}).get("name", "")
            path = item.get("path", "")
            # Extract module name from path
            parts = path.split("/")
            module = parts[0] if len(parts) > 1 else repo_name
            results.append(
                {
                    "module": module,
                    "repo": repo_name,
                    "title": module.replace("_", " ").title(),
                    "description": "",
                    "snippet": "",
                    "url": f"https://github.com/{GITHUB_ORG}/{repo_name}/tree/{BRANCH}/{module}",
                    "score": item.get("score", 0),
                }
            )

    return results


def _list_known_modules(query: str, repos: list[str], limit: int) -> list[dict]:
    """Simple keyword match against known repo descriptions."""
    q = query.lower()
    results = []
    for repo_name in repos:
        desc = TRACKED_REPOS.get(repo_name, "")
        if q in repo_name.lower() or q in desc.lower():
            results.append(
                {
                    "module": repo_name,
                    "repo": repo_name,
                    "title": repo_name.replace("-", " ").title(),
                    "description": desc,
                    "snippet": desc,
                    "url": f"https://github.com/{GITHUB_ORG}/{repo_name}/tree/{BRANCH}",
                    "score": 0,
                }
            )
        if len(results) >= limit:
            break
    return results


async def _fetch_module_info(repo: str, module: str) -> str:
    """Fetch README and manifest for a specific OCA module."""
    base = f"https://raw.githubusercontent.com/{GITHUB_ORG}/{repo}/{BRANCH}/{module}"

    output_parts = [f"# OCA Module: {module}\n**Repo**: {GITHUB_ORG}/{repo} (branch {BRANCH})\n"]

    async with httpx.AsyncClient(timeout=15) as client:
        # Fetch __manifest__.py
        resp = await client.get(f"{base}/__manifest__.py", headers=_github_headers())
        if resp.status_code == 200:
            output_parts.append(f"## __manifest__.py\n```python\n{resp.text}\n```\n")
        else:
            output_parts.append(f"## __manifest__.py\nNot found (HTTP {resp.status_code})\n")

        # Fetch README.rst (primary) or README.md (fallback)
        for readme in ("README.rst", "README.md"):
            resp = await client.get(f"{base}/{readme}", headers=_github_headers())
            if resp.status_code == 200:
                content = resp.text
                if len(content) > 6000:
                    content = content[:6000] + "\n\n[...truncated]"
                output_parts.append(f"## {readme}\n{content}\n")
                break
        else:
            output_parts.append("## README\nNo README found.\n")

    url = f"https://github.com/{GITHUB_ORG}/{repo}/tree/{BRANCH}/{module}"
    output_parts.append(f"\n**GitHub**: {url}")

    return "\n".join(output_parts)


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

app = Server("oca-docs")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_oca_modules",
            description="Search OCA (Odoo Community Association) modules by keyword across tracked 18.0 repos.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'reconciliation', 'queue_job', 'payroll')",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Restrict to OCA repo (e.g., 'account-financial-tools')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 10, max 30)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_oca_module_info",
            description="Get README, __manifest__.py, and metadata for a specific OCA module from GitHub.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "OCA repo name (e.g., 'account-financial-tools')",
                    },
                    "module": {
                        "type": "string",
                        "description": "Module technical name (e.g., 'account_reconcile_oca')",
                    },
                },
                "required": ["repo", "module"],
            },
        ),
        Tool(
            name="list_oca_repos",
            description="List all tracked OCA repositories with descriptions.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    if name == "search_oca_modules":
        query = arguments["query"]
        repo = arguments.get("repo")
        limit = min(arguments.get("limit", 10), 30)

        results = await _search_azure(query, repo, limit)
        if not results:
            results = await _search_github(query, repo, limit)

        formatted = json.dumps(results, indent=2)
        return CallToolResult(content=[TextContent(type="text", text=formatted)])

    elif name == "get_oca_module_info":
        repo = arguments["repo"]
        module = arguments["module"]
        content = await _fetch_module_info(repo, module)
        return CallToolResult(content=[TextContent(type="text", text=content)])

    elif name == "list_oca_repos":
        output = f"# Tracked OCA Repositories (branch: {BRANCH})\n\n"
        for repo_name, desc in sorted(TRACKED_REPOS.items()):
            url = f"https://github.com/{GITHUB_ORG}/{repo_name}/tree/{BRANCH}"
            output += f"- **{repo_name}**: {desc}\n  {url}\n"
        return CallToolResult(content=[TextContent(type="text", text=output)])

    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )


async def main():
    logger.info("Starting oca-docs MCP server (org: %s, branch: %s)", GITHUB_ORG, BRANCH)
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
