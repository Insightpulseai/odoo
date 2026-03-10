#!/bin/bash
# IPAI AI Agent Seed Script
# Idempotent loader for YAML agent configurations into Odoo
#
# Usage: ./scripts/ipai_ai_seed.sh [config_dir] [db_name]
#
# This script:
# 1. Reads YAML agent configurations from config/ipai_ai/agents/
# 2. Creates or updates agents, topics, and tool assignments in Odoo
# 3. Is idempotent - safe to run multiple times

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CONFIG_DIR="${1:-$REPO_ROOT/config/ipai_ai/agents}"
DB_NAME="${2:-odoo_core}"
CONTAINER_NAME="${CONTAINER_NAME:-odoo-core}"

echo "=== IPAI AI Agent Seed Script ==="
echo "Config directory: $CONFIG_DIR"
echo "Database: $DB_NAME"
echo "Container: $CONTAINER_NAME"
echo ""

# Check if config directory exists
if [[ ! -d "$CONFIG_DIR" ]]; then
    echo "ERROR: Config directory not found: $CONFIG_DIR"
    exit 1
fi

# Check if any YAML files exist
YAML_FILES=$(find "$CONFIG_DIR" -name "*.yaml" -o -name "*.yml" 2>/dev/null || true)
if [[ -z "$YAML_FILES" ]]; then
    echo "WARNING: No YAML files found in $CONFIG_DIR"
    exit 0
fi

# Generate Python seed script
SEED_SCRIPT=$(cat <<'PYTHON_SCRIPT'
#!/usr/bin/env python3
# Auto-generated seed script for IPAI AI agents
import os
import sys
import yaml
from pathlib import Path

def load_yaml_configs(config_dir):
    """Load all YAML config files from directory."""
    configs = []
    for path in Path(config_dir).glob("*.yaml"):
        with open(path) as f:
            data = yaml.safe_load(f)
            if data and "agents" in data:
                configs.extend(data["agents"])
    for path in Path(config_dir).glob("*.yml"):
        with open(path) as f:
            data = yaml.safe_load(f)
            if data and "agents" in data:
                configs.extend(data["agents"])
    return configs

def seed_agents(env, configs):
    """Create or update agents from configuration."""
    Agent = env["ipai.ai.agent"]
    Topic = env["ipai.ai.topic"]
    Tool = env["ipai.ai.tool"]

    stats = {"agents_created": 0, "agents_updated": 0, "topics_created": 0}

    for config in configs:
        agent_key = config.get("key", config["name"].lower().replace(" ", "_"))

        # Find or create agent
        agent = Agent.search([("name", "=", config["name"])], limit=1)
        agent_vals = {
            "name": config["name"],
            "system_prompt": config.get("system_prompt", ""),
            "style": config.get("style", "professional"),
            "provider": config.get("provider", "openai"),
            "model": config.get("model", "gpt-4o"),
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2048),
            "active": config.get("enabled", True),
        }

        if agent:
            agent.write(agent_vals)
            stats["agents_updated"] += 1
            print(f"  Updated agent: {config['name']}")
        else:
            agent = Agent.create(agent_vals)
            stats["agents_created"] += 1
            print(f"  Created agent: {config['name']}")

        # Process topics
        for topic_config in config.get("topics", []):
            topic = Topic.search([
                ("agent_id", "=", agent.id),
                ("name", "=", topic_config["name"])
            ], limit=1)

            # Resolve tool IDs
            tool_ids = []
            for tool_key in topic_config.get("tools", []):
                tool = Tool.search([("key", "=", tool_key)], limit=1)
                if tool:
                    tool_ids.append(tool.id)
                else:
                    print(f"    WARNING: Tool not found: {tool_key}")

            topic_vals = {
                "name": topic_config["name"],
                "agent_id": agent.id,
                "instructions": topic_config.get("instructions", ""),
                "tool_ids": [(6, 0, tool_ids)],
            }

            if topic:
                topic.write(topic_vals)
                print(f"    Updated topic: {topic_config['name']}")
            else:
                Topic.create(topic_vals)
                stats["topics_created"] += 1
                print(f"    Created topic: {topic_config['name']}")

    return stats

if __name__ == "__main__":
    config_dir = sys.argv[1] if len(sys.argv) > 1 else "/mnt/extra-addons/config/ipai_ai/agents"

    # When run inside Odoo shell, env is available
    configs = load_yaml_configs(config_dir)
    print(f"Loaded {len(configs)} agent configurations")

    if configs:
        stats = seed_agents(env, configs)
        print(f"\nSeed complete:")
        print(f"  Agents created: {stats['agents_created']}")
        print(f"  Agents updated: {stats['agents_updated']}")
        print(f"  Topics created: {stats['topics_created']}")
        env.cr.commit()
    else:
        print("No configurations to process")
PYTHON_SCRIPT
)

# Write seed script to temp file
TEMP_SEED_SCRIPT=$(mktemp)
echo "$SEED_SCRIPT" > "$TEMP_SEED_SCRIPT"

# Check if running in Docker or native
if command -v docker &> /dev/null && docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
    echo "Running in Docker container: $CONTAINER_NAME"

    # Copy config files and script to container
    docker cp "$CONFIG_DIR" "$CONTAINER_NAME":/tmp/ipai_ai_config/
    docker cp "$TEMP_SEED_SCRIPT" "$CONTAINER_NAME":/tmp/ipai_ai_seed.py

    # Run seed script via odoo shell
    docker exec "$CONTAINER_NAME" python3 /usr/bin/odoo shell -d "$DB_NAME" --no-http < "$TEMP_SEED_SCRIPT" <<EOF
import sys
sys.path.insert(0, '/tmp')
exec(open('/tmp/ipai_ai_seed.py').read())
exit()
EOF

else
    echo "Running locally (requires Odoo environment)"
    echo "Please run this script inside Odoo shell or Docker container"
    echo ""
    echo "For Docker:"
    echo "  docker compose exec odoo-core odoo shell -d $DB_NAME < scripts/ipai_ai_seed.py"
    echo ""
    echo "For local development:"
    echo "  odoo shell -d $DB_NAME < scripts/ipai_ai_seed.py"
fi

# Cleanup
rm -f "$TEMP_SEED_SCRIPT"

echo ""
echo "=== Seed script completed ==="
