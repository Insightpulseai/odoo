# EE Parity Matrix — Odoo CE 19

> **Generated**: 2026-02-24  
> **Source**: `odoo/ssot/parity_targets.yaml`  
> **Validator**: `scripts/parity/augment_parity_fields.py`

## Coverage Summary

| Total | Installed | Planned | Blocked |
|-------|-----------|---------|---------|
| 69 | 65 | 2 | 2 |

| By Resolution | Count |
|---------------|-------|
| BRIDGE | 14 |
| CE | 15 |
| GAP | 3 |
| OCA | 34 |
| PORT | 3 |

| By Tier | Count |
|---------|-------|
| Tier 1 — must\_have | 38 |
| Tier 2 — scope\_based | 29 |
| Tier 3 — optional | 2 |

---

## Tier 1 — Must-Have Parity

| ID | Capability | Delivery | Status | OCA Modules |
|----|-----------|---------|--------|-------------|
| A01 | Chart of accounts, journals, fiscal year | CE | ✅ installed | `l10n_ph` |
| A02 | Customer invoicing & vendor bills | CE | ✅ installed | `account_move_name_sequence` |
| A03 | PH withholding tax (EWT / expanded) | OCA | ✅ installed | `l10n_account_withholding_tax`, `l10n_account_withholding_tax_pos` |
| A04 | Bank statement import (CSV / CAMT) | OCA | ✅ installed | `account_statement_base`, `account_statement_import_base`, `account_statement_import_camt`, `account_statement_import_file`, `account_statement_import_online` |
| A05 | Bank reconciliation | CE | ✅ installed | — |
| A06 | Payment orders / SEPA | OCA | ✅ installed | `account_payment_order`, `account_payment_order_grouped_output`, `account_payment_mode`, `account_payment_sale`, `account_payment_purchase` |
| A07 | Financial reporting (P&L, BS, cashflow) | OCA | ✅ installed | `account_financial_report`, `mis_builder`, `mis_builder_budget` |
| A08 | Tax balance / analytic reporting | OCA | ✅ installed | `account_tax_balance`, `bi_sql_editor` |
| A09 | Sales orders, quotations, pricelists | CE | ✅ installed | — |
| A13 | Purchase orders, RFQ, types | OCA | ✅ installed | `purchase_order_type`, `purchase_request`, `purchase_force_invoiced`, `purchase_order_general_discount`, `purchase_order_owner` |
| A14 | Inventory, moves, routes | CE | ✅ installed | — |
| A21 | Human resources (employees, leaves, attendance) | CE | ✅ installed | — |
| A24 | CRM / leads pipeline | CE | ✅ installed | — |
| B01 | BIR compliance automation (PH) | 🔌 BRIDGE | ✅ installed | `l10n_ph`, `l10n_account_withholding_tax` |
| B02 | IBAN / bank / VAT validation | OCA | ✅ installed | `base_iban`, `base_vat`, `partner_vat_unique` |
| B03 | Audit log | OCA | ✅ installed | `auditlog` |
| B04 | Partner deduplication / GDPR | OCA | ✅ installed | `partner_auto_archive`, `privacy_lookup`, `data_recycle` |
| B05 | Field-level data encryption | OCA | ✅ installed | `data_encryption` |
| C01 | SMTP relay (Zoho Mail) | 🔌 BRIDGE | ✅ installed | bridge: zoho_smtp |
| C05 | Outbound static domain | OCA | ✅ installed | `mail_outbound_static` |
| C09 | Mass mailing / email marketing | CE | ✅ installed | — |
| D01 | SSO / OIDC | OCA | ✅ installed | `auth_oidc`, `auth_oauth`, `auth_oauth_multi_token` |
| D02 | 2FA / TOTP | CE | ✅ installed | — |
| D04 | Session timeout | OCA | ✅ installed | `auth_session_timeout` |
| D05 | Role-based access control | OCA | ✅ installed | `base_user_role` |
| D07 | Server environment tiering | OCA | ✅ installed | `server_environment` |
| D08 | Database access control | CE | ✅ installed | — |
| E01 | CI build + test | 🔌 BRIDGE | ✅ installed | bridge: github_actions |
| E02 | Staging environment | 🔌 BRIDGE | ✅ installed | bridge: digitalocean, docker |
| E03 | DB promotion (staging → prod) | 🔌 BRIDGE | ✅ installed | bridge: supabase, digitalocean |
| E05 | DNS management | 🔌 BRIDGE | ✅ installed | bridge: cloudflare |
| E06 | Observability (metrics/logs/traces) | 🔌 BRIDGE | ✅ installed | bridge: digitalocean_monitoring, supabase |
| E07 | Backup / disaster recovery | 🔌 BRIDGE | ✅ installed | bridge: digitalocean_managed_db |
| G01 | MIS Builder (financial templates) | OCA | ✅ installed | `mis_builder`, `mis_builder_budget` |
| G03 | Spreadsheet / pivot dashboards | CE | ✅ installed | — |
| H01 | Job queue (async, batch, cron) | OCA | ✅ installed | `queue_job`, `queue_job_batch`, `queue_job_cron`, `queue_job_subscribe` |
| H02 | Connector base framework | OCA | ✅ installed | `connector`, `component`, `component_event` |
| H03 | n8n automation bus | 🔌 BRIDGE | ✅ installed | bridge: n8n, supabase |

