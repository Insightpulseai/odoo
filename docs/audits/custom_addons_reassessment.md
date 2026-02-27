# Custom Addons Reassessment — Odoo 19 + OCA Alignment

**Audit date**: 2026-02-27
**Branch**: `feat/ipai-module-audit-odoo19`
**Auditor**: Claude Code (automated manifest + view scan)
**Scope**: `addons/ipai/` — 59 real modules (primary) + `addons/ipai_*/` root-level — 40 legacy modules

> **⚠️ Architectural finding**: The repo contains two populations of custom modules:
> - **`addons/ipai/`** (59 modules) — in the configured `addons-path`, Odoo can see these
> - **`addons/ipai_*/`** root-level (40 modules) — **NOT in any addons-path config** (DevContainer, prod, dev, stage)
>
> Root-level modules are unreachable by Odoo. They appear to be legacy 18.0 modules
> that predate the `addons/ipai/` consolidation and have not been migrated.
> `ipai_bir_tax_compliance` at `addons/ipai_bir_tax_compliance/` (18.0.x) is one of these —
> it exists on disk but is invisible to Odoo. The 7 modules blocked by missing deps in this
> audit remain correctly disabled until 19.0-compatible versions are placed in `addons/ipai/`.

---

## Summary

| Classification | Count | Action |
|---------------|-------|--------|
| DEPRECATED (installable=False) | 23 | No action — already gated |
| DISABLE (installable=True → should be False) | 1 | Set installable=False |
| KEEP — clean | 23 | No changes |
| KEEP — needs tree→list patch | 4 | Patch `<tree>` → `<list>`, `view_mode` |
| KEEP — needs version fix | 1 | Patch version to `19.0.x.x.x` |
| KEEP — missing dep (unresolvable in-tree) | 7 | Installable=False until dep created |

---

## Full Module Table

Legend — **Decision**: KEEP | KEEP/PATCH | DISABLE | DEPRECATED
**OCA Alt**: OCA module that could replace if desired
**Compat Gate**: known Odoo 19 issues (tree→list, view_mode, missing dep, wrong version)

### Core / Technical

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_foundation` | 19.0.1.0.0 | ✅ | KEEP | — | None | Phase 1 control plane foundation |
| `ipai_rest_controllers` | 19.0.1.0.0 | ✅ | KEEP | `base_rest` (19.0 pending) | None | Interim until OCA base_rest ≥19.0 |
| `ipai_ai_platform` | 19.0.1.0.0 | ✅ | KEEP | — | None | HTTP client to Supabase Edge Functions |
| `ipai_ops_connector` | 19.0.1.0.0 | ✅ | KEEP | — | None | Thin bridge to external service queue |
| `ipai_system_config` | 19.0.1.0.0 | ✅ | KEEP | — | None | Env-backed SSOT for Odoo settings |
| `ipai_mail_compat` | 19.0.1.0.0 | ✅ | KEEP | — | None | **auto_install=True** — OCA mail shim |
| `ipai_web_mail_compat` | 19.0.1.0.0 | ✅ | KEEP | — | None | **auto_install=True** — mail_tracking compat |
| `ipai_odooops_shell` | **1.0.0** | ✅ | KEEP/PATCH | — | ⚠️ Version not 19.0.x.x.x | QWeb shell for auth/nav + Next.js embed |

### AI Modules

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_ai_copilot` | 19.0.1.0.0 | ✅ | KEEP | — | None | M365 Copilot-class AI for CE |
| `ipai_ai_widget` | 19.0.1.0.0 | ✅ | KEEP | — | None | Ask AI widget, no IAP dep |
| `ipai_ai_agents_ui` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_ai_core` | Set installable=False until ipai_ai_core created |

### Authentication

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_auth_oidc` | 19.0.1.0.0 | ✅ | KEEP | `auth_oidc` (OCA server-auth) | None | OIDC SSO + TOTP MFA |

