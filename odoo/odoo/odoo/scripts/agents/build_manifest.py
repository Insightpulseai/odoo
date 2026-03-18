#!/usr/bin/env python3
"""Build unified agent capability manifest from all registries."""
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / "ssot/agents"

def main():
    skills_path = AGENTS_DIR / "skills" / "skills_registry.json"
    tools_path = AGENTS_DIR / "tools" / "tools_registry.json"
    knowledge_path = AGENTS_DIR / "knowledge" / "knowledge_registry.json"

    missing = []
    for p, name in [(skills_path, "skills"), (tools_path, "tools"), (knowledge_path, "knowledge")]:
        if not p.exists():
            missing.append(name)

    if missing:
        print(f"ERROR: Missing registries: {', '.join(missing)}")
        print("Run snapshot_skills.py, snapshot_tools.py, snapshot_knowledge.py first.")
        return 1

    skills = json.loads(skills_path.read_text())
    tools = json.loads(tools_path.read_text())
    knowledge = json.loads(knowledge_path.read_text())

    manifest = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registries": {
            "skills": {
                "source": str(skills_path.relative_to(REPO_ROOT)),
                "generated_at": skills["generated_at"],
                "summary": skills["summary"],
            },
            "tools": {
                "source": str(tools_path.relative_to(REPO_ROOT)),
                "generated_at": tools["generated_at"],
                "summary": tools["summary"],
            },
            "knowledge": {
                "source": str(knowledge_path.relative_to(REPO_ROOT)),
                "generated_at": knowledge["generated_at"],
                "summary": knowledge["summary"],
            },
        },
        "combined_summary": {
            "total_skills": skills["summary"]["total_skills"],
            "total_agent_instructions": skills["summary"]["total_agent_instructions"],
            "mcp_servers_live": tools["summary"]["mcp_servers_live"],
            "mcp_servers_total": tools["summary"]["mcp_servers_found"],
            "claude_allowed_tools": tools["summary"]["claude_allowed_tools"],
            "knowledge_files": knowledge["summary"]["total_files"],
            "knowledge_lines": knowledge["summary"]["total_lines"],
        },
    }

    out_file = AGENTS_DIR / "capability_manifest.json"
    out_file.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Unified manifest written to: {out_file.relative_to(REPO_ROOT)}")
    print(f"  Skills: {manifest['combined_summary']['total_skills']}")
    print(f"  Agent instructions: {manifest['combined_summary']['total_agent_instructions']}")
    print(f"  MCP servers: {manifest['combined_summary']['mcp_servers_live']} live / {manifest['combined_summary']['mcp_servers_total']} total")
    print(f"  Knowledge corpus: {manifest['combined_summary']['knowledge_files']} files, {manifest['combined_summary']['knowledge_lines']} lines")
    return 0

if __name__ == "__main__":
    exit(main())
