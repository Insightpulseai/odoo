# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Sources (Odoo Export)",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Export Odoo data (tasks, KB articles) to Supabase KB for RAG retrieval",
    "description": """
IPAI AI Sources - Odoo Export
=============================

Exports Odoo content to Supabase KB for AI retrieval.

Features:
---------
* Scheduled export of project tasks
* Scheduled export of knowledge articles (if OCA document_page installed)
* Incremental sync (only exports changes)
* Tenant-scoped data (per company)
* Upsert logic to prevent duplicates

Supported Sources:
------------------
* project.task - Tasks with descriptions, stages, project context
* document.page - Knowledge base articles (OCA knowledge module)

Configuration:
--------------
Set these environment variables:

    IPAI_SUPABASE_URL=https://<project>.supabase.co
    IPAI_SUPABASE_SERVICE_ROLE_KEY=<key>
    IPAI_KB_EXPORT_LOOKBACK_HOURS=24
    IPAI_PUBLIC_BASE_URL=https://your-odoo.com

Usage:
------
1. Install this module
2. Configure environment variables
3. Cron runs automatically every 15 minutes
4. View sync status in AI → KB Export Runs

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/exporter_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
