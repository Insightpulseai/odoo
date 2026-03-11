#!/usr/bin/env python3
"""Odoo Copilot Benchmark Runner.

Executes benchmark scenarios against a running Odoo instance,
captures evidence, computes scores, and generates reports.

Usage:
    python scripts/benchmark/run_benchmark.py --url http://localhost:8069 --db odoo_dev
    python scripts/benchmark/run_benchmark.py --domain crm --url http://localhost:8069 --db odoo_dev

Prerequisites:
    - Running Odoo instance with ipai_ai_copilot installed
    - Benchmark personas seeded (7 users with correct groups)
    - Demo data seeded for target domains
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

SPEC_ROOT = Path(__file__).resolve().parent.parent.parent / "spec" / "odoo-copilot-benchmark"
SCENARIOS_DIR = SPEC_ROOT / "scenarios"
CONFIG_PATH = SPEC_ROOT / "benchmark.config.yaml"
EVIDENCE_ROOT = Path(__file__).resolve().parent.parent.parent / "docs" / "evidence"


def load_config() -> dict:
    """Load benchmark configuration."""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_scenarios(domain: str | None = None) -> list[dict]:
    """Load all scenarios, optionally filtered by domain."""
    scenarios = []
    for domain_dir in sorted(SCENARIOS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        if domain and domain_dir.name != domain:
            continue
        for yaml_file in sorted(domain_dir.glob("*.yaml")):
            if yaml_file.name.startswith("_"):
                continue
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data and "scenarios" in data:
                scenarios.extend(data["scenarios"])
    return scenarios


def execute_scenario(scenario: dict, odoo_url: str, db: str, config: dict) -> dict:
    """Execute a single benchmark scenario and return evidence envelope.

    TODO: Implement JSON-RPC connection to Odoo, copilot invocation,
    evidence capture, and gate evaluation. This is the Epic 3 deliverable.
    """
    now = datetime.now(timezone.utc)
    sid = scenario["id"]
    cap_class = scenario["capability_class"]

    # Placeholder: return NOT_IMPLEMENTED envelope
    envelope = {
        "scenario_id": sid,
        "timestamp": now.isoformat(),
        "odoo_version": "19.0",
        "copilot_version": "0.0.0",
        "benchmark_version": config.get("benchmark", {}).get("version", "1.0.0"),
        "persona": scenario.get("persona"),
        "prompt": scenario.get("prompt"),
        "response": None,
        "action_trace": None,
        "retrieved_sources": None,
        "hard_gates": {
            "capability": False,
            "correctness": False,
        },
        "soft_scores": {},
        "latency_ms": 0,
        "weighted_score": 0.0,
        "result": "NOT_IMPLEMENTED",
        "notes": "Runner not yet connected to Odoo. Epic 3 pending.",
    }

    return envelope


def compute_scores(envelopes: list[dict], config: dict) -> dict:
    """Compute aggregate scores from evidence envelopes.

    TODO: Implement domain/class/overall aggregation. Epic 4 deliverable.
    """
    total = len(envelopes)
    passed = sum(1 for e in envelopes if e["result"] == "PASS")
    failed = sum(1 for e in envelopes if e["result"] == "FAIL")
    not_impl = sum(1 for e in envelopes if e["result"] == "NOT_IMPLEMENTED")
    errors = sum(1 for e in envelopes if e["result"] == "ERROR")

    return {
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "not_implemented": not_impl,
        "errors": errors,
        "pass_rate": passed / total if total > 0 else 0,
    }


def generate_report(envelopes: list[dict], scores: dict, config: dict) -> str:
    """Generate Markdown summary report.

    TODO: Full per-domain/per-class tables. Epic 6 deliverable.
    """
    now = datetime.now(timezone.utc)
    lines = [
        f"# Odoo Copilot Benchmark — Run {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- Scenarios: {scores['total_scenarios']}",
        f"- Passed: {scores['passed']}",
        f"- Failed: {scores['failed']}",
        f"- Not Implemented: {scores['not_implemented']}",
        f"- Errors: {scores['errors']}",
        f"- Pass Rate: {scores['pass_rate']:.0%}",
        "",
        "## Scenario Results",
        "",
        "| ID | Domain | Class | Persona | Result |",
        "|---|---|---|---|---|",
    ]
    for e in envelopes:
        lines.append(
            f"| {e['scenario_id']} | {e.get('persona', '-')} | "
            f"{e.get('result', '-')} | {e.get('result', '-')} | {e['result']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run Odoo Copilot Benchmark")
    parser.add_argument("--url", default="http://localhost:8069", help="Odoo URL")
    parser.add_argument("--db", default="odoo_dev", help="Odoo database")
    parser.add_argument("--domain", help="Run only this domain")
    parser.add_argument("--dry-run", action="store_true", help="Validate scenarios without executing")
    args = parser.parse_args()

    config = load_config()
    scenarios = load_scenarios(args.domain)

    if not scenarios:
        print("No scenarios found.")
        sys.exit(1)

    print(f"Loaded {len(scenarios)} scenarios")

    if args.dry_run:
        print("Dry run — skipping execution.")
        for s in scenarios:
            print(f"  {s['id']}: {s['capability_class']} / {s['domain']} / {s['persona']}")
        sys.exit(0)

    # Execute scenarios
    envelopes = []
    for scenario in scenarios:
        print(f"  Running {scenario['id']}...", end=" ")
        envelope = execute_scenario(scenario, args.url, args.db, config)
        envelopes.append(envelope)
        print(envelope["result"])

    # Compute scores
    scores = compute_scores(envelopes, config)

    # Write evidence
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    evidence_dir = EVIDENCE_ROOT / timestamp / "copilot-benchmark"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = evidence_dir / "results.json"
    with open(evidence_path, "w") as f:
        json.dump({"envelopes": envelopes, "scores": scores}, f, indent=2)

    report_path = evidence_dir / "report.md"
    report = generate_report(envelopes, scores, config)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nResults: {scores['passed']}/{scores['total_scenarios']} passed")
    print(f"Evidence: {evidence_path}")
    print(f"Report:   {report_path}")


if __name__ == "__main__":
    main()
