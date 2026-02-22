# ERP SaaS Parity Matrix — Odoo CE 19

> SSOT for capability-level decisions: what's resolved via CE config, OCA install,
> OCA port, integration bridge, or accepted gap.
>
> Machine-readable twin: `odoo/ssot/parity_targets.yaml`
> CI validation: `scripts/odoo/validate_parity_targets.py`
> Gate: `.github/workflows/parity-targets-gate.yml`

---

## Resolution Key

| Code | Meaning |
|------|---------|
| **CE** | Configuration or lightweight glue inside CE — no new module |
| **OCA** | Upstream OCA module installed, pinned via submodule |
| **PORT** | OCA module with a targeted compatibility patch applied in this repo |
| **BRIDGE** | External service + thin `ipai_*` connector (connector-only, not feature clone) |
| **GAP** | Accepted gap — documented rationale, no current plan to close |

**Policy:** `ipai_*` modules are connectors and governance glue only. No EE-parity re-implementations.

---

## A. Core ERP

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| A01 | Chart of accounts, journals, fiscal year | CE | `account` | PH localization via `l10n_ph` |
| A02 | Customer invoicing & vendor bills | CE | `account`, `account_move_name_sequence` | Sequence enforced |
| A03 | PH withholding tax (EWT / expanded) | OCA | `l10n_account_withholding_tax`, `l10n_account_withholding_tax_pos` | Installed |
| A04 | Bank statement import (CSV / CAMT) | OCA | `account_statement_base`, `account_statement_import_base`, `account_statement_import_camt`, `account_statement_import_file`, `account_statement_import_online` | Installed |
| A05 | Bank reconciliation | CE | `account` reconciliation engine | Native v19 |
| A06 | Payment orders / SEPA | OCA | `account_payment_order`, `account_payment_order_grouped_output`, `account_payment_mode`, `account_payment_sale`, `account_payment_purchase` | Installed |
| A07 | Financial reporting (P&L, BS, cashflow) | OCA | `account_financial_report`, `mis_builder`, `mis_builder_budget` | Installed |
| A08 | Tax balance / analytic reporting | OCA | `account_tax_balance`, `bi_sql_editor` | Installed |
| A09 | Sales orders, quotations, pricelists | CE | `sale`, `sale_management` | Native |
| A10 | Sale discounts (order + line) | OCA | `sale_order_general_discount`, `base_global_discount` | Installed |
| A11 | Sale order types, priorities, exceptions | OCA | `sale_order_type`, `sale_order_priority`, `sale_exception` | Installed |
| A12 | Auto-workflow (invoice on confirm, etc.) | OCA | `sale_automatic_workflow` | Installed |
| A13 | Purchase orders, RFQ, purchase types | OCA | `purchase_order_type`, `purchase_request`, `purchase_force_invoiced`, `purchase_order_general_discount`, `purchase_order_owner` | Installed |
| A14 | Inventory, moves, routes | CE | `stock`, `stock_account`, `stock_delivery` | Native |
| A15 | Manufacturing, BOM, MO lifecycle | CE | `mrp`, `mrp_account`, `mrp_subcontracting` | Native |
| A16 | MRP quality control | OCA | `quality_control_oca`, `quality_control_stock_oca` | Installed |
| A17 | MRP ops extensions | OCA | `mrp_attachment_mgmt`, `mrp_bom_component_menu`, `mrp_bom_image`, `mrp_bom_note`, `mrp_bom_tracking`, `mrp_production_back_to_draft`, `mrp_sale_info`, `mrp_tag` | Installed |
| A18 | Project management, timesheets | CE | `project`, `hr_timesheet` | Native |
| A19 | Project stage management | OCA | `project_task_default_stage`, `project_task_stage_mgmt`, `project_task_stage_state` | Installed |
| A20 | Timesheet controls | OCA | `hr_timesheet_task_stage`, `hr_timesheet_time_control` | Installed |
| A21 | Human resources (employees, leaves, attendance) | CE | `hr`, `hr_attendance`, `hr_holidays`, `hr_expense` | Native |
| A22 | HR recruitment | CE | `hr_recruitment`, `hr_recruitment_skills` | Native |
| A23 | Point of sale | CE | `point_of_sale`, `pos_restaurant`, `pos_hr` | Native |
| A24 | CRM / leads pipeline | CE | `crm`, `crm_iap_enrich` | Native |

---

## B. Compliance & Localisation

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| B01 | BIR compliance automation (PH) | BRIDGE + OCA | `l10n_ph`, `l10n_account_withholding_tax`; `ipai_finance_ppm` connector; n8n BIR workflows | `docs/ops/SUPABASE_N8N.md` |
| B02 | IBAN / bank validation | OCA | `base_iban`, `base_vat`, `partner_vat_unique` | Installed |
| B03 | Audit log | OCA | `auditlog` | Installed |
| B04 | Partner deduplication / GDPR | OCA | `partner_auto_archive`, `privacy_lookup`, `data_recycle` | Installed |
| B05 | Data encryption at rest (field-level) | OCA | `data_encryption` | Installed, keys in env |

---

## C. Mail & Communications

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| C01 | SMTP relay (Odoo → Zoho Mail) | BRIDGE | Zoho SMTP `smtp.zoho.com:587`; `ipai_mail_bridge_zoho` connector | `docs/ops/SUPABASE_N8N.md` |
| C02 | Mail debranding | OCA + PORT | `mail_debranding` | Installed; Odoo 19 port applied |
| C03 | Activity reminders | OCA | `mail_activity_reminder` | Installed |
| C04 | Optional autofollow | OCA | `mail_optional_autofollow` | Installed |
| C05 | Outbound static domain | OCA | `mail_outbound_static` | Installed |
| C06 | Deferred mail sending | OCA | `mail_post_defer` | Installed |
| C07 | Delivery confirmations | OCA | `mail_send_confirmation` | Installed |
| C08 | Mail open/click tracking | PORT | `mail_tracking` | Installed; `_init_messaging()` patched for Odoo 19 `store.add()` API change |
| C09 | Transactional email / marketing | CE | `mass_mailing`, `mass_mailing_crm` | Native |

