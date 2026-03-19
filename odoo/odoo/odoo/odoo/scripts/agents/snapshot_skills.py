#!/usr/bin/env python3
"""Snapshot agent skills from SKILL.md and CLAUDE.md files."""
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "ssot/agents/skills"

def hash_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

def scan_skill_files():
    skills = []
    # Scan for SKILL.md or skill.md
    for p in sorted(REPO_ROOT.rglob("**/[Ss][Kk][Ii][Ll][Ll].[Mm][Dd]")):
        if ".git" in str(p) or "node_modules" in str(p):
            continue
        rel = str(p.relative_to(REPO_ROOT))
        content = p.read_text(errors="replace")
        # Extract first heading as name
        name = None
        for line in content.splitlines():
            if line.startswith("#"):
                name = line.lstrip("#").strip()
                break
        skills.append({
            "path": rel,
            "name": name or rel,
            "type": "skill_md",
            "sha256_prefix": hash_file(p),
            "lines": len(content.splitlines()),
        })

    # Scan for .claude/commands/*.md (slash commands)
    cmd_dir = REPO_ROOT / ".claude" / "commands"
    if cmd_dir.is_dir():
        for p in sorted(cmd_dir.glob("*.md")):
            rel = str(p.relative_to(REPO_ROOT))
            content = p.read_text(errors="replace")
            skills.append({
                "path": rel,
                "name": p.stem,
                "type": "claude_command",
                "sha256_prefix": hash_file(p),
                "lines": len(content.splitlines()),
            })

    # Scan for skills/ directories with skill.md
    for p in sorted(REPO_ROOT.rglob("skills/*/skill.md")):
        if ".git" in str(p) or "node_modules" in str(p):
            continue
        rel = str(p.relative_to(REPO_ROOT))
        content = p.read_text(errors="replace")
        name = None
        for line in content.splitlines():
            if line.startswith("#"):
                name = line.lstrip("#").strip()
                break
        # Avoid duplicates
        if not any(s["path"] == rel for s in skills):
            skills.append({
                "path": rel,
                "name": name or p.parent.name,
                "type": "skill_contract",
                "sha256_prefix": hash_file(p),
                "lines": len(content.splitlines()),
            })

    return skills

def scan_claude_md_files():
    """Scan CLAUDE.md files for agent instructions."""
    agents = []
    for p in sorted(REPO_ROOT.rglob("CLAUDE.md")):
        if ".git" in str(p) or "node_modules" in str(p):
            continue
        rel = str(p.relative_to(REPO_ROOT))
        content = p.read_text(errors="replace")
        agents.append({
            "path": rel,
            "type": "claude_md",
            "sha256_prefix": hash_file(p),
            "lines": len(content.splitlines()),
        })
    return agents

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    skills = scan_skill_files()
    agents = scan_claude_md_files()

    registry = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "skills": skills,
        "agent_instructions": agents,
        "summary": {
            "total_skills": len(skills),
            "total_agent_instructions": len(agents),
            "skill_types": {},
        }
    }

    for s in skills:
        t = s["type"]
        registry["summary"]["skill_types"][t] = registry["summary"]["skill_types"].get(t, 0) + 1

    out_file = OUT / "skills_registry.json"
    out_file.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"Skills registry: {len(skills)} skills, {len(agents)} agent instructions")
    print(f"Written to: {out_file.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    main()
