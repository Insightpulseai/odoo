#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 18 View Compatibility Fix Script

This standalone script fixes two critical Odoo 18 breaking changes:

1. tree -> list: Updates ir.actions.act_window.view_mode from 'tree' to 'list'
2. Kanban card template: Detects (and optionally deactivates) kanban views
   missing the required t-name="card" template.

Usage (inside Docker container):

    # Basic run (fix tree->list, report broken kanban)
    export ODOO_DB=odoo
    export ODOO_CONF=/etc/odoo/odoo.conf
    python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py

    # With auto-deactivation of broken kanban views
    export ODOO_DB=odoo
    export ODOO_CONF=/etc/odoo/odoo.conf
    export DEACTIVATE_BROKEN_KANBAN=1
    python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py

    # Full Docker command
    docker exec -it odoo-erp-prod bash -lc '
      export ODOO_DB=odoo
      export ODOO_CONF=/etc/odoo/odoo.conf
      python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py
    '

Environment Variables:
    ODOO_DB: Database name (default: "odoo")
    ODOO_CONF: Path to odoo.conf (default: "/etc/odoo/odoo.conf")
    DEACTIVATE_BROKEN_KANBAN: Set to "1" to auto-deactivate broken kanban views
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger("fix_odoo18_views")


def fix_tree_to_list(env):
    """
    Replace 'tree' with 'list' in ir.actions.act_window.view_mode.

    Odoo 18 renamed the 'tree' view type to 'list'. Actions using the old
    'tree' keyword will fail with:
        "View types not defined tree found in act_window action ..."

    Args:
        env: Odoo environment

    Returns:
        int: Number of actions updated
    """
    ActWindow = env["ir.actions.act_window"].sudo()
    actions = ActWindow.search([("view_mode", "ilike", "tree")])

    _logger.info("Found %s actions with 'tree' in view_mode", len(actions))

    changed = 0
    for action in actions:
        modes = [m.strip() for m in (action.view_mode or "").split(",") if m.strip()]
        if not modes:
            continue

        new_modes = ["list" if m == "tree" else m for m in modes]

        if new_modes != modes:
            old_mode = action.view_mode
            action.write({"view_mode": ",".join(new_modes)})
            _logger.info(
                "Updated action %s (%s): '%s' -> '%s'",
                action.id,
                action.name,
                old_mode,
                ",".join(new_modes),
            )
            changed += 1

    _logger.info("tree->list: Updated %s actions", changed)
    return changed


def find_broken_kanban(env):
    """
    Find active kanban views missing the required t-name="card" template.

    Odoo 18's KanbanArchParser requires a <templates><t t-name="card">...</t></templates>
    structure. Views missing this will fail with:
        "Missing 'card' template."

    Args:
        env: Odoo environment

    Returns:
        list: List of broken view records
    """
    View = env["ir.ui.view"].sudo()
    views = View.search([("type", "=", "kanban"), ("active", "=", True)])

    _logger.info("Checking %s active kanban views for card template...", len(views))

    broken = []
    for view in views:
        arch = view.arch_db or ""
        # Check for both single and double quote variants
        if 't-name="card"' not in arch and "t-name='card'" not in arch:
            broken.append(view)

    _logger.info(
        "Found %s kanban views missing 't-name=\"card\"' template", len(broken)
    )

    # Log details of broken views (limit to 200 to avoid log spam)
    for view in broken[:200]:
        _logger.warning(
            "BROKEN: id=%s, xml_id=%s, name=%s, model=%s, module=%s",
            view.id,
            view.xml_id or "(no xml_id)",
            view.name,
            view.model,
            view.module or "(unknown)",
        )

    if len(broken) > 200:
        _logger.warning("... and %s more broken views", len(broken) - 200)

    return broken


