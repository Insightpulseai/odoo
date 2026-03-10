# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

# Keep these two lists in lockstep with __manifest__.py assets stanza.
# They are the contract: verifier script + smoke test both assert against them.
_REMOVED_UPSTREAM = [
    "mail_tracking/static/src/services/store_service_patch.esm.js",
    "mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
]
_ADDED_COMPAT = [
    "ipai_web_mail_compat/static/src/services/store_service_patch.esm.js",
    "ipai_web_mail_compat/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
    "ipai_web_mail_compat/static/src/compat_probe.esm.js",
]


class IpaiCompatProbe(models.AbstractModel):
    _name = "ipai.compat.probe"
    _description = "IPAI Compatibility Probes (CI/ops verification only)"

    @api.model
    def mail_tracking(self):
        """Return the deterministic contract for the mail_tracking compat overlay.

        Consumed by:
        - scripts/verify_ipai_web_mail_compat.py  (CI asset check)
        - tests/test_mail_compat_smoke.py          (regression guard)
        - ops console / MCP health endpoints

        Returns a plain dict so callers can compare field-by-field without ORM.
        """
        module_name = "ipai_web_mail_compat"
        mod = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", module_name)], limit=1)
        )
        version = (
            mod.installed_version or mod.latest_version or "unknown"
        ) if mod else "missing"

        return {
            "active": bool(mod and mod.state == "installed"),
            "module": module_name,
            "version": version,
            "target_oca_module": "mail_tracking",
            "target_oca_version": "19.0.1.0.8",
            "fixes": [
                "store_service_patch: Record.one() removed in Odoo 19 → plain object in onStarted()",
                "template_inherit: mail.Discuss.mobileTopbar → mail.DiscussContent.mobileTopbar",
            ],
            "bundle": "web.assets_backend",
            "removed_upstream_assets": _REMOVED_UPSTREAM,
            "added_compat_assets": _ADDED_COMPAT,
        }
