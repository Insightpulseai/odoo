#!/usr/bin/env python3
"""
Odoo Module Inventory — Full CE + OCA + IPAI Audit (Prod-Ready)

Queries a running Odoo instance via XML-RPC and generates a complete
inventory of ALL modules: installed, installable, and uninstallable.

Outputs: JSON, CSV, and Markdown reports.

Usage:
    # Env-driven (recommended for prod):
    export ODOO_URL=https://erp.insightpulseai.com
    export ODOO_DB=odoo_prod
    export ODOO_USER=admin
    export ODOO_PASSWORD=<from-vault>
    python scripts/inventory_modules.py

    # CLI args:
    python scripts/inventory_modules.py \
        --url https://erp.insightpulseai.com \
        --db odoo_prod \
        --user admin \
        --password <password> \
        --output docs/audits/module_inventory

    # Via docker exec against local stack:
    docker compose exec -T web odoo shell -d odoo_dev --stop-after-init \
        < scripts/inventory_modules_shell.py
"""

import argparse
import csv
import json
import os
import sys
import xmlrpc.client
from collections import Counter, defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Classification Rules
# ---------------------------------------------------------------------------


def classify_module(name, author="", category=""):
    """Classify module origin: ce_core, oca, ipai, third_party."""
    if name.startswith("ipai_"):
        return "ipai"
    author_lower = (author or "").lower()
    if "odoo community association" in author_lower or "oca" in author_lower:
        return "oca"
    if "odoo s.a" in author_lower or "odoo sa" in author_lower:
        return "ce_core"
    # Heuristic: base Odoo modules
    if author_lower in ("", "odoo", "openerp"):
        return "ce_core"
    return "third_party"


def classify_state(state):
    """Normalize Odoo module state to a human label."""
    state_map = {
        "installed": "Installed",
        "uninstalled": "Installable",
        "to install": "Pending Install",
        "to upgrade": "Pending Upgrade",
        "to remove": "Pending Remove",
        "uninstallable": "Uninstallable",
    }
    return state_map.get(state, state)


# ---------------------------------------------------------------------------
# XML-RPC Connection
# ---------------------------------------------------------------------------


def connect(url, db, user, password):
    """Authenticate via XML-RPC, return (uid, models_proxy, db, password)."""
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, user, password, {})
    if not uid:
        raise ConnectionError(
            f"Authentication failed for {user}@{db}. Check credentials."
        )
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    return uid, models, db, password


# ---------------------------------------------------------------------------
# Module Fetch
# ---------------------------------------------------------------------------

FIELDS = [
    "name",
    "state",
    "shortdesc",
    "author",
    "category_id",
    "installed_version",
    "latest_version",
    "website",
    "license",
    "application",
    "auto_install",
    "summary",
]


def fetch_all_modules(uid, models, db, password):
    """Fetch every record from ir.module.module."""
    return models.execute_kw(
        db,
        uid,
        password,
        "ir.module.module",
        "search_read",
        [[]],
        {"fields": FIELDS, "order": "name asc"},
    )


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------


def build_inventory(modules):
    """Enrich raw module records with classification."""
    inventory = []
    for mod in modules:
        cat_name = mod["category_id"][1] if mod["category_id"] else "Uncategorized"
        origin = classify_module(mod["name"], mod.get("author", ""), cat_name)
        inventory.append(
            {
                "name": mod["name"],
                "display_name": mod.get("shortdesc") or mod["name"],
                "state": mod["state"],
                "state_label": classify_state(mod["state"]),
                "origin": origin,
                "category": cat_name,
                "version": mod.get("installed_version")
                or mod.get("latest_version")
                or "-",
                "author": mod.get("author", ""),
                "license": mod.get("license", ""),
                "application": mod.get("application", False),
                "auto_install": mod.get("auto_install", False),
                "summary": (mod.get("summary") or "")[:120],
            }
        )
    return inventory


def generate_summary(inventory):
    """Generate summary statistics."""
    by_origin = Counter(m["origin"] for m in inventory)
    by_state = Counter(m["state_label"] for m in inventory)
    by_origin_state = defaultdict(lambda: Counter())
    for m in inventory:
        by_origin_state[m["origin"]][m["state_label"]] += 1

    return {
        "total_modules": len(inventory),
        "by_origin": dict(by_origin),
        "by_state": dict(by_state),
        "by_origin_state": {k: dict(v) for k, v in by_origin_state.items()},
        "installed_count": by_state.get("Installed", 0),
        "installable_count": by_state.get("Installable", 0),
        "applications": sum(1 for m in inventory if m["application"]),
        "auto_install": sum(1 for m in inventory if m["auto_install"]),
    }


