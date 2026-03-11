# Odoo Module Inventory — Reconciled (Prod + Filesystem)

**Source:** Live prod screenshot (`erp.insightpulseai.com`) + filesystem scan
**Date:** 2026-03-09
**Database:** `odoo` (prod runtime)
**Odoo Version:** 19.0
**Total visible in prod:** 26 modules (page 1-26 of 26 with "oca" filter)

## Prod Screenshot — Modules Visible (erp.insightpulseai.com)

Extracted from browser screenshot at `https://erp.insightpulseai.com/odoo/apps?view_type=list`
Filter active: "Module: oca"

| # | Module Name | Technical Name | Author | Version | Status |
|---|-------------|----------------|--------|---------|--------|
| 1 | Time Off | hr_holidays | Odoo S.A. | 19.0.1.6 | **Installed** |
| 2 | Account Financial Reports | account_financial_report | Camptocamp,initOS GmbH,redCOR AG,ForgeFlow,OCA | 19.0.0.0.2 | **Installed** |
| 3 | IPAI Vertical Media (CES) | ipai_vertical_media | InsightPulse AI | 19.0.1.0.0 | Not Installed |
| 4 | IPAI Vertical Retail (Scout) | ipai_vertical_retail | InsightPulse AI | 19.0.1.0.0 | Not Installed |
| 5 | LATAM Localization Base | l10n_latam_base | Odoo S.A., ADHOC SA | 19.0.1.0 | Not Installed |
| 6 | Add Partner GLN | account_add_gln | Odoo S.A. | 19.0.1.0 | Not Installed |
| 7 | AI - Generate text using Ollama | ai_oca_native_generate_ollama | Dixmit,OCA | 19.0.1.0.0 | **Installed** |
| 8 | Partners Geolocation | base_geolocalize | Odoo S.A. | 19.0.2.1 | **Installed** |
| 9 | Location management (aka Better ZIP) | base_location | Camptocamp,ACYSOS S.L.,OCA | 19.0.1.0.1 | **Installed** |
| 10 | Base Location Geonames Import | base_location_geonames_import | Akretion,OCA | 19.0.1.0.0 | **Installed** |
| 11 | Cloud Storage Migration | cloud_storage_migration | Odoo S.A. | 19.0.1.0 | Not Installed |
| 12 | IPAI Account Settings Compat | ipai_account_settings_compat | InsightPulse AI | 19.0.1.0.0 | **Installed** |
| 13 | DEPRECATED: Documents AI | ipai_documents_ai | InsightPulse AI | 19.0.1.0.0 | **Uninstallable** |
| 14 | IPAI Mail Compatibility Shims (Odoo 19) — TEMPORARY | ipai_mail_compat | InsightPulse AI | 19.0.1.0.0 | Not Installed |
| 15 | DEPRECATED: Electronic Sign | ipai_sign | InsightPulse AI | 19.0.1.0.0 | Not Installed |
| 16 | Odoo 19 Web Mail Compat (OCA overlays) | ipai_web_mail_compat | InsightPulse AI | 19.0.1.0.0 | Not Installed |
| 17 | Belgian POS Restaurant Localization | l10n_be_pos_restaurant | Odoo S.A. | 19.0.1.0 | Not Installed |
| 18 | Spain - Point of Sale | l10n_es_pos | Odoo S.A. | 19.0.1.0 | Not Installed |
| 19 | France - Localizations | l10n_fr | Odoo S.A. | 19.0.2.1 | Not Installed |
| 20 | India - Time Off | l10n_in_hr_holidays | Odoo S.A. | 19.0.1.0 | Not Installed |
| 21 | Sri Lanka - Accounting | l10n_lk | Odoo S.A. | 19.0.1.0 | Not Installed |
| 22 | United States - Localizations | l10n_us | Odoo S.A. | 19.0.1.1 | Not Installed |
| 23 | Partner Statement | partner_statement | ForgeFlow, OCA | 19.0.1.0.0 | **Installed** |
| 24 | Quality Control OCA | quality_control_oca | AvanzOSC, Tecnativa, OCA | 19.0.1.2.0 | **Installed** |
| 25 | Quality control - Stock (OCA) | quality_control_stock_oca | Tecnativa,AvanzOSC,OCA | 19.0.1.0.1 | **Installed** |
| 26 | Maintenance - HR | hr_maintenance | Odoo S.A. | 19.0.1.0 | **Installed** |

