#!/usr/bin/env python3
"""
register_agent_v2.py — Register named agents in Microsoft Foundry (SDK v2).

Reads agent definitions from ssot/ai/agents.yaml and instructions from
ssot/ai/foundry_instructions.md, then registers each agent via
project.agents.create_version().

Usage:
    python scripts/foundry/register_agent_v2.py --agent pulser-odoo-ask \
        [--dry-run]
    python scripts/foundry/register_agent_v2.py --all [--dry-run]

Environment:
    Uses DefaultAzureCredential (managed identity or az login).
    No API keys required.

SSOT: ssot/ai/agents.yaml
SDK:  azure-ai-projects >= 2.0.0
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# SSOT paths
AGENTS_YAML = REPO_ROOT / "ssot" / "ai" / "agents.yaml"
INSTRUCTIONS_MD = REPO_ROOT / "ssot" / "ai" / "foundry_instructions.md"

# Instruction section markers (mapped from prompts.yaml)
SECTION_MAP = {
    "pulser-odoo-ask": "## Ask Agent Mode",
    "pulser-odoo-authoring": "## Authoring Agent Mode",
    "pulser-odoo-livechat": "## Livechat Agent Mode",
    "pulser-odoo-transaction": "## Transaction Agent Mode",
}


def load_instructions() -> dict[str, str]:
    """Load and parse instruction sections from foundry_instructions.md.

    Returns dict mapping section header to full instruction text
    (global rules + agent-specific section).
    """
    text = INSTRUCTIONS_MD.read_text(encoding="utf-8")

    # Extract global rules (everything before first ## Agent Mode section)
    lines = text.split("\n")
    global_lines = []
    agent_sections: dict[str, list[str]] = {}
    current_section = None

    for line in lines:
        if any(line.strip().startswith(marker) for marker in SECTION_MAP.values()):
            current_section = line.strip()
            agent_sections[current_section] = [line]
        elif line.strip().startswith("## Mode Detection"):
            current_section = None  # skip mode detection section
        elif current_section:
            agent_sections[current_section].append(line)
        elif not line.strip().startswith("## "):
            global_lines.append(line)

    global_text = "\n".join(global_lines).strip()

    # Build per-agent instructions: global + agent-specific
    result = {}
    for agent_name, section_header in SECTION_MAP.items():
        section_lines = agent_sections.get(section_header, [])
        section_text = "\n".join(section_lines).strip()
        result[agent_name] = f"{global_text}\n\n---\n\n{section_text}"

    return result


def load_agents_yaml() -> dict:
    """Load agents.yaml using basic YAML parsing."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    with open(AGENTS_YAML) as f:
        return yaml.safe_load(f)


def register_agent(agent_name: str, instructions: str, model: str,
                   project_endpoint: str, dry_run: bool = False) -> dict:
    """Register a named agent in Foundry via SDK v2."""

    print(f"\n{'=' * 60}")
    print(f"Agent:        {agent_name}")
    print(f"Model:        {model}")
    print(f"Instructions: {len(instructions)} chars")
    print(f"Endpoint:     {project_endpoint}")

    if dry_run:
        print(f"\n[DRY RUN] Would call project.agents.create_version(")
        print(f"    agent_name='{agent_name}',")
        print(f"    definition=PromptAgentDefinition(")
        print(f"        model='{model}',")
        print(f"        instructions='<{len(instructions)} chars>',")
        print(f"    )")
        print(f")")
        return {"status": "dry_run", "agent_name": agent_name}

    try:
        from azure.ai.projects import AIProjectClient
        from azure.ai.projects.models import PromptAgentDefinition
        from azure.identity import DefaultAzureCredential, AzureCliCredential
    except ImportError as e:
        print(f"ERROR: Missing SDK dependency: {e}", file=sys.stderr)
        print("Install: pip install azure-ai-projects>=2.0.0 azure-identity", file=sys.stderr)
        sys.exit(1)

    # Try CLI credential first (works locally), fallback to Default
    try:
        cred = AzureCliCredential()
        cred.get_token("https://ai.azure.com/.default")
    except Exception:
        cred = DefaultAzureCredential()

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=cred,
    )

    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions=instructions,
        ),
    )

    print(f"\nRegistered successfully.")
    print(f"  Name:    {agent_name}")
    print(f"  Version: {agent.version}")
    print(f"  Model:   {model}")

    return {
        "status": "registered",
        "agent_name": agent_name,
        "version": agent.version,
    }


def main():
    parser = argparse.ArgumentParser(description="Register named agents in Foundry (SDK v2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--agent", type=str,
        help="Agent name to register (e.g. pulser-odoo-ask)",
    )
    group.add_argument("--all", action="store_true", help="Register all agents")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be registered")
    parser.add_argument("--model", type=str, default=None, help="Override model (default: from agents.yaml)")
    args = parser.parse_args()

    # Load SSOT
    config = load_agents_yaml()
    project_config = config.get("foundry_project", {})
    project_endpoint = project_config.get("project_endpoint")
    default_model = "gpt-4.1"  # from agents.yaml model_deployments

    if not project_endpoint:
        print("ERROR: project_endpoint not found in agents.yaml", file=sys.stderr)
        sys.exit(1)

    instructions = load_instructions()
    agents = config.get("agents", {})

    # Determine which agents to register
    if args.all:
        target_agents = list(agents.keys())
    else:
        if args.agent not in agents:
            print(f"ERROR: Agent '{args.agent}' not found in agents.yaml", file=sys.stderr)
            print(f"Available: {', '.join(agents.keys())}", file=sys.stderr)
            sys.exit(1)
        target_agents = [args.agent]

    model = args.model or default_model
    results = []

    for agent_name in target_agents:
        agent_instructions = instructions.get(agent_name)
        if not agent_instructions:
            print(f"WARNING: No instructions found for {agent_name}, skipping", file=sys.stderr)
            continue

        result = register_agent(
            agent_name=agent_name,
            instructions=agent_instructions,
            model=model,
            project_endpoint=project_endpoint,
            dry_run=args.dry_run,
        )
        results.append(result)

    print(f"\n{'=' * 60}")
    print(f"Summary: {len(results)} agent(s) processed")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
