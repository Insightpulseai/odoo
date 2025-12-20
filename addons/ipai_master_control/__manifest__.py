# -*- coding: utf-8 -*-
{
    "name": "Master Control - Work Intake",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Bridge Odoo events to Master Control work items",
    "description": """
Master Control Work Intake Adapter
==================================

This module emits webhooks to the Pulser Master Control system when
key business events occur in Odoo:

* Employee hired (create onboarding work item)
* Employee departure set (create offboarding work item)
* Expense submitted (create approval work item)
* Large purchase order (create review work item)

The Master Control system then orchestrates cross-lane tasks (HR → IT → Finance)
with SLA timers and evidence collection.

Configuration:
--------------
* Set `master_control.webhook_url` system parameter
* Set `master_control.tenant_id` system parameter
* Enable specific event types via `master_control.events.*` parameters

SAP Mapping:
-----------
* SuccessFactors → Odoo HR + Master Control onboarding
* Concur → Odoo Expenses + Master Control approval workflow
* Signavio → BPMN → Master Control process runtime
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "hr_expense",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
