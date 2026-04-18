"""Eval runner stub — delegates to Foundry evaluation service in Phase 2."""

from __future__ import annotations

from pathlib import Path

import yaml

from agent_platform.logging import get_logger

_logger = get_logger(__name__)

_SCENARIOS_YAML = Path(__file__).resolve().parents[3] / "ssot" / "eval" / "scenarios.yaml"


class EvalRunner:
    def __init__(self, scenarios_path: Path = _SCENARIOS_YAML) -> None:
        self._scenarios_path = scenarios_path

    def load_scenarios(self) -> list[dict]:
        if not self._scenarios_path.exists():
            _logger.warning("eval_runner.scenarios_missing")
            return []
        return yaml.safe_load(self._scenarios_path.read_text()).get("scenarios", [])

    async def run_all(self) -> dict[str, float]:
        """Stub — returns empty scores until Foundry eval wired in Phase 2."""
        _logger.info("eval_runner.run_all.stub")
        return {}
