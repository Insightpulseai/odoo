"""Tool registry — enforces MCP allowlist from SSOT."""

from __future__ import annotations

from agent_platform.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def mutation_tools(self) -> list[Tool]:
        return [t for t in self._tools.values() if t.mutation]
