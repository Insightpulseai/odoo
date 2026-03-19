# Template: __manifest__.py for IPAI modules
# Version format: 19.0.<major>.<minor>.<patch>
# License: always LGPL-3 for CE modules
# Data order: security groups, ACLs, data, views

{
    "name": "IPAI <Domain> <Feature>",
    "version": "19.0.1.0.0",
    "category": "<Category>",
    "summary": "<One-line summary>",
    "description": "<Longer description>",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        # Add minimal required dependencies
    ],
    "data": [
        # Order matters: security first, then data, then views
        "security/ir.model.access.csv",
        # "data/data.xml",
        "views/views.xml",
    ],
    "demo": [
        # "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    # development_status: Alpha -> Beta -> Stable -> Mature
    "development_status": "Alpha",
}
