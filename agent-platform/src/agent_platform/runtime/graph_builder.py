"""Graph builder — constructs agent execution graphs from SSOT YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from agent_platform.logging import get_logger
from agent_platform.runtime.registry import AgentRegistry, AgentSpec

_logger = get_logger(__name__)

_AGENTS_YAML = Path(__file__).resolve().parents[3] / "ssot" / "runtime" / "agents.yaml"


def build_registry_from_ssot(yaml_path: Path = _AGENTS_YAML) -> AgentRegistry:
    registry = AgentRegistry()
    if not yaml_path.exists():
        _logger.warning("graph_builder.ssot_missing", path=str(yaml_path))
        return registry
    data = yaml.safe_load(yaml_path.read_text())
    for agent_id, cfg in (data.get("agents") or {}).items():
        registry.register(
            AgentSpec(
                agent_id=agent_id,
                domain=cfg.get("domain", "general"),
                tools=cfg.get("tools", []),
            )
        )
    return registry
