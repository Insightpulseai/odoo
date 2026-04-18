"""Agent runtime engine — MAF client wiring stub."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent_platform.logging import get_logger

_logger = get_logger(__name__)


@dataclass
class AgentRequest:
    task: str
    context: dict[str, Any] = field(default_factory=dict)
    session_id: str | None = None


@dataclass
class AgentResponse:
    result: str
    trace_id: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class RuntimeEngine:
    """Stub engine — wires to MAF AzureAIAgentClient in Phase 1."""

    def __init__(self) -> None:
        _logger.info("runtime_engine.init")

    async def execute(self, request: AgentRequest) -> AgentResponse:
        _logger.info("runtime_engine.execute", task=request.task[:80])
        # Phase 1: delegate to supervisor via MAF client
        return AgentResponse(result="stub_response", trace_id="stub-trace-001")
