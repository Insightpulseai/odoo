# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
"""Backfill NULLs so Odoo can enforce NOT NULL on action queue fields."""

import logging

_logger = logging.getLogger(__name__)

_DEFAULTS = {
    'summary': 'Untitled action',
    'workflow_id': 'unknown',
    'target_model': 'res.partner',
    'action_type': 'action',
    'action_payload': '{}',
    'state': 'pending',
}


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_name = 'ipai_copilot_action_queue')"
    )
    if not cr.fetchone()[0]:
        return

    for col, default in _DEFAULTS.items():
        cr.execute(
            f"UPDATE ipai_copilot_action_queue SET {col} = %s WHERE {col} IS NULL",
            (default,),
        )
        if cr.rowcount:
            _logger.info("Backfilled %d NULL rows in action_queue.%s", cr.rowcount, col)

    # company_id: set to first company
    cr.execute(
        "UPDATE ipai_copilot_action_queue SET company_id = "
        "(SELECT id FROM res_company ORDER BY id LIMIT 1) "
        "WHERE company_id IS NULL"
    )
    if cr.rowcount:
        _logger.info("Backfilled %d NULL rows in action_queue.company_id", cr.rowcount)
