"""
MCP Server: odoo-docs
Odoo 18 documentation search server for Foundry agents + Claude Code.

Provides three tools:
  - search_odoo_docs: keyword search across Odoo 18 documentation
  - get_odoo_doc_page: fetch a specific documentation page
  - list_odoo_doc_sections: list available doc sections

Two modes:
  1. Azure AI Search mode (production): queries srch-ipai-copilot index
  2. Fetch mode (fallback): direct HTTP fetch from odoo.com/documentation/18.0

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
from urllib.parse import quote_plus, urljoin

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("mcp.odoo-docs")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ODOO_DOCS_BASE = os.getenv(
    "ODOO_DOCS_BASE_URL", "https://www.odoo.com/documentation/18.0"
)
SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE", "srch-ipai-copilot")
SEARCH_INDEX = os.getenv("ODOO_DOCS_INDEX", "odoo-docs-18")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
SEARCH_API_VERSION = "2024-07-01"
MAX_RESULTS = int(os.getenv("ODOO_DOCS_MAX_RESULTS", "10"))

SECTIONS = {
    "developer": {
        "path": "/developer",
        "description": "Developer docs — ORM, controllers, views, JS framework, testing",
        "subsections": [
            "reference/backend/orm",
            "reference/backend/actions",
            "reference/backend/views",
            "reference/backend/security",
            "reference/frontend/framework_overview",
            "reference/frontend/owl_components",
            "tutorials/server_framework_101",
            "tutorials/define_module_data",
            "tutorials/restrict_data_access",
        ],
    },
    "applications": {
        "path": "/applications",
        "description": "Functional docs — accounting, HR, sales, inventory, CRM",
        "subsections": [
            "finance/accounting",
            "sales/sales",
            "inventory_and_mrp/inventory",
            "hr/employees",
            "hr/payroll",
            "services/project",
            "services/helpdesk",
        ],
    },
    "administration": {
        "path": "/administration",
        "description": "Admin — installation, configuration, security, upgrade",
        "subsections": [
            "install",
            "on_premise",
            "maintain",
            "upgrade",
        ],
    },
    "contributing": {
        "path": "/contributing",
        "description": "Contributing — coding guidelines, documentation, git",
        "subsections": [
            "development/coding_guidelines",
            "development/git_guidelines",
        ],
    },
}


# ---------------------------------------------------------------------------
# Search backends
# ---------------------------------------------------------------------------


async def _search_azure(query: str, section: str | None, limit: int) -> list[dict]:
    """Query Azure AI Search index for Odoo docs."""
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
        "captions": "extractive",
        "answers": "extractive",
    }
    if section:
        body["filter"] = f"section eq '{section}'"

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
                "title": doc.get("title", ""),
                "path": doc.get("path", ""),
                "url": doc.get("url", ""),
                "snippet": doc.get("content", "")[:500],
                "section": doc.get("section", ""),
                "score": doc.get("@search.score", 0),
            }
        )
    return results


async def _search_fallback(query: str, section: str | None, limit: int) -> list[dict]:
    """Fallback: scrape Odoo docs search page."""
    search_url = f"{ODOO_DOCS_BASE}/search.html"
    params = {"q": query, "check_keywords": "yes", "area": "default"}

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(search_url, params=params)
        if resp.status_code != 200:
            return [
                {
                    "title": "Search unavailable",
                    "path": "",
                    "url": search_url,
                    "snippet": f"Odoo docs search returned HTTP {resp.status_code}. Try get_odoo_doc_page with a specific path.",
                    "section": "",
                    "score": 0,
                }
            ]

    # Parse basic search results from HTML (best-effort)
    results = []
    # Look for search result entries — Sphinx-based search page
    pattern = re.compile(
        r'<li>\s*<a href="([^"]+)"[^>]*>([^<]+)</a>\s*(?:<span[^>]*>([^<]*)</span>)?',
        re.DOTALL,
    )
    for match in pattern.finditer(resp.text):
        path, title, snippet = match.group(1), match.group(2), match.group(3) or ""
        if section and section not in path:
            continue
        results.append(
            {
                "title": title.strip(),
                "path": path,
                "url": urljoin(ODOO_DOCS_BASE + "/", path),
                "snippet": snippet.strip()[:300],
                "section": path.split("/")[0] if "/" in path else "",
                "score": 0,
            }
        )
        if len(results) >= limit:
            break

    if not results:
        results.append(
            {
                "title": f"No results for '{query}'",
                "path": "",
                "url": f"{ODOO_DOCS_BASE}/search.html?q={quote_plus(query)}",
                "snippet": "Try broader terms or use get_odoo_doc_page with a known path.",
                "section": "",
                "score": 0,
            }
        )
    return results


async def _fetch_page(path: str) -> str:
    """Fetch a documentation page and extract text content."""
    url = f"{ODOO_DOCS_BASE}{path}"
    if not path.startswith("/"):
        url = f"{ODOO_DOCS_BASE}/{path}"

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return f"Error: HTTP {resp.status_code} fetching {url}"

    # Strip HTML to get readable text (best-effort)
    text = resp.text
    # Remove script/style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL)
    # Remove nav, header, footer
    text = re.sub(r"<(nav|header|footer)[^>]*>.*?</\1>", "", text, flags=re.DOTALL)
    # Extract main content area if possible
    main_match = re.search(
        r'<(?:main|article|div[^>]*class="[^"]*document[^"]*")[^>]*>(.*?)</(?:main|article|div)>',
        text,
        re.DOTALL,
    )
    if main_match:
        text = main_match.group(1)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate to reasonable size
    if len(text) > 8000:
        text = text[:8000] + "\n\n[...truncated — use a more specific path]"

    return f"Source: {url}\n\n{text}"


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

app = Server("odoo-docs")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_odoo_docs",
            description="Search Odoo 18 documentation by keyword or topic. Returns titles, paths, and snippets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'compute fields', 'account.move', 'QWeb templates')",
                    },
                    "section": {
                        "type": "string",
                        "description": "Restrict to: developer, applications, administration, contributing",
                        "enum": ["developer", "applications", "administration", "contributing"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 5, max 20)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_odoo_doc_page",
            description="Fetch a specific Odoo 18 documentation page by path. Returns extracted text content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Doc path (e.g., '/developer/reference/backend/orm', '/applications/finance/accounting')",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="list_odoo_doc_sections",
            description="List available Odoo 18 documentation sections and their key topics.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    if name == "search_odoo_docs":
        query = arguments["query"]
        section = arguments.get("section")
        limit = min(arguments.get("limit", 5), 20)

        # Try Azure AI Search first, fall back to direct fetch
        results = await _search_azure(query, section, limit)
        if not results:
            results = await _search_fallback(query, section, limit)

        formatted = json.dumps(results, indent=2)
        return CallToolResult(content=[TextContent(type="text", text=formatted)])

    elif name == "get_odoo_doc_page":
        path = arguments["path"]
        content = await _fetch_page(path)
        return CallToolResult(content=[TextContent(type="text", text=content)])

    elif name == "list_odoo_doc_sections":
        output = "# Odoo 18 Documentation Sections\n\n"
        for key, sec in SECTIONS.items():
            output += f"## {key} ({sec['path']})\n"
            output += f"{sec['description']}\n\n"
            for sub in sec["subsections"]:
                output += f"  - {sec['path']}/{sub}\n"
            output += "\n"
        return CallToolResult(content=[TextContent(type="text", text=output)])

    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )


async def main():
    logger.info("Starting odoo-docs MCP server (base: %s)", ODOO_DOCS_BASE)
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
