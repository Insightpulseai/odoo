#!/usr/bin/env python3
"""Index mirrored Anthropic skills — produces JSON + Markdown catalog."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIRROR = ROOT / "third_party" / "anthropic_skills"


def find_skill_md_files():
    """Upstream uses SKILL.md files within skill folders."""
    return sorted(MIRROR.glob("**/SKILL.md"))


def main():
    if not MIRROR.exists():
        raise SystemExit(f"Missing mirror dir: {MIRROR}")

    items = []
    for p in find_skill_md_files():
        rel = p.relative_to(MIRROR).as_posix()
        skill_id = "/".join(rel.split("/")[:-1])
        items.append({
            "skill_id": skill_id,
            "skill_md": rel,
        })

    out_json = ROOT / "reports" / "anthropic_skills_index.json"
    out_md = ROOT / "docs" / "agents" / "ANTHROPIC_SKILLS_INDEX.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({
        "upstream": "anthropics/skills",
        "upstream_url": "https://github.com/anthropics/skills",
        "count": len(items),
        "items": items,
    }, indent=2), encoding="utf-8")
    print(f"  JSON: {out_json.relative_to(ROOT)}")

    lines = [
        "# Anthropic Skills Index (mirrored)",
        "",
        "- Upstream: [anthropics/skills](https://github.com/anthropics/skills)",
        f"- Skills discovered (SKILL.md): **{len(items)}**",
        "",
        "## Entries",
        "",
    ]
    for it in items:
        lines.append(f"- `{it['skill_id']}` — `{it['skill_md']}`")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Markdown: {out_md.relative_to(ROOT)}")
    print(f"\nIndexed {len(items)} skills from mirror.")


if __name__ == "__main__":
    main()
