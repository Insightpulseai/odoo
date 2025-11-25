"""
Intelligent routing logic for MCP Coordinator
"""
from typing import Dict, List, Optional, Any
from enum import Enum
import httpx
from .config import settings


class MCPTarget(str, Enum):
    """Available MCP targets"""
    ODOO_PROD = "odoo_prod"
    ODOO_LAB = "odoo_lab"


class RoutingDecision:
    """Routing decision with reasoning"""

    def __init__(
        self,
        target: MCPTarget,
        reason: str,
        confidence: float,
        fallback: Optional[MCPTarget] = None,
    ):
        self.target = target
        self.reason = reason
        self.confidence = confidence
        self.fallback = fallback


class MCPRouter:
    """Intelligent MCP request router"""

    def __init__(self):
        self.target_urls = {
            MCPTarget.ODOO_PROD: settings.odoo_prod_mcp_url,
            MCPTarget.ODOO_LAB: settings.odoo_lab_mcp_url,
        }

    def route_request(self, request_data: Dict[str, Any]) -> RoutingDecision:
        """
        Route request based on context analysis

        Priority:
        1. Explicit target override
        2. Context-based routing (finance-ssc → prod, migration/oca → lab)
        3. Default with failover
        """
        # Check for explicit target
        if "target" in request_data:
            target = request_data["target"]
            if target in [t.value for t in MCPTarget]:
                return RoutingDecision(
                    target=MCPTarget(target),
                    reason="Explicit target specified",
                    confidence=1.0,
                )

        # Context-based routing
        context = request_data.get("context", {})
        query = request_data.get("query", "").lower()

        # Finance SSC production data
        if "finance-ssc" in context or "finance-ssc" in query:
            return RoutingDecision(
                target=MCPTarget.ODOO_PROD,
                reason="Finance SSC context requires production data",
                confidence=0.95,
                fallback=MCPTarget.ODOO_LAB,
            )

        # Migration or OCA development
        if any(
            keyword in query
            for keyword in ["migration", "oca", "development", "testing"]
        ):
            return RoutingDecision(
                target=MCPTarget.ODOO_LAB,
                reason="Development/testing context",
                confidence=0.90,
                fallback=MCPTarget.ODOO_PROD,
            )

        # Default to production with lab failover
        return RoutingDecision(
            target=MCPTarget(settings.default_target),
            reason="Default routing",
            confidence=0.75,
            fallback=MCPTarget.ODOO_LAB,
        )

    async def forward_request(
        self, target: MCPTarget, endpoint: str, method: str = "GET", **kwargs
    ) -> Dict[str, Any]:
        """Forward request to target MCP server"""
        url = f"{self.target_urls[target]}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    async def aggregate_requests(
        self, targets: List[MCPTarget], endpoint: str, method: str = "GET", **kwargs
    ) -> Dict[str, List[Any]]:
        """Aggregate responses from multiple MCP servers"""
        results = {}

        for target in targets:
            try:
                result = await self.forward_request(target, endpoint, method, **kwargs)
                results[target.value] = result
            except Exception as e:
                results[target.value] = {"error": str(e)}

        return results


# Global router instance
router = MCPRouter()
