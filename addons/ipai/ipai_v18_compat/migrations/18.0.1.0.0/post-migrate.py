# -*- coding: utf-8 -*-
"""
Post-migration script for ipai_v18_compat module upgrade.

This script runs after the module is upgraded, ensuring that any new
actions introduced by other module upgrades also get patched.

Fixes:
1. view_mode 'tree' → 'list' (Odoo 18 breaking change)
2. Kanban views missing t-name="card" template (optional deactivation)
"""
import logging

_logger = logging.getLogger(__name__)


def _fix_tree_to_list(env):
    """
    Fix view_mode 'tree' → 'list' for all ir.actions.act_window records.

    Odoo 18 renamed 'tree' to 'list'. This function patches all actions
    that still reference the old 'tree' view type.

    Returns:
        int: Number of actions patched
    """
    ActWindow = env["ir.actions.act_window"].sudo()
    actions = ActWindow.search([("view_mode", "ilike", "tree")])

    changed = 0
    for a in actions:
        modes = [m.strip() for m in (a.view_mode or "").split(",") if m.strip()]
        if not modes:
            continue
        new_modes = ["list" if m == "tree" else m for m in modes]
        if new_modes != modes:
            _logger.info(
                "ipai_v18_compat: patching action %s [%s]: '%s' → '%s'",
                a.id, a.name, a.view_mode, ",".join(new_modes)
            )
            a.write({"view_mode": ",".join(new_modes)})
            changed += 1

    _logger.warning("ipai_v18_compat: tree→list updated %s act_window actions", changed)
    return changed


def _find_kanban_missing_card(env):
    """
    Find kanban views missing t-name="card" template.

    Odoo 18 requires kanban views to have a card template. Missing it
    triggers KanbanArchParser errors.

    Returns:
        list: List of view records with missing card template
    """
    View = env["ir.ui.view"].sudo()
    views = View.search([("type", "=", "kanban"), ("active", "=", True)])

    broken = []
    for v in views:
        arch = v.arch_db or ""
        if 't-name="card"' not in arch and "t-name='card'" not in arch:
            broken.append(v)
            _logger.info(
                "ipai_v18_compat: broken kanban: id=%s xmlid=%s name=%s model=%s module=%s",
                v.id, v.xml_id, v.name, v.model, getattr(v, 'module', 'N/A')
            )

    _logger.warning(
        "ipai_v18_compat: found %s active kanban views missing card template",
        len(broken)
    )
    return broken


def _deactivate_views(env, views):
    """
    Deactivate broken views to prevent UI crashes.

    This is a safety measure - it's better to have missing views than
    crashing UI. The views can be patched and reactivated later.

    Returns:
        int: Number of views deactivated
    """
    if not views:
        return 0

    view_ids = [v.id for v in views]
    env["ir.ui.view"].sudo().browse(view_ids).write({"active": False})
    _logger.warning("ipai_v18_compat: deactivated %s broken kanban views", len(views))
    return len(views)


def migrate(cr, version):
    """
    Post-migration hook for module upgrade.

    Re-runs the view_mode fix to catch any new actions that may have
    been introduced by other module installations/upgrades.

    To enable automatic deactivation of broken kanban views, set:
        Settings → Technical → Parameters → System Parameters
        key: ipai_v18_compat.deactivate_broken_kanban = 1
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.warning("ipai_v18_compat: post-migrate start (version=%s)", version)

    # Fix tree → list in view_mode
    changed = _fix_tree_to_list(env)

    # Find broken kanban views
    broken_kanban = _find_kanban_missing_card(env)

    # Check if auto-deactivation is enabled via system parameter
    deactivate = env["ir.config_parameter"].sudo().get_param(
        "ipai_v18_compat.deactivate_broken_kanban"
    ) in ("1", "true", "True")

    deactivated = 0
    if deactivate and broken_kanban:
        deactivated = _deactivate_views(env, broken_kanban)

    # Clear registry cache to ensure changes take effect
    env.registry.clear_cache()

    _logger.warning(
        "ipai_v18_compat: post-migrate done. "
        "Patched %d actions, found %d broken kanbans, deactivated %d views.",
        changed, len(broken_kanban), deactivated
    )
