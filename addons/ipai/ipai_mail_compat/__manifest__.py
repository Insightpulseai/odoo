# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Mail Compatibility Shims (Odoo 19)",
    "version": "19.0.1.0.0",
    "summary": "Backward-compat shims for OCA modules ported from Odoo 17 to 19",
    "description": """
IPAI Mail Compatibility Shims
==============================

Provides two backward-compatibility fixes for OCA modules that were ported
from Odoo 17 to Odoo 19 without fully reconciling API changes:

1. **Stub QWeb template**: ``mail.Discuss.mobileTopbar``
   - Existed in Odoo 17 (``mail/static/src/core/common/discuss.xml``)
   - Removed in Odoo 18+; the mobile Discuss UI was restructured.
   - OCA modules that ``t-inherit`` this template cause:
     ``Missing (extension) parent templates: mail.Discuss.mobileTopbar``
   - This module registers an empty stub so extensions load without error.

2. **JS Record field-definition shim**: ``Record.one / .many / .attr``
   - In Odoo 17 the mail Record class exposed static helpers:
     ``Record.one()``, ``Record.many()``, ``Record.attr()``
   - In Odoo 19 these moved to a standalone ``fields`` object:
     ``fields.One()``, ``fields.Many()``, ``fields.Attr()``
     (exported from ``@mail/model/misc``)
   - OCA JS patches that still call ``Record.one()`` throw:
     ``TypeError: Record.one is not a function``
   - This module patches the Record class to re-add the aliases.

Install this module **before** installing OCA mail-related addons
(mail_tracking, web_responsive, etc.) on an Odoo 19 database.
    """,
    "category": "Mail",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["mail"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "ipai_mail_compat/static/src/xml/discuss_compat.xml",
            "ipai_mail_compat/static/src/js/record_compat.js",
        ],
    },
    "installable": True,
    "auto_install": True,
    "application": False,
}