def generate_markdown(inventory, summary, db_name, url):
    """Generate markdown report."""
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Odoo Module Inventory",
        "",
        f"**Database:** `{db_name}` | **URL:** `{url}` | **Generated:** {ts}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total modules | {summary['total_modules']} |",
        f"| Installed | {summary['installed_count']} |",
        f"| Installable (not installed) | {summary['installable_count']} |",
        f"| Applications | {summary['applications']} |",
        f"| Auto-install | {summary['auto_install']} |",
        "",
        "### By Origin",
        "",
        "| Origin | Installed | Installable | Uninstallable | Total |",
        "|--------|-----------|-------------|---------------|-------|",
    ]

    for origin in ["ce_core", "oca", "ipai", "third_party"]:
        states = summary["by_origin_state"].get(origin, {})
        installed = states.get("Installed", 0)
        installable = states.get("Installable", 0)
        uninstallable = states.get("Uninstallable", 0)
        total = summary["by_origin"].get(origin, 0)
        label = {
            "ce_core": "CE Core",
            "oca": "OCA",
            "ipai": "IPAI",
            "third_party": "Third Party",
        }
        lines.append(
            f"| {label.get(origin, origin)} | {installed} | {installable} | {uninstallable} | {total} |"
        )

    # Installed modules by origin
    for origin, label in [
        ("ce_core", "CE Core"),
        ("oca", "OCA"),
        ("ipai", "IPAI"),
        ("third_party", "Third Party"),
    ]:
        origin_mods = [m for m in inventory if m["origin"] == origin]
        if not origin_mods:
            continue
        installed = [m for m in origin_mods if m["state"] == "installed"]
        installable = [m for m in origin_mods if m["state"] == "uninstalled"]

        lines.append("")
        lines.append(
            f"## {label} Modules ({len(installed)} installed, {len(installable)} installable)"
        )
        lines.append("")
        lines.append("| Module | State | Version | Category | License |")
        lines.append("|--------|-------|---------|----------|---------|")
        for m in origin_mods:
            state_icon = {
                "Installed": "**Installed**",
                "Installable": "Installable",
                "Uninstallable": "~~Uninstallable~~",
            }.get(m["state_label"], m["state_label"])
            lines.append(
                f"| `{m['name']}` | {state_icon} | {m['version']} | {m['category']} | {m['license']} |"
            )

    return "\n".join(lines)


def write_csv(inventory, filepath):
    """Write inventory to CSV."""
    fieldnames = [
        "name",
        "display_name",
        "state",
        "state_label",
        "origin",
        "category",
        "version",
        "author",
        "license",
        "application",
        "auto_install",
        "summary",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate full Odoo module inventory via XML-RPC"
    )
    parser.add_argument("--url", default=os.getenv("ODOO_URL"), help="Odoo URL")
    parser.add_argument("--db", default=os.getenv("ODOO_DB"), help="Database name")
    parser.add_argument(
        "--user", default=os.getenv("ODOO_USER", "admin"), help="Username"
    )
    parser.add_argument(
        "--password", default=os.getenv("ODOO_PASSWORD"), help="Password"
    )
    parser.add_argument(
        "--output",
        default="docs/audits/module_inventory",
        help="Output directory (default: docs/audits/module_inventory)",
    )

    args = parser.parse_args()

    if not args.url or not args.db or not args.password:
        print(
            "Missing required config. Set ODOO_URL, ODOO_DB, ODOO_PASSWORD "
            "env vars or pass --url, --db, --password.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Connect
    print(f"Connecting to {args.url} (db: {args.db})...")
    uid, models, db, pwd = connect(args.url, args.db, args.user, args.password)
    print(f"Authenticated as UID {uid}")

    # Fetch
    print("Fetching all modules from ir.module.module...")
    raw_modules = fetch_all_modules(uid, models, db, pwd)
    print(f"Found {len(raw_modules)} modules")

    # Build inventory
    inventory = build_inventory(raw_modules)
    summary = generate_summary(inventory)

    # Output
    os.makedirs(args.output, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")

    json_path = os.path.join(args.output, f"inventory_{ts}.json")
    csv_path = os.path.join(args.output, f"inventory_{ts}.csv")
    md_path = os.path.join(args.output, f"inventory_{ts}.md")
    latest_json = os.path.join(args.output, "latest.json")

    # Write JSON
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "database": args.db,
        "url": args.url,
        "summary": summary,
        "modules": inventory,
    }
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    with open(latest_json, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    # Write CSV
    write_csv(inventory, csv_path)

    # Write Markdown
    md_content = generate_markdown(inventory, summary, args.db, args.url)
    with open(md_path, "w") as f:
        f.write(md_content)

    # Print summary to stdout
    print(f"\n{'=' * 60}")
    print("MODULE INVENTORY COMPLETE")
    print("=" * 60)
    print(f"Total modules:  {summary['total_modules']}")
    print(f"  CE Core:      {summary['by_origin'].get('ce_core', 0)}")
    print(f"  OCA:          {summary['by_origin'].get('oca', 0)}")
    print(f"  IPAI:         {summary['by_origin'].get('ipai', 0)}")
    print(f"  Third Party:  {summary['by_origin'].get('third_party', 0)}")
    print()
    print(f"Installed:      {summary['installed_count']}")
    print(f"Installable:    {summary['installable_count']}")
    print(f"Applications:   {summary['applications']}")
    print()
    print("Reports written:")
    print(f"  JSON:  {json_path}")
    print(f"  CSV:   {csv_path}")
    print(f"  MD:    {md_path}")
    print(f"  Latest: {latest_json}")


if __name__ == "__main__":
    main()
