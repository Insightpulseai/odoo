"""Supervisor — mediates worker invocations; workers never invoke workers directly."""

from __future__ import annotations

from agent_platform.logging import get_logger
from agent_platform.orchestration.router import TaskRouter
from agent_platform.runtime.engine import AgentRequest, AgentResponse, RuntimeEngine

_logger = get_logger(__name__)


class Supervisor:
    def __init__(self, engine: RuntimeEngine, router: TaskRouter) -> None:
        self._engine = engine
        self._router = router

    async def handle(self, task: str, context: dict | None = None) -> AgentResponse:
        agent_id = self._router.route(task)
        _logger.info("supervisor.dispatch", agent=agent_id)
        request = AgentRequest(task=task, context=context or {})
        # Phase 1: delegate to MAF agent by agent_id
        response = await self._engine.execute(request)
        _logger.info("supervisor.done", trace_id=response.trace_id)
        return response
