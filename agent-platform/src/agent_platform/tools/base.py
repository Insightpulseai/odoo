"""Tool ABC — all tools must implement this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolResult:
    def __init__(self, data: Any, error: str | None = None) -> None:
        self.data = data
        self.error = error

    @property
    def ok(self) -> bool:
        return self.error is None


class Tool(ABC):
    name: str
    mutation: bool = False
    approval_required: bool = False

    @abstractmethod
    async def run(self, **kwargs: Any) -> ToolResult:
        """Execute the tool and return a ToolResult."""