### Mail

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_mail_bridge_zoho` | 19.0.1.0.0 | ✅ | KEEP | — | None | Zoho Mail API over HTTPS (bypasses DO SMTP block) |
| `ipai_zoho_mail` | 19.0.1.1.0 | ✅ | KEEP | — | None | Zoho SMTP/IMAP with settings panel |
| `ipai_zoho_mail_api` | 19.0.1.0.0 | ✅ | KEEP | — | None | Zoho REST API send (no SMTP) |
| `ipai_mailgun_smtp` | 19.0.1.0.0 | ✅ (**BUG**) | **DISABLE** | — | ⚠️ installable=True but deprecated per CLAUDE.md | Mailgun → Zoho Mail. Set installable=False immediately. |

### Finance / Accounting

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_account_settings_compat` | 19.0.1.0.0 | ✅ | KEEP | — | None | Safety-net shim for anglo_saxon_accounting |
| `ipai_finance_ppm` | 19.0.1.0.0 | ✅ | KEEP | — | None | Finance + Project + Analytic controls |
| `ipai_finance_close_seed` | 19.0.1.0.0 | ✅ | KEEP | — | None | Seed data: 89 tasks, 6 stages, 11 milestones |
| `ipai_finance_workflow` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_workspace_core` | Set installable=False until ipai_workspace_core created |

### HR / Payroll / Expenses

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_expense_ocr` | 19.0.1.0.0 | ✅ | KEEP | — | None | OCR receipt ingestion to hr.expense |
| `ipai_hr_expense_liquidation` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ `<tree>` in 3 places; `view_mode=tree,form` in 3 places | Patch tree→list |
| `ipai_hr_payroll_ph` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ `<tree>` + `view_mode=tree,form`; depends on missing `ipai_bir_tax_compliance` | Patch tree→list; set installable=False until dep exists |

### BIR / Philippine Compliance

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_bir_notifications` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_bir_tax_compliance` | Set installable=False until ipai_bir_tax_compliance exists |
| `ipai_bir_plane_sync` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_bir_tax_compliance` | Set installable=False until ipai_bir_tax_compliance exists |

### Helpdesk

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_helpdesk` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | `helpdesk_mgmt` (OCA) | ⚠️ `<tree>` in 4 places across 2 view files; `view_mode=kanban,tree,form` | Patch tree→list; consider OCA helpdesk_mgmt long-term |

### Design / Themes

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_design_system_apps_sdk` | 19.0.1.0.0 | ✅ | KEEP | — | None | SSOT for all IPAI UI tokens/components |
| `ipai_theme_tbwa` | 19.0.2.0.0 | ✅ | KEEP | — | None | TBWA brand skin; depends on design_system_apps_sdk |
| `ipai_theme_copilot` | 19.0.1.0.0 | ✅ | KEEP | — | None | Fluent-style TBWA theme |
| `ipai_theme_fluent2` | 19.0.1.0.0 | ✅ | KEEP | — | None | 10-theme multi-aesthetic system |
| `ipai_web_icons_fluent` | 19.0.1.0.0 | ✅ | KEEP | — | None | Microsoft Fluent System Icons |

### Platform / Integration

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_enterprise_bridge` | 19.0.1.0.0 | ✅ | KEEP | — | None | EE model stubs; broad deps (hr_expense, project, maintenance) |
| `ipai_platform_api` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ `<tree>` in 2 view files; `view_mode=tree,form` in both | Patch tree→list |
| `ipai_company_scope_omc` | 19.0.1.0.0 | ✅ | KEEP | — | None | OMC.com email domain enforcement |
| `ipai_odooops_shell` | **1.0.0** | ✅ | **KEEP/PATCH** | — | ⚠️ version `1.0.0` not `19.0.x.x.x` | Bump version to 19.0.1.0.0 |

### Website

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_website_coming_soon` | 19.0.2.0.0 | ✅ | KEEP | — | None | Production homepage; Bootstrap native |

### Verticals

| Module | Version | installable | Decision | OCA Alt | Compat Gate | Notes |
|--------|---------|-------------|----------|---------|-------------|-------|
| `ipai_vertical_media` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_workspace_core` | Set installable=False until ipai_workspace_core created |
| `ipai_vertical_retail` | 19.0.1.0.0 | ✅ | **KEEP/PATCH** | — | ⚠️ Depends on missing `ipai_workspace_core` | Set installable=False until ipai_workspace_core created |

---

## DEPRECATED Modules (installable=False — already gated)

These require no action. Listed for completeness.

| Module | Migrated To |
|--------|-------------|
| `ipai_ai_agent_builder` | `ipai_enterprise_bridge` |
| `ipai_ai_automations` | `ipai_enterprise_bridge` |
| `ipai_ai_fields` | `ipai_enterprise_bridge` |
| `ipai_ai_livechat` | `ipai_enterprise_bridge` |
| `ipai_ai_rag` | `ipai_enterprise_bridge` |
| `ipai_ai_tools` | `ipai_enterprise_bridge` |
| `ipai_chatgpt_sdk_theme` | `ipai_design_system_apps_sdk` |
| `ipai_copilot_ui` | `ipai_design_system_apps_sdk` |
| `ipai_design_system` | `ipai_design_system_apps_sdk` |
| `ipai_documents_ai` | `dms` (OCA) + `ipai_enterprise_bridge` |
| `ipai_equity` | `ipai_enterprise_bridge` |
| `ipai_esg` | `ipai_enterprise_bridge` |
| `ipai_esg_social` | `ipai_enterprise_bridge` |
| `ipai_finance_tax_return` | `ipai_enterprise_bridge` |
| `ipai_helpdesk_refund` | Merged into `ipai_helpdesk` |
| `ipai_planning_attendance` | `ipai_enterprise_bridge` |
| `ipai_platform_theme` | `ipai_design_system_apps_sdk` |
| `ipai_project_templates` | `ipai_enterprise_bridge` |
| `ipai_sign` | `sign` (OCA) |
| `ipai_ui_brand_tokens` | `ipai_design_system_apps_sdk` |
| `ipai_web_fluent2` | `ipai_design_system_apps_sdk` |
| `ipai_web_theme_tbwa` | `ipai_design_system_apps_sdk` |
| `ipai_whatsapp_connector` | `ipai_enterprise_bridge` |

