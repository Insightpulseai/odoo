#!/usr/bin/env python3
"""Evidence capture and persistence for benchmark runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


EVIDENCE_ROOT = Path(__file__).resolve().parent.parent.parent / "docs" / "evidence"


def get_evidence_dir(timestamp: str | None = None) -> Path:
    """Get or create the evidence directory for a benchmark run."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    evidence_dir = EVIDENCE_ROOT / timestamp / "copilot-benchmark"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir


def write_envelopes(evidence_dir: Path, envelopes: list[dict]) -> Path:
    """Write raw evidence envelopes to JSON."""
    path = evidence_dir / "envelopes.json"
    with open(path, "w") as f:
        json.dump(envelopes, f, indent=2, default=str)
    return path


def write_scores(evidence_dir: Path, scores: dict) -> Path:
    """Write computed scores to JSON."""
    path = evidence_dir / "scores.json"
    with open(path, "w") as f:
        json.dump(scores, f, indent=2)
    return path


def write_report(evidence_dir: Path, report_md: str) -> Path:
    """Write Markdown report."""
    path = evidence_dir / "report.md"
    with open(path, "w") as f:
        f.write(report_md)
    return path


def write_summary(evidence_dir: Path, envelopes: list[dict], scores: dict) -> Path:
    """Write a combined summary JSON for machine consumption."""
    summary = {
        "benchmark_version": envelopes[0].get("benchmark_version", "1.0.0") if envelopes else "1.0.0",
        "timestamp": envelopes[0].get("timestamp") if envelopes else None,
        "odoo_version": envelopes[0].get("odoo_version") if envelopes else None,
        "total_scenarios": len(envelopes),
        "scores": scores,
        "scenarios": [
            {
                "id": e["scenario_id"],
                "result": e["result"],
                "weighted_score": e.get("weighted_score", 0),
                "latency_ms": e.get("latency_ms", 0),
            }
            for e in envelopes
        ],
    }
    path = evidence_dir / "summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    return path
