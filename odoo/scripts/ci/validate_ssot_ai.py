#!/usr/bin/env python3
"""SSOT AI Manifest Integrity Validator.

Validates cross-references between ssot/ai/*.yaml manifests:
- Orphaned IDs (referenced but not defined)
- Invalid policy references
- Invalid source references
- Missing Foundry runtime defaults
- Logical agent → physical agent mapping issues
- Prompt → agent mapping issues

Usage:
    python scripts/ci/validate_ssot_ai.py [--ssot-dir ssot/ai]

Exit codes:
    0 = all checks pass
    1 = validation errors found
    2 = file/parse error
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse {path}: {e}", file=sys.stderr)
        sys.exit(2)


def validate(ssot_dir):
    errors = []
    ssot = Path(ssot_dir)

    # Load all manifests
    agents_data = load_yaml(ssot / "agents.yaml")
    models_data = load_yaml(ssot / "models.yaml")
    policies_data = load_yaml(ssot / "policies.yaml")
    sources_data = load_yaml(ssot / "sources.yaml")
    prompts_data = load_yaml(ssot / "prompts.yaml")

    if agents_data is None:
        errors.append("agents.yaml not found")
        return errors
    if models_data is None:
        errors.append("models.yaml not found")
    if policies_data is None:
        errors.append("policies.yaml not found")
    if sources_data is None:
        errors.append("sources.yaml not found")
    if prompts_data is None:
        errors.append("prompts.yaml not found")

    if errors:
        return errors

    agents = agents_data.get("agents", {})
    models = models_data.get("models", {})
    policies = policies_data.get("policies", {})
    sources = sources_data.get("sources", {})
    prompts = prompts_data.get("prompts", {})

    agent_ids = set(agents.keys())
    model_ids = set(models.keys())
    policy_ids = set(policies.keys())
    source_ids = set(sources.keys())
    prompt_ids = set(prompts.keys())

    physical_agents = {
        k for k, v in agents.items() if v.get("type") == "physical"
    }
    logical_agents = {
        k for k, v in agents.items() if v.get("type") == "logical"
    }

    # 1. Physical agents must have model_ref in models.yaml
    for agent_id, agent in agents.items():
        if agent.get("type") != "physical":
            continue
        model_ref = agent.get("model_ref")
        if model_ref and model_ref not in model_ids:
            errors.append(
                f"agents.yaml: {agent_id}.model_ref '{model_ref}' "
                f"not found in models.yaml"
            )
        # Must have memory_default and read_only_default
        if "memory_default" not in agent:
            errors.append(
                f"agents.yaml: {agent_id} missing memory_default"
            )
        if "read_only_default" not in agent:
            errors.append(
                f"agents.yaml: {agent_id} missing read_only_default"
            )

    # 2. Logical agents must reference valid physical agent
    for agent_id, agent in agents.items():
        if agent.get("type") != "logical":
            continue
        phys_ref = agent.get("physical_agent_ref")
        if phys_ref and phys_ref not in physical_agents:
            errors.append(
                f"agents.yaml: {agent_id}.physical_agent_ref '{phys_ref}' "
                f"not found as physical agent"
            )

    # 3. Logical agents: policy_ref must exist in policies.yaml
    for agent_id, agent in agents.items():
        if agent.get("type") != "logical":
            continue
        policy_ref = agent.get("policy_ref")
        if policy_ref and policy_ref not in policy_ids:
            errors.append(
                f"agents.yaml: {agent_id}.policy_ref '{policy_ref}' "
                f"not found in policies.yaml"
            )

    # 4. Logical agents: prompt_ref must exist in prompts.yaml
    for agent_id, agent in agents.items():
        if agent.get("type") != "logical":
            continue
        prompt_ref = agent.get("prompt_ref")
        if prompt_ref and prompt_ref not in prompt_ids:
            errors.append(
                f"agents.yaml: {agent_id}.prompt_ref '{prompt_ref}' "
                f"not found in prompts.yaml"
            )

    # 5. Logical agents: source_refs must exist in sources.yaml
    for agent_id, agent in agents.items():
        if agent.get("type") != "logical":
            continue
        for src_ref in agent.get("source_refs", []):
            if src_ref not in source_ids:
                errors.append(
                    f"agents.yaml: {agent_id}.source_refs '{src_ref}' "
                    f"not found in sources.yaml"
                )

    # 6. Physical agent logical_agents must all be defined
    for agent_id, agent in agents.items():
        if agent.get("type") != "physical":
            continue
        for la in agent.get("logical_agents", []):
            if la not in logical_agents:
                errors.append(
                    f"agents.yaml: {agent_id}.logical_agents '{la}' "
                    f"not defined as logical agent"
                )

    # 7. Prompts: agent_ref must exist in agents.yaml
    for prompt_id, prompt in prompts.items():
        agent_ref = prompt.get("agent_ref")
        if agent_ref and agent_ref not in agent_ids:
            errors.append(
                f"prompts.yaml: {prompt_id}.agent_ref '{agent_ref}' "
                f"not found in agents.yaml"
            )

    # 8. Sources: used_by must reference valid agents
    for source_id, source in sources.items():
        for agent_ref in source.get("used_by", []):
            if agent_ref not in agent_ids:
                errors.append(
                    f"sources.yaml: {source_id}.used_by '{agent_ref}' "
                    f"not found in agents.yaml"
                )

    # 9. Models: used_by must reference valid agents
    for model_id, model in models.items():
        for agent_ref in model.get("used_by", []):
            if agent_ref not in agent_ids:
                errors.append(
                    f"models.yaml: {model_id}.used_by '{agent_ref}' "
                    f"not found in agents.yaml"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate SSOT AI manifest integrity"
    )
    parser.add_argument(
        "--ssot-dir",
        default="ssot/ai",
        help="Path to ssot/ai directory (default: ssot/ai)",
    )
    args = parser.parse_args()

    errors = validate(args.ssot_dir)

    if errors:
        print(f"FAIL: {len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("OK: All SSOT AI manifest cross-references are valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
