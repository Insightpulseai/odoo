#!/usr/bin/env python3
"""
Odoo OCA Module Audit Script

Audits whether specific OCA modules are installed in an Odoo database
via XML-RPC API and produces a clean status report.

Usage:
    python scripts/audit_oca_modules.py --url URL --db DATABASE --user USER --password PASSWORD

Example:
    python scripts/audit_oca_modules.py \
        --url https://erp.insightpulseai.com \
        --db odoo_core \
        --user admin \
        --password your_password

Output: Markdown table with installation status per module.
"""

import argparse
import sys
import xmlrpc.client
from typing import Optional

# Modules to audit by category
MODULES_TO_AUDIT = {
    "BASE (Must Have)": [
        "partner_contact_access_link",
        "partner_firstname",
        "queue_job",
        "report_xlsx",
        "password_security",
        "disable_odoo_online",
        "remove_odoo_enterprise",
        "auditlog",
        "base_name_search_improved",
        "date_range",
        "server_action_mass_edit",
        "web_advanced_search",
        "web_dialog_size",
        "web_environment_ribbon",
        "web_favicon",
        "web_listview_range_select",
        "web_m2x_options",
        "web_no_bubble",
        "web_pivot_computed_measure",
        "web_refresher",
        "web_responsive",
        "web_search_with_and",
        "web_tree_many2one_clickable",
        "mail_debrand",
        "mail_tracking",
        "document_url",
        "base_search_mail_content",
        "mail_activity_plan",
    ],
    "SALES (Must Have)": [
        "portal_sale_order_search",
        "sale_cancel_reason",
        "sale_commercial_partner",
        "sale_delivery_state",
        "sale_fixed_discount",
        "sale_order_archive",
        "sale_order_line_delivery_state",
        "sale_order_line_input",
        "sale_order_line_menu",
        "sale_order_line_price_history",
        "sale_report_salesperson_from_partner",
    ],
    "ACCOUNTING (Must Have)": [
        "account_analytic_required",
        "partner_statement",
        "account_asset_management",
        "account_chart_update",
        "account_journal_lock_date",
        "account_lock_date_update",
        "account_move_line_tax_editable",
        "account_usability",
        "account_reconcile_oca",
        "account_reconcile_model_oca",
        "account_statement_base",
        "currency_rate_update",
        "mis_builder",
        "mis_builder_demo",
        "mis_builder_budget",
        "account_financial_report",
        "date_range_account",
    ],
}

# Modules that may be replaced by Odoo 18 core functionality
REPLACED_BY_CORE = {
    "mail_activity_plan": "Activity plans are native in Odoo 18 (mail module)",
    "web_responsive": "Odoo 18 has improved responsive design natively",
    "account_chart_update": "Chart update functionality improved in Odoo 18",
}


def connect_odoo(url: str, db: str, username: str, password: str):
    """Connect to Odoo via XML-RPC and return connection objects."""
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")

    # Authenticate
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed. Check credentials.")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models, db, password


def get_module_info(models, db: str, uid: int, password: str, module_name: str) -> dict:
    """Query a single module's info from ir.module.module."""
    result = models.execute_kw(
        db,
        uid,
        password,
        "ir.module.module",
        "search_read",
        [[["name", "=", module_name]]],
        {
            "fields": [
                "name",
                "state",
                "installed_version",
                "latest_version",
                "shortdesc",
            ]
        },
    )

    if result:
        return result[0]
    return None


def audit_modules(url: str, db: str, username: str, password: str) -> dict:
    """Audit all modules and return results."""
    print(f"Connecting to {url}...")
    uid, models, db, pwd = connect_odoo(url, db, username, password)
    print(f"Connected as UID {uid}")
    print()

    results = {}

    for category, modules in MODULES_TO_AUDIT.items():
        results[category] = []
        print(f"Auditing {category}...")

        for module_name in modules:
            info = get_module_info(models, db, uid, pwd, module_name)

            if info is None:
                # Module not found in database
                note = REPLACED_BY_CORE.get(
                    module_name, "Code not present in addons path"
                )
                results[category].append(
                    {
                        "name": module_name,
                        "status": "Not found",
                        "version": "-",
                        "notes": note,
                    }
                )
            else:
                state = info.get("state", "unknown")
                version = (
                    info.get("installed_version") or info.get("latest_version") or "-"
                )
                shortdesc = info.get("shortdesc", "")

                if state == "installed":
                    status = "Installed"
                    note = shortdesc[:50] if shortdesc else ""
                elif state == "uninstalled":
                    status = "Present, not installed"
                    note = "Available to install"
                elif state == "to install":
                    status = "Pending install"
                    note = "Queued for installation"
                elif state == "to upgrade":
                    status = "Pending upgrade"
                    note = ""
                else:
                    status = f"State: {state}"
                    note = ""

                results[category].append(
                    {
                        "name": module_name,
                        "status": status,
                        "version": version,
                        "notes": note,
                    }
                )

    return results


def generate_report(results: dict) -> str:
    """Generate markdown report from results."""
    lines = []
    lines.append("# OCA Module Audit Report")
    lines.append("")
    lines.append(f"**Odoo Version:** 18.0 CE")
    lines.append("")

    # Summary counters
    total_installed = 0
    total_present = 0
    total_not_found = 0
    missing_modules = []

    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| Category | Module (technical name) | Status | Version | Notes |")
    lines.append("|----------|------------------------|--------|---------|-------|")

    for category, modules in results.items():
        for i, mod in enumerate(modules):
            cat_col = category if i == 0 else ""
            lines.append(
                f"| {cat_col} | `{mod['name']}` | {mod['status']} | {mod['version']} | {mod['notes']} |"
            )

            # Count stats
            if mod["status"] == "Installed":
                total_installed += 1
            elif mod["status"] == "Present, not installed":
                total_present += 1
                missing_modules.append((category, mod["name"]))
            elif "Not found" in mod["status"]:
                total_not_found += 1
                missing_modules.append((category, mod["name"]))

    # Summary section
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| **Installed** | {total_installed} |")
    lines.append(f"| **Present (not installed)** | {total_present} |")
    lines.append(f"| **Not found** | {total_not_found} |")
    lines.append(
        f"| **Total audited** | {total_installed + total_present + total_not_found} |"
    )
    lines.append("")

    # Per-category summary
    lines.append("### Installed per Category")
    lines.append("")
    for category, modules in results.items():
        installed = sum(1 for m in modules if m["status"] == "Installed")
        total = len(modules)
        lines.append(f"- **{category}**: {installed}/{total} installed")
    lines.append("")

    # Top missing
    if missing_modules:
        lines.append("### Top Missing Modules (action required)")
        lines.append("")
        for cat, name in missing_modules[:10]:
            note = REPLACED_BY_CORE.get(name, "")
            if note:
                lines.append(f"- `{name}` ({cat.split()[0]}) - *{note}*")
            else:
                lines.append(f"- `{name}` ({cat.split()[0]})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit OCA modules in Odoo via XML-RPC"
    )
    parser.add_argument(
        "--url", required=True, help="Odoo URL (e.g., https://erp.insightpulseai.com)"
    )
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--user", required=True, help="Username (login)")
    parser.add_argument("--password", required=True, help="Password or API key")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args()

    try:
        results = audit_modules(args.url, args.db, args.user, args.password)
        report = generate_report(results)

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")
        else:
            print("\n" + "=" * 60)
            print(report)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
