# Expense Liquidation — Module Install Matrix

> Module-by-module breakdown: stock Odoo vs OCA vs custom IPAI vs config-only steps.

---

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| `hr_expense` | Installed | Stock Odoo expenses — visible in Settings |
| `account` | Installed | Base accounting |
| `hr` | Installed | HR base |
| Expense OCR / Digitalization | Enabled in Settings | Toggle visible |
| Expense Card (Stripe) | Visible in Settings | Not yet configured |
| Incoming Emails for expenses | Visible in Settings | Alias domain not configured |
| 2FA by email | Enabled | |
| LDAP / OAuth | Visible | |
| Cloudflare Turnstile | Enabled | |
| `ipai_hr_expense_liquidation` | **Skeleton only** | `installable: False`, manifest only, no implementation files |
| `ipai_document_intelligence` | **Installable** | Azure Document Intelligence bridge (active) |
| n8n receipt capture workflow | **Active** | `expense_receipt_capture.json` (Telegram + webhook ingress) |

---

## Install Matrix by Goal

### Goal 1: Azure Blob Attachment Offload

| Step | Type | Module / Action | Depends | Notes |
|------|------|----------------|---------|-------|
| 1 | **Stock Odoo (CE)** | `cloud_storage` | `base_setup`, `mail` | LGPL-3 CE module — in `vendor/odoo/addons/`. Adds Cloud Storage settings block. |
| 2 | **Stock Odoo (CE)** | `cloud_storage_azure` | `cloud_storage` | LGPL-3 CE module — adds Azure Blob provider. |
| 3 | **Config only** | Set Azure account name, container, tenant ID, client ID | — | Credentials via Key Vault (`kv-ipai-dev`), NOT hardcoded. |
| 4 | **Config only** | Set minimum file size threshold | — | Attachments below threshold stay in database. |

**Install command:**
```bash
vendor/odoo/odoo-bin -d odoo_dev -i cloud_storage,cloud_storage_azure --stop-after-init
```

**Verification:** Settings > Technical > Cloud Storage section appears with Azure Blob fields.

---

### Goal 2: Email-to-Expense (Alias Routing)

| Step | Type | Module / Action | Depends | Notes |
|------|------|----------------|---------|-------|
| 1 | **Config only** | Configure mail alias domain | — | Settings > Discuss > Alias Domain. Set to `insightpulseai.com`. |
| 2 | **Config only** | Configure inbound email routing | — | Zoho SMTP is already canonical. Inbound requires catchall/alias config. |
| 3 | **Config only** | Set expense email alias | `hr_expense` | Settings > Expenses > Incoming Emails. Default alias: `expense@insightpulseai.com`. |

**No new module install needed.** This is pure configuration on top of already-installed `hr_expense` + `mail`.

---

### Goal 3: OCR Receipt Processing

| Step | Type | Module / Action | Depends | Notes |
|------|------|----------------|---------|-------|
| 1 | **Already installed** | `ipai_document_intelligence` | `ipai_copilot_actions` | Azure Document Intelligence bridge — active and installable. |
| 2 | **Config only** | Azure Document Intelligence endpoint + key | — | Set via `ir.config_parameter` or Key Vault. Uses `docai-ipai-dev` in `rg-ipai-ai-dev`. |
| 3 | **n8n workflow** | `expense_receipt_capture.json` | — | Already active. Telegram + webhook ingress → Foundry OCR → Odoo line creation. |

**Stock Odoo OCR path (alternative):** The built-in "Expense Digitalization" toggle in Settings uses Odoo IAP credits. Since we are CE-only with no IAP, use the `ipai_document_intelligence` + Azure Document Intelligence path instead.

---

### Goal 4: Full Cash-Advance Liquidation Workflow

This is the primary custom capability. Stock `hr_expense` does **not** provide cash-advance lifecycle management.

