#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update is_finance_ppm field for all tasks in project 30"""

import odoo
from odoo import api, SUPERUSER_ID

# Initialize Odoo
odoo.tools.config.parse_config(["-d", "production"])
registry = odoo.registry("production")

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Update is_finance_ppm field directly via SQL
    cr.execute(
        """
        UPDATE project_task
        SET is_finance_ppm = (
            COALESCE(finance_logframe_id, 0) > 0 OR
            COALESCE(bir_schedule_id, 0) > 0 OR
            COALESCE(x_external_key, '') != ''
        )
        WHERE project_id = 30
    """
    )

    affected_rows = cr.rowcount
    cr.commit()
    print(f"Updated {affected_rows} rows")

    # Verify results
    finance_ppm_tasks = env["project.task"].search(
        [("project_id", "=", 30), ("is_finance_ppm", "=", True)]
    )
    print(f"Tasks with is_finance_ppm=True: {len(finance_ppm_tasks)}")

    # Sample check
    sample = env["project.task"].search([("project_id", "=", 30)], limit=1)
    print(f"\nSample task {sample.id}:")
    print(f"  x_external_key: {bool(sample.x_external_key)}")
    print(f"  is_finance_ppm: {sample.is_finance_ppm}")
