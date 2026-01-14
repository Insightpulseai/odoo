# Production Installed Modules (Authoritative)

**Date**: 2026-01-14 09:27 UTC
**Server**: erp.insightpulseai.net (178.128.112.214)
**Database**: odoo (PostgreSQL 16)
**Odoo Version**: 18.0-20251222
**Source of Truth**: `ir.module.module` where `state = 'installed'`

## Summary

- **Total installed modules**: 106
- **Top-level installed modules** (auto_install = false): 41
- **Enterprise dependencies**: 0 (verified via manifest scan)

## Installed modules (all)

```json
[
  "account",
  "account_add_gln",
  "account_edi_ubl_cii",
  "account_payment",
  "analytic",
  "auth_signup",
  "auth_totp",
  "auth_totp_mail",
  "auth_totp_portal",
  "barcodes",
  "barcodes_gs1_nomenclature",
  "base",
  "base_import",
  "base_import_module",
  "base_install_request",
  "base_setup",
  "bus",
  "calendar",
  "calendar_sms",
  "contacts",
  "crm",
  "crm_iap_enrich",
  "crm_iap_mine",
  "crm_mail_plugin",
  "crm_sms",
  "digest",
  "google_account",
  "google_calendar",
  "google_gmail",
  "google_recaptcha",
  "hr",
  "hr_calendar",
  "hr_contract",
  "hr_expense",
  "hr_org_chart",
  "hr_skills",
  "html_editor",
  "http_routing",
  "iap",
  "iap_crm",
  "iap_mail",
  "ipai_superset_connector",
  "mail",
  "mail_bot",
  "mail_bot_hr",
  "mail_plugin",
  "microsoft_account",
  "oca",
  "onboarding",
  "partner_autocomplete",
  "payment",
  "phone_validation",
  "portal",
  "portal_rating",
  "privacy_lookup",
  "product",
  "project",
  "project_account",
  "project_hr_expense",
  "project_hr_skills",
  "project_mail_plugin",
  "project_sale_expense",
  "project_sms",
  "project_stock",
  "project_stock_account",
  "project_todo",
  "rating",
  "resource",
  "resource_mail",
  "sale",
  "sale_crm",
  "sale_expense",
  "sale_management",
  "sale_pdf_quote_builder",
  "sale_project",
  "sale_project_stock_account",
  "sale_service",
  "sales_team",
  "sms",
  "snailmail",
  "snailmail_account",
  "social_media",
  "spreadsheet",
  "spreadsheet_account",
  "spreadsheet_dashboard",
  "spreadsheet_dashboard_account",
  "spreadsheet_dashboard_hr_expense",
  "stock",
  "stock_account",
  "stock_sms",
  "theme_paptic",
  "theme_test_custo",
  "uom",
  "utm",
  "web",
  "web_editor",
  "web_hierarchy",
  "web_tour",
  "web_unsplash",
  "website",
  "website_crm",
  "website_crm_sms",
  "website_mail",
  "website_payment",
  "website_project",
  "website_sms"
]
```

## Top-level installed modules (auto_install = false)

```json
[
  "account",
  "analytic",
  "barcodes",
  "barcodes_gs1_nomenclature",
  "calendar",
  "contacts",
  "crm",
  "digest",
  "google_account",
  "google_calendar",
  "google_recaptcha",
  "hr",
  "hr_contract",
  "hr_expense",
  "http_routing",
  "ipai_superset_connector",
  "mail",
  "mail_plugin",
  "microsoft_account",
  "oca",
  "onboarding",
  "payment",
  "portal",
  "product",
  "project",
  "rating",
  "resource",
  "sale",
  "sale_management",
  "sale_service",
  "sales_team",
  "social_media",
  "spreadsheet",
  "spreadsheet_dashboard",
  "stock",
  "theme_paptic",
  "theme_test_custo",
  "uom",
  "utm",
  "web_hierarchy",
  "website"
]
```

