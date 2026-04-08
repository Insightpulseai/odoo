"""
Tool executor — bridges Foundry agent function calls to MCP connector + Search.

When the Foundry agent calls a tool, this executor:
1. Routes Odoo tools to the MCP connector
2. Routes search tools to Azure AI Search
3. Returns structured results back to the agent

Usage:
    Called by the agent loop, not directly.
"""

import os
import json
import httpx

MCP_ENDPOINT = os.environ.get(
    "MCP_ENDPOINT",
    "https://ipai-odoo-connector.salmontree-b7d27e19.southeastasia.azurecontainerapps.io/mcp"
)

SEARCH_ENDPOINT = os.environ.get(
    "SEARCH_ENDPOINT",
    "https://srch-ipai-copilot.search.windows.net"
)
SEARCH_INDEX = "odoo-knowledge"
SEARCH_API_VERSION = "2024-07-01"


async def execute_tool(tool_name: str, arguments: dict) -> str:
    """Route a tool call to the appropriate backend."""

    if tool_name == "search_odoo_knowledge":
        return await _search_knowledge(arguments.get("query", ""))
    elif tool_name.startswith("odoo_"):
        return await _call_mcp_tool(tool_name, arguments)
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


async def _call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call an Odoo tool via the MCP connector."""
    async with httpx.AsyncClient(timeout=30) as client:
        # Initialize MCP session
        init_resp = await client.post(
            MCP_ENDPOINT,
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "foundry-agent", "version": "1.0"},
                },
                "id": 1,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        session_id = init_resp.headers.get("mcp-session-id", "")

        # Call the tool
        tool_resp = await client.post(
            MCP_ENDPOINT,
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
                "id": 2,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

        # Parse SSE response
        text = tool_resp.text
        if "data: " in text:
            data_line = [l for l in text.split("\n") if l.startswith("data: ")][0]
            result = json.loads(data_line[6:])
            content = result.get("result", {}).get("content", [])
            if content:
                return content[0].get("text", json.dumps(result))
        return text


async def _search_knowledge(query: str) -> str:
    """Search the Odoo knowledge index."""
    search_key = os.environ.get("SEARCH_API_KEY", "")
    if not search_key:
        return json.dumps({"error": "SEARCH_API_KEY not set"})

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{SEARCH_ENDPOINT}/indexes/{SEARCH_INDEX}/docs/search?api-version={SEARCH_API_VERSION}",
            json={
                "search": query,
                "top": 5,
                "select": "title,content,category,module",
            },
            headers={
                "Content-Type": "application/json",
                "api-key": search_key,
            },
        )
        data = resp.json()
        results = []
        for doc in data.get("value", []):
            results.append({
                "title": doc.get("title", ""),
                "content": doc.get("content", ""),
                "category": doc.get("category", ""),
                "module": doc.get("module", ""),
            })
        return json.dumps({"results": results, "count": len(results)})
