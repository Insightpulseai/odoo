# Production Installed Modules (Authoritative)

**Generated**: 2026-01-14 09:35 UTC
**Database**: odoo
**Source of Truth**: `ir.module.module` where `state = 'installed'`

## Summary
- Installed modules: **106**
- Top-level modules (auto_install=false): **41**

## Policy: CE-Only with Optional IAP

**Allowed**:
- `iap_*` modules installed but unused (no paid endpoints configured)
- `sms`, `*_sms` modules with external SMS provider (optional)
- `google_*`, `microsoft_account` OAuth integrations (optional)
- `mail_plugin`, `*_mail_plugin` external mail client integrations (optional)

**Disallowed**:
- Any module requiring paid endpoints for core operations
- Any module with `web_enterprise` or `enterprise` dependencies

**Enforcement**: CI drift gate fails if Enterprise dependencies detected.

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

## Top-level modules
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

## Suspects (review list)

Modules requiring review for CE-only policy compliance:

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
  "payment",
  "project_mail_plugin",
  "project_sms",
  "sms",
  "stock_sms",
  "website_crm_sms",
  "website_payment",
  "website_sms"
]
```

---

**Regenerate**: `python3 scripts/audit_installed_modules.py`
