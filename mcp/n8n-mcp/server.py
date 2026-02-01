#!/usr/bin/env python3
"""
n8n MCP Server
==============
Model Context Protocol server for n8n workflow automation integration.
Provides tools for triggering workflows, checking executions, and managing workflows.

Usage:
    python server.py

Environment Variables:
    N8N_URL: n8n instance URL (default: https://n8n.insightpulseai.com)
    N8N_API_KEY: API key for authentication
"""

import os
import json
import logging
from typing import Any, Optional
import httpx
from dataclasses import dataclass

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class N8nConfig:
    """n8n connection configuration."""
    url: str
    api_key: str


class N8nClient:
    """HTTP client for n8n API operations."""

    def __init__(self, config: N8nConfig):
        self.config = config
        self.base_url = f"{config.url}/api/v1"
        self.headers = {
            "X-N8N-API-KEY": config.api_key,
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an HTTP request to n8n API."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def list_workflows(self, active: Optional[bool] = None) -> list:
        """List all workflows."""
        params = {}
        if active is not None:
            params["active"] = str(active).lower()
        return await self._request("GET", "/workflows", params=params)

    async def get_workflow(self, workflow_id: str) -> dict:
        """Get workflow details."""
        return await self._request("GET", f"/workflows/{workflow_id}")

    async def execute_workflow(self, workflow_id: str, data: dict = None) -> dict:
        """Execute a workflow."""
        return await self._request(
            "POST",
            f"/workflows/{workflow_id}/execute",
            json={"data": data or {}}
        )

    async def get_executions(self, workflow_id: str = None, limit: int = 20) -> list:
        """Get workflow executions."""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        return await self._request("GET", "/executions", params=params)

    async def get_execution(self, execution_id: str) -> dict:
        """Get execution details."""
        return await self._request("GET", f"/executions/{execution_id}")

    async def activate_workflow(self, workflow_id: str, active: bool = True) -> dict:
        """Activate or deactivate a workflow."""
        return await self._request(
            "PATCH",
            f"/workflows/{workflow_id}",
            json={"active": active}
        )


# Initialize MCP Server
server = Server("n8n-mcp")

# Global n8n client
_n8n_client: Optional[N8nClient] = None


def get_n8n_client() -> N8nClient:
    """Get or create n8n client."""
    global _n8n_client
    if _n8n_client is None:
        config = N8nConfig(
            url=os.environ.get('N8N_URL', 'https://n8n.insightpulseai.com'),
            api_key=os.environ.get('N8N_API_KEY', ''),
        )
        if not config.api_key:
            raise ValueError("N8N_API_KEY environment variable required")
        _n8n_client = N8nClient(config)
    return _n8n_client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available n8n tools."""
    return [
        Tool(
            name="n8n_list_workflows",
            description="List all n8n workflows",
            inputSchema={
                "type": "object",
                "properties": {
                    "active": {
                        "type": "boolean",
                        "description": "Filter by active status"
                    }
                }
            }
        ),
        Tool(
            name="n8n_get_workflow",
            description="Get details of a specific workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="n8n_trigger_workflow",
            description="Trigger/execute a workflow with optional data",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID to execute"
                    },
                    "data": {
                        "type": "object",
                        "description": "Data to pass to the workflow"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="n8n_get_executions",
            description="Get recent workflow executions",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Filter by workflow ID"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum executions to return"
                    }
                }
            }
        ),
        Tool(
            name="n8n_get_execution",
            description="Get details of a specific execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "string",
                        "description": "Execution ID"
                    }
                },
                "required": ["execution_id"]
            }
        ),
        Tool(
            name="n8n_toggle_workflow",
            description="Activate or deactivate a workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Set active status"
                    }
                },
                "required": ["workflow_id", "active"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    client = get_n8n_client()

    try:
        if name == "n8n_list_workflows":
            result = await client.list_workflows(arguments.get("active"))

        elif name == "n8n_get_workflow":
            result = await client.get_workflow(arguments["workflow_id"])

        elif name == "n8n_trigger_workflow":
            result = await client.execute_workflow(
                arguments["workflow_id"],
                arguments.get("data")
            )

        elif name == "n8n_get_executions":
            result = await client.get_executions(
                arguments.get("workflow_id"),
                arguments.get("limit", 20)
            )

        elif name == "n8n_get_execution":
            result = await client.get_execution(arguments["execution_id"])

        elif name == "n8n_toggle_workflow":
            result = await client.activate_workflow(
                arguments["workflow_id"],
                arguments["active"]
            )

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(main())
