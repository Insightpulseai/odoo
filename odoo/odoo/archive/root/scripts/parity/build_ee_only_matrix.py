#!/usr/bin/env python3
"""
Generate Odoo EE Parity Matrix artifacts (JSON + Markdown) from YAML source.
Deterministic output for CI drift checking.
"""

import yaml
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SOURCE_YAML = ROOT / "parity/ee_only/ee_only_matrix.yaml"
OUTPUT_JSON = ROOT / "parity/ee_only/ee_only_matrix.generated.json"
OUTPUT_MD = ROOT / "docs/parity/EE_ONLY_PARITY.md"


def load_matrix():
    if not SOURCE_YAML.exists():
        print(f"ERROR: {SOURCE_YAML} not found")
        sys.exit(1)
    with open(SOURCE_YAML) as f:
        return yaml.safe_load(f)


def generate_json(data):
    # Sort for determinism
    data_sorted = sorted(data, key=lambda x: x["id"])

    wrapper = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(SOURCE_YAML.relative_to(ROOT)),
            "item_count": len(data_sorted),
        },
        "features": data_sorted,
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(wrapper, f, indent=2, sort_keys=True)
    print(f"Generated {OUTPUT_JSON}")


def generate_markdown(data):
    data_sorted = sorted(data, key=lambda x: (x["category"], x["id"]))

    lines = [
        "# Odoo Enterprise vs Community Parity Matrix",
        "",
        "**Status**: Open Replacement Strategy",
        f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Summary",
        "This document maps Odoo Enterprise-only features to their Open Source replacements (CE + OCA + IPAI).",
        "",
        "| ID | Feature | Category | Replacement | Confidence | Evidence |",
        "|---|---|---|---|---|---|",
    ]

    for item in data_sorted:
        strategy = item.get("replacement", {}).get("strategy", "Unknown")
        modules = ", ".join(item.get("replacement", {}).get("modules", []))
        repl_str = f"**{strategy}**"
        if modules:
            repl_str += f"<br>`{modules}`"

        evidence = f"[Link]({item.get('evidence_url')})" if item.get("evidence_url") else "-"

        lines.append(
            f"| `{item['id']}` | **{item['name']}** | {item['category']} | {repl_str} | {item['confidence']}/5 | {evidence} |"
        )

    lines.append("")
    lines.append("## Details")

    for item in data_sorted:
        lines.append(f"### {item['name']} ({item['category']})")
        lines.append(f"- **ID**: `{item['id']}`")
        lines.append(f"- **EE Status**: {item['ee_status']}")
        lines.append(f"- **CE Status**: {item['ce_status']}")

        repl = item.get("replacement", {})
        lines.append(f"- **Strategy**: {repl.get('strategy')}")
        if repl.get("modules"):
            lines.append(f"- **Modules**: `{', '.join(repl['modules'])}`")
        if repl.get("external_service"):
            lines.append(f"- **External Service**: {repl['external_service']}")
        if repl.get("notes"):
            lines.append(f"- **Notes**: {repl['notes']}")

        lines.append("")

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"Generated {OUTPUT_MD}")


def main():
    print(f"Loading {SOURCE_YAML}...")
    data = load_matrix()
    generate_json(data)
    generate_markdown(data)
    print("Done.")


if __name__ == "__main__":
    main()
