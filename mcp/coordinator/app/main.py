"""
MCP Coordinator - Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from .config import settings
from .routing import router, MCPTarget, RoutingDecision
from . import __version__


app = FastAPI(
    title="MCP Coordinator",
    description="Context-aware routing for multiple MCP servers",
    version=__version__,
)


# Request/Response models
class MCPRequest(BaseModel):
    """Generic MCP request"""

    query: str
    context: Optional[Dict[str, Any]] = {}
    target: Optional[str] = None
    mode: Optional[str] = "route"  # route | aggregate


class MCPResponse(BaseModel):
    """MCP response with routing metadata"""

    data: Any
    routing: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    targets: List[str]


# Authentication dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key for protected endpoints"""
    if x_api_key != settings.coordinator_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Health and status endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        version=__version__,
        targets=[t.value for t in MCPTarget],
    )


@app.get("/status")
async def get_status(authenticated: bool = Depends(verify_api_key)):
    """Detailed status with target health"""
    target_status = {}

    for target in MCPTarget:
        try:
            result = await router.forward_request(target, "/health", method="GET")
            target_status[target.value] = {"status": "healthy", "details": result}
        except Exception as e:
            target_status[target.value] = {"status": "unhealthy", "error": str(e)}

    return {
        "coordinator": {"status": "ok", "version": __version__},
        "targets": target_status,
        "config": {
            "default_target": settings.default_target,
            "aggregation_enabled": settings.enable_aggregation,
        },
    }


# Core routing endpoints
@app.post("/route", response_model=MCPResponse)
async def route_mcp_request(
    request: MCPRequest, authenticated: bool = Depends(verify_api_key)
):
    """
    Route MCP request to appropriate server

    Supports:
    - Explicit target override
    - Context-based routing
    - Automatic failover
    """
    # Get routing decision
    decision: RoutingDecision = router.route_request(request.dict())

    try:
        # Forward to target
        result = await router.forward_request(
            decision.target,
            "/query",  # Assume query endpoint
            method="POST",
            json={"query": request.query, "context": request.context},
        )

        return MCPResponse(
            data=result,
            routing={
                "target": decision.target.value,
                "reason": decision.reason,
                "confidence": decision.confidence,
            },
        )

    except Exception as e:
        # Try fallback if available
        if decision.fallback:
            try:
                result = await router.forward_request(
                    decision.fallback,
                    "/query",
                    method="POST",
                    json={"query": request.query, "context": request.context},
                )

                return MCPResponse(
                    data=result,
                    routing={
                        "target": decision.fallback.value,
                        "reason": f"Failover from {decision.target.value}",
                        "confidence": 0.5,
                    },
                )
            except Exception as fallback_error:
                raise HTTPException(
                    status_code=502,
                    detail=f"Primary failed: {str(e)}, Fallback failed: {str(fallback_error)}",
                )
        else:
            raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")


@app.post("/aggregate")
async def aggregate_mcp_request(
    request: MCPRequest, authenticated: bool = Depends(verify_api_key)
):
    """
    Aggregate responses from multiple MCP servers

    Useful for:
    - Cross-environment comparisons
    - Comprehensive searches
    - Data validation
    """
    if not settings.enable_aggregation:
        raise HTTPException(status_code=403, detail="Aggregation is disabled")

    targets = [MCPTarget.ODOO_PROD, MCPTarget.ODOO_LAB]
    results = await router.aggregate_requests(
        targets,
        "/query",
        method="POST",
        json={"query": request.query, "context": request.context},
    )

    return {
        "query": request.query,
        "results": results,
        "aggregation": {"targets": [t.value for t in targets], "mode": "parallel"},
    }


# Passthrough endpoints for direct access
@app.get("/skills")
async def list_skills(
    target: Optional[str] = None, authenticated: bool = Depends(verify_api_key)
):
    """List skills from target MCP server"""
    target_enum = MCPTarget(target) if target else MCPTarget(settings.default_target)

    result = await router.forward_request(target_enum, "/skills", method="GET")
    return result


@app.get("/conversations")
async def list_conversations(
    target: Optional[str] = None, authenticated: bool = Depends(verify_api_key)
):
    """List conversations from target MCP server"""
    target_enum = MCPTarget(target) if target else MCPTarget(settings.default_target)

    result = await router.forward_request(target_enum, "/conversations", method="GET")
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8766)
