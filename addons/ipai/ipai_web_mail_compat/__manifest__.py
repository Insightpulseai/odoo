# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
# PURPOSE
# -------
# OCA mail_tracking 19.0.1.0.8 ships two Odoo-19 incompatibilities.
# This module is a *web-asset compat overlay only* — it replaces two broken
# upstream files and provides live-proof signals.  It adds NO product logic.
#
# REMOVAL CRITERIA  (see UPSTREAM.md)
# ----------------
# Delete this module when OCA/mail / mail_tracking fixes:
#   1. store_service_patch.esm.js  – removes Record.one() from setup()
#   2. discuss_sidebar_mailboxes.xml – updates t-inherit to mail.DiscussContent.mobileTopbar
#
# UPSTREAM BROKEN FILES (full asset paths as Odoo resolves them)
# -------------------------
#   mail_tracking/static/src/services/store_service_patch.esm.js
#   mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml
{
    "name": "Odoo 19 Web Mail Compat (OCA overlays)",
    "summary": (
        "Compat overlay for OCA mail_tracking 19.0.x: fixes Record.one() "
        "removal and mail.DiscussContent.mobileTopbar template rename in Odoo 19."
    ),
    "version": "19.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://github.com/Insightpulseai/odoo",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["mail", "mail_tracking"],
    "post_init_hook": "post_init_hook",
    "assets": {
        # Target: same bundle mail_tracking uses (web.assets_backend).
        # Order matters: remove first, then add replacement, then probe.
        "web.assets_backend": [
            # -- Fix 1: Record.one() removed in Odoo 19 ------------------
            # OCA file calls Record.one("Thread") in Store.setup(); that
            # static method no longer exists.  Our replacement initialises
            # store.failed as a plain object in onStarted() instead.
            (
                "remove",
                "mail_tracking/static/src/services/store_service_patch.esm.js",
            ),
            "ipai_web_mail_compat/static/src/services/store_service_patch.esm.js",
            # -- Fix 2: template parent renamed in Odoo 19 ----------------
            # OCA template inherits from mail.Discuss.mobileTopbar which no
            # longer exists; correct parent is mail.DiscussContent.mobileTopbar.
            # We remove the whole file and re-add a corrected copy that keeps
            # the two working templates (Mailbox.main, DiscussSidebarMailboxes)
            # unchanged.
            (
                "remove",
                "mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
            ),
            "ipai_web_mail_compat/static/src/core/discuss/discuss_sidebar_mailboxes.xml",
            # -- Compat probe: runtime proof the overlay is live ----------
            "ipai_web_mail_compat/static/src/compat_probe.esm.js",
        ],
    },
}