## Installed Modules Summary (from screenshot)

### OCA Modules — INSTALLED on Prod

| Technical Name | OCA Repo | Must-Have? |
|----------------|----------|------------|
| `account_financial_report` | account-financial-reporting | **Yes** (Tier 3) |
| `ai_oca_native_generate_ollama` | ai | No (Tier 8) |
| `base_location` | partner-contact | No |
| `base_location_geonames_import` | partner-contact | No |
| `partner_statement` | account-financial-reporting | **Yes** (baseline_accounting) |
| `quality_control_oca` | manufacture | **Yes** (Tier 7) |
| `quality_control_stock_oca` | manufacture | **Yes** (Tier 7) |

### CE Core Modules — INSTALLED on Prod (visible in screenshot)

| Technical Name | Category |
|----------------|----------|
| `hr_holidays` | Human Resources |
| `base_geolocalize` | Partners |
| `hr_maintenance` | Maintenance |

### IPAI Modules — INSTALLED on Prod

| Technical Name | Status |
|----------------|--------|
| `ipai_account_settings_compat` | Installed |

### Deprecated/Uninstallable IPAI Modules

| Technical Name | Status | Note |
|----------------|--------|------|
| `ipai_documents_ai` | Uninstallable | Deprecated |
| `ipai_sign` | Not Installed | Deprecated |

## OCA Must-Have Gap Analysis

**Installed OCA must-haves:** 4 of 108 (3.7%)

| Profile | Installed | Total | Coverage |
|---------|-----------|-------|----------|
| baseline_core | 0 | 11 | 0% |
| baseline_accounting | 2 | 10 | 20% |
| baseline_sales | 0 | 6 | 0% |
| baseline_purchase_controls | 0 | 4 | 0% |
| baseline_optional_ux | 0 | 15 | 0% |
| Other must-haves | 2 | 62 | 3% |

### Critical Missing (baseline_core — every CE deployment needs these)

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `queue_job` | queue | Async job processing |
| `auditlog` | server-tools | Change audit trail |
| `password_security` | server-auth | Password policy enforcement |
| `date_range` | server-ux | Date range management |
| `web_responsive` | web | Mobile-friendly UI |
| `web_m2x_options` | web | Many2one/many2many UX |
| `web_environment_ribbon` | web | Dev/staging/prod visual indicator |
| `mail_tracking` | social | Email delivery tracking |
| `mail_activity_plan` | social | Activity plans |
| `report_xlsx` | reporting-engine | Excel exports |
| `base_name_search_improved` | server-tools | Better name search |

### Critical Missing (baseline_accounting)

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `account_asset_management` | account-financial-tools | Fixed asset tracking |
| `account_reconcile_oca` | account-reconcile | Bank reconciliation |
| `account_reconcile_model_oca` | account-reconcile | Reconciliation models |
| `mis_builder` | mis-builder | Financial reporting framework |
| `mis_builder_budget` | mis-builder | Budget management |
| `currency_rate_update` | account-financial-tools | Auto currency rates |
| `account_journal_lock_date` | account-financial-tools | Journal lock dates |
| `account_lock_date_update` | account-financial-tools | Lock date management |

## Filesystem vs Prod Reconciliation

| Metric | Filesystem Scan | Prod Screenshot |
|--------|----------------|-----------------|
| Total IPAI modules | 103 | 26 visible (oca filter) |
| IPAI installable | 73 | — |
| OCA modules present | 0 (not hydrated) | 7 installed |
| OCA must-haves installed | N/A | 4/108 (3.7%) |
| CE modules visible | 0 (in Docker image) | 3+ visible |

## Key Finding

**OCA modules ARE installed on prod** (7 confirmed) even though `addons/oca/` in the repo is empty.
This means OCA modules were either:
1. Baked into the Docker image via `Dockerfile.unified` during a previous build
2. Installed manually via the Odoo Apps UI
3. Present in an older build layer

**The repo is out of sync with prod.** The `gitaggregate` hydration step must be run
to bring `addons/oca/` in sync with what's actually deployed.

## Next Steps

1. **Hydrate OCA repos**: `gitaggregate -c oca-aggregate.yml`
2. **Install baseline_core profile** (11 modules) — highest impact
3. **Install baseline_accounting profile** (remaining 8 of 10)
4. **Re-scan**: `python scripts/scan_module_inventory.py` after hydration
5. **Run prod audit**: `python scripts/inventory_modules.py` with XML-RPC credentials
