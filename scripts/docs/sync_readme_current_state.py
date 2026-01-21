#!/usr/bin/env python3
"""
Sync README.md current state block from filesystem (authoritative).

Scans addons/ and addons/ipai/ for Odoo modules and generates a
"Current State" section in README.md between marker comments.

CI gates ensure this stays in sync with actual repo state.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

# Canonical modules (single bridge + vertical bundles)
CANONICAL = {
    "ipai_enterprise_bridge",
    "ipai_scout_bundle",
    "ipai_ces_bundle",
}


def find_modules(base: Path) -> list[str]:
    """Find Odoo modules in a directory (has __manifest__.py or __openerp__.py)."""
    if not base.exists():
        return []
    mods = []
    for p in sorted(base.iterdir()):
        if not p.is_dir():
            continue
        if (p / "__manifest__.py").exists() or (p / "__openerp__.py").exists():
            mods.append(p.name)
    return mods


def main():
    addons_root = ROOT / "addons"
    ipai_ns = addons_root / "ipai"

    flat = find_modules(addons_root)
    nested = find_modules(ipai_ns)

    all_mods = sorted(set(flat + nested))

    canon_present = [m for m in all_mods if m in CANONICAL]
    other_ipai = [m for m in all_mods if m.startswith("ipai_") and m not in CANONICAL]
    non_ipai = [m for m in all_mods if not m.startswith("ipai_") and m != "oca"]

    block = []
    block.append("<!-- CURRENT_STATE:BEGIN -->")
    block.append("")
    block.append("## Current State (Authoritative)")
    block.append("")
    block.append("**Canonical IPAI strategy (single-bridge + vertical bundles):**")
    block.append("")
    block.append("| Module | Role | Description |")
    block.append("|--------|------|-------------|")
    block.append(
        "| `ipai_enterprise_bridge` | Bridge | Thin cross-cutting layer: config, approvals, AI/infra integration, shared mixins |"
    )
    block.append(
        "| `ipai_scout_bundle` | Vertical | Meta-bundle for Scout retail ops + analytics (depends-only, no business logic) |"
    )
    block.append(
        "| `ipai_ces_bundle` | Vertical | Meta-bundle for CES creative effectiveness ops (depends-only, no business logic) |"
    )
    block.append("")
    block.append("**Detected in repo:**")
    block.append("")
    block.append(
        f"- Canonical modules present: `{', '.join(canon_present)}`"
        if canon_present
        else "- Canonical modules present: (none)"
    )
    block.append(f"- Other IPAI modules (feature/legacy): {len(other_ipai)}")
    block.append(f"- Non-IPAI modules at addons root: {len(non_ipai)}")
    block.append("")
    block.append("**Policy:**")
    block.append("- Only canonical modules define the platform surface area")
    block.append(
        "- Feature modules must be explicitly referenced by a bundle dependency"
    )
    block.append(
        "- Deprecated modules should be moved to `addons/_deprecated/` and blocked by CI"
    )
    block.append("")
    block.append("**Install canonical stack:**")
    block.append("```bash")
    block.append(
        "docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init"
    )
    block.append(
        "docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init"
    )
    block.append(
        "docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init"
    )
    block.append("```")
    block.append("")
    block.append("<!-- CURRENT_STATE:END -->")

    new_block = "\n".join(block) + "\n"

    text = README.read_text(encoding="utf-8")

    pattern = re.compile(
        r"<!-- CURRENT_STATE:BEGIN -->.*?<!-- CURRENT_STATE:END -->\n?", re.S
    )
    if pattern.search(text):
        text = pattern.sub(new_block, text)
    else:
        # Insert after Key Constraints section (before Repository Layout)
        insert_marker = "## Repository Layout"
        insert_at = text.find(insert_marker)
        if insert_at != -1:
            text = text[:insert_at] + new_block + "\n" + text[insert_at:]
        else:
            # Fallback: append at end
            text = text.rstrip() + "\n\n" + new_block

    README.write_text(text, encoding="utf-8")
    print(
        f"Synced README current state block (canonical: {len(canon_present)}, other ipai: {len(other_ipai)})"
    )


if __name__ == "__main__":
    main()