---

## Tier 2 — Scope-Based Parity

| ID | Capability | Delivery | Status | OCA Modules |
|----|-----------|---------|--------|-------------|
| A10 | Sale discounts (order + line level) | OCA | ✅ installed | `sale_order_general_discount`, `base_global_discount` |
| A11 | Sale order types, priorities, exceptions | OCA | ✅ installed | `sale_order_type`, `sale_order_priority`, `sale_exception` |
| A12 | Sale automatic workflow | OCA | ✅ installed | `sale_automatic_workflow` |
| A15 | Manufacturing, BOM, MO lifecycle | CE | ✅ installed | — |
| A16 | MRP quality control | OCA | ✅ installed | `quality_control_oca`, `quality_control_stock_oca` |
| A17 | MRP operations extensions | OCA | ✅ installed | `mrp_attachment_mgmt`, `mrp_bom_component_menu`, `mrp_bom_image`, `mrp_bom_note`, `mrp_bom_tracking`, `mrp_production_back_to_draft`, `mrp_sale_info`, `mrp_tag` |
| A18 | Project management, timesheets | CE | ✅ installed | — |
| A19 | Project stage management | OCA | ✅ installed | `project_task_default_stage`, `project_task_stage_mgmt`, `project_task_stage_state` |
| A20 | Timesheet controls | OCA | ✅ installed | `hr_timesheet_task_stage`, `hr_timesheet_time_control` |
| A22 | HR recruitment | CE | ✅ installed | — |
| A23 | Point of sale | CE | ✅ installed | — |
| C02 | Mail debranding | PORT | ✅ installed | `mail_debranding` |
| C03 | Activity reminders | OCA | ✅ installed | `mail_activity_reminder` |
| C06 | Deferred mail sending | OCA | ✅ installed | `mail_post_defer` |
| C07 | Delivery confirmations | OCA | ✅ installed | `mail_send_confirmation` |
| C08 | Mail open/click tracking | PORT | ✅ installed | `mail_tracking` |
| D03 | Passkey / WebAuthn | OCA | ✅ installed | `auth_passkey`, `auth_passkey_portal` |
| D06 | Impersonation (support) | OCA | ✅ installed | `impersonate_login` |
| E04 | Preview deploys (web surfaces) | 🔌 BRIDGE | ✅ installed | bridge: vercel, n8n |
| E08 | Security posture / GHAS | 🏗️ PLATFORM | 🔵 planned | bridge: github_advanced_security |
| F01 | Vendor bill OCR (invoice ingestion) | 🔌 BRIDGE | ✅ installed | bridge: paddleocr, claude_llm, n8n, supabase |
| F02 | Document management (DMS) | PORT | ✅ installed | `document_url` |
| F03 | Attachment indexing (full-text search) | OCA | ✅ installed | `attachment_indexation` |
| F04 | File storage (S3 / external) | 🔌 BRIDGE | 🔴 blocked | bridge: supabase_storage |
| F05 | e-Signature workflow | 🔌 BRIDGE | 🔵 planned | — |
| G02 | BI SQL views (custom reports) | OCA | ✅ installed | `bi_sql_editor` |
| G04 | External BI (Superset / Tableau) | 🔌 BRIDGE | ✅ installed | bridge: apache_superset, supabase |
| G05 | REST API framework for external consumers | 🔌 BRIDGE | 🔴 blocked | — |
| H04 | External event bus | 🔌 BRIDGE | ✅ installed | bridge: supabase_realtime |

