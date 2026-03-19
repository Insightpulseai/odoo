#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path("/Users/tbwa/Documents/GitHub/Insightpulseai/odoo")
OUT_DIR = REPO_ROOT / "docs" / "capabilities"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))
        return res.stdout.strip()
    except Exception:
        return ""


# Phase 1: Repo Discovery
def discover_repo():
    repo_name = "Insightpulseai/odoo"
    branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    sha = run_cmd("git rev-parse HEAD")

    inventory = {
        "metadata": {
            "repo": repo_name,
            "branch": branch,
            "sha": sha,
            "scanned_at": datetime.utcnow().isoformat() + "Z",
        },
        "skills": [],
        "tools": [],
        "surfaces": [],
        "references": [],
    }

    # Helper for safe traversal
    def safe_walk(base_dir):
        if not base_dir.exists():
            return
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [
                d for d in dirs if d not in [".git", "node_modules", ".next", ".venv", "venv"]
            ]
            for f in files:
                yield Path(root) / f

    # Skills & Global
    for p in safe_walk(REPO_ROOT):
        try:
            # Skills
            if p.name in ["SKILL.md", "AGENT_PROMPT.md"]:
                inventory["skills"].append(
                    {
                        "id": f"skill_{p.parent.name}",
                        "name": p.parent.name,
                        "path": str(p.relative_to(REPO_ROOT)),
                        "surface": "agent_prompt",
                    }
                )

            # References
            if p.name in [".cursor/rules", "CLAUDE.md", "gemini.md", "llms-full.txt"]:
                inventory["references"].append(
                    {"id": f"ref_{p.name}", "path": str(p.relative_to(REPO_ROOT))}
                )
        except PermissionError:
            continue

    # Scripts
    for p in safe_walk(REPO_ROOT / "scripts"):
        if p.suffix in [".sh", ".py"]:
            inventory["tools"].append(
                {
                    "id": f"script_{p.name}",
                    "name": p.name,
                    "path": str(p.relative_to(REPO_ROOT)),
                    "surface": "script",
                }
            )

    # Subdirectories for tools
    for td in ["bin", "tools", "mcp"]:
        for p in safe_walk(REPO_ROOT / td):
            if not p.name.startswith("."):
                try:
                    is_exec = os.access(p, os.X_OK)
                except PermissionError:
                    is_exec = False
                if is_exec:
                    inventory["tools"].append(
                        {
                            "id": f"tool_{p.name}",
                            "name": p.name,
                            "path": str(p.relative_to(REPO_ROOT)),
                            "surface": "cli",
                        }
                    )

    # CI Workflows
    for p in safe_walk(REPO_ROOT / ".github" / "workflows"):
        if p.suffix == ".yml":
            inventory["surfaces"].append(
                {
                    "id": f"ci_{p.stem}",
                    "name": p.name,
                    "path": str(p.relative_to(REPO_ROOT)),
                    "type": "ci_job",
                }
            )

    # Dedupe and sort
    for k in ["skills", "tools", "surfaces", "references"]:
        unique = {x["id"]: x for x in inventory[k]}.values()
        inventory[k] = sorted(list(unique), key=lambda x: x["id"])

    with open(OUT_DIR / "repo_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    return inventory


# Phase 2: Machine Discovery
def discover_machine():
    tools_to_check = [
        "git",
        "gh",
        "docker",
        "supabase",
        "psql",
        "node",
        "npm",
        "pnpm",
        "yarn",
        "python3",
        "pip3",
        "rg",
        "fd",
        "jq",
        "superclaude",
        "claude",
    ]

    cli_tools = []
    for t in tools_to_check:
        path = run_cmd(f"which {t}")
        if path:
            version = run_cmd(f"{t} --version").split("\n")[0][:50]
            cli_tools.append({"name": t, "path": path, "version": version.strip()})

    mcp_servers = []
    # basic heuristic check
    for server_dir in ["mcp/servers/odoo-erp-server", "mcp/servers/memory-mcp-server"]:
        p = REPO_ROOT / server_dir
        if p.exists():
            mcp_servers.append(
                {
                    "name": p.name,
                    "config_path": str(p.relative_to(REPO_ROOT)),
                    "tools_exposed": ["unknown"],  # would need deep parse
                }
            )

    inventory = {
        "cli_tools": sorted(cli_tools, key=lambda x: x["name"]),
        "mcp_servers": sorted(mcp_servers, key=lambda x: x["name"]),
        "runtimes": {"os": run_cmd("uname -a")[:100], "shell": os.environ.get("SHELL", "unknown")},
        "detected_services": [],
    }

    with open(OUT_DIR / "machine_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    return inventory


# Phase 3: Normalize and Map
def generate_maps(repo, machine):
    map_data = {"items": []}

    for s in repo["skills"]:
        map_data["items"].append(
            {
                "id": s["id"],
                "name": s["name"],
                "type": "skill",
                "location": "repo_only",
                "path": s.get("path"),
            }
        )
    for t in repo["tools"]:
        map_data["items"].append(
            {
                "id": t["id"],
                "name": t["name"],
                "type": "tool",
                "location": "repo_only",
                "path": t.get("path"),
            }
        )
    for m in machine["cli_tools"]:
        map_data["items"].append(
            {
                "id": f"cli_{m['name']}",
                "name": m["name"],
                "type": "cli",
                "location": "both"
                if any(x["name"] == m["name"] for x in repo["tools"])
                else "machine_only",
                "path": m.get("path"),
            }
        )

    map_data["items"] = sorted(map_data["items"], key=lambda x: x["name"])

    with open(OUT_DIR / "capability_map.json", "w") as f:
        json.dump(map_data, f, indent=2)

    # Generate MD Map
    md = "# Capability Map\n\n## Skills\n| Name | Path | Type |\n|---|---|---|\n"
    for i in map_data["items"]:
        if i["type"] == "skill":
            md += f"| {i['name']} | `{i['path']}` | {i['location']} |\n"

    md += "\n## Repo Tools\n| Name | Path |\n|---|---|\n"
    for i in map_data["items"]:
        if i["type"] == "tool":
            md += f"| {i['name']} | `{i['path']}` |\n"

    md += "\n## Machine CLIs\n| Name | Path |\n|---|---|\n"
    for i in map_data["items"]:
        if i["type"] == "cli":
            md += f"| {i['name']} | `{i['path']}` |\n"

    with open(OUT_DIR / "capability_map.md", "w") as f:
        f.write(md)

    # Generation Gaps & Drift
    gaps = "# Gaps & Drift\n\n- Need to document full MCP tool schemas.\n- Duplicate tool verification required.\n- Add missing slash commands."
    with open(OUT_DIR / "gaps_and_drift.md", "w") as f:
        f.write(gaps)

    readme = "# Capabilities Inventory\n\nGenerated mapping of all repo and machine capabilities."
    with open(OUT_DIR / "README.md", "w") as f:
        f.write(readme)


if __name__ == "__main__":
    r = discover_repo()
    m = discover_machine()
    generate_maps(r, m)
    print(f"Written to {OUT_DIR}")
