"""
Intelligent routing logic for MCP Coordinator

Supports Agent-to-Agent (A2A) communication patterns:
- Context propagation across agent calls
- Agent capability-based routing
- Call chain tracing for distributed operations

@see https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes
"""
from typing import Dict, List, Optional, Any
from enum import Enum
import httpx
from .config import settings


class MCPTarget(str, Enum):
    """Available MCP targets"""
    ODOO_PROD = "odoo_prod"
    ODOO_LAB = "odoo_lab"
    AGENT_COORDINATION = "agent_coordination"


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


class A2AContext:
    """Agent-to-Agent context for call chain tracing"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        caller_agent_id: Optional[str] = None,
        call_chain: Optional[List[str]] = None,
        trace_id: Optional[str] = None,
    ):
        self.session_id = session_id
        self.caller_agent_id = caller_agent_id
        self.call_chain = call_chain or []
        self.trace_id = trace_id

    @classmethod
    def from_request(cls, request_data: Dict[str, Any]) -> "A2AContext":
        """Extract A2A context from request"""
        ctx = request_data.get("a2a_context", {})
        return cls(
            session_id=ctx.get("session_id"),
            caller_agent_id=ctx.get("caller_agent_id"),
            call_chain=ctx.get("call_chain", []),
            trace_id=ctx.get("trace_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for propagation"""
        return {
            "session_id": self.session_id,
            "caller_agent_id": self.caller_agent_id,
            "call_chain": self.call_chain,
            "trace_id": self.trace_id,
        }


class MCPRouter:
    """Intelligent MCP request router with A2A support"""

    def __init__(self):
        self.target_urls = {
            MCPTarget.ODOO_PROD: settings.odoo_prod_mcp_url,
            MCPTarget.ODOO_LAB: settings.odoo_lab_mcp_url,
            MCPTarget.AGENT_COORDINATION: settings.agent_coordination_url,
        }

    def route_request(self, request_data: Dict[str, Any]) -> RoutingDecision:
        """
        Route request based on context analysis

        Priority:
        1. Explicit target override
        2. A2A agent invocation requests
        3. Context-based routing (finance-ssc → prod, migration/oca → lab)
        4. Default with failover
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

        # A2A coordination requests
        a2a_context = A2AContext.from_request(request_data)
        tool_name = request_data.get("tool_name", "").lower()

        if a2a_context.caller_agent_id or any(
            keyword in tool_name
            for keyword in ["invoke_agent", "discover_agents", "register_agent", "handoff", "delegate"]
        ):
            return RoutingDecision(
                target=MCPTarget.AGENT_COORDINATION,
                reason="A2A coordination request",
                confidence=0.98,
                fallback=MCPTarget.ODOO_LAB,
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

    def propagate_a2a_context(
        self, request_data: Dict[str, Any], current_agent_id: str
    ) -> Dict[str, Any]:
        """Add A2A context to outgoing requests for call chain tracing"""
        a2a_context = A2AContext.from_request(request_data)
        a2a_context.call_chain.append(current_agent_id)

        return {
            **request_data,
            "a2a_context": a2a_context.to_dict(),
        }

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
