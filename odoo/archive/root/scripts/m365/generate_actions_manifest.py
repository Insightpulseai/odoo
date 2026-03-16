#!/usr/bin/env python3
"""
generate_actions_manifest.py — M365 Declarative Agent Manifest Generator

Reads SSOT YAML sources for the insightpulseai_ops_advisor declarative agent
and generates dist/m365/agents/insightpulseai_ops_advisor/manifest.json.

SSOT inputs:
    ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml
    ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml

Generated output (never hand-edit):
    dist/m365/agents/insightpulseai_ops_advisor/manifest.json

Usage:
    python scripts/m365/generate_actions_manifest.py
    python scripts/m365/generate_actions_manifest.py --validate-only
    python scripts/m365/generate_actions_manifest.py --repo-root /path/to/odoo

Exit 0 = success (generated or validated OK).
Exit 1 = error or drift detected (--validate-only mode).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("FAIL [setup] pyyaml not installed — run: pip install pyyaml", flush=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Stable agent constants (bump version manually for breaking manifest changes)
# ---------------------------------------------------------------------------
AGENT_ID = "insightpulseai_ops_advisor"
PACKAGE_NAME = "com.insightpulseai.copilot.ops-advisor"
MANIFEST_VERSION = "1.5"
AGENT_VERSION = "1.0.0"

DEVELOPER = {
    "name": "InsightPulse AI",
    "websiteUrl": "https://insightpulseai.com",
    "privacyUrl": "https://insightpulseai.com/privacy",
    "termsOfUseUrl": "https://insightpulseai.com/terms",
}

SCHEMA_URL = (
    "https://developer.microsoft.com/json-schemas/copilot/"
    "declarative-agent/v1.5/schema.json"
)

# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------
ACTIONS_YAML_REL = Path("ssot/m365/agents/insightpulseai_ops_advisor/actions.yaml")
CAPABILITIES_YAML_REL = Path("ssot/m365/agents/insightpulseai_ops_advisor/capabilities.yaml")
MANIFEST_OUT_REL = Path("dist/m365/agents/insightpulseai_ops_advisor/manifest.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_action_parameters(params: list[dict]) -> dict[str, Any]:
    """Convert SSOT parameter list to JSON Schema object for M365 manifest."""
    if not params:
        return {"type": "object", "properties": {}, "required": []}

    properties: dict[str, Any] = {}
    required: list[str] = []

    for param in params:
        name = param["name"]
        schema: dict[str, Any] = {"type": param.get("type", "string")}

        if "description" in param:
            schema["description"] = param["description"]
        if "enum" in param:
            schema["enum"] = param["enum"]
        if "default" in param:
            schema["default"] = param["default"]

        properties[name] = schema
        if param.get("required", False):
            required.append(name)

    result: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        result["required"] = required
    return result


def build_manifest(actions_data: dict, capabilities_data: dict) -> dict[str, Any]:
    """Assemble the M365 declarative agent manifest JSON."""
    # Build actions array
    actions = []
    for action in actions_data.get("actions", []):
        m365_action: dict[str, Any] = {
            "id": action["id"],
            "type": action["type"],
            "displayName": action["display_name"],
            "description": action["description"],
            "parameters": build_action_parameters(action.get("parameters", [])),
        }
        if action.get("confirmation_required"):
            m365_action["confirmationRequired"] = True
            if "confirmation_message" in action:
                m365_action["confirmationMessage"] = action["confirmation_message"]
        actions.append(m365_action)

    # Build capabilities array
    capabilities = []
    for cap in capabilities_data.get("capabilities", []):
        m365_cap: dict[str, Any] = {
            "name": cap["id"],
            "displayName": cap["display_name"],
            "description": cap["description"].strip(),
        }
        if "sample_prompts" in cap:
            m365_cap["samplePrompts"] = [
                {"text": p} for p in cap["sample_prompts"]
            ]
        capabilities.append(m365_cap)

    # Assemble full manifest
    connector = capabilities_data.get("connector", {})
    manifest: dict[str, Any] = {
        "$schema": SCHEMA_URL,
        "manifestVersion": MANIFEST_VERSION,
        "version": AGENT_VERSION,
        "id": AGENT_ID,
        "packageName": PACKAGE_NAME,
        "developer": DEVELOPER,
        "name": {
            "short": "IPAI Ops Advisor",
            "full": "InsightPulse AI — Ops Advisor",
        },
        "description": {
            "short": "Access IPAI operational data from M365 Copilot",
            "full": (
                "Access Ops Advisor findings, agentic coding run audit trails, "
                "and Odoo operational KPIs directly from Microsoft 365 Copilot. "
                "All data is fetched live from IPAI infrastructure via a "
                "federated connector — nothing is synced to Microsoft."
            ),
        },
        "connector": {
            "type": connector.get("type", "federated"),
            "endpoint": connector.get("endpoint", ""),
            "authMethod": connector.get("auth_method", "jwt"),
        },
        "actions": actions,
        "capabilities": capabilities,
    }
    return manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate M365 declarative agent manifest from SSOT YAML"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: .)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Check whether manifest.json is up to date without writing files. "
            "Exit 0 = up to date. Exit 1 = drift detected or file missing."
        ),
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    actions_path = repo_root / ACTIONS_YAML_REL
    capabilities_path = repo_root / CAPABILITIES_YAML_REL
    manifest_out_path = repo_root / MANIFEST_OUT_REL

    # Verify SSOT sources exist
    for path in (actions_path, capabilities_path):
        if not path.exists():
            print(f"FAIL [setup] SSOT source not found: {path}", flush=True)
            sys.exit(1)

    # Load SSOT sources
    actions_data = load_yaml(actions_path)
    capabilities_data = load_yaml(capabilities_path)

    # Build manifest
    manifest = build_manifest(actions_data, capabilities_data)
    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    if args.validate_only:
        if not manifest_out_path.exists():
            print(
                f"FAIL [drift] manifest.json not found at {manifest_out_path.relative_to(repo_root)}\n"
                f"       Run: python scripts/m365/generate_actions_manifest.py",
                flush=True,
            )
            sys.exit(1)
        committed = manifest_out_path.read_text(encoding="utf-8")
        if committed == manifest_json:
            print(
                f"PASS [drift] manifest.json is up to date "
                f"({manifest_out_path.relative_to(repo_root)})",
                flush=True,
            )
            sys.exit(0)
        else:
            print(
                f"FAIL [drift] manifest.json is out of sync with SSOT YAML.\n"
                f"       Run: python scripts/m365/generate_actions_manifest.py\n"
                f"       Then commit the updated {MANIFEST_OUT_REL}",
                flush=True,
            )
            sys.exit(1)

    # Write manifest
    manifest_out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_out_path.write_text(manifest_json, encoding="utf-8")
    print(f"PASS [generate] manifest written to {MANIFEST_OUT_REL}", flush=True)
    print(f"       actions: {len(manifest['actions'])}", flush=True)
    print(f"       capabilities: {len(manifest['capabilities'])}", flush=True)


if __name__ == "__main__":
    main()