---

## Missing Dependency Modules (not in addons/ipai/)

These modules are referenced in `depends` but do not exist in the repo. All dependents should have `installable=False` until the dependency is scaffolded.

| Missing Module | Referenced By | Impact |
|---------------|---------------|--------|
| `ipai_bir_tax_compliance` | `ipai_bir_notifications`, `ipai_bir_plane_sync`, `ipai_hr_payroll_ph` | 3 modules will fail to install |
| `ipai_workspace_core` | `ipai_finance_workflow`, `ipai_vertical_media`, `ipai_vertical_retail` | 3 modules will fail to install |
| `ipai_ai_core` | `ipai_ai_agents_ui` | 1 module will fail to install |

---

## Tree→List Violations (Odoo 19 Compatibility)

In Odoo 19, `<tree>` is deprecated in favor of `<list>` and `view_mode` values must use `list` not `tree`.

| Module | File | Violation Count | Patch Type |
|--------|------|----------------|-----------|
| `ipai_helpdesk` | `views/helpdesk_ticket_views.xml` | 1 `<tree>` + 1 `view_mode=kanban,tree,form` | Replace `<tree>` with `<list>`, `tree` → `list` in view_mode |
| `ipai_helpdesk` | `views/helpdesk_team_views.xml` | 3 `<tree>` + 1 `view_mode=tree,form` | Same |
| `ipai_hr_expense_liquidation` | `views/expense_liquidation_views.xml` | 2 `<tree>` + 3 `view_mode=tree,form` | Same |
| `ipai_hr_payroll_ph` | `views/hr_payslip_views.xml` | 1 `<tree>` + 1 `view_mode=tree,form` | Same |
| `ipai_platform_api` | `views/platform_feature_views.xml` | 1 `<tree>` + 1 `view_mode=tree,form` | Same |
| `ipai_platform_api` | `views/platform_deployment_views.xml` | 1 `<tree>` + 1 `view_mode=tree,form` | Same |

---

## Action Items (Code Changes)

### Immediate (this PR)

1. **Set `installable=False`** in `ipai_mailgun_smtp/__manifest__.py` — deprecated per CLAUDE.md
2. **Patch `<tree>` → `<list>`** in 6 view files across 4 modules
3. **Patch `view_mode`** to use `list` not `tree` in same files
4. **Fix version** in `ipai_odooops_shell/__manifest__.py`: `1.0.0` → `19.0.1.0.0`
5. **Set `installable=False`** in 7 modules with missing dependencies:
   - `ipai_ai_agents_ui` (missing `ipai_ai_core`)
   - `ipai_bir_notifications`, `ipai_bir_plane_sync`, `ipai_hr_payroll_ph` (missing `ipai_bir_tax_compliance`)
   - `ipai_finance_workflow`, `ipai_vertical_media`, `ipai_vertical_retail` (missing `ipai_workspace_core`)

### Future PRs (out of scope here)

- Scaffold `ipai_bir_tax_compliance` 19.0 in `addons/ipai/` (Philippine BIR core + filing forms)
- Scaffold `ipai_workspace_core` 19.0 in `addons/ipai/` (shared workspace primitives for verticals)
- Scaffold `ipai_ai_core` 19.0 in `addons/ipai/` (shared AI provider config for AI modules)
- Audit root-level `addons/ipai_*/` legacy modules — decide: port to 19.0+addons/ipai/, archive, or delete
- Evaluate OCA `helpdesk_mgmt` as replacement for `ipai_helpdesk` (lower maintenance burden)
- Evaluate OCA `auth_oidc` as replacement for `ipai_auth_oidc`

---

## Root-Level Legacy Modules (addons/ipai_*/ — NOT in addons-path)

These 40 modules exist under `addons/` root but are **not in any configured addons-path**.
They are unreachable by Odoo. Most are Odoo 18.0 vintage and predate the `addons/ipai/` consolidation.

