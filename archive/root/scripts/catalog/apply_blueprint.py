#!/usr/bin/env python3
"""
apply_blueprint.py
──────────────────
Generate an Agent Relay Template prompt for a given blueprint id.
The prompt is self-contained and ready to paste into Claude Code (or any agent).

Exit codes:
  0  Prompt written to stdout (or file)
  2  Error (blueprint not found, invalid YAML, missing pyyaml)

Usage:
  python3 scripts/catalog/apply_blueprint.py <blueprint-id>
  python3 scripts/catalog/apply_blueprint.py ops-console-dashboard
  python3 scripts/catalog/apply_blueprint.py --list
  python3 scripts/catalog/apply_blueprint.py ops-console-dashboard --env-file .blueprint.env
  python3 scripts/catalog/apply_blueprint.py ops-console-dashboard --output prompt.txt
"""

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).parent.parent.parent
BLUEPRINT_DIR = REPO_ROOT / "docs" / "catalog" / "blueprints"


def list_blueprints() -> None:
    files = sorted(BLUEPRINT_DIR.glob("*.blueprint.yaml"))
    if not files:
        print("No blueprints found.")
        return
    print("Available blueprints:\n")
    for f in files:
        try:
            with open(f) as fh:
                data = yaml.safe_load(fh)
            bp_id = data.get("id", "?")
            title = data.get("title", "")
            category = data.get("category", "")
            print(f"  {bp_id:40s} [{category}] {title}")
        except Exception:
            print(f"  {f.name} (could not parse)")
    print()


def load_env_file(env_file: str) -> dict[str, str]:
    env: dict[str, str] = {}
    try:
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        print(f"WARNING: env file '{env_file}' not found — variables will be unset", file=sys.stderr)
    return env


def generate_prompt(data: dict, env_vars: dict[str, str]) -> str:
    bp_id = data.get("id", "")
    title = data.get("title", "")
    category = data.get("category", "")
    target = data.get("target", {})
    variables = data.get("variables", [])
    steps = data.get("automation", {}).get("steps", [])
    checks = data.get("verification", {}).get("required_checks", [])
    minor = data.get("notes", {}).get("minor_customization", [])
    rollback = data.get("rollback", {})

    lines = [
        f"You are a coding agent applying blueprint `{bp_id}` to the Insightpulseai/odoo monorepo.",
        "",
        f"Blueprint: {title}",
        f"Category: {category}",
        f"Target directory: {target.get('app_dir', '?')}",
        "",
        "## Context",
        "",
        "This is a pnpm monorepo with Turborepo. The ops-console is at apps/ops-console/.",
        "All secrets are server-only (no NEXT_PUBLIC_ prefix). Commit with OCA-style messages.",
        f"See docs/catalog/blueprints/{bp_id}.blueprint.yaml for full blueprint definition.",
        "",
        "## Variables",
        "",
    ]

    for v in variables:
        name = v.get("name", "")
        desc = v.get("description", "")
        required = v.get("required", False)
        value = env_vars.get(name, "<FILL_IN>" if required else v.get("example", ""))
        req_label = "(required)" if required else "(optional)"
        lines.append(f"  {name}={value}  # {desc} {req_label}")

    lines.extend([
        "",
        "## Steps to execute (in order)",
        "",
    ])

    for i, step in enumerate(steps, 1):
        name = step.get("name", "")
        desc = step.get("description", "")
        agent_instruction = step.get("agent_instruction", "").strip()
        lines.append(f"### Step {i}: {name}")
        lines.append(desc)
        if agent_instruction:
            lines.append("")
            lines.append(agent_instruction)
        lines.append("")

    lines.extend([
        "## Verification",
        "",
        "After completing all steps, verify these CI checks pass:",
        "",
    ])
    for check in checks:
        lines.append(f"  - {check}")

    lines.extend([
        "",
        "## Rollback",
        "",
        f"Strategy: {rollback.get('strategy', 'manual')}",
    ])
    if rollback.get("notes"):
        lines.append(rollback["notes"])

    lines.extend([
        "",
        "## Manual steps (not automated — do after agent completes)",
        "",
    ])
    for item in minor:
        lines.append(f"  - {item}")

    lines.extend([
        "",
        "## Commit",
        "",
        f"Open a PR with title: feat({category}): apply {bp_id} blueprint",
        "Include evidence: git log --oneline -5 and any verification outputs.",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    args = sys.argv[1:]

    if not args or "--list" in args:
        list_blueprints()
        return 0

    # Parse args
    blueprint_id = None
    env_file = None
    output_file = None

    i = 0
    while i < len(args):
        if args[i] == "--env-file" and i + 1 < len(args):
            env_file = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif not args[i].startswith("--"):
            blueprint_id = args[i]
            i += 1
        else:
            i += 1

    if not blueprint_id:
        print("Usage: apply_blueprint.py <blueprint-id> [--env-file .blueprint.env] [--output file.txt]", file=sys.stderr)
        print("       apply_blueprint.py --list", file=sys.stderr)
        return 2

    # Find blueprint file
    bp_path = BLUEPRINT_DIR / f"{blueprint_id}.blueprint.yaml"
    if not bp_path.exists():
        print(f"ERROR: Blueprint not found: {bp_path}", file=sys.stderr)
        print("Run apply_blueprint.py --list to see available blueprints.", file=sys.stderr)
        return 2

    with open(bp_path) as f:
        data = yaml.safe_load(f)

    env_vars = load_env_file(env_file) if env_file else {}
    prompt = generate_prompt(data, env_vars)

    if output_file:
        Path(output_file).write_text(prompt)
        print(f"Prompt written to {output_file}")
    else:
        print(prompt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
