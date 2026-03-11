#!/usr/bin/env python3
"""
MCP SSOT Validator — ensures .claude/mcp-servers.json matches ssot/mcp/servers.yaml.

Checks:
  1. Every server in mcp-servers.json exists in SSOT
  2. Every SSOT server exists in mcp-servers.json
  3. Auth type consistency (token/oauth/none/env)
  4. Transport type consistency (stdio/http)
  5. No blocked domains in any endpoint URL
  6. Status field matches (built/source_only)

Exit codes:
  0 = all checks pass
  1 = validation failures found
"""
import json
import sys
from pathlib import Path

import yaml


def load_mcp_config(path: Path) -> dict:
    """Load and parse MCP server config JSON."""
    with open(path) as f:
        data = json.load(f)
    return data.get("mcpServers", {})


def load_ssot(path: Path) -> dict:
    """Load SSOT YAML and return dict keyed by server id."""
    with open(path) as f:
        data = yaml.safe_load(f)
    servers = {}
    for s in data.get("servers", []):
        servers[s["id"]] = s
    return servers, data.get("blocked_domains", [])


def infer_auth_type(server_config: dict) -> str:
    """Infer auth type from MCP server config."""
    env_vars = server_config.get("env", {})
    if not env_vars:
        return "none"
    env_keys = " ".join(env_vars.keys()).lower()
    if "oauth" in env_keys:
        return "oauth"
    if any(k in env_keys for k in ["token", "key", "pat", "secret"]):
        return "token"
    if any(k in env_keys for k in ["url", "password", "username", "host"]):
        return "env"
    return "env"


def infer_transport_type(server_config: dict) -> str:
    """Infer transport type from MCP server config."""
    if server_config.get("type") == "http" or "url" in server_config:
        return "http"
    return "stdio"


def check_blocked_domains(server_id: str, server_config: dict, blocked: list) -> list:
    """Check if any endpoint URLs contain blocked domains."""
    errors = []
    # Check URL field
    url = server_config.get("url", "")
    for domain in blocked:
        if domain in url:
            errors.append(f"  [{server_id}] URL contains blocked domain '{domain}': {url}")
    # Check args for URLs
    for arg in server_config.get("args", []):
        if isinstance(arg, str):
            for domain in blocked:
                if domain in arg:
                    errors.append(f"  [{server_id}] Arg contains blocked domain '{domain}': {arg}")
    # Check env values for URLs
    for key, val in server_config.get("env", {}).items():
        if isinstance(val, str):
            for domain in blocked:
                if domain in val:
                    errors.append(f"  [{server_id}] Env {key} contains blocked domain '{domain}'")
    return errors


def validate(repo_root: Path) -> list[str]:
    """Run all validation checks. Returns list of error strings."""
    mcp_path = repo_root / ".claude" / "mcp-servers.json"
    ssot_path = repo_root / "ssot" / "mcp" / "servers.yaml"

    if not mcp_path.exists():
        return [f"MCP config not found: {mcp_path}"]
    if not ssot_path.exists():
        return [f"SSOT not found: {ssot_path}"]

    mcp_servers = load_mcp_config(mcp_path)
    ssot_servers, blocked_domains = load_ssot(ssot_path)

    errors = []

    # 1. Every MCP server must be in SSOT
    for sid in mcp_servers:
        if sid not in ssot_servers:
            errors.append(f"  [{sid}] In mcp-servers.json but NOT in ssot/mcp/servers.yaml — add it or remove it")

    # 2. Every SSOT server must be in MCP config
    for sid in ssot_servers:
        if sid not in mcp_servers:
            errors.append(f"  [{sid}] In SSOT but NOT in mcp-servers.json — sync required")

    # 3. Auth type consistency
    for sid in mcp_servers:
        if sid not in ssot_servers:
            continue
        mcp_auth = infer_auth_type(mcp_servers[sid])
        ssot_auth = ssot_servers[sid]["auth"]
        # Allow 'env' to match 'token' since env vars often carry tokens
        if mcp_auth != ssot_auth and not (
            {mcp_auth, ssot_auth} <= {"env", "token"}
        ):
            errors.append(f"  [{sid}] Auth mismatch: mcp={mcp_auth}, ssot={ssot_auth}")

    # 4. Transport type consistency
    for sid in mcp_servers:
        if sid not in ssot_servers:
            continue
        mcp_type = infer_transport_type(mcp_servers[sid])
        ssot_type = ssot_servers[sid].get("type", "stdio")
        if mcp_type != ssot_type:
            errors.append(f"  [{sid}] Transport mismatch: mcp={mcp_type}, ssot={ssot_type}")

    # 5. Blocked domains
    for sid, config in mcp_servers.items():
        errors.extend(check_blocked_domains(sid, config, blocked_domains))

    # 6. Status match
    for sid in mcp_servers:
        if sid not in ssot_servers:
            continue
        mcp_status = mcp_servers[sid].get("status", "built")
        ssot_status = ssot_servers[sid].get("status", "built")
        if mcp_status != ssot_status:
            errors.append(f"  [{sid}] Status mismatch: mcp={mcp_status}, ssot={ssot_status}")

    return errors


def main():
    # Find repo root (walk up from script location)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent  # scripts/ci/ → repo root
    if not (repo_root / ".git").exists():
        # Fallback: try cwd
        repo_root = Path.cwd()

    print(f"MCP SSOT Validator")
    print(f"  Repo root: {repo_root}")
    print(f"  MCP config: .claude/mcp-servers.json")
    print(f"  SSOT: ssot/mcp/servers.yaml")
    print()

    errors = validate(repo_root)

    if errors:
        print(f"FAIL: {len(errors)} validation error(s):\n")
        for e in errors:
            print(e)
        print()
        print("Fix: Update ssot/mcp/servers.yaml to match .claude/mcp-servers.json (or vice versa).")
        sys.exit(1)
    else:
        print("PASS: MCP config matches SSOT registry.")
        sys.exit(0)


if __name__ == "__main__":
    main()
