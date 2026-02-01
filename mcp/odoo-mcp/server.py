#!/usr/bin/env python3
"""
Odoo MCP Server
===============
Model Context Protocol server for Odoo 18 CE integration.
Provides tools for searching, reading, creating, and executing Odoo operations.

Usage:
    python server.py

Environment Variables:
    ODOO_URL: Odoo instance URL (default: https://erp.insightpulseai.com)
    ODOO_DB: Database name (default: odoo)
    ODOO_USER: Username for authentication
    ODOO_PASSWORD: Password for authentication
"""

import os
import json
import logging
from typing import Any, Optional
import xmlrpc.client
from dataclasses import dataclass

# MCP SDK imports (install via: pip install mcp)
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OdooConfig:
    """Odoo connection configuration."""
    url: str
    db: str
    username: str
    password: str
    uid: Optional[int] = None


class OdooClient:
    """XML-RPC client for Odoo operations."""

    def __init__(self, config: OdooConfig):
        self.config = config
        self.common = xmlrpc.client.ServerProxy(f'{config.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{config.url}/xmlrpc/2/object')
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate and store UID."""
        try:
            self.config.uid = self.common.authenticate(
                self.config.db,
                self.config.username,
                self.config.password,
                {}
            )
            if not self.config.uid:
                raise ValueError("Authentication failed")
            logger.info(f"Authenticated as UID {self.config.uid}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute an Odoo model method."""
        return self.models.execute_kw(
            self.config.db,
            self.config.uid,
            self.config.password,
            model,
            method,
            args,
            kwargs
        )

    def search(self, model: str, domain: list, limit: int = 100, offset: int = 0) -> list:
        """Search for record IDs matching domain."""
        return self.execute(model, 'search', domain, limit=limit, offset=offset)

    def read(self, model: str, ids: list, fields: list = None) -> list:
        """Read records by IDs."""
        return self.execute(model, 'read', ids, fields=fields or [])

    def search_read(self, model: str, domain: list, fields: list = None,
                    limit: int = 100, offset: int = 0, order: str = None) -> list:
        """Search and read in one call."""
        kwargs = {'fields': fields or [], 'limit': limit, 'offset': offset}
        if order:
            kwargs['order'] = order
        return self.execute(model, 'search_read', domain, **kwargs)

    def create(self, model: str, values: dict) -> int:
        """Create a new record."""
        return self.execute(model, 'create', values)

    def write(self, model: str, ids: list, values: dict) -> bool:
        """Update existing records."""
        return self.execute(model, 'write', ids, values)

    def unlink(self, model: str, ids: list) -> bool:
        """Delete records."""
        return self.execute(model, 'unlink', ids)


# Initialize MCP Server
server = Server("odoo-mcp")

# Global Odoo client (initialized on first use)
_odoo_client: Optional[OdooClient] = None


def get_odoo_client() -> OdooClient:
    """Get or create Odoo client."""
    global _odoo_client
    if _odoo_client is None:
        config = OdooConfig(
            url=os.environ.get('ODOO_URL', 'https://erp.insightpulseai.com'),
            db=os.environ.get('ODOO_DB', 'odoo'),
            username=os.environ.get('ODOO_USER', 'admin'),
            password=os.environ.get('ODOO_PASSWORD', ''),
        )
        _odoo_client = OdooClient(config)
    return _odoo_client


# Tool Definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Odoo tools."""
    return [
        Tool(
            name="odoo_search",
            description="Search for Odoo records matching a domain filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name (e.g., 'res.partner', 'account.move')"
                    },
                    "domain": {
                        "type": "array",
                        "description": "Search domain as list of tuples (e.g., [['state', '=', 'posted']])"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return (empty for all)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum records to return"
                    },
                    "order": {
                        "type": "string",
                        "description": "Sort order (e.g., 'date desc')"
                    }
                },
                "required": ["model", "domain"]
            }
        ),
        Tool(
            name="odoo_read",
            description="Read specific Odoo records by their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Record IDs to read"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return"
                    }
                },
                "required": ["model", "ids"]
            }
        ),
        Tool(
            name="odoo_create",
            description="Create a new Odoo record",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "values": {
                        "type": "object",
                        "description": "Field values for the new record"
                    }
                },
                "required": ["model", "values"]
            }
        ),
        Tool(
            name="odoo_write",
            description="Update existing Odoo records",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Record IDs to update"
                    },
                    "values": {
                        "type": "object",
                        "description": "Field values to update"
                    }
                },
                "required": ["model", "ids", "values"]
            }
        ),
        Tool(
            name="odoo_execute",
            description="Execute a custom method on an Odoo model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "method": {
                        "type": "string",
                        "description": "Method name to call"
                    },
                    "args": {
                        "type": "array",
                        "description": "Positional arguments"
                    },
                    "kwargs": {
                        "type": "object",
                        "description": "Keyword arguments"
                    }
                },
                "required": ["model", "method"]
            }
        ),
        Tool(
            name="odoo_fields_get",
            description="Get field definitions for an Odoo model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Field attributes to return (e.g., ['type', 'string', 'required'])"
                    }
                },
                "required": ["model"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    client = get_odoo_client()

    try:
        if name == "odoo_search":
            result = client.search_read(
                model=arguments["model"],
                domain=arguments.get("domain", []),
                fields=arguments.get("fields"),
                limit=arguments.get("limit", 100),
                order=arguments.get("order")
            )

        elif name == "odoo_read":
            result = client.read(
                model=arguments["model"],
                ids=arguments["ids"],
                fields=arguments.get("fields")
            )

        elif name == "odoo_create":
            record_id = client.create(
                model=arguments["model"],
                values=arguments["values"]
            )
            result = {"id": record_id, "success": True}

        elif name == "odoo_write":
            success = client.write(
                model=arguments["model"],
                ids=arguments["ids"],
                values=arguments["values"]
            )
            result = {"success": success}

        elif name == "odoo_execute":
            result = client.execute(
                arguments["model"],
                arguments["method"],
                *arguments.get("args", []),
                **arguments.get("kwargs", {})
            )

        elif name == "odoo_fields_get":
            result = client.execute(
                arguments["model"],
                "fields_get",
                attributes=arguments.get("attributes", ['type', 'string', 'required'])
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
