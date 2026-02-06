{
    "name": "IPAI Foundation",
    "summary": "Phase 1 vertical slice - core control plane foundation",
    "version": "19.0.1.0.0",
    "category": "IPAI/Core",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_frontend": [
            "ipai_foundation/static/src/js/process_shim.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
