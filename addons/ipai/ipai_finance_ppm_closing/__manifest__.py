# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM Closing Generator",
    "summary": "Idempotent Month-End Close & BIR Task Generator with audit trail.",
    "description": """
Month-End Close Task Generator
==============================

This module provides an idempotent task generator for recurring month-end
closing and BIR filing workflows.

Key Features:
- Deterministic external keys for idempotent upserts
- SHA256 hashing for change detection
- Complete audit trail via generation runs
- Completeness reporting (PASS/WARN/FAIL)
- Business day computation for deadlines
- Employee code resolution for assignments

Usage:
------
1. Store seed JSON in ir.config_parameter 'ipai.close.seed_json'
2. Set x_employee_code on res.users for assignment resolution
3. Run generator via cron or manually:
   env['ipai.close.generator'].run_from_config('MONTH_END_CLOSE')

The generator creates:
- One project per cycle
- Parent tasks per template
- Child tasks per step with computed deadlines
- Audit records for traceability
    """,
    "version": "18.0.1.1.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "project",
        "ipai_finance_ppm",
        "ipai_ppm_monthly_close",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
