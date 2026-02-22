# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mail Tracking – Odoo 19 Compat",
    "summary": (
        "Fixes two Odoo-19 regressions in OCA mail_tracking: "
        "Record.one() removed from Store.setup() and "
        "template renamed to mail.DiscussContent.mobileTopbar"
    ),
    "version": "19.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://github.com/Insightpulseai/odoo",
    "license": "AGPL-3",
    "depends": ["mail_tracking"],
    "installable": True,
    "auto_install": True,
    "assets": {
        "web.assets_backend": [
            # --- JS fix: Record.one() not available in Odoo 19 ---
            (
                "remove",
                "mail_tracking/static/src/services/store_service_patch.esm.js",
            ),
            "ipai_mail_tracking_compat/static/src/services/store_service_patch.esm.js",
            # --- XML fix: parent template renamed in Odoo 19 ---
            (
                "remove",
                "mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
            ),
            "ipai_mail_tracking_compat/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
        ],
    },
}
