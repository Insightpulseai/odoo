# -*- coding: utf-8 -*-
"""
IPAI Odoo 18 Compatibility Post-Migration Script

This script runs automatically when the ipai_v18_compat module is upgraded.
It fixes two critical Odoo 18 breaking changes:

1. tree -> list: Updates ir.actions.act_window.view_mode from 'tree' to 'list'
2. Kanban card template: Detects (and optionally deactivates) kanban views
   missing the required t-name="card" template.

Usage:
    # Standard upgrade (runs this migration)
    odoo -d <database> -u ipai_v18_compat --stop-after-init

    # Enable auto-deactivation of broken kanban views
    # Set system parameter: ipai_v18_compat.deactivate_broken_kanban = 1
"""

import logging

_logger = logging.getLogger(__name__)


def _fix_tree_to_list(env):
    """
    Replace 'tree' with 'list' in ir.actions.act_window.view_mode.

    Odoo 18 renamed the 'tree' view type to 'list'. Actions using the old
    'tree' keyword will fail with:
        "View types not defined tree found in act_window action ..."

    Returns:
        int: Number of actions updated
    """
    ActWindow = env["ir.actions.act_window"].sudo()
    actions = ActWindow.search([("view_mode", "ilike", "tree")])

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
                "ipai_v18_compat: Updated action %s (%s): '%s' -> '%s'",
                action.id,
                action.name,
                old_mode,
                ",".join(new_modes),
            )
            changed += 1

    _logger.warning(
        "ipai_v18_compat: tree->list migration completed. Updated %s act_window actions.",
        changed,
    )
    return changed


def _find_kanban_missing_card(env):
    """
    Find active kanban views missing the required t-name="card" template.

    Odoo 18's KanbanArchParser requires a <templates><t t-name="card">...</t></templates>
    structure. Views missing this will fail with:
        "Missing 'card' template."

    Returns:
        recordset: ir.ui.view records with broken kanban templates
    """
    View = env["ir.ui.view"].sudo()
    views = View.search([("type", "=", "kanban"), ("active", "=", True)])

    broken = View.browse()
    for view in views:
        arch = view.arch_db or ""
        # Check for both single and double quote variants
        if 't-name="card"' not in arch and "t-name='card'" not in arch:
            broken |= view
            _logger.info(
                "ipai_v18_compat: Kanban view missing card template: "
                "id=%s, xml_id=%s, name=%s, model=%s, module=%s",
                view.id,
                view.xml_id or "(no xml_id)",
                view.name,
                view.model,
                view.module or "(unknown)",
            )

    _logger.warning(
        "ipai_v18_compat: Found %s active kanban views missing 't-name=\"card\"' template.",
        len(broken),
    )
    return broken


def _deactivate_broken_views(env, views):
    """
    Deactivate broken kanban views to prevent UI crashes.

    This is the safest approach: it allows the system to boot while you
    patch the source modules. The views can be re-activated after fixing
    their templates.

    Args:
        env: Odoo environment
        views: recordset of ir.ui.view to deactivate

    Returns:
        int: Number of views deactivated
    """
    if not views:
        return 0

    deactivated = []
    for view in views:
        deactivated.append(
            {
                "id": view.id,
                "xml_id": view.xml_id or "(no xml_id)",
                "name": view.name,
                "model": view.model,
            }
        )

    views.write({"active": False})

    for info in deactivated:
        _logger.warning(
            "ipai_v18_compat: DEACTIVATED kanban view id=%s xml_id=%s name=%s model=%s",
            info["id"],
            info["xml_id"],
            info["name"],
            info["model"],
        )

    _logger.warning(
        "ipai_v18_compat: Deactivated %s broken kanban views. "
        "Re-activate after fixing their templates.",
        len(views),
    )
    return len(views)


def migrate(cr, version):
    """
    Post-migration hook for ipai_v18_compat module.

    This function is automatically called by Odoo during module upgrade.

    Args:
        cr: Database cursor
        version: Current module version (before migration)
    """
    # Import here to avoid issues during module loading
    from odoo.api import Environment
    from odoo import SUPERUSER_ID

    _logger.warning(
        "ipai_v18_compat: Starting post-migration (from version=%s)", version
    )

    env = Environment(cr, SUPERUSER_ID, {})

    # Fix 1: tree -> list in view_mode
    tree_count = _fix_tree_to_list(env)

    # Fix 2: Find broken kanban views
    broken_kanban = _find_kanban_missing_card(env)

    # Optionally deactivate broken views (opt-in via system parameter)
    # Set in Odoo: Settings -> Technical -> Parameters -> System Parameters
    # Key: ipai_v18_compat.deactivate_broken_kanban = 1
    deactivate_param = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("ipai_v18_compat.deactivate_broken_kanban", "0")
    )
    should_deactivate = deactivate_param in ("1", "true", "True", "yes", "Yes")

    deactivated_count = 0
    if should_deactivate and broken_kanban:
        deactivated_count = _deactivate_broken_views(env, broken_kanban)
    elif broken_kanban:
        _logger.warning(
            "ipai_v18_compat: To auto-deactivate broken kanban views, set system parameter "
            "'ipai_v18_compat.deactivate_broken_kanban' to '1'"
        )

    # Clear caches to ensure changes take effect
    env.registry.clear_cache()

    _logger.warning(
        "ipai_v18_compat: Post-migration completed. "
        "tree->list: %s actions updated, "
        "broken kanban: %s found, %s deactivated.",
        tree_count,
        len(broken_kanban),
        deactivated_count,
    )
