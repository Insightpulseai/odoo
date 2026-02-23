#!/usr/bin/env python3
"""
check_graphrag_manifest.py — CI validator for GraphRAG indexer manifest.

Validates that `reports/graphrag_manifest.json` exists and contains the
required fields with sane values. This is a non-blocking gate by default
(the workflow uses continue-on-error: true).

Exit codes:
  0  — manifest present and valid (or advisory mode: file absent, just warn)
  1  — manifest present but invalid (missing required fields, zero counts)

Usage:
  python scripts/ci/check_graphrag_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "reports" / "graphrag_manifest.json"

REQUIRED_FIELDS = [
    "contract_version",
    "indexer_version",
    "git_sha",
    "timestamp",
    "addons_path",
    "input_checksum",
    "stats",
]

REQUIRED_STATS = ["nodes_written", "edges_written"]


def _emit_summary(lines: list[str]) -> None:
    """Write to GitHub step summary if available, otherwise stdout."""
    summary_path = Path(__file__).parent  # fallback
    ghs = Path(str(summary_path))  # unused
    import os
    ghs_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if ghs_file:
        with open(ghs_file, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    else:
        for line in lines:
            print(line)


def main() -> int:
    if not MANIFEST_PATH.exists():
        msg = (
            f"[ADVISORY] {MANIFEST_PATH.relative_to(REPO_ROOT)} not found.\n"
            "Re-run the indexer to generate it:\n"
            "  python scripts/build_kb_graph.py\n"
            "This check is advisory (continue-on-error: true) until the indexer\n"
            "runs in CI with DB credentials."
        )
        print(msg)
        _emit_summary([
            "## GraphRAG Manifest: ADVISORY",
            "",
            f"> `{MANIFEST_PATH.relative_to(REPO_ROOT)}` not found.",
            "> Re-run: `python scripts/build_kb_graph.py`",
        ])
        # Exit 0 — advisory; do not fail CI for missing manifest
        return 0

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Manifest is not valid JSON: {exc}")
        return 1

    errors: list[str] = []

    # Check required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field!r}")

    # Check stats sub-fields
    stats = manifest.get("stats", {})
    if isinstance(stats, dict):
        for sf in REQUIRED_STATS:
            if sf not in stats:
                errors.append(f"Missing stats.{sf}")
            elif not isinstance(stats[sf], int) or stats[sf] < 0:
                errors.append(f"stats.{sf} must be a non-negative integer, got {stats[sf]!r}")
        if stats.get("nodes_written", 0) == 0:
            errors.append("stats.nodes_written is 0 — indexer may not have run successfully")
        if stats.get("edges_written", 0) == 0:
            errors.append("stats.edges_written is 0 — no edges were written")
    else:
        errors.append("'stats' must be a JSON object")

    if errors:
        print("[FAIL] Manifest validation failed:")
        for e in errors:
            print(f"  - {e}")
        _emit_summary([
            "## GraphRAG Manifest: FAIL",
            "",
            "Validation errors:",
            *[f"- {e}" for e in errors],
            "",
            "> Re-run: `python scripts/build_kb_graph.py`",
        ])
        return 1

    # All good
    nodes = stats.get("nodes_written", 0)
    edges = stats.get("edges_written", 0)
    sha   = manifest.get("git_sha", "(unknown)")
    ts    = manifest.get("timestamp", "(unknown)")
    cv    = manifest.get("contract_version", "(unknown)")
    iv    = manifest.get("indexer_version", "(unknown)")

    summary = [
        "## GraphRAG Manifest: PASS",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| contract_version | {cv} |",
        f"| indexer_version | {iv} |",
        f"| git_sha | {sha} |",
        f"| timestamp | {ts} |",
        f"| nodes_written | {nodes} |",
        f"| edges_written | {edges} |",
    ]
    print(f"[PASS] Manifest valid — {nodes} nodes, {edges} edges, git_sha={sha}")
    _emit_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
