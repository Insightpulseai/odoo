#!/usr/bin/env python3
"""Validate benchmark scenario YAML files against the schema.

Usage:
    python scripts/benchmark/validate_scenarios.py
    python scripts/benchmark/validate_scenarios.py --domain crm
"""

import argparse
import sys
from pathlib import Path

import yaml


SPEC_ROOT = Path(__file__).resolve().parent.parent.parent / "spec" / "odoo-copilot-benchmark"
SCENARIOS_DIR = SPEC_ROOT / "scenarios"

VALID_DOMAINS = {
    "crm", "sales", "purchase", "accounting", "inventory",
    "project-helpdesk", "settings-admin", "knowledge-sop", "documents",
}
VALID_CLASSES = {"transactional", "navigational", "informational"}
VALID_PERSONAS = {
    "sales_rep", "sales_mgr", "accountant", "inv_operator",
    "project_mgr", "admin", "exec_readonly",
}
VALID_TYPES = {
    "create", "write", "unlink", "action",
    "navigate", "search", "aggregate", "rag_retrieve",
}
VALID_RESULTS = {"PASS", "FAIL", "NOT_IMPLEMENTED", "ERROR"}

ID_PATTERN_DOMAIN_MAP = {
    "CRM": "crm",
    "SAL": "sales",
    "PUR": "purchase",
    "ACC": "accounting",
    "INV": "inventory",
    "PRJ": "project-helpdesk",
    "ADM": "settings-admin",
    "KNW": "knowledge-sop",
    "DOC": "documents",
}

HARD_GATES_REQUIRED = {
    "transactional": {"capability", "correctness", "permission_check", "confirmation_required", "audit_trace"},
    "navigational": {"capability", "correctness", "permission_check"},
    "informational": {"capability", "correctness", "grounding"},
}


def validate_scenario(scenario: dict, file_path: Path) -> list[str]:
    """Validate a single scenario dict. Returns list of error messages."""
    errors = []
    sid = scenario.get("id", "<missing id>")

    # Required fields
    for field in ("id", "domain", "capability_class", "persona", "prompt", "expected_behavior", "hard_gates"):
        if field not in scenario:
            errors.append(f"{sid}: missing required field '{field}'")

    # ID format
    sid_str = str(sid)
    if not (sid_str.startswith("BM-") and len(sid_str.split("-")) == 3):
        # More lenient: BM-XXX-X-NNN has 4 parts with first being BM
        parts = sid_str.split("-")
        if len(parts) != 4 or parts[0] != "BM":
            errors.append(f"{sid}: ID must match BM-<DOMAIN>-<T|N|I>-<NNN>")

    # Domain
    domain = scenario.get("domain")
    if domain and domain not in VALID_DOMAINS:
        errors.append(f"{sid}: invalid domain '{domain}'")

    # Capability class
    cap_class = scenario.get("capability_class")
    if cap_class and cap_class not in VALID_CLASSES:
        errors.append(f"{sid}: invalid capability_class '{cap_class}'")

    # Persona
    persona = scenario.get("persona")
    if persona and persona not in VALID_PERSONAS:
        errors.append(f"{sid}: invalid persona '{persona}'")

    # Expected behavior type
    eb = scenario.get("expected_behavior", {})
    eb_type = eb.get("type")
    if eb_type and eb_type not in VALID_TYPES:
        errors.append(f"{sid}: invalid expected_behavior.type '{eb_type}'")

    # Hard gates: check required gates per class
    if cap_class and cap_class in HARD_GATES_REQUIRED:
        hard_gates = scenario.get("hard_gates", {})
        required = HARD_GATES_REQUIRED[cap_class]
        present = set(k for k, v in hard_gates.items() if v is True)
        missing = required - present
        if missing:
            errors.append(f"{sid}: missing required hard gates for {cap_class}: {missing}")

    # Prompt length
    prompt = scenario.get("prompt", "")
    if len(prompt) < 10:
        errors.append(f"{sid}: prompt too short (min 10 chars)")

    return errors


def validate_file(file_path: Path) -> list[str]:
    """Validate all scenarios in a YAML file."""
    errors = []
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"{file_path}: YAML parse error: {e}"]

    if not data or "scenarios" not in data:
        return [f"{file_path}: missing 'scenarios' key"]

    scenarios = data["scenarios"]
    if not isinstance(scenarios, list):
        return [f"{file_path}: 'scenarios' must be a list"]

    seen_ids = set()
    for scenario in scenarios:
        sid = scenario.get("id", "<unknown>")
        if sid in seen_ids:
            errors.append(f"{file_path}: duplicate scenario ID '{sid}'")
        seen_ids.add(sid)
        errors.extend(validate_scenario(scenario, file_path))

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate benchmark scenarios")
    parser.add_argument("--domain", help="Validate only this domain")
    args = parser.parse_args()

    all_errors = []
    scenario_count = 0
    file_count = 0

    for domain_dir in sorted(SCENARIOS_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_dir.name.startswith("_"):
            continue
        if args.domain and domain_dir.name != args.domain:
            continue

        for yaml_file in sorted(domain_dir.glob("*.yaml")):
            if yaml_file.name.startswith("_"):
                continue
            file_count += 1
            file_errors = validate_file(yaml_file)
            all_errors.extend(file_errors)

            # Count scenarios
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if data and "scenarios" in data:
                    scenario_count += len(data["scenarios"])
            except Exception:
                pass

    # Summary
    print(f"Validated {file_count} files, {scenario_count} scenarios")

    if all_errors:
        print(f"\n{len(all_errors)} errors found:\n")
        for err in all_errors:
            print(f"  ERROR: {err}")
        sys.exit(1)
    else:
        print("All scenarios valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