---

## Tier 3 — Optional / Bridge-First

| ID | Capability | Delivery | Status | OCA Modules |
|----|-----------|---------|--------|-------------|
| C04 | Optional autofollow | OCA | ✅ installed | `mail_optional_autofollow` |
| H05 | AI / LLM copilot (ask AI) | OCA | ✅ installed | `ai_oca_native_generate_ollama` |

---

## Capability Detail by Domain

### A. Core ERP

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| A01 | Chart of accounts, journals, fiscal year | CE | Tier 1 | ✅ installed | `l10n_ph` |
| A02 | Customer invoicing & vendor bills | CE | Tier 1 | ✅ installed | `account_move_name_sequence` |
| A03 | PH withholding tax (EWT / expanded) | OCA | Tier 1 | ✅ installed | `l10n_account_withholding_tax`, `l10n_account_withholding_tax_pos` |
| A04 | Bank statement import (CSV / CAMT) | OCA | Tier 1 | ✅ installed | `account_statement_base`, `account_statement_import_base`, `account_statement_import_camt`, `account_statement_import_file`, `account_statement_import_online` |
| A05 | Bank reconciliation | CE | Tier 1 | ✅ installed | — |
| A06 | Payment orders / SEPA | OCA | Tier 1 | ✅ installed | `account_payment_order`, `account_payment_order_grouped_output`, `account_payment_mode`, `account_payment_sale`, `account_payment_purchase` |
| A07 | Financial reporting (P&L, BS, cashflow) | OCA | Tier 1 | ✅ installed | `account_financial_report`, `mis_builder`, `mis_builder_budget` |
| A08 | Tax balance / analytic reporting | OCA | Tier 1 | ✅ installed | `account_tax_balance`, `bi_sql_editor` |
| A09 | Sales orders, quotations, pricelists | CE | Tier 1 | ✅ installed | — |
| A10 | Sale discounts (order + line level) | OCA | Tier 2 | ✅ installed | `sale_order_general_discount`, `base_global_discount` |
| A11 | Sale order types, priorities, exceptions | OCA | Tier 2 | ✅ installed | `sale_order_type`, `sale_order_priority`, `sale_exception` |
| A12 | Sale automatic workflow | OCA | Tier 2 | ✅ installed | `sale_automatic_workflow` |
| A13 | Purchase orders, RFQ, types | OCA | Tier 1 | ✅ installed | `purchase_order_type`, `purchase_request`, `purchase_force_invoiced`, `purchase_order_general_discount`, `purchase_order_owner` |
| A14 | Inventory, moves, routes | CE | Tier 1 | ✅ installed | — |
| A15 | Manufacturing, BOM, MO lifecycle | CE | Tier 2 | ✅ installed | — |
| A16 | MRP quality control | OCA | Tier 2 | ✅ installed | `quality_control_oca`, `quality_control_stock_oca` |
| A17 | MRP operations extensions | OCA | Tier 2 | ✅ installed | `mrp_attachment_mgmt`, `mrp_bom_component_menu`, `mrp_bom_image`, `mrp_bom_note`, `mrp_bom_tracking`, `mrp_production_back_to_draft`, `mrp_sale_info`, `mrp_tag` |
| A18 | Project management, timesheets | CE | Tier 2 | ✅ installed | — |
| A19 | Project stage management | OCA | Tier 2 | ✅ installed | `project_task_default_stage`, `project_task_stage_mgmt`, `project_task_stage_state` |
| A20 | Timesheet controls | OCA | Tier 2 | ✅ installed | `hr_timesheet_task_stage`, `hr_timesheet_time_control` |
| A21 | Human resources (employees, leaves, attendance) | CE | Tier 1 | ✅ installed | — |
| A22 | HR recruitment | CE | Tier 2 | ✅ installed | — |
| A23 | Point of sale | CE | Tier 2 | ✅ installed | — |
| A24 | CRM / leads pipeline | CE | Tier 1 | ✅ installed | — |

