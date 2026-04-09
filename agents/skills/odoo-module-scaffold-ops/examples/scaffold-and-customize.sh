#!/usr/bin/env bash
# Example: Scaffold a module and customize the manifest
set -euo pipefail

MODULE="ipai_finance_budget"

echo "=== Scaffold module ==="
# ~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin scaffold "${MODULE}" addons/ipai

echo "=== Expected __manifest__.py content ==="
cat <<'MANIFEST'
{
    "name": "IPAI Finance Budget",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Budget management for InsightPulse AI",
    "description": "Custom budget management module.",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
MANIFEST

echo "=== Test install ==="
# ~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
#   -d test_${MODULE} -i ${MODULE} --stop-after-init \
#   --addons-path=vendor/odoo/addons,addons/ipai