| Step | Type | Module / Action | Depends | Notes |
|------|------|----------------|---------|-------|
| 1 | **Custom IPAI** | `ipai_hr_expense_liquidation` | `base`, `hr`, `hr_expense`, `account` | **Currently skeleton** (`installable: False`). Needs full implementation. |
| 2 | **Custom IPAI** | Implement models | — | `hr.expense.liquidation`, `hr.expense.liquidation.line`, `hr.expense.policy.rule`, `hr.expense.policy.violation` |
| 3 | **Custom IPAI** | Implement views | — | Form, tree, search, kanban for liquidation + policy |
| 4 | **Custom IPAI** | Implement security | — | Groups, ACLs, record rules |
| 5 | **Custom IPAI** | Implement workflow | — | 8-state approval: draft → submitted → manager → finance → released → in_liquidation → liquidated → closed |
| 6 | **Custom IPAI** | Implement accounting | — | Release entries (debit advance, credit cash), liquidation entries (debit expense, credit advance) |
| 7 | **Custom IPAI** | Implement policy engine | — | Amount limits, receipt requirements, overdue checks |
| 8 | **n8n workflow** | Receipt capture already active | — | `expense_receipt_capture.json` calls `hr.expense.liquidation.line` |
| 9 | **Bridge (optional)** | Copilot tools integration | `ipai_ai_copilot` | 4 tools declared in manifest but commented out pending `ipai.copilot.tool` model |

**Spec bundle:** `spec/expense-liquidation-agent/` (constitution, prd, plan, tasks — all complete)

---

### Goal 5: Stripe Expense Card

| Step | Type | Module / Action | Depends | Notes |
|------|------|----------------|---------|-------|
| 1 | **Config only** | Stripe Issuing account setup | — | External: Stripe dashboard, Issuing activation |
| 2 | **Config only** | Connect Stripe to Odoo | `hr_expense` | Settings > Expenses > Expense Card section |
| 3 | **Config only** | Payment method / accounting alignment | `account` | Map Stripe card transactions to journal entries |

**Not a module install** — this is Stripe account + configuration work.

---

## Priority Order (Recommended)

| Priority | Goal | Effort | Blocking? |
|----------|------|--------|-----------|
| **P0** | Goal 4: Liquidation module implementation | High (models, views, security, workflow, accounting) | Yes — skeleton exists, no implementation |
| **P1** | Goal 1: Azure Blob storage | Low (2 CE modules + config) | No |
| **P1** | Goal 2: Email alias routing | Low (config only) | No |
| **P2** | Goal 3: OCR receipts | Low (already installed, config remaining) | No |
| **P3** | Goal 5: Stripe card | Medium (external account + config) | No |

---

## Module Dependency Graph

```
                    ┌─────────────────────┐
                    │    base / hr / account│
                    └──────┬──────────────┘
                           │
              ┌────────────┼──────────────┐
              │            │              │
       ┌──────▼──────┐  ┌─▼───────┐  ┌───▼──────────────┐
       │  hr_expense  │  │  mail   │  │  base_setup      │
       └──────┬──────┘  └─┬───────┘  └───┬──────────────┘
              │            │              │
    ┌─────────▼──────────┐ │   ┌──────────▼──────────────┐
    │ipai_hr_expense_    │ │   │   cloud_storage          │
    │liquidation (P0)    │ │   └──────────┬──────────────┘
    └────────────────────┘ │              │
                           │   ┌──────────▼──────────────┐
              ┌────────────┘   │  cloud_storage_azure     │
              │                └─────────────────────────┘
    ┌─────────▼──────────┐
    │ipai_document_      │
    │intelligence (OCR)  │
    └────────────────────┘
```

---

## CE vs Enterprise Verification

| Module | License | CE Compatible? |
|--------|---------|---------------|
| `cloud_storage` | LGPL-3 | Yes — in `vendor/odoo/addons/` |
| `cloud_storage_azure` | LGPL-3 | Yes — in `vendor/odoo/addons/` |
| `hr_expense` | LGPL-3 | Yes — stock CE |
| `cloud_storage_google` | LGPL-3 | Yes (not needed — Azure is canonical) |
| Expense Digitalization (IAP) | N/A | No IAP in CE-only — use `ipai_document_intelligence` instead |

---

*Last updated: 2026-03-21*
