#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 18 View Compatibility Fix Script

Standalone script for fixing Odoo 18 view_mode breaking changes.
Can be run during deployment or manually via shell.

Fixes:
1. view_mode 'tree' → 'list' (Odoo 18 breaking change)
2. Kanban views missing t-name="card" template (optional deactivation)

Usage:
    # Set environment variables
    export ODOO_DB=odoo
    export ODOO_CONF=/etc/odoo/odoo.conf

    # Run (detect only)
    python fix_odoo18_views.py

    # Run with auto-deactivation of broken kanbans
    export DEACTIVATE_BROKEN_KANBAN=1
    python fix_odoo18_views.py

Docker usage:
    docker exec -it odoo-erp-prod bash -lc '
      export ODOO_DB=odoo
      export ODOO_CONF=/etc/odoo/odoo.conf
      # optional: export DEACTIVATE_BROKEN_KANBAN=1
      python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py
    '
    docker restart odoo-erp-prod
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger("fix_odoo18_views")


def fix_tree_to_list(env):
    """
    Fix view_mode 'tree' → 'list' for all ir.actions.act_window records.

    Odoo 18 renamed 'tree' to 'list'. This function patches all actions
    that still reference the old 'tree' view type.

    Args:
        env: Odoo environment

    Returns:
        int: Number of actions patched
    """
    ActWindow = env["ir.actions.act_window"].sudo()
    actions = ActWindow.search([("view_mode", "ilike", "tree")])

    _logger.info("Found %s actions with 'tree' in view_mode", len(actions))

    changed = 0
    for a in actions:
        modes = [m.strip() for m in (a.view_mode or "").split(",") if m.strip()]
        if not modes:
            continue
        new_modes = ["list" if m == "tree" else m for m in modes]
        if new_modes != modes:
            _logger.info(
                "  [%s] %s: '%s' → '%s'",
                a.id, a.name or "(no name)", a.view_mode, ",".join(new_modes)
            )
            a.write({"view_mode": ",".join(new_modes)})
            changed += 1

    _logger.info("tree→list updated %s actions", changed)
    return changed


def list_broken_kanban(env):
    """
    Find kanban views missing t-name="card" template.

    Odoo 18 requires kanban views to have a card template. Missing it
    triggers KanbanArchParser errors.

    Args:
        env: Odoo environment

    Returns:
        list: List of view records with missing card template
    """
    View = env["ir.ui.view"].sudo()
    views = View.search([("type", "=", "kanban"), ("active", "=", True)])

    _logger.info("Scanning %s active kanban views...", len(views))

    broken = []
    for v in views:
        arch = v.arch_db or ""
        if 't-name="card"' not in arch and "t-name='card'" not in arch:
            broken.append(v)

    _logger.info("Found %s active kanban views missing card template", len(broken))

    # Log details for first 200 broken views
    for v in broken[:200]:
        _logger.info(
            "  broken kanban: id=%s xmlid=%s name=%s model=%s module=%s",
            v.id, v.xml_id, v.name, v.model, getattr(v, 'module', 'N/A')
        )

    return broken


def deactivate_views(env, views):
    """
    Deactivate broken views to prevent UI crashes.

    This is a safety measure - it's better to have missing views than
    crashing UI. The views can be patched and reactivated later.

    Args:
        env: Odoo environment
        views: List of view records to deactivate

    Returns:
        int: Number of views deactivated
    """
    if not views:
        return 0

    view_ids = [v.id for v in views]
    env["ir.ui.view"].sudo().browse(view_ids).write({"active": False})
    _logger.info("Deactivated %s views", len(views))
    return len(views)


def main():
    """
    Main entry point for standalone script execution.
    """
    db = os.environ.get("ODOO_DB", "odoo")
    conf = os.environ.get("ODOO_CONF", "/etc/odoo/odoo.conf")
    deactivate_broken = os.environ.get("DEACTIVATE_BROKEN_KANBAN") == "1"

    _logger.info("=" * 60)
    _logger.info("Odoo 18 View Compatibility Fix")
    _logger.info("=" * 60)
    _logger.info("Database: %s", db)
    _logger.info("Config: %s", conf)
    _logger.info("Deactivate broken kanbans: %s", deactivate_broken)
    _logger.info("=" * 60)

    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        from odoo.tools import config

        # Parse config and setup Odoo
        config.parse_config(["-c", conf, "-d", db])

        # For Odoo 18, use the new setup pattern
        try:
            odoo.setup()
        except AttributeError:
            # Fallback for older setup pattern
            pass

        with api.Environment.manage():
            registry = odoo.registry(db)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})

                # Fix tree → list
                changed = fix_tree_to_list(env)

                # Find broken kanbans
                broken = list_broken_kanban(env)

                # Optionally deactivate broken views
                deactivated = 0
                if deactivate_broken and broken:
                    deactivated = deactivate_views(env, broken)

                # Clear cache
                env.registry.clear_cache()

                # Commit changes
                cr.commit()

                _logger.info("")
                _logger.info("=" * 60)
                _logger.info("Summary:")
                _logger.info("  - Actions patched (tree→list): %s", changed)
                _logger.info("  - Broken kanbans found: %s", len(broken))
                _logger.info("  - Views deactivated: %s", deactivated)
                _logger.info("=" * 60)

    except ImportError as e:
        _logger.error(
            "Odoo not found in Python path. "
            "Run this script from within the Odoo container or set PYTHONPATH. "
            "Error: %s", e
        )
        sys.exit(1)
    except Exception as e:
        _logger.error("Error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
