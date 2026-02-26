# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
{
    "name": "IPAI Account Settings Compat",
    "version": "19.0.1.0.0",
    "summary": (
        "Ensures res.config.settings.anglo_saxon_accounting is always defined, "
        "regardless of whether account_usability (OCA) is loadable. "
        "Fixes OwlError when Settings form renders and account_usability view XML "
        "is in the database but the OCA module is not in the addons path."
    ),
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
