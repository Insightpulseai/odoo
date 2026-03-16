#!/usr/bin/env python3
"""Snapshot MCP tool surface and Claude Code policy."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "ssot/agents/tools"

def scan_mcp_servers():
    """Find MCP server directories and configs."""
    servers = []

    # Scan mcp/servers/
    mcp_dir = REPO_ROOT / "mcp" / "servers"
    if mcp_dir.is_dir():
        for d in sorted(mcp_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                # Check for key files
                has_package = (d / "package.json").exists()
                has_index = (d / "index.ts").exists() or (d / "index.js").exists() or (d / "src" / "index.ts").exists()
                has_readme = (d / "README.md").exists()

                entry = {
                    "name": d.name,
                    "path": str(d.relative_to(REPO_ROOT)),
                    "has_package_json": has_package,
                    "has_entrypoint": has_index,
                    "has_readme": has_readme,
                    "status": "live" if has_package and has_index else "stub",
                }

                # Read package.json for description
                if has_package:
                    try:
                        pkg = json.loads((d / "package.json").read_text())
                        entry["description"] = pkg.get("description", "")
                        entry["version"] = pkg.get("version", "")
                    except Exception:
                        pass

                servers.append(entry)

    return servers

def scan_mcp_configs():
    """Find .mcp.json (canonical) and legacy .claude/mcp-servers.legacy.json."""
    configs = []

    # Canonical project config at repo root
    root_mcp = REPO_ROOT / ".mcp.json"
    if root_mcp.exists():
        try:
            data = json.loads(root_mcp.read_text())
            server_names = list(data.get("mcpServers", {}).keys())
            configs.append({"path": str(root_mcp), "servers": server_names, "scope": "project"})
        except (json.JSONDecodeError, OSError):
            pass

    # Legacy catalog (transitional reference)
    for name in ["mcp-servers.legacy.json", "mcp-servers.json"]:
        p = REPO_ROOT / ".claude" / name
        if p.exists():
            try:
                data = json.loads(p.read_text())
                server_names = []
                if isinstance(data, dict):
                    if "mcpServers" in data:
                        server_names = list(data["mcpServers"].keys())
                    elif "servers" in data:
                        server_names = list(data["servers"].keys())
                    else:
                        server_names = list(data.keys())
                configs.append({
                    "path": str(p.relative_to(REPO_ROOT)),
                    "servers_configured": server_names,
                    "count": len(server_names),
                })
            except Exception:
                pass

    return configs

def scan_claude_settings():
    """Read .claude/settings.json for allowed tools."""
    settings_path = REPO_ROOT / ".claude" / "settings.json"
    if not settings_path.exists():
        return None

    try:
        data = json.loads(settings_path.read_text())
        return {
            "path": str(settings_path.relative_to(REPO_ROOT)),
            "allowed_tools": data.get("allowedTools", []),
            "allowed_tools_count": len(data.get("allowedTools", [])),
        }
    except Exception:
        return None

def scan_ssot_tools_registry():
    """Read ssot/tools/registry.yaml if it exists."""
    try:
        import yaml
    except ImportError:
        return None

    reg_path = REPO_ROOT / "ssot" / "tools" / "registry.yaml"
    if not reg_path.exists():
        return None

    try:
        data = yaml.safe_load(reg_path.read_text())
        tools = data.get("tools", [])
        return {
            "path": str(reg_path.relative_to(REPO_ROOT)),
            "tool_count": len(tools),
            "tool_ids": [t.get("id", "unknown") for t in tools],
        }
    except Exception:
        return None

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    servers = scan_mcp_servers()
    configs = scan_mcp_configs()
    settings = scan_claude_settings()
    ssot_tools = scan_ssot_tools_registry()

    registry = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mcp_servers": servers,
        "mcp_configs": configs,
        "claude_code_policy": settings,
        "ssot_tools_registry": ssot_tools,
        "summary": {
            "mcp_servers_found": len(servers),
            "mcp_servers_live": sum(1 for s in servers if s.get("status") == "live"),
            "mcp_servers_stub": sum(1 for s in servers if s.get("status") == "stub"),
            "mcp_configs_found": len(configs),
            "claude_allowed_tools": settings["allowed_tools_count"] if settings else 0,
        }
    }

    out_file = OUT / "tools_registry.json"
    out_file.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"Tool surface: {len(servers)} MCP servers ({registry['summary']['mcp_servers_live']} live)")
    print(f"Written to: {out_file.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    main()
