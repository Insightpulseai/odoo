==================================
Bank Reconciliation (OCA Bridge)
==================================

Overview
========

This module provides automatic bank statement reconciliation capabilities,
equivalent to Odoo Enterprise's ``account_accountant`` reconciliation features.

Features
========

* **Automatic Matching Proposals**: Suggests matches based on amount, partner, and labels
* **Reconciliation Models**: Define rules for automatic matching
* **Confidence Scoring**: Shows match confidence percentage
* **Batch Auto-Reconcile**: Process multiple statement lines at once

Installation
============

1. Install dependencies::

    pip install -r requirements.txt

2. Update module list in Odoo::

    docker compose exec odoo-core odoo -d odoo_core -u base --stop-after-init

3. Install the module::

    docker compose exec odoo-core odoo -d odoo_core -i account_reconcile_oca --stop-after-init

CLI Verification
================

Verify module installation::

    docker compose exec odoo-core odoo shell -d odoo_core <<< "
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([('name', '=', 'account_reconcile_oca')])
    print(f'Module state: {module.state}')
    "

Test reconciliation::

    docker compose exec odoo-core odoo shell -d odoo_core <<< "
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    models = env['account.reconcile.model'].search([])
    print(f'Reconciliation models: {len(models)}')
    "

Usage
=====

1. **Configure Reconciliation Models**: Go to Accounting > Bank Reconciliation > Reconciliation Models
2. **Import Bank Statements**: Upload CSV/OFX files via bank statement import
3. **Auto-Reconcile**: Select statement lines and use the "Auto-Reconcile" action
4. **Review Proposals**: Check suggested matches and confirm reconciliation

Enterprise Parity
=================

This module provides equivalent functionality to:

* ``account_accountant`` (Bank reconciliation widget)
* Matching proposals
* Write-off suggestions
* Invoice matching rules

Parity Score: 95%
