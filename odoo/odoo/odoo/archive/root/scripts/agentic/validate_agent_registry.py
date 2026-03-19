#!/usr/bin/env python3
"""Validate agent registry completeness and maturity.

Ensures every registered agent has:
- All required fields populated
- Referenced files (persona, loop, policies) actually exist
- Memory contract with schema + version
- No duplicate agent IDs
- No "prompt-only" agents (all refs must point to real files)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"
REGISTRY = AGENTS_DIR / "registry" / "agents.json"

REQUIRED_FIELDS = [
    "id",
    "name",
    "owner",
    "status",
    "persona_ref",
    "loop_ref",
    "policies_ref",
    "memory_contract",
    "skills",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not REGISTRY.exists():
        fail(f"Missing registry: {REGISTRY}")

    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {REGISTRY}: {e}")

    if not isinstance(data, dict) or "agents" not in data:
        fail("agents/registry/agents.json must have top-level 'agents' key")

    agents = data["agents"]
    if not isinstance(agents, list):
        fail("'agents' must be an array")

    if len(agents) == 0:
        fail("Agent registry is empty. At least one agent required.")

    ids: set[str] = set()
    errors: list[str] = []

    for agent in agents:
        if not isinstance(agent, dict):
            errors.append("Each agent entry must be an object")
            continue

        agent_id = agent.get("id", "<no id>")

        # Check required fields
        for field in REQUIRED_FIELDS:
            val = agent.get(field)
            if val is None or val == "" or val == [] or val == {}:
                errors.append(f"Agent '{agent_id}' missing required field: {field}")

        # Check for duplicate IDs
        if agent_id in ids:
            errors.append(f"Duplicate agent id: {agent_id}")
        ids.add(agent_id)

        # Validate file references exist (no prompt-only agents)
        for ref_field in ("persona_ref", "loop_ref", "policies_ref"):
            ref_val = agent.get(ref_field)
            if ref_val:
                ref_path = AGENTS_DIR / ref_val
                if not ref_path.exists():
                    errors.append(
                        f"Agent '{agent_id}' references missing file: "
                        f"{ref_field} -> {ref_path.relative_to(ROOT)}"
                    )

        # Validate memory contract structure
        mc = agent.get("memory_contract")
        if isinstance(mc, dict):
            if "schema" not in mc or "version" not in mc:
                errors.append(
                    f"Agent '{agent_id}' memory_contract must include 'schema' + 'version'"
                )
        elif mc is not None:
            errors.append(
                f"Agent '{agent_id}' memory_contract must be an object with schema + version"
            )

    if errors:
        print("Agent Registry Validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Agent registry OK: {len(agents)} agent(s) validated")


if __name__ == "__main__":
    main()
