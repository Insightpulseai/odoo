# -*- coding: utf-8 -*-
{
    "name": "IPAI Enterprise Bridge",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "summary": "Single glue module: CE+OCA composition + PH Finance overlays + AI integration interfaces",
    "description": """
IPAI Enterprise Bridge
======================

**Purpose**: Composition + policy + seed + interface layer for Odoo 18 CE + OCA stack

**What This Module Does**:
- Installs baseline CE business apps + curated OCA modules in one shot
- Standardizes tier validation, document policies, and governance across stack
- Adds PH Finance overlays (BIR schedules + month-end close scaffolding)
- Provides AI integration interfaces (summary, tags, confidence) as abstract mixins
- Grocery/retail product extensions (shelf codes, expiry tracking, substitutions)

**What This Module Does NOT Do**:
- Re-implement Enterprise features (use OCA equivalents instead)
- Fork OCA modules (thin glue layer only)
- Provide heavy inference/OCR engines (external services via n8n/Supabase)
- Replace Studio/Odoo.sh/mobile apps (out of scope)

**Feature Flags** (Settings → General Settings → IPAI Enterprise Bridge):
- Enable/disable optional bundles: Retail, DMS, Helpdesk, Field Service, Month-End Close

**Dependencies**:
- Core CE: base, web, mail, contacts, account, sale, purchase, stock, POS, project, HR
- OCA Foundation: base_tier_validation, base_exception, date_range
- Optional OCA: DMS, helpdesk, fieldservice (auto-detected, conditional integration)
    """,
    "author": "IPAI / TBWA",
    "license": "AGPL-3",
    "depends": [
        # ═══════════════════════════════════════════════════════════════════
        # CORE ODOO CE (Always Required)
        # ═══════════════════════════════════════════════════════════════════
        "base",
        "web",
        "mail",
        "contacts",

        # ═══════════════════════════════════════════════════════════════════
        # CE BUSINESS APPS (Baseline Stack)
        # ═══════════════════════════════════════════════════════════════════
        "account",              # Accounting & Finance
        "sale_management",      # Sales (includes sale)
        "purchase",             # Purchase Management
        "stock",                # Inventory & Warehouse
        "point_of_sale",        # POS (Retail)
        "project",              # Project Management
        "hr",                   # Human Resources
        "hr_timesheet",         # Timesheets

        # ═══════════════════════════════════════════════════════════════════
        # OCA FOUNDATION (Governance & Approvals)
        # ═══════════════════════════════════════════════════════════════════
        "base_tier_validation", # Multi-tier approval framework
        "base_exception",       # Exception handling framework
        "date_range",           # Date range management

        # ═══════════════════════════════════════════════════════════════════
        # OPTIONAL OCA (Conditional - check module presence in code)
        # ═══════════════════════════════════════════════════════════════════
        # "dms",                # Document Management (conditional)
        # "helpdesk_mgmt",      # Helpdesk (conditional)
        # "fieldservice",       # Field Service (conditional)
    ],
    "data": [
        # ═══════════════════════════════════════════════════════════════════
        # SECURITY
        # ═══════════════════════════════════════════════════════════════════
        "security/security.xml",
        "security/ir.model.access.csv",

        # ═══════════════════════════════════════════════════════════════════
        # SEED DATA (Idempotent)
        # ═══════════════════════════════════════════════════════════════════
        "data/groups.xml",
        "data/sequences.xml",
        "data/scheduled_actions.xml",

        # ═══════════════════════════════════════════════════════════════════
        # VIEWS
        # ═══════════════════════════════════════════════════════════════════
        "views/res_config_settings_views.xml",
        "views/ipai_policy_views.xml",
        "views/ipai_close_views.xml",
        "views/product_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
