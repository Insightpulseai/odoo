"""Agent registry — maps agent IDs to MAF agent configs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentSpec:
    agent_id: str
    domain: str
    tools: list[str]


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        self._agents[spec.agent_id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self._agents.get(agent_id)

    def all_agents(self) -> list[AgentSpec]:
        return list(self._agents.values())
