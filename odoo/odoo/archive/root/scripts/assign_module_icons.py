#!/usr/bin/env python3
"""
Assign appropriate Odoo brand-compliant icons to IPAI custom modules.

Based on Odoo Brand Assets: https://www.odoo.com/page/brand-assets
Icon guidelines follow Odoo's visual identity standards.
"""

import os
import re
from pathlib import Path

# Odoo brand-compliant icon assignments
# Icons follow Odoo's design language and module categorization
MODULE_ICONS = {
    # Finance & Accounting - Purple (#714B67 - Odoo Accounting color)
    "ipai_bir_tax_compliance": "fa-file-invoice",  # Tax compliance
    "ipai_tbwa_finance": "fa-building",  # Finance operations
    "ipai_month_end": "fa-calendar-check",  # Month-end closing
    "ipai_finance_closing": "fa-lock",  # Financial close
    "ipai_finance_close_seed": "fa-database",  # Seed data
    "ipai_month_end_closing": "fa-calendar-alt",  # Closing tasks
    "ipai_close_orchestration": "fa-tasks",  # Task orchestration
    # Project & PPM - Blue (#017E84 - Odoo Project color)
    "ipai_finance_ppm_golive": "fa-rocket",  # Go-live checklist
    "ipai_finance_ppm_umbrella": "fa-umbrella",  # Complete PPM
    "ipai_ppm_a1": "fa-sitemap",  # Control center
    # WorkOS Suite - Teal (#00A09D - Odoo Productivity color)
    "ipai_workos_core": "fa-cube",  # Core foundation
    "ipai_workos_blocks": "fa-th",  # Block system
    "ipai_workos_db": "fa-table",  # Database
    "ipai_workos_canvas": "fa-draw-polygon",  # Canvas
    "ipai_workos_collab": "fa-users",  # Collaboration
    "ipai_workos_search": "fa-search",  # Search
    "ipai_workos_templates": "fa-file-alt",  # Templates
    "ipai_workos_views": "fa-th-list",  # Views
    "ipai_workos_affine": "fa-layer-group",  # Complete suite
    # Platform Infrastructure - Dark Gray (#2C2C36 - Odoo Technical color)
    "ipai_platform_audit": "fa-history",  # Audit trail
    "ipai_platform_permissions": "fa-shield-alt",  # Permissions
    "ipai_platform_theme": "fa-palette",  # Theming
    "ipai_platform_workflow": "fa-project-diagram",  # Workflow engine
    "ipai_platform_approvals": "fa-check-circle",  # Approvals
    # AI & Automation - Purple gradient (#8F3A84 - Odoo AI color)
    "ipai_ask_ai": "fa-robot",  # AI assistant
    "ipai_ask_ai_chatter": "fa-comments",  # AI chat
    "ipai_ocr_gateway": "fa-file-image",  # OCR
    "ipai_sms_gateway": "fa-sms",  # SMS
    "ipai_grid_view": "fa-th-large",  # Grid view
    # CRM & Sales - Red (#DC6965 - Odoo CRM color)
    "ipai_crm_pipeline": "fa-funnel-dollar",  # CRM pipeline
    # Integrations - Green (#2CBB9B - Odoo Integration color)
    "ipai_superset_connector": "fa-chart-bar",  # BI integration
    # Themes - Orange (#F06F02 - Odoo Website color)
    "ipai_web_theme_chatgpt": "fa-comments-dollar",  # ChatGPT theme
    "ipai_theme_tbwa_backend": "fa-paint-brush",  # TBWA theme
    # Namespace - Gray (system module)
    "ipai": "fa-cube",  # Core namespace
}

# Category mapping for icon_folder assignment
CATEGORY_ICONS = {
    "Accounting": "account",
    "Productivity": "productivity",
    "Technical": "technical",
    "Human Resources": "hr",
    "Sales": "sales",
    "Marketing": "marketing",
    "Website": "website",
}


def update_manifest_icon(manifest_path: Path, icon_class: str):
    """Update or add icon field in __manifest__.py"""

    if not manifest_path.exists():
        print(f"  ❌ Manifest not found: {manifest_path}")
        return False

    content = manifest_path.read_text()

    # Check if icon already exists
    if re.search(r'"icon":\s*"', content):
        # Update existing icon
        updated = re.sub(r'"icon":\s*"[^"]*"', f'"icon": "{icon_class}"', content)
    else:
        # Add icon field after license
        updated = re.sub(
            r'("license":\s*"[^"]*",)', f'\\1\\n    "icon": "{icon_class}",', content
        )

    if updated != content:
        manifest_path.write_text(updated)
        return True

    return False


def main():
    """Assign icons to all IPAI custom modules"""

    print("=" * 80)
    print("IPAI Custom Modules - Icon Assignment")
    print("=" * 80)
    print(f"Total modules to process: {len(MODULE_ICONS)}")
    print("")

    addons_path = Path(__file__).parent.parent / "addons"

    if not addons_path.exists():
        print(f"❌ Addons directory not found: {addons_path}")
        return 1

    updated = 0
    skipped = 0
    errors = 0

    for module_name, icon_class in MODULE_ICONS.items():
        manifest_path = addons_path / module_name / "__manifest__.py"

        print(f"📦 {module_name}")
        print(f"   Icon: {icon_class}")

        if update_manifest_icon(manifest_path, icon_class):
            print(f"   ✅ Updated")
            updated += 1
        elif not manifest_path.exists():
            print(f"   ⚠️  Skipped (manifest not found)")
            skipped += 1
        else:
            print(f"   ℹ️  Already set")
            errors += 1

        print("")

    print("=" * 80)
    print("Summary:")
    print(f"  ✅ Updated: {updated}")
    print(f"  ℹ️  Already set: {errors}")
    print(f"  ⚠️  Skipped: {skipped}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