---

## D. Security & Identity

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| D01 | SSO / OIDC (Google, Azure, custom IdP) | OCA | `auth_oidc`, `auth_oauth`, `auth_oauth_multi_token` | Installed |
| D02 | 2FA / TOTP | CE | `auth_totp`, `auth_totp_mail`, `auth_totp_portal` | Native v19 |
| D03 | Passkey (WebAuthn) | OCA | `auth_passkey`, `auth_passkey_portal` | Installed |
| D04 | Session timeout | OCA | `auth_session_timeout` | Installed |
| D05 | Role-based access control | OCA | `base_user_role` | Installed |
| D06 | Impersonation (support) | OCA | `impersonate_login` | Installed |
| D07 | Server environment tiering | OCA | `server_environment` | Installed |
| D08 | Database access control | CE | `list_db=False`, `proxy_mode=True` in `odoo.conf` | Configuration |

---

## E. Platform / Odoo.sh Parity

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| E01 | CI build + test | BRIDGE | GitHub Actions (`.github/workflows/`) | `docs/ops/TESTING.md` |
| E02 | Staging environment | BRIDGE | DigitalOcean droplet + branch-gated deploy | `docs/ops/ODOO_SH_EQUIVALENT_MATRIX.md` |
| E03 | DB promotion (staging → prod) | BRIDGE | Supabase ops control plane + promotion checklist | `docs/ops/PROMOTION_CHECKLIST.md` |
| E04 | Preview deploys | BRIDGE | Vercel (web surfaces); n8n preview approval gate | `docs/architecture/ENVIRONMENTS.md` |
| E05 | DNS management | BRIDGE | Cloudflare (delegated); `infra/dns/subdomain-registry.yaml` SSOT | `docs/ops/CLOUDFLARE_DNS_SSOT.md` |
| E06 | Observability (metrics/logs/traces) | BRIDGE | DigitalOcean monitoring + Supabase `ops.run_events` | `docs/ops/DIGITALOCEAN_OBSERVABILITY.md` |
| E07 | Backup / DR | BRIDGE | DO managed DB automated backups + runbook | `docs/ops/ODOO_SH_EQUIVALENT_MATRIX.md` |
| E08 | Security posture / GHAS | BRIDGE | GitHub Advanced Security + policy docs | `docs/architecture/SECURITY_REMEDIATION_LANE.md` |

---

## F. Document & OCR Pipeline

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| F01 | Vendor bill OCR (invoice ingestion) | BRIDGE | PaddleOCR-VL + Claude LLM + n8n pipeline → Odoo XML-RPC | `automations/n8n/workflows/invoice_ocr_to_odoo.json` |
| F02 | Document management (DMS) | OCA + PORT | `document_url` | Installed; v19 compat patches applied |
| F03 | Attachment indexing | OCA | `attachment_indexation` | Installed |
| F04 | File storage (S3/external) | GAP | `fs_attachment` — OCA sets `installable: False` on v19 | Blocked upstream; use Supabase Storage via bridge |
| F05 | Signature workflow | GAP | OCA `sign`-equivalent not yet ported to v19 | Bridge via DocuSign/HelloSign via `ipai_sign_bridge_*` when needed |

---

## G. BI & Reporting

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| G01 | MIS Builder (P&L, BS templates) | OCA | `mis_builder`, `mis_builder_budget` | Installed |
| G02 | BI SQL views (custom reports) | OCA | `bi_sql_editor` | Installed |
| G03 | Spreadsheet / pivot dashboards | CE | `spreadsheet`, `spreadsheet_dashboard`, `spreadsheet_account` | Native v19 |
| G04 | External BI (Superset / Tableau) | BRIDGE | Apache Superset at `superset.insightpulseai.com`; read replica query | `docs/ops/SUPABASE_METRICS.md` |
| G05 | REST API for external consumers | GAP | `rest-framework` / `fastapi` — OCA `installable: False` on v19 | Use Odoo JSON-RPC or bridge via n8n until OCA ports |

---

## H. Integration Framework

| # | Capability | Resolution | Modules / Service | Runbook / Notes |
|---|-----------|------------|-------------------|-----------------|
| H01 | Job queue (async, batch, cron) | OCA | `queue_job`, `queue_job_batch`, `queue_job_cron`, `queue_job_subscribe` | Installed |
| H02 | Connector base framework | OCA | `connector`, `component`, `component_event` | Installed |
| H03 | n8n automation bus | BRIDGE | n8n at `n8n.insightpulseai.com`; Supabase webhook bus | `docs/ops/SUPABASE_N8N.md` |
| H04 | External event bus | BRIDGE | Supabase Realtime + `ops.run_events` table | `docs/ops/SUPABASE_METRICS.md` |
| H05 | AI / LLM copilot (ask AI) | OCA | `ai_oca_native_generate_ollama` | Installed; Ollama backend |

---

## Accepted Gaps Summary

| ID | Capability | Rationale |
|----|-----------|-----------|
| F04 | File storage (S3) | `fs_attachment` OCA sets `installable: False` on v19; use Supabase Storage bridge |
| F05 | e-Signature | No OCA v19 port; defer to `ipai_sign_bridge_*` when business need arises |
| G05 | REST API framework | `rest-framework` / `fastapi` OCA modules not ready for v19; JSON-RPC sufficient |

---

*Last updated: 2026-02-23 | Managed by `odoo/ssot/parity_targets.yaml`*
