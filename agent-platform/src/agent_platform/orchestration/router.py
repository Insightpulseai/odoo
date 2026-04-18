"""Task router — maps incoming requests to specialist workers."""

from __future__ import annotations

from agent_platform.logging import get_logger
from agent_platform.runtime.registry import AgentRegistry

_logger = get_logger(__name__)

_DOMAIN_KEYWORDS: dict[str, str] = {
    "finance": "finance_specialist",
    "invoice": "finance_specialist",
    "balance": "finance_specialist",
    "project": "project_specialist",
    "task": "project_specialist",
}


class TaskRouter:
    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def route(self, task: str) -> str:
        """Return agent_id for the task. Defaults to 'supervisor'."""
        lower = task.lower()
        for keyword, agent_id in _DOMAIN_KEYWORDS.items():
            if keyword in lower:
                _logger.info("router.matched", keyword=keyword, agent=agent_id)
                return agent_id
        return "supervisor"
