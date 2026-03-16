#!/usr/bin/env python3
"""Odoo Copilot Benchmark Runner.

Executes benchmark scenarios against a running Odoo instance,
captures evidence, computes scores, and generates reports.

Usage:
    python scripts/benchmark/run_benchmark.py --url http://localhost:8069 --db odoo_dev
    python scripts/benchmark/run_benchmark.py --domain crm --dry-run
    python scripts/benchmark/run_benchmark.py --domain crm --url http://localhost:8069 --db odoo_dev

Prerequisites:
    - Running Odoo instance with ipai_ai_copilot installed
    - Benchmark personas seeded (7 users with correct groups)
    - Demo data seeded for target domains
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Allow imports from this directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runner import ScenarioRunner          # noqa: E402
from evaluator import compute_overall_scores  # noqa: E402
from reporter import generate_markdown_report  # noqa: E402
from evidence import (                     # noqa: E402
    get_evidence_dir,
    write_envelopes,
    write_scores,
    write_report,
    write_summary,
)

SPEC_ROOT = Path(__file__).resolve().parent.parent.parent / "spec" / "odoo-copilot-benchmark"
SCENARIOS_DIR = SPEC_ROOT / "scenarios"
CONFIG_PATH = SPEC_ROOT / "benchmark.config.yaml"


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


def main():
    parser = argparse.ArgumentParser(description="Run Odoo Copilot Benchmark")
    parser.add_argument("--url", default="http://localhost:8069", help="Odoo URL")
    parser.add_argument("--db", default="odoo_dev", help="Odoo database")
    parser.add_argument("--domain", help="Run only this domain")
    parser.add_argument("--dry-run", action="store_true", help="List scenarios without executing")
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
    runner = ScenarioRunner(args.url, args.db, config)
    envelopes = []
    for scenario in scenarios:
        print(f"  Running {scenario['id']}...", end=" ", flush=True)
        envelope = runner.execute(scenario)
        envelopes.append(envelope)
        print(envelope["result"])

    # Compute scores
    scores = compute_overall_scores(envelopes, config)

    # Generate report
    report_md = generate_markdown_report(envelopes, scores, config)

    # Write evidence
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    evidence_dir = get_evidence_dir(timestamp)
    env_path = write_envelopes(evidence_dir, envelopes)
    scores_path = write_scores(evidence_dir, scores)
    report_path = write_report(evidence_dir, report_md)
    summary_path = write_summary(evidence_dir, envelopes, scores)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"Benchmark complete: {scores['passed']}/{scores['total']} passed")
    print(f"  Pass rate:      {scores['pass_rate']:.0%}")
    print(f"  Avg score:      {scores['avg_weighted_score']:.1%}")
    print(f"  Certified:      {'YES' if scores['certified'] else 'NO'}")
    print(f"  Evidence:       {evidence_dir}")
    print(f"    envelopes:    {env_path.name}")
    print(f"    scores:       {scores_path.name}")
    print(f"    report:       {report_path.name}")
    print(f"    summary:      {summary_path.name}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
