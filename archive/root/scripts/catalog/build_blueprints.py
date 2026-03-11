#!/usr/bin/env python3
"""
build_blueprints.py
───────────────────
Generate docs/catalog/generated/<id>.md from each *.blueprint.yaml.
Output is deterministic per blueprint.

Exit codes:
  0  All generated docs written (or up-to-date with --check)
  1  Drift detected (only with --check)
  2  Error

Usage:
  python3 scripts/catalog/build_blueprints.py         # write all generated docs
  python3 scripts/catalog/build_blueprints.py --check # fail if any generated doc would change
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).parent.parent.parent
BLUEPRINT_DIR = REPO_ROOT / "docs" / "catalog" / "blueprints"
GENERATED_DIR = BLUEPRINT_DIR / "generated"

CHECK_MODE = "--check" in sys.argv


def render_blueprint_doc(data: dict) -> str:
    bp_id = data.get("id", "unknown")
    title = data.get("title", "")
    category = data.get("category", "")
    sources = data.get("sources", [])
    target = data.get("target", {})
    variables = data.get("variables", [])
    steps = data.get("automation", {}).get("steps", [])
    checks = data.get("verification", {}).get("required_checks", [])
    preview_exp = data.get("verification", {}).get("preview", {}).get("expectations", [])
    rollback = data.get("rollback", {})
    minor_customization = data.get("notes", {}).get("minor_customization", [])

    lines = [
        f"<!-- AUTO-GENERATED from blueprints/{bp_id}.blueprint.yaml — do not edit directly -->",
        f"<!-- Run: python3 scripts/catalog/build_blueprints.py -->",
        "",
        f"# Blueprint: {title}",
        "",
        f"**ID**: `{bp_id}`  ",
        f"**Category**: `{category}`  ",
        f"**Target**: `{target.get('app_dir', '?')}`",
        "",
        "---",
        "",
        "## Sources",
        "",
    ]

    for src in sources:
        src_type = src.get("type", "")
        url = src.get("url", "")
        catalog_id = src.get("catalog_id", "")
        if catalog_id:
            lines.append(f"- **{src_type}** — [{url}]({url}) (catalog id: `{catalog_id}`)")
        else:
            lines.append(f"- **{src_type}** — [{url}]({url})")

    lines.extend(["", "---", "", "## Required Variables", ""])

    req_vars = [v for v in variables if v.get("required")]
    opt_vars = [v for v in variables if not v.get("required")]

    if req_vars:
        lines.append("**Required**:")
        lines.append("")
        lines.append("| Variable | Description | Example |")
        lines.append("|----------|-------------|---------|")
        for v in req_vars:
            name = v.get("name", "")
            desc = v.get("description", "")
            example = v.get("example", "")
            lines.append(f"| `{name}` | {desc} | `{example}` |")
        lines.append("")

    if opt_vars:
        lines.append("**Optional**:")
        lines.append("")
        lines.append("| Variable | Description | Example |")
        lines.append("|----------|-------------|---------|")
        for v in opt_vars:
            name = v.get("name", "")
            desc = v.get("description", "")
            example = v.get("example", "")
            lines.append(f"| `{name}` | {desc} | `{example}` |")
        lines.append("")

    lines.extend(["---", "", "## Automation Steps", ""])

    for i, step in enumerate(steps, 1):
        name = step.get("name", "")
        desc = step.get("description", "")
        agent_instruction = step.get("agent_instruction", "").strip()

        lines.append(f"### Step {i}: {name}")
        lines.append("")
        lines.append(f"{desc}")
        lines.append("")
        if agent_instruction:
            lines.append("**Agent instruction**:")
            lines.append("")
            lines.append("```")
            lines.append(agent_instruction)
            lines.append("```")
            lines.append("")

    lines.extend(["---", "", "## Verification", ""])
    lines.append("**Required CI checks:**")
    lines.append("")
    for check in checks:
        lines.append(f"- `{check}`")
    lines.append("")

    if preview_exp:
        lines.append("**Preview expectations:**")
        lines.append("")
        for exp in preview_exp:
            lines.append(f"- {exp}")
        lines.append("")

    lines.extend(["---", "", "## Rollback", ""])
    lines.append(f"**Strategy**: `{rollback.get('strategy', 'manual')}`")
    if rollback.get("notes"):
        lines.append("")
        lines.append(rollback["notes"])
    lines.append("")

    lines.extend(["---", "", "## Minor Customization (manual steps after agent applies blueprint)", ""])
    for item in minor_customization:
        lines.append(f"- {item}")
    lines.append("")

    lines.extend(["---", "", "## Agent Relay Template", ""])
    lines.extend([
        "Paste this prompt to apply this blueprint:",
        "",
        "```text",
        f"Apply blueprint `{bp_id}` from docs/catalog/blueprints/{bp_id}.blueprint.yaml.",
        "",
        "Variables to set before running:",
    ])
    for v in req_vars:
        lines.append(f"  {v.get('name')}: <value>")
    lines.extend([
        "",
        "Steps to execute in order:",
    ])
    for i, step in enumerate(steps, 1):
        lines.append(f"  {i}. {step.get('name')}: {step.get('description', '')}")
    lines.extend([
        "",
        "After completing all steps:",
        f"  - Verify required checks pass: {', '.join(checks)}",
        "  - Complete minor_customization items (see blueprint notes)",
        "  - Open PR with title: feat({category}): apply {bp_id} blueprint",
        "```",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    blueprint_files = sorted(BLUEPRINT_DIR.glob("*.blueprint.yaml"))
    if not blueprint_files:
        print(f"ERROR: No *.blueprint.yaml files found in {BLUEPRINT_DIR}", file=sys.stderr)
        return 2

    total_drift = 0
    for path in blueprint_files:
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"ERROR: Cannot parse {path.name}: {e}", file=sys.stderr)
            return 2

        bp_id = data.get("id", path.stem.replace(".blueprint", ""))
        out_path = GENERATED_DIR / f"{bp_id}.md"
        content = render_blueprint_doc(data)

        if CHECK_MODE:
            if out_path.exists() and out_path.read_text() == content:
                print(f"✅ {out_path.relative_to(REPO_ROOT)} up-to-date")
            else:
                print(f"❌ {out_path.relative_to(REPO_ROOT)} out of date", file=sys.stderr)
                total_drift += 1
        else:
            out_path.write_text(content)
            print(f"✅ Wrote {out_path.relative_to(REPO_ROOT)}")

    if CHECK_MODE and total_drift > 0:
        print(f"\n{total_drift} generated doc(s) out of date. Run: python3 scripts/catalog/build_blueprints.py", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