### B. Compliance & Localisation

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| B01 | BIR compliance automation (PH) | 🔌 BRIDGE | Tier 1 | ✅ installed | `l10n_ph`, `l10n_account_withholding_tax` |
| B02 | IBAN / bank / VAT validation | OCA | Tier 1 | ✅ installed | `base_iban`, `base_vat`, `partner_vat_unique` |
| B03 | Audit log | OCA | Tier 1 | ✅ installed | `auditlog` |
| B04 | Partner deduplication / GDPR | OCA | Tier 1 | ✅ installed | `partner_auto_archive`, `privacy_lookup`, `data_recycle` |
| B05 | Field-level data encryption | OCA | Tier 1 | ✅ installed | `data_encryption` |

### C. Mail & Communications

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| C01 | SMTP relay (Zoho Mail) | 🔌 BRIDGE | Tier 1 | ✅ installed | zoho_smtp |
| C02 | Mail debranding | PORT | Tier 2 | ✅ installed | `mail_debranding` |
| C03 | Activity reminders | OCA | Tier 2 | ✅ installed | `mail_activity_reminder` |
| C04 | Optional autofollow | OCA | Tier 3 | ✅ installed | `mail_optional_autofollow` |
| C05 | Outbound static domain | OCA | Tier 1 | ✅ installed | `mail_outbound_static` |
| C06 | Deferred mail sending | OCA | Tier 2 | ✅ installed | `mail_post_defer` |
| C07 | Delivery confirmations | OCA | Tier 2 | ✅ installed | `mail_send_confirmation` |
| C08 | Mail open/click tracking | PORT | Tier 2 | ✅ installed | `mail_tracking` |
| C09 | Mass mailing / email marketing | CE | Tier 1 | ✅ installed | — |

### D. Security & Identity

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| D01 | SSO / OIDC | OCA | Tier 1 | ✅ installed | `auth_oidc`, `auth_oauth`, `auth_oauth_multi_token` |
| D02 | 2FA / TOTP | CE | Tier 1 | ✅ installed | — |
| D03 | Passkey / WebAuthn | OCA | Tier 2 | ✅ installed | `auth_passkey`, `auth_passkey_portal` |
| D04 | Session timeout | OCA | Tier 1 | ✅ installed | `auth_session_timeout` |
| D05 | Role-based access control | OCA | Tier 1 | ✅ installed | `base_user_role` |
| D06 | Impersonation (support) | OCA | Tier 2 | ✅ installed | `impersonate_login` |
| D07 | Server environment tiering | OCA | Tier 1 | ✅ installed | `server_environment` |
| D08 | Database access control | CE | Tier 1 | ✅ installed | — |

