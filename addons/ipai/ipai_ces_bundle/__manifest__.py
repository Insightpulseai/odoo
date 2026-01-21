# -*- coding: utf-8 -*-
{
    "name": "IPAI CES Bundle (Creative Ops)",
    "summary": "One-click meta-installer for CES creative effectiveness vertical",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Vertical",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ces_bundle",
    "license": "AGPL-3",
    "depends": [
        # CE core services backbone
        "project",
        "hr",
        "hr_timesheet",
        "mail",
        "portal",
        # OCA governance baseline
        "base_tier_validation",
        "base_exception",
        "date_range",
        # IPAI bridge (the only custom code layer)
        "ipai_enterprise_bridge",
    ],
    # No data, no models - this is a pure meta-installer
    "data": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
