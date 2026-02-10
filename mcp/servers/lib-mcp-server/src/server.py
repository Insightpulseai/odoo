"""
LIB MCP Server - Main server with auto-scan on startup

Provides MCP tools for local filesystem intelligence:
- File search by metadata
- Full-text search across content (FTS5)
- Manual directory scanning
- Scan run history
"""

import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

# Add scripts/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts" / "lib"))

from lib_db import init_database
from lib_scan import scan_repository
from .config import settings
from .tools import TOOLS

# Setup logging
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle handler - auto-scan on startup

    User decision: Auto-scan on startup (not on-demand)
    """
    # Initialize database
    logger.info(f"Initializing LIB database at {settings.lib_db_path}")
    await init_database(settings.lib_db_path)

    # Auto-scan configured roots on startup
    if settings.auto_scan_on_startup and settings.scan_roots:
        logger.info("Starting auto-scan on startup...")
        scan_roots = [Path(r) for r in settings.scan_roots]

        try:
            stats = await scan_repository(scan_roots, settings.lib_db_path, verbose=False)
            logger.info(f"Auto-scan completed: {stats}")
        except Exception as e:
            logger.error(f"Auto-scan failed: {e}")

    yield

    # Cleanup (if needed)
    logger.info("LIB MCP server shutting down")


app = FastAPI(
    title="LIB MCP Server",
    description="Local Intelligence Brain - Filesystem metadata and content search",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response models
class ToolRequest(BaseModel):
    """MCP tool request"""
    name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    """MCP tool response"""
    content: list[Dict[str, Any]]
    isError: bool = False


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": str(settings.lib_db_path),
        "auto_scan": settings.auto_scan_on_startup,
        "fts5_enabled": settings.fts5_enabled
    }


@app.get("/tools/list")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in TOOLS
        ]
    }


@app.post("/tools/call")
async def call_tool(request: ToolRequest) -> ToolResponse:
    """
    Call an MCP tool

    Args:
        request: Tool request with name and arguments

    Returns:
        Tool response with content or error
    """
    # Find tool
    tool = next((t for t in TOOLS if t["name"] == request.name), None)

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")

    # Call handler
    try:
        result = await tool["handler"](**request.arguments)

        return ToolResponse(
            content=[
                {
                    "type": "text",
                    "text": str(result)
                }
            ]
        )
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return ToolResponse(
            content=[
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            isError=True
        )


# Individual tool endpoints for direct HTTP access
@app.post("/tools/lib_search_files")
async def search_files_endpoint(
    query: Optional[str] = None,
    ext: Optional[str] = None,
    mime: Optional[str] = None,
    repo_root: Optional[str] = None,
    limit: int = 100
):
    """Search files endpoint"""
    from .tools import handle_search_files
    return await handle_search_files(query, ext, mime, repo_root, limit)


@app.post("/tools/lib_get_file_info")
async def get_file_info_endpoint(path: str):
    """Get file info endpoint"""
    from .tools import handle_get_file_info
    return await handle_get_file_info(path)


@app.post("/tools/lib_scan_directory")
async def scan_directory_endpoint(path: str):
    """Scan directory endpoint"""
    from .tools import handle_scan_directory
    return await handle_scan_directory(path)


@app.get("/tools/lib_query_runs")
async def query_runs_endpoint(limit: int = 10):
    """Query scan runs endpoint"""
    from .tools import handle_query_runs
    return await handle_query_runs(limit)


@app.post("/tools/lib_fts_search")
async def fts_search_endpoint(query: str, limit: int = 50):
    """FTS5 search endpoint"""
    from .tools import handle_fts_search
    return await handle_fts_search(query, limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level
    )