### E. Platform / Odoo.sh Parity

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| E01 | CI build + test | 🔌 BRIDGE | Tier 1 | ✅ installed | github_actions |
| E02 | Staging environment | 🔌 BRIDGE | Tier 1 | ✅ installed | digitalocean + docker |
| E03 | DB promotion (staging → prod) | 🔌 BRIDGE | Tier 1 | ✅ installed | supabase + digitalocean |
| E04 | Preview deploys (web surfaces) | 🔌 BRIDGE | Tier 2 | ✅ installed | vercel + n8n |
| E05 | DNS management | 🔌 BRIDGE | Tier 1 | ✅ installed | cloudflare |
| E06 | Observability (metrics/logs/traces) | 🔌 BRIDGE | Tier 1 | ✅ installed | digitalocean_monitoring + supabase |
| E07 | Backup / disaster recovery | 🔌 BRIDGE | Tier 1 | ✅ installed | digitalocean_managed_db |
| E08 | Security posture / GHAS | 🏗️ PLATFORM | Tier 2 | 🔵 planned | github_advanced_security |

### F. Document & OCR Pipeline

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| F01 | Vendor bill OCR (invoice ingestion) | 🔌 BRIDGE | Tier 2 | ✅ installed | paddleocr + claude_llm + n8n + supabase |
| F02 | Document management (DMS) | PORT | Tier 2 | ✅ installed | `document_url` |
| F03 | Attachment indexing (full-text search) | OCA | Tier 2 | ✅ installed | `attachment_indexation` |
| F04 | File storage (S3 / external) | 🔌 BRIDGE | Tier 2 | 🔴 blocked | supabase_storage |
| F05 | e-Signature workflow | 🔌 BRIDGE | Tier 2 | 🔵 planned | — |

### G. BI & Reporting

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| G01 | MIS Builder (financial templates) | OCA | Tier 1 | ✅ installed | `mis_builder`, `mis_builder_budget` |
| G02 | BI SQL views (custom reports) | OCA | Tier 2 | ✅ installed | `bi_sql_editor` |
| G03 | Spreadsheet / pivot dashboards | CE | Tier 1 | ✅ installed | — |
| G04 | External BI (Superset / Tableau) | 🔌 BRIDGE | Tier 2 | ✅ installed | apache_superset + supabase |
| G05 | REST API framework for external consumers | 🔌 BRIDGE | Tier 2 | 🔴 blocked | — |

### H. Integration Framework

| ID | Capability | Delivery | Tier | v19 Status | Bridge / Modules |
|----|-----------|---------|------|-----------|-----------------|
| H01 | Job queue (async, batch, cron) | OCA | Tier 1 | ✅ installed | `queue_job`, `queue_job_batch`, `queue_job_cron`, `queue_job_subscribe` |
| H02 | Connector base framework | OCA | Tier 1 | ✅ installed | `connector`, `component`, `component_event` |
| H03 | n8n automation bus | 🔌 BRIDGE | Tier 1 | ✅ installed | n8n + supabase |
| H04 | External event bus | 🔌 BRIDGE | Tier 2 | ✅ installed | supabase_realtime |
| H05 | AI / LLM copilot (ask AI) | OCA | Tier 3 | ✅ installed | `ai_oca_native_generate_ollama` |

---

## Gaps & Blocked Capabilities

| ID | Capability | Resolution | Status | Notes |
|----|-----------|-----------|--------|-------|
| E08 | Security posture / GHAS | BRIDGE | 🔵 planned |  |
| F04 | File storage (S3 / external) | GAP | 🔴 blocked | fs_attachment: OCA sets installable=False on v19. Use Supabase Storage via bridge when needed. |
| F05 | e-Signature workflow | GAP | 🔵 planned | No OCA v19 port. Defer to ipai_sign_bridge_* when business need arises. |
| G05 | REST API framework for external consumers | GAP | 🔴 blocked | rest-framework / fastapi OCA modules set installable=False on v19. Use Odoo JSON-RPC or n8n bridge. |


---

## OCA Naming Validation

✅ All OCA modules in parity_targets.yaml are present in `oca_installed_allowlist.yaml`.
