{
    "name": "IPAI Ops Connector (Bridge Platform)",
    "version": "19.0.1.0.0",
    "summary": "Thin CE bridge to external services (queue + run ledger + callbacks)",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_ops_run_views.xml",
        "data/ir_cron_ops_dispatch.xml",
    ],
    "installable": True,
    "application": False,
}