**Decision needed**: port 19.0-compatible ones to `addons/ipai/`, archive or delete the rest.

| Module | Version | Functional Area | Migration Path |
|--------|---------|----------------|----------------|
| `ipai_ai_agent_builder` | 19.0.1.0.0 | AI | Has 19.0 equivalent in addons/ipai/ (deprecated) — skip |
| `ipai_ai_rag` | 18.0.1.0.0 | AI | Port to 19.0 + addons/ipai/ or supersede with ipai_ai_copilot |
| `ipai_ai_tools` | 18.0.1.0.0 | AI | Port to 19.0 + addons/ipai/ or supersede with ipai_ai_copilot |
| `ipai_ask_ai` | 1.0.0 | AI | Evaluate: superseded by ipai_ai_widget? |
| `ipai_ask_ai_chatter` | 18.0.1.1.0 | AI | Evaluate: superseded by ipai_ai_copilot? |
| `ipai_bir_data` | 18.0.1.0.0 | BIR | Port to 19.0 — needed by BIR suite |
| `ipai_bir_tax_compliance` | 18.0.1.0.0 | BIR | **Priority port** — unblocks 3 addons/ipai/ modules |
| `ipai_crm_pipeline` | 18.0.1.0.0 | CRM | Evaluate: OCA crm replacement? |
| `ipai_doc_ocr_bridge` | 19.0.1.0.0 | OCR | 19.0 — consider moving to addons/ipai/ |
| `ipai_docflow_review` | 19.0.1.0.0 | OCR | 19.0 — consider moving to addons/ipai/ |
| `ipai_enterprise_bridge` | 19.0.1.0.0 | Core | Duplicate of addons/ipai/ipai_enterprise_bridge — resolve |
| `ipai_finance_closing` | 18.0.1.0.0 | Finance | Port to 19.0 or use ipai_finance_close_seed |
| `ipai_finance_ppm_golive` | 18.0.1.0.0 | Finance | Port to 19.0 or archive |
| `ipai_finance_ppm_umbrella` | 19.0.1.1.0 | Finance | 19.0 — move to addons/ipai/ |
| `ipai_grid_view` | 18.0.1.0.0 | UI | OCA web_grid available — consider OCA-first |
| `ipai_month_end` | 18.0.1.0.0 | Finance | Superseded by ipai_finance_close_seed? |
| `ipai_month_end_closing` | 18.0.1.0.0 | Finance | Superseded by ipai_finance_close_seed? |
| `ipai_ocr_gateway` | 19.0.1.0.0 | OCR | 19.0 — move to addons/ipai/ |
| `ipai_ops_mirror` | 18.0.1.0.0 | Ops | Supabase SSOT mirror — port to 19.0 |
| `ipai_platform_approvals` | 18.0.1.0.0 | Platform | Port to 19.0 or use native Odoo approvals |
| `ipai_platform_audit` | 18.0.1.0.0 | Platform | Port to 19.0 or use OCA audit_log |
| `ipai_platform_permissions` | 18.0.1.0.0 | Platform | Port to 19.0 |
| `ipai_platform_theme` | 18.0.1.3.0 | UI | Deprecated in addons/ipai/ — archive root version |
| `ipai_platform_workflow` | 18.0.1.0.0 | Platform | Port to 19.0 |
| `ipai_ppm_okr` | 18.0.1.0.0 | Finance | Port to 19.0 — OKR for PPM |
| `ipai_sms_gateway` | 18.0.1.0.0 | Comms | Port or use OCA sms |
| `ipai_superset_connector` | 18.0.1.0.0 | BI | Port to 19.0 |
| `ipai_tbwa_finance` | 18.0.1.0.0 | Finance | Port to 19.0 |
| `ipai_theme_tbwa` | 18.0.1.0.0 | UI | 19.0 version already in addons/ipai/ — archive root |
| `ipai_theme_tbwa_backend` | 18.0.1.3.0 | UI | Evaluate vs ipai_theme_tbwa (19.0) |
| `ipai_web_theme_chatgpt` | 18.0.1.0.0 | UI | Archive — replaced by design_system_apps_sdk |
| `ipai_workos_affine` | 18.0.1.0.0 | WorkOS | WorkOS suite (10 modules) — architecture decision needed |
| `ipai_workos_blocks` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_canvas` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_collab` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_core` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_db` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_search` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_templates` | 18.0.1.0.0 | WorkOS | Same |
| `ipai_workos_views` | 18.0.1.0.0 | WorkOS | Same |

**WorkOS suite note**: 10 `ipai_workos_*` modules implement an AFFiNE-like workspace. All are 18.0 and unreachable. Requires a strategic decision: port to 19.0, sunset, or replace with OCA knowledge + wiki.