def deactivate_views(env, views):
    """
    Deactivate broken kanban views to prevent UI crashes.

    Args:
        env: Odoo environment
        views: List of ir.ui.view records to deactivate

    Returns:
        int: Number of views deactivated
    """
    if not views:
        return 0

    # Get the recordset from list
    View = env["ir.ui.view"].sudo()
    view_ids = [v.id for v in views]
    recordset = View.browse(view_ids)

    recordset.write({"active": False})

    for view in views:
        _logger.warning(
            "DEACTIVATED: id=%s, xml_id=%s, name=%s, model=%s",
            view.id,
            view.xml_id or "(no xml_id)",
            view.name,
            view.model,
        )

    _logger.info("Deactivated %s broken kanban views", len(views))
    return len(views)


def main():
    """
    Main entry point for the fix script.
    """
    # Get configuration from environment
    db_name = os.environ.get("ODOO_DB", "odoo")
    conf_path = os.environ.get("ODOO_CONF", "/etc/odoo/odoo.conf")
    deactivate_broken = os.environ.get("DEACTIVATE_BROKEN_KANBAN", "0") in (
        "1",
        "true",
        "True",
        "yes",
        "Yes",
    )

    _logger.info("=" * 60)
    _logger.info("Odoo 18 View Compatibility Fix Script")
    _logger.info("=" * 60)
    _logger.info("Database: %s", db_name)
    _logger.info("Config: %s", conf_path)
    _logger.info("Deactivate broken kanban: %s", deactivate_broken)
    _logger.info("=" * 60)

    # Initialize Odoo
    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        from odoo.tools import config
    except ImportError as e:
        _logger.error(
            "Failed to import Odoo. Make sure this script is run "
            "inside the Odoo container or environment: %s",
            e,
        )
        sys.exit(1)

    # Parse config
    try:
        config.parse_config(["-c", conf_path, "-d", db_name])
    except Exception as e:
        _logger.error("Failed to parse Odoo config: %s", e)
        sys.exit(1)

    # Initialize Odoo
    try:
        odoo.cli.server.report_configuration()
        odoo.service.server.load_server_wide_modules()
    except Exception as e:
        _logger.warning("Server-wide module load issue (may be okay): %s", e)

    # Get database registry and environment
    try:
        registry = odoo.registry(db_name)
    except Exception as e:
        _logger.error("Failed to get database registry for '%s': %s", db_name, e)
        sys.exit(1)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        _logger.info("")
        _logger.info("=== Fix 1: tree -> list in view_mode ===")
        tree_count = fix_tree_to_list(env)

        _logger.info("")
        _logger.info("=== Fix 2: Detect broken kanban views ===")
        broken_kanban = find_broken_kanban(env)

        deactivated_count = 0
        if deactivate_broken and broken_kanban:
            _logger.info("")
            _logger.info("=== Deactivating broken kanban views ===")
            deactivated_count = deactivate_views(env, broken_kanban)
        elif broken_kanban:
            _logger.warning("")
            _logger.warning(
                "To auto-deactivate broken kanban views, set DEACTIVATE_BROKEN_KANBAN=1"
            )

        # Commit changes
        cr.commit()

        # Clear caches
        env.registry.clear_cache()

        _logger.info("")
        _logger.info("=" * 60)
        _logger.info("Summary:")
        _logger.info("  - tree->list: %s actions updated", tree_count)
        _logger.info("  - Broken kanban: %s found", len(broken_kanban))
        _logger.info("  - Kanban deactivated: %s", deactivated_count)
        _logger.info("=" * 60)

        if broken_kanban and not deactivated_count:
            _logger.warning(
                "You have %s broken kanban views that may cause UI errors!",
                len(broken_kanban),
            )
            _logger.warning("Options:")
            _logger.warning(
                '  1. Patch the source modules to add t-name="card" templates'
            )
            _logger.warning(
                "  2. Re-run with DEACTIVATE_BROKEN_KANBAN=1 to auto-deactivate"
            )

    _logger.info("")
    _logger.info("Done! Restart Odoo to apply changes.")


if __name__ == "__main__":
    main()
