#!/usr/bin/env python3
"""Generate MCP client configs from SSOT registry."""
import json
import pathlib
import yaml
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "adapters"


def load_registry() -> Dict[str, Any]:
    """Load MCP registry."""
    with open(ROOT / "mcp/registry/servers.yaml") as f:
        return yaml.safe_load(f)


def load_secrets_schema() -> Dict[str, Any]:
    """Load secrets schema."""
    with open(ROOT / "secrets/schema.json") as f:
        return json.load(f)


def gen_claude_code_config(registry: Dict[str, Any]) -> None:
    """Generate Claude Code CLI MCP config."""
    config = {"mcpServers": {}}
    
    # External servers
    for name, spec in registry.get("external_servers", {}).items():
        config["mcpServers"][name] = {
            "command": spec["command"],
            "args": spec["args"],
            "env": {k: f"${k}" for k in spec.get("env_required", [])}
        }
    
    # Custom servers
    for name, spec in registry.get("custom_servers", {}).items():
        if spec.get("build_required"):
            config["mcpServers"][name] = {
                "command": spec["command"],
                "args": [str(ROOT / spec["path"] / spec["args"][0])],
                "env": {k: f"${k}" for k in spec.get("env_required", [])}
            }
    
    out = ADAPTERS / "claude-code" / "mcp-servers.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated {out}")


def gen_claude_desktop_config(registry: Dict[str, Any]) -> None:
    """Generate Claude Desktop MCP config."""
    config = {"mcpServers": {}}
    
    # External servers only (local STDIO)
    for name, spec in registry.get("external_servers", {}).items():
        config["mcpServers"][name] = {
            "command": spec["command"],
            "args": spec["args"],
            "env": {k: f"${k}" for k in spec.get("env_required", [])}
        }
    
    out = ADAPTERS / "claude-desktop" / "claude_desktop_config.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated {out}")


def gen_cursor_config(registry: Dict[str, Any]) -> None:
    """Generate Cursor project-level MCP config."""
    config = {
        "version": "1.0",
        "mcp": {
            "servers": {}
        }
    }
    
    # All servers for Cursor (full IDE integration)
    for name, spec in registry.get("external_servers", {}).items():
        config["mcp"]["servers"][name] = {
            "command": spec["command"],
            "args": spec["args"],
            "env": {k: f"${k}" for k in spec.get("env_required", [])}
        }
    
    out = ADAPTERS / "cursor" / ".cursor-mcp.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated {out}")


def gen_vercel_sandbox_config(registry: Dict[str, Any]) -> None:
    """Generate Vercel Sandbox MCP config (env vars)."""
    env_vars = []
    secrets_schema = load_secrets_schema()
    
    for category in secrets_schema.get("required", {}).values():
        for var_name in category.keys():
            env_vars.append(var_name)
    
    config = {
        "version": "1.0",
        "sandbox": {
            "mcp_servers": list(registry.get("external_servers", {}).keys()),
            "env_required": sorted(set(env_vars))
        }
    }
    
    out = ADAPTERS / "vercel-sandbox" / "mcp-env.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated {out}")


def gen_e2b_config(registry: Dict[str, Any]) -> None:
    """Generate E2B sandbox MCP config."""
    config = {
        "version": "1.0",
        "e2b": {
            "template": "node-20",
            "mcp_servers": [],
            "env": {}
        }
    }
    
    # External servers only (remote execution)
    for name, spec in registry.get("external_servers", {}).items():
        config["e2b"]["mcp_servers"].append({
            "name": name,
            "command": spec["command"],
            "args": spec["args"]
        })
        for env_var in spec.get("env_required", []):
            config["e2b"]["env"][env_var] = f"${env_var}"
    
    out = ADAPTERS / "e2b" / "mcp-config.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated {out}")


def main():
    """Generate all MCP client adapters."""
    registry = load_registry()
    
    ADAPTERS.mkdir(parents=True, exist_ok=True)
    (ADAPTERS / "README.md").write_text(
        "# MCP Client Adapters\n\n"
        "Generated from `mcp/registry/servers.yaml`. **DO NOT EDIT MANUALLY.**\n\n"
        "Regenerate with: `python scripts/gen_mcp_adapters.py`\n"
    )
    
    gen_claude_code_config(registry)
    gen_claude_desktop_config(registry)
    gen_cursor_config(registry)
    gen_vercel_sandbox_config(registry)
    gen_e2b_config(registry)
    
    print("\n✅ All MCP adapters generated successfully")


if __name__ == "__main__":
    main()
