"""Smoke tests for agent_platform package — no network, no Azure calls."""

import asyncio

import pytest

from agent_platform import __version__
from agent_platform.config import is_development, is_production
from agent_platform.evals.scorecards import load_thresholds, passes_gate
from agent_platform.orchestration.router import TaskRouter
from agent_platform.runtime.engine import AgentRequest, AgentResponse, RuntimeEngine
from agent_platform.runtime.graph_builder import build_registry_from_ssot
from agent_platform.runtime.registry import AgentRegistry, AgentSpec
from agent_platform.settings import Settings
from agent_platform.tools.base import Tool, ToolResult
from agent_platform.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

def test_version_is_set() -> None:
    assert __version__ == "0.1.0"


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def test_settings_defaults() -> None:
    s = Settings()
    assert s.env == "development"
    assert s.port == 8000
    assert "ipai-copilot-resource" in s.foundry_endpoint


def test_config_helpers() -> None:
    s = Settings()
    assert is_development(s) is True
    assert is_production(s) is False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_agent_registry_roundtrip() -> None:
    reg = AgentRegistry()
    spec = AgentSpec(agent_id="test_agent", domain="finance", tools=["odoo_accounting"])
    reg.register(spec)
    assert reg.get("test_agent") is spec
    assert len(reg.all_agents()) == 1


def test_graph_builder_from_ssot() -> None:
    """Loads agents.yaml from ssot/ — file must exist and parse cleanly."""
    reg = build_registry_from_ssot()
    # supervisor + at least 2 specialists defined in ssot/runtime/agents.yaml
    assert len(reg.all_agents()) >= 2


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def test_router_finance_keyword() -> None:
    reg = AgentRegistry()
    router = TaskRouter(reg)
    assert router.route("What is the invoice balance?") == "finance_specialist"


def test_router_project_keyword() -> None:
    reg = AgentRegistry()
    router = TaskRouter(reg)
    assert router.route("Show me all project tasks") == "project_specialist"


def test_router_default_fallback() -> None:
    reg = AgentRegistry()
    router = TaskRouter(reg)
    assert router.route("Hello world") == "supervisor"


# ---------------------------------------------------------------------------
# Engine (stub — no network)
# ---------------------------------------------------------------------------

def test_engine_returns_response() -> None:
    engine = RuntimeEngine()
    req = AgentRequest(task="test task")
    resp = asyncio.run(engine.execute(req))
    assert isinstance(resp, AgentResponse)
    assert resp.result == "stub_response"


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

class _DummyTool(Tool):
    name = "dummy"
    mutation = False

    async def run(self, **kwargs) -> ToolResult:
        return ToolResult(data="ok")


def test_tool_registry_register_and_get() -> None:
    reg = ToolRegistry()
    tool = _DummyTool()
    reg.register(tool)
    assert reg.get("dummy") is tool
    assert reg.mutation_tools() == []


# ---------------------------------------------------------------------------
# Evals / scorecards
# ---------------------------------------------------------------------------

def test_scorecards_load_thresholds() -> None:
    thresholds = load_thresholds()
    assert "accuracy" in thresholds
    assert thresholds["accuracy"] >= 0.0


def test_passes_gate_true() -> None:
    assert passes_gate({"accuracy": 0.9, "safety": 0.97}, {"accuracy": 0.85, "safety": 0.95})


def test_passes_gate_false() -> None:
    assert not passes_gate({"accuracy": 0.7, "safety": 0.97}, {"accuracy": 0.85, "safety": 0.95})