## Suspects list (requires review)

These modules may indicate IAP/integrations/plugins and should be reviewed for CE-only policy:

```json
[
  "calendar_sms",
  "crm_iap_enrich",
  "crm_iap_mine",
  "crm_mail_plugin",
  "crm_sms",
  "google_account",
  "google_calendar",
  "google_gmail",
  "google_recaptcha",
  "iap",
  "iap_crm",
  "iap_mail",
  "mail_plugin",
  "project_mail_plugin",
  "project_sms",
  "sms",
  "stock_sms",
  "website_crm_sms",
  "website_sms"
]
```

### Analysis of Suspects

**IAP Modules** (In-App Purchases - CE compatible but optional):
- `iap` - IAP infrastructure (CE-compatible, free tier available)
- `iap_crm` - CRM data enrichment (optional IAP service)
- `iap_mail` - Mail enrichment (optional IAP service)
- `crm_iap_enrich` - Lead enrichment (optional IAP service)
- `crm_iap_mine` - Lead generation (optional IAP service)

**Mail Plugin Modules** (CE-compatible, external integrations):
- `mail_plugin` - Mail client integration base
- `crm_mail_plugin` - Turn emails into leads
- `project_mail_plugin` - Project inbox integration

**Google Integrations** (CE-compatible, external OAuth):
- `google_account` - Google OAuth base
- `google_calendar` - Calendar sync
- `google_gmail` - Gmail integration
- `google_recaptcha` - Anti-spam protection

**SMS Modules** (CE-compatible, external SMS provider required):
- `sms` - SMS infrastructure
- `calendar_sms`, `crm_sms`, `project_sms`, `stock_sms`, `website_crm_sms`, `website_sms` - SMS feature integrations

**Recommendation**: All suspects are CE-compatible. IAP modules provide optional paid services but do NOT require Enterprise license.

## Not Installable Modules (Warnings)

- `ipai_superset_connector` - Custom module, not installable (manifest issue)
- `oca` - Marker module, not installable (expected)

## Enterprise Dependencies Check

```bash
# Scanned all manifest files in /usr/lib/python3/dist-packages/odoo/addons
# Searched for: "web_enterprise", "\"enterprise\""
# Result: 0 Enterprise dependencies found
```

✅ **No Enterprise modules or dependencies detected**

## Verification Commands

```bash
# Count installed modules
docker exec odoo-prod odoo shell -d odoo --no-http <<'PY'
count = env['ir.module.module'].sudo().search_count([('state','=','installed')])
print(f"Installed: {count}")
PY

# Check for Enterprise dependencies
docker exec odoo-prod bash -c 'grep -r "web_enterprise\|\"enterprise\"" /usr/lib/python3/dist-packages/odoo/addons/*/\__manifest__.py | wc -l'
```

## Critical Modules Inventory

### Core Business (11 modules)
- `account`, `account_payment` - Accounting
- `sale`, `sale_management`, `sale_crm`, `sale_project` - Sales
- `crm` - Customer relationship management
- `project`, `project_hr_expense` - Project management
- `hr`, `hr_expense` - Human resources

### Infrastructure (8 modules)
- `base`, `web`, `web_editor` - Platform core
- `mail`, `mail_bot` - Communication
- `portal` - External access
- `bus` - Real-time messaging
- `http_routing` - HTTP routing

### Integrations (6 modules)
- `google_account`, `google_calendar`, `google_gmail` - Google
- `microsoft_account` - Microsoft
- `payment`, `website_payment` - Payments

### Data & Analytics (5 modules)
- `spreadsheet`, `spreadsheet_dashboard` - Dashboards
- `analytic` - Analytics
- `ipai_superset_connector` - Superset BI
- `digest` - Digest emails

---

**Generated**: 2026-01-14 09:27 UTC
**Method**: Direct query of `ir.module.module` table
**Verified**: No Enterprise dependencies in manifest files
