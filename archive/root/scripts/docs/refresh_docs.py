#!/usr/bin/env python3
"""
Documentation Generator (refresh_docs.py)
Compiles runtime artifacts + specs + registry into apps/docs/content/_generated/
Driven by docs/docs.manifest.yaml
"""

import datetime
import json
import os
import sys
import yaml
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
DOCS_APP_ROOT = ROOT / "apps" / "docs"
GENERATED_DIR = DOCS_APP_ROOT / "content" / "_generated"
MANIFEST_PATH = ROOT / "docs" / "docs.manifest.yaml"


def load_manifest():
    if not MANIFEST_PATH.exists():
        sys.exit(f"Manifest not found: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


def ensure_dirs():
    (GENERATED_DIR / "reference").mkdir(parents=True, exist_ok=True)


def render_header(title, evidence_path=None):
    timestamp = datetime.datetime.utcnow().isoformat()
    meta = f"""---
title: {title}
last_verified: {timestamp}
"""
    if evidence_path:
        meta += f"evidence: {evidence_path}\n"

    meta += "---\n\n"

    # Warning banner
    meta += "::banner{type='warning'}\n"
    meta += "**Generated Content**: This page is auto-generated from runtime artifacts. Do not edit manually.\n"
    meta += "::\n\n"

    if evidence_path and Path(evidence_path).exists():
        meta += f"::verify-badge{{path='{evidence_path}'}}\n::\n\n"
    else:
        meta += (
            "::banner{type='error'}\n**Verification Failed**: Source evidence not found.\n::\n\n"
        )

    return meta


def render_agent_registry(rule):
    source_path = ROOT / rule["source"]
    target_path = ROOT / rule["target"]

    if not source_path.exists():
        print(f"!! Source missing: {source_path}")
        return

    with open(source_path, "r") as f:
        data = yaml.safe_load(f)

    content = render_header("Agent Registry", str(rule["source"]))
    content += "# OdooOps Agent Registry\n\n"
    content += "List of registered agents and skills available in the platform.\n\n"

    if "skills" in data:
        content += "## Procedural Skills\n\n"
        for skill in data["skills"]:
            content += f"### {skill.get('title', skill['id'])}\n\n"
            content += f"- **ID**: `{skill['id']}`\n"
            content += f"- **Type**: `{skill['type']}`\n"
            content += f"- **Domains**: {', '.join(skill.get('domains', []))}\n"

            if "guardrails" in skill:
                content += "- **Guardrails**:\n"
                for k, v in skill["guardrails"].items():
                    content += f"  - `{k}`: {v}\n"
            content += "\n"

    with open(target_path, "w") as f:
        f.write(content)
    print(f">> Generated: {target_path}")


def render_runtime_snapshot(rule):
    source_path = ROOT / rule["source"]
    target_path = ROOT / rule["target"]

    if not source_path.exists():
        print(f"!! Source missing: {source_path}")
        return

    content = render_header("Runtime Snapshot", str(rule["source"]))

    # Simple copy of the MD content for now, preserving the warning header
    with open(source_path, "r") as f:
        source_content = f.read()

    content += source_content

    with open(target_path, "w") as f:
        f.write(content)
    print(f">> Generated: {target_path}")


def main():
    print(f"Starting Docs Refresh from {MANIFEST_PATH}")
    manifest = load_manifest()
    ensure_dirs()

    rules = manifest.get("generation_rules", [])
    for rule in rules:
        processor_name = rule.get("processor")
        if processor_name == "render_agent_registry":
            render_agent_registry(rule)
        elif processor_name == "render_runtime_snapshot":
            render_runtime_snapshot(rule)
        else:
            print(f"?? Unknown processor: {processor_name}")

    print("Docs Refresh Complete.")


if __name__ == "__main__":
    main()
