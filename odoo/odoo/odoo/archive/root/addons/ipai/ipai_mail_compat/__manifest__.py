# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Mail Compatibility Shims (Odoo 19) — TEMPORARY",
    "version": "19.0.1.0.0",
    "summary": (
        "TEMPORARY migration shim: backward-compat stubs for OCA modules "
        "ported from Odoo 17→19. Remove when all OCA deps ship native 19.0 code."
    ),
    "description": """
IPAI Mail Compatibility Shims — TEMPORARY MIGRATION SHIM
==========================================================

**Status**: Temporary — this module exists only until upstream OCA modules
ship native Odoo 19 code that no longer references the removed APIs below.

**Removal criteria** (remove this module when ALL are true):
  1. OCA ``mail_tracking`` no longer inherits ``mail.Discuss.mobileTopbar``
  2. OCA ``web_responsive`` / any OCA JS no longer calls ``Record.one()``
  3. All OCA modules in ``oca-aggregate.yml`` target 19.0 natively
  4. ``addons/oca/`` is fully checked out and tested on Odoo 19

**What this module does** (and ONLY does):

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

**What this module must NEVER do**:
  - Implement business logic (EE parity or otherwise)
  - Add Python models, views, security rules, or data files
  - Grow beyond pure JS/XML shims for removed upstream APIs
  - Become a catch-all compatibility layer

See: ``docs/architecture/EE_PARITY_POLICY.md`` §Temporary Compatibility Shims
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
