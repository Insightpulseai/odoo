#!/usr/bin/env python3
"""Probe MCP server capabilities and generate inventory."""
import json
import pathlib
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPABILITIES = ROOT / "capabilities"


def probe_server(name: str, command: str, args: List[str], env: Dict[str, str]) -> Dict[str, Any]:
    """Probe a single MCP server."""
    try:
        # Test if server binary is available
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            timeout=5,
            env=env
        )
        available = result.returncode == 0
        
        return {
            "name": name,
            "available": available,
            "command": command,
            "version": result.stdout.decode().strip() if available else None,
            "error": result.stderr.decode().strip() if not available else None
        }
    except Exception as e:
        return {
            "name": name,
            "available": False,
            "command": command,
            "error": str(e)
        }


def main():
    """Probe all MCP servers and generate capability inventory."""
    CAPABILITIES.mkdir(parents=True, exist_ok=True)
    
    # Load registry
    import yaml
    with open(ROOT / "mcp/registry/servers.yaml") as f:
        registry = yaml.safe_load(f)
    
    inventory = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "version": "1.0",
        "external_servers": {},
        "custom_servers": {},
        "summary": {
            "total": 0,
            "available": 0,
            "unavailable": 0
        }
    }
    
    # Probe external servers
    for name, spec in registry.get("external_servers", {}).items():
        result = probe_server(name, spec["command"], spec["args"], {})
        inventory["external_servers"][name] = result
        inventory["summary"]["total"] += 1
        if result["available"]:
            inventory["summary"]["available"] += 1
        else:
            inventory["summary"]["unavailable"] += 1
    
    # Check custom servers (build status)
    for name, spec in registry.get("custom_servers", {}).items():
        dist_path = ROOT / spec["path"] / "dist"
        available = dist_path.exists() and (dist_path / "index.js").exists()
        
        inventory["custom_servers"][name] = {
            "name": name,
            "available": available,
            "path": spec["path"],
            "built": available,
            "error": "Not built (run: npm run build)" if not available else None
        }
        inventory["summary"]["total"] += 1
        if available:
            inventory["summary"]["available"] += 1
        else:
            inventory["summary"]["unavailable"] += 1
    
    # Write inventory
    (CAPABILITIES / "current.json").write_text(json.dumps(inventory, indent=2))
    
    # Print summary
    print(f"\n📊 MCP Server Inventory:")
    print(f"  Total: {inventory['summary']['total']}")
    print(f"  Available: {inventory['summary']['available']}")
    print(f"  Unavailable: {inventory['summary']['unavailable']}")
    
    if inventory["summary"]["unavailable"] > 0:
        print("\n⚠️  Unavailable servers:")
        for name, result in {**inventory["external_servers"], **inventory["custom_servers"]}.items():
            if not result["available"]:
                print(f"    - {name}: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    print("\n✅ All MCP servers available")


if __name__ == "__main__":
    main()
