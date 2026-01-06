#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 18 View Compatibility Fix Script

Standalone script wrapper for fixing Odoo 18 view_mode breaking changes.
Can be run during deployment or manually via shell.

Usage:
    # From Odoo shell
    python addons/ipai/scripts/fix_odoo18_views.py

    # Or via odoo-bin shell
    odoo-bin shell -d odoo_core --addons-path=addons/ipai
    >>> exec(open('addons/ipai/scripts/fix_odoo18_views.py').read())

    # Or directly with database connection
    python addons/ipai/scripts/fix_odoo18_views.py --database odoo_core

This script provides the same functionality as the ipai_v18_compat module
but can be run independently without installing the module.
"""
import argparse
import logging
import re
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger(__name__)


def fix_tree_to_list(env):
    """
    Fix view_mode 'tree' → 'list' for all ir.actions.act_window records.

    Args:
        env: Odoo environment

    Returns:
        int: Number of actions patched
    """
    _logger.info("Searching for actions with 'tree' in view_mode...")

    actions = env["ir.actions.act_window"].search([
        ("view_mode", "ilike", "tree")
    ])

    _logger.info("Found %d actions to check", len(actions))

    patched_count = 0
    for action in actions:
        old_mode = action.view_mode
        new_mode = re.sub(r'\btree\b', 'list', old_mode)

        if new_mode != old_mode:
            _logger.info(
                "  [%d] %s: '%s' → '%s'",
                action.id, action.name or "(no name)", old_mode, new_mode
            )
            action.write({"view_mode": new_mode})
            patched_count += 1

    return patched_count


def detect_broken_kanbans(env):
    """
    Detect kanban views that may need t-name="card" template.

    Args:
        env: Odoo environment

    Returns:
        list: List of potentially broken view IDs and names
    """
    _logger.info("Scanning kanban views for potential issues...")

    broken = []
    kanban_views = env["ir.ui.view"].search([
        ("type", "=", "kanban"),
        ("active", "=", True)
    ])

    for view in kanban_views:
        arch = view.arch_db or ""
        if 'kanban-box' in arch and 't-name="card"' not in arch:
            broken.append({
                "id": view.id,
                "name": view.name,
                "model": view.model,
            })
            _logger.warning(
                "  [%d] %s (model: %s) - may need t-name='card'",
                view.id, view.name, view.model
            )

    return broken


def main_with_env(env):
    """
    Main function when Odoo environment is available.

    Args:
        env: Odoo environment
    """
    _logger.info("=" * 60)
    _logger.info("Odoo 18 View Compatibility Fix")
    _logger.info("=" * 60)

    # Fix tree → list
    patched = fix_tree_to_list(env)
    _logger.info("Patched %d actions (tree → list)", patched)

    # Detect broken kanbans
    broken = detect_broken_kanbans(env)
    _logger.info("Found %d potentially broken kanban views", len(broken))

    if broken:
        _logger.info("")
        _logger.info("Kanban views needing manual review:")
        for v in broken:
            _logger.info("  - [%d] %s (model: %s)", v["id"], v["name"], v["model"])

    _logger.info("")
    _logger.info("=" * 60)
    _logger.info("Fix complete!")
    _logger.info("=" * 60)

    # Commit the transaction
    env.cr.commit()

    return {"patched": patched, "broken_kanbans": len(broken)}


def main():
    """
    Standalone entry point with argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="Fix Odoo 18 view_mode breaking changes"
    )
    parser.add_argument(
        "-d", "--database",
        default="odoo_core",
        help="Database name (default: odoo_core)"
    )
    parser.add_argument(
        "-c", "--config",
        help="Odoo config file path"
    )
    args = parser.parse_args()

    # Check if we're already in Odoo environment
    try:
        # Try to use existing environment (e.g., from odoo shell)
        from odoo import api, SUPERUSER_ID
        from odoo.cli import server
        from odoo.tools import config

        if args.config:
            config.parse_config(["-c", args.config])

        # Get database registry
        from odoo.modules.registry import Registry
        registry = Registry(args.database)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            result = main_with_env(env)
            return result

    except ImportError:
        _logger.error(
            "Odoo not found in Python path. "
            "Run this script from Odoo shell or set PYTHONPATH."
        )
        sys.exit(1)
    except Exception as e:
        _logger.error("Error: %s", e)
        sys.exit(1)


# Allow running from Odoo shell with exec()
if __name__ == "__main__":
    main()
else:
    # When exec'd from Odoo shell, 'env' should be available
    try:
        if 'env' in dir():
            main_with_env(env)  # noqa: F821
    except NameError:
        pass  # Not in Odoo shell context
