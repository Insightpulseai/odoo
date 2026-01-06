# -*- coding: utf-8 -*-
{
    "name": "IPAI Module Production Gating",
    "summary": "Automated production readiness assessment and install/upgrade gating for Odoo modules",
    "description": """
IPAI Module Production Gating
=============================

This module provides automated production readiness assessment for all Odoo modules,
with visual badges, install/upgrade blocking, and exportable audit reports.

Features
--------

**Risk Assessment**
- Computes stability stage per module: Stable ✅, Beta ⚠️, Experimental 🧪, Deprecated ☠️
- Calculates risk score (0-100) based on multiple factors
- Detects missing dependencies, version mismatches, breaking patterns

**Production Gating**
- Blocks install/upgrade for high-risk modules unless explicitly allowed
- Integrates with ipai_v18_compat for tree→list view mode fixes
- Tracks known-issue signatures (dependency conflicts, model warnings)

**Visual Indicators**
- Badges in Apps list showing stage and risk level
- Color-coded risk indicators in module views
- Quick-action buttons for risk management

**Audit & Reporting**
- Export CSV reports for compliance/audit
- Generate markdown status reports
- Scheduled risk recomputation via cron

Stage Definitions
-----------------

- **Stable/Production ✅**: Major version matches server, all deps OK, no breaking patterns
- **Beta ⚠️**: Deps OK but missing tests/docs or has optional integration warnings
- **Experimental 🧪**: Version mismatch, requires migration, or has UI breakage risks
- **Deprecated ☠️**: Backup modules, explicitly deprecated, or retired

Configuration
-------------

System Parameters:
- ipai_module_gating.auto_block: Enable/disable automatic install blocking (default: 1)
- ipai_module_gating.block_experimental: Block experimental modules (default: 1)
- ipai_module_gating.allow_override: Allow admin override of blocks (default: 1)

Usage
-----

1. Install this module
2. Navigate to Apps → Module Health Report (menu action)
3. Click "Recompute All Risk" to assess all modules
4. Use "Export Report" to generate audit artifacts
    """,
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_module_module_views.xml",
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
