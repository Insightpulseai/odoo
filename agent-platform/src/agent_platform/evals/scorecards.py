"""Scorecard helpers — load thresholds from SSOT YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

# Resolve from this file: src/agent_platform/evals/scorecards.py
# ../../.. → src/  ../../../../ → agent-platform/  then ssot/eval/
_PKG_ROOT = Path(__file__).resolve().parents[3]  # agent-platform/
_THRESHOLDS_YAML = _PKG_ROOT / "ssot" / "eval" / "score_thresholds.yaml"


def load_thresholds(path: Path | None = None) -> dict[str, float]:
    """Return {metric_name: min_score} from SSOT thresholds YAML."""
    resolved = path or _THRESHOLDS_YAML
    if not resolved.exists():
        return {}
    data = yaml.safe_load(resolved.read_text())
    return {
        name: cfg["min_score"]
        for name, cfg in (data.get("thresholds") or {}).items()
    }


def passes_gate(scores: dict[str, float], thresholds: dict[str, float]) -> bool:
    return all(scores.get(k, 0.0) >= v for k, v in thresholds.items())
