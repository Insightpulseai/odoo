"""
Create or update the Odoo Copilot agent in Azure AI Foundry.

Usage:
    python create_agent.py
    python create_agent.py --dry-run

Requires:
    pip install azure-ai-projects azure-identity
    FOUNDRY_PROJECT_ENDPOINT env var set

References:
    https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview
"""

import os
import json
import yaml
import argparse
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "agent_config.yaml"


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def create_agent(config, dry_run=False):
    agent = config["agent"]
    tools = config["tools"]
    instructions = config["instructions"]

    print(f"Agent: {agent['display_name']}")
    print(f"Model: {agent['model']}")
    print(f"Project: {agent['project']}")
    print(f"Tools: {len(tools)}")
    print(f"Instructions: {len(instructions)} chars")
    print(f"Search: {config['search']['service']}/{config['search']['index']}")
    print(f"Auth: {config['auth']['mode']}")
    print()

    if dry_run:
        print("[DRY RUN] Would create agent with the above config.")
        print()
        print("Tool list:")
        for t in tools:
            fname = t.get("function", {}).get("name", "?")
            print(f"  - {fname}")
        return

    # Real creation requires azure-ai-projects SDK
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        endpoint = os.environ.get(
            "FOUNDRY_PROJECT_ENDPOINT",
            "https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph"
        )

        client = AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )

        # Create the agent
        agent_result = client.agents.create_agent(
            model=agent["model"],
            name=agent["name"],
            instructions=instructions,
            tools=[
                {"type": t["type"], "function": t["function"]}
                for t in tools
            ],
        )

        print(f"Agent created: {agent_result.id}")
        print(f"Name: {agent_result.name}")
        print(f"Model: {agent_result.model}")

        # Save agent ID for future reference
        with open(Path(__file__).parent / "agent_id.txt", "w") as f:
            f.write(agent_result.id)
        print(f"Agent ID saved to agent_id.txt")

    except ImportError:
        print("ERROR: azure-ai-projects not installed.")
        print("Run: pip install azure-ai-projects azure-identity")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config()
    create_agent(config, dry_run=args.dry_run)
