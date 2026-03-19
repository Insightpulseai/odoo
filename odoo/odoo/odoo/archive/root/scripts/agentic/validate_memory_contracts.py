#!/usr/bin/env python3
"""Validate agent memory contracts against platform contract.

Ensures:
- Platform memory contract exists and declares supported versions
- Every registered agent's memory_contract.version is supported
- Every registered agent's memory_contract.schema matches 'memory'
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"
REGISTRY = AGENTS_DIR / "registry" / "agents.json"

# Platform memory contract location
PLATFORM_DB = ROOT / "platform" / "db"
MEMORY_CONTRACT = PLATFORM_DB / "contracts" / "memory_contract.json"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not MEMORY_CONTRACT.exists():
        fail(f"Missing platform memory contract: {MEMORY_CONTRACT}")

    try:
        contract = json.loads(MEMORY_CONTRACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {MEMORY_CONTRACT}: {e}")

    supported = set(contract.get("supported_versions", []))
    if not supported:
        fail("memory_contract.json must include non-empty 'supported_versions'")

    if not REGISTRY.exists():
        fail(f"Missing agent registry: {REGISTRY}")

    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {REGISTRY}: {e}")

    agents = data.get("agents", [])
    errors: list[str] = []

    for agent in agents:
        agent_id = agent.get("id", "<no id>")
        mc = agent.get("memory_contract")

        if not isinstance(mc, dict):
            errors.append(f"Agent '{agent_id}' has no valid memory_contract")
            continue

        schema = mc.get("schema")
        version = mc.get("version")

        if schema != "memory":
            errors.append(
                f"Agent '{agent_id}' memory_contract.schema must be 'memory' (got '{schema}')"
            )

        if version not in supported:
            errors.append(
                f"Agent '{agent_id}' requests unsupported memory contract version: "
                f"'{version}' (supported: {sorted(supported)})"
            )

    if errors:
        print("Memory Contract Validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Memory contracts OK: {len(agents)} agent(s) compatible "
        f"with platform contract (versions: {sorted(supported)})"
    )


if __name__ == "__main__":
    main()
