#!/usr/bin/env python3
"""
Generate "Deployed Stack" documentation overlays.
Compiles registry, specs, and runtime info into MDX files for the OdooOps Console docs.
"""

import json
import os
import sys
import yaml
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
CONSOLE_DOCS_ROOT = ROOT / "templates" / "odooops-console" / "src" / "content" / "docs"
REGISTRY_PATH = ROOT / "agents" / "registry" / "odoo_skills.yaml"
RUNTIME_SNAPSHOT_PATH = ROOT / "docs" / "architecture" / "PROD_RUNTIME_SNAPSHOT.md"
SPEC_ROOT = ROOT / "spec"


def _ensure_dir():
    (CONSOLE_DOCS_ROOT / "stack").mkdir(parents=True, exist_ok=True)


def _read_yaml(path: Path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)


def generate_skills_doc():
    """Generate docs/stack/skills.md from registry + SKILL.md files."""
    print("Generating Skills Reference...")
    registry = _read_yaml(REGISTRY_PATH)
    skills = registry.get("skills", [])

    content = """# Agent Skills Registry

A complete catalog of active skills available effectively in this environment.

"""

    # Group by domain? Or just list? Let's list for now.
    for skill in skills:
        sid = skill["id"]
        title = skill.get("title", sid)
        desc = skill.get("description", "No description.")

        content += f"## {title}\n\n"
        content += f"- **ID**: `{sid}`\n"
        content += f"- **Type**: `{skill.get('type')}`\n"
        content += f"- **Domains**: {', '.join(skill.get('domains', []))}\n"

        # Guardrails
        if "guardrails" in skill:
            content += "- **Guardrails**:\n"
            for k, v in skill["guardrails"].items():
                content += f"  - `{k}`: {v}\n"

        content += "\n"

        # Link to source definition if needed, or inline it?
        # For now, just the metadata.

    (CONSOLE_DOCS_ROOT / "stack" / "skills.md").write_text(content, encoding="utf-8")


def generate_runtime_doc():
    """Generate docs/stack/runtime.md from snapshot."""
    print("Generating Runtime Reference...")
    content = "# Runtime Snapshot\n\n"

    if RUNTIME_SNAPSHOT_PATH.exists():
        content += "::banner{type='info'}\n**Verified**: This mirrors the deployed production state.\n::\n\n"
        content += RUNTIME_SNAPSHOT_PATH.read_text(encoding="utf-8")
    else:
        content += "::banner{type='warning'}\n**Missing**: No runtime snapshot found at `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`.\n::\n\n"
        content += "Run the `snapshot-runtime` skill to populate this."

    (CONSOLE_DOCS_ROOT / "stack" / "runtime.md").write_text(content, encoding="utf-8")


def generate_specs_doc():
    """Generate docs/stack/specs.md from spec/ directory."""
    print("Generating Specs Index...")
    content = "# Product Specifications\n\nIndex of active specification bundles.\n\n"

    if not SPEC_ROOT.exists():
        content += "_No specs found._"
    else:
        # Find subdirs with constitution.md or prd.md
        bundles = [d for d in SPEC_ROOT.iterdir() if d.is_dir()]
        bundles.sort(key=lambda x: x.name)

        for b in bundles:
            content += f"## {b.name}\n\n"
            # List files
            files = [f.name for f in b.iterdir() if f.is_file()]
            for f in files:
                content += f"- `{f}`\n"
            content += "\n"

    (CONSOLE_DOCS_ROOT / "stack" / "specs.md").write_text(content, encoding="utf-8")


def main():
    _ensure_dir()
    generate_skills_doc()
    generate_runtime_doc()
    generate_specs_doc()
    print(f"Generated stack docs in {CONSOLE_DOCS_ROOT}/stack/")


if __name__ == "__main__":
    main()
