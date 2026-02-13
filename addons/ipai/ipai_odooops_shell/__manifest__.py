{
    "name": "IPAI OdooOps Shell (Hybrid)",
    "version": "1.0.0",
    "category": "Tools",
    "summary": "QWeb shell for auth/nav + Next.js dashboard embed",
    "depends": ["website"],
    "data": [
        "views/shell_templates.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ipai_odooops_shell/static/src/css/shell.css",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
