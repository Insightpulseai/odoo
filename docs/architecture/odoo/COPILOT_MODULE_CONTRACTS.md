# Odoo Copilot + Agent Module Contracts

> SSOT: `ssot/odoo/module_contracts/odoo_copilot_foundry.yaml`

## Canonical install surface

### Base Odoo apps

| Module | Purpose |
|---|---|
| `account` | Vendor bills, journals, accounting workflow |
| `purchase` | PO/vendor linkage and invoice matching |
| `hr_expense` | Expense drafts, approval, reimbursement |
| `documents` | Document storage, attachment workflow |
| `mail` | Chatter, activities, approval communication |
| `contacts` | Vendors, employees, approvers |

### Custom modules (6 total)

| Module | Type | Purpose |
|---|---|---|
| `ipai_enterprise_bridge` | Bridge | Shared config, security groups, feature flags, audit mixins |
| `ipai_ai_core` | Core bridge | Agent sessions, tool registry, correlation IDs |
| `ipai_foundry_bridge` | External bridge | Odoo ↔ Foundry Agent Service |
| `ipai_document_intelligence_bridge` | External bridge | Odoo ↔ Azure Document Intelligence |
| `ipai_odoo_copilot` | UX bridge | Embedded copilot UI (Joule-like) |
| `ipai_ap_expense_capture` | Workflow | Invoice/expense capture (Concur-like) |

## Safe tool surface (v1)

| Tool | Action | Allowed |
|---|---|---|
| `fetch_record_context` | Read | Yes |
| `create_vendor_bill_draft` | Draft write | Yes |
| `create_expense_draft` | Draft write | Yes |
| `match_vendor_or_employee` | Assistive | Yes |
| `route_for_approval` | Workflow | Yes |
| `explain_capture_exception` | Read | Yes |
| `post_vendor_bill` | Financial posting | **No** |
| `approve_payment` | Financial action | **No** |

## Event flows

### Invoice: upload → OCR → draft bill → approval

```
Document upload → ipai_document_intelligence_bridge → OCR result
  → ipai_ap_expense_capture → vendor/PO/tax/duplicate check
  → create_vendor_bill_draft → exception or approval route
  → human review → standard Odoo accounting workflow
```

### Expense: receipt → OCR → draft expense → approval

```
Receipt upload → ipai_document_intelligence_bridge → OCR result
  → ipai_ap_expense_capture → employee/category/amount/duplicate check
  → create_expense_draft → exception or approval route
  → human review → standard Odoo expense workflow
```

### Copilot: context → Foundry → safe tool → response

```
User opens record → ipai_odoo_copilot builds context
  → ipai_foundry_bridge invokes Foundry agent
  → agent selects safe tool(s) → Odoo records run + trace
  → response returned to copilot panel
```

## Excluded modules

| Module | Reason |
|---|---|
| `ipai_agent` | Fold into ipai_ai_core or ipai_foundry_bridge |
| `ipai_theme_copilot` | Fold UI into ipai_odoo_copilot |
| `ipai_hr_expense_liquidation` | Refactor into ipai_ap_expense_capture |
| `ipai_helpdesk` | Unrelated to AP/expense copilot target |
| `ipai_mail_compat` | Runtime-only config (Azure Key Vault) |
| `ipai_foundation` | Absorbed by ipai_enterprise_bridge |
