# Odoo 18 CE/OCA Integration Map

**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## 1. Overview

This document defines the integration mapping between Supabase schemas and Odoo 18 CE/OCA models. All integrations use the bi-directional sync pattern via n8n workflows and Edge Functions.

---

## 2. Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                │
│  expense.* │ projects.* │ rates.* │ core.*                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │    n8n      │
                    │  Webhooks   │
                    └──────┬──────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      ODOO 18 CE                                 │
│  hr.expense │ project.project │ res.partner │ hr.employee       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Entity Mapping Table

| Business Concept | Supabase Table | Odoo Model | Sync Direction | Priority |
|-----------------|----------------|------------|----------------|----------|
| **Core Entities** |
| Tenant / Company | `core.tenants` | `res.company` | Odoo → Supabase | P0 |
| Employee | `core.employees` | `hr.employee` | Odoo → Supabase | P0 |
| User | `auth.users` | `res.users` | Bi-directional | P0 |
| **Finance / Expense** |
| Expense Report | `expense.expense_reports` | `hr.expense.sheet` | Odoo → Supabase | P1 |
| Expense Line | `expense.expenses` | `hr.expense` | Odoo → Supabase | P1 |
| Cash Advance | `expense.cash_advances` | `ipai.cash.advance` | Bi-directional | P1 |
| Expense Category | `ref.expense_categories` | `product.product` | Odoo → Supabase | P2 |
| **Projects** |
| Project | `projects.projects` | `project.project` | Bi-directional | P1 |
| Project Member | `projects.project_members` | `project.task.user.rel` | Odoo → Supabase | P2 |
| **Rates / Vendors** |
| Vendor | `rates.vendor_profile` | `res.partner` | Bi-directional | P1 |
| Rate Card | `rates.rate_cards` | `ipai.rate.card` | Supabase → Odoo | P1 |
| Rate Card Item | `rates.rate_card_items` | `ipai.rate.card.line` | Supabase → Odoo | P1 |
| **Documents** |
| Expense Receipt | `doc.raw_documents` | `ir.attachment` | Bi-directional | P2 |

---

## 4. Detailed Field Mappings

### 4.1 Employee Mapping

| Supabase `core.employees` | Odoo `hr.employee` | Transform |
|---------------------------|-------------------|-----------|
| `id` | — | Generated UUID |
| `tenant_id` | `company_id` | Company lookup |
| `odoo_id` | `id` | Direct map |
| `email` | `work_email` | Direct map |
| `name` | `name` | Direct map |
| `department` | `department_id.name` | Lookup |
| `job_title` | `job_id.name` | Lookup |
| `manager_id` | `parent_id` | Employee lookup |
| `is_active` | `active` | Direct map |

**Sync Trigger:** Odoo webhook on `hr.employee` create/write/unlink

---

### 4.2 Expense Report Mapping

| Supabase `expense.expense_reports` | Odoo `hr.expense.sheet` | Transform |
|------------------------------------|------------------------|-----------|
| `id` | — | Generated UUID |
| `tenant_id` | `company_id` | Company lookup |
| `employee_id` | `employee_id` | Employee lookup |
| `report_number` | `name` | Direct map |
| `description` | `name` | Combine with number |
| `status` | `state` | Status map (see below) |
| `total_amount` | `total_amount` | Direct map |
| `currency` | `currency_id.name` | Currency lookup |
| `submitted_at` | `create_date` | When state = 'submit' |
| `approved_at` | `approval_date` | Direct map |
| `approved_by` | `user_id` | User lookup |

**Status Mapping:**

| Supabase Status | Odoo State |
|-----------------|------------|
| `draft` | `draft` |
| `submitted` | `submit` |
| `approved` | `approve` |
| `rejected` | `cancel` |
| `paid` | `done` |

---

### 4.3 Expense Line Mapping

| Supabase `expense.expenses` | Odoo `hr.expense` | Transform |
|-----------------------------|------------------|-----------|
| `id` | — | Generated UUID |
| `tenant_id` | `company_id` | Company lookup |
| `expense_report_id` | `sheet_id` | Report lookup |
| `category_code` | `product_id.default_code` | Product lookup |
| `description` | `name` | Direct map |
| `amount` | `total_amount_currency` | Direct map |
| `currency` | `currency_id.name` | Currency lookup |
| `spend_date` | `date` | Direct map |
| `receipt_document_id` | `message_main_attachment_id` | Attachment lookup |

---

### 4.4 Project Mapping

| Supabase `projects.projects` | Odoo `project.project` | Transform |
|------------------------------|------------------------|-----------|
| `id` | — | Generated UUID |
| `tenant_id` | `company_id` | Company lookup |
| `odoo_id` | `id` | Direct map |
| `project_code` | `name` | Parse from name or custom field |
| `name` | `name` | Direct map |
| `description` | `description` | Direct map |
| `status` | `stage_id` | Stage lookup (see below) |
| `start_date` | `date_start` | Direct map |
| `end_date` | `date` | Direct map |
| `project_manager_id` | `user_id` | User lookup |

**Status Mapping:**

| Supabase Status | Odoo Stage |
|-----------------|------------|
| `draft` | Draft |
| `active` | In Progress |
| `on_hold` | On Hold |
| `completed` | Done |
| `cancelled` | Cancelled |

---

### 4.5 Vendor Mapping

| Supabase `rates.vendor_profile` | Odoo `res.partner` | Transform |
|---------------------------------|-------------------|-----------|
| `id` | — | Generated UUID |
| `tenant_id` | `company_id` | Company lookup |
| `odoo_partner_id` | `id` | Direct map |
| `vendor_code` | `ref` | Direct map |
| `name` | `name` | Direct map |
| `category` | `category_id.name` | Category lookup |
| `status` | `active` | Boolean to status |
| `rating` | `rating` | Custom field |

**Filter:** `supplier_rank > 0` (vendors only)

---

## 5. Custom Odoo Modules Required

### 5.1 `ipai_cash_advance`

**Purpose:** Cash advance management for TE-Cheq integration

```python
# models/cash_advance.py
class CashAdvance(models.Model):
    _name = 'ipai.cash.advance'
    _description = 'Cash Advance'

    name = fields.Char(string='Reference', required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one('res.currency', required=True)
    purpose = fields.Text()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    trip_start_date = fields.Date()
    trip_end_date = fields.Date()
    reconciled_amount = fields.Monetary()
    expense_sheet_ids = fields.One2many('hr.expense.sheet', 'cash_advance_id')
```

---

### 5.2 `ipai_srm_rate_governance`

**Purpose:** Supplier rate card management

**Directory Structure:**
```
addons/ipai_srm_rate_governance/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── ipai_rate_card.py
│   └── ipai_rate_card_line.py
├── views/
│   └── ipai_rate_card_views.xml
├── security/
│   └── ir.model.access.csv
└── data/
    └── ipai_rate_card_data.xml
```

**Core Model:**
```python
# models/ipai_rate_card.py
class RateCard(models.Model):
    _name = 'ipai.rate.card'
    _description = 'Supplier Rate Card'

    name = fields.Char(string='Rate Card Name', required=True)
    code = fields.Char(string='Code', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    effective_from = fields.Date(required=True)
    effective_to = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('expired', 'Expired'),
        ('superseded', 'Superseded'),
    ], default='draft')
    approved_by = fields.Many2one('res.users')
    approved_at = fields.Datetime()
    line_ids = fields.One2many('ipai.rate.card.line', 'rate_card_id')
    supabase_id = fields.Char(string='Supabase UUID', readonly=True)

    @api.model
    def sync_from_supabase(self, data):
        """Create or update rate card from Supabase payload"""
        pass

    def sync_to_supabase(self):
        """Push rate card to Supabase"""
        pass
```

---

## 6. Sync Workflows

### 6.1 Odoo → Supabase (Push)

**Trigger:** Odoo webhook on model changes

**n8n Workflow:**
1. Receive webhook from Odoo
2. Transform payload to Supabase schema
3. Lookup/create related records (tenant, employee, etc.)
4. Upsert to Supabase table
5. Log sync event to `logs.sync_events`

---

### 6.2 Supabase → Odoo (Pull)

**Trigger:** Supabase Edge Function on table changes

**n8n Workflow:**
1. Receive webhook from Supabase
2. Transform payload to Odoo format
3. Authenticate with Odoo API
4. Create/update record in Odoo
5. Update `odoo_id` in Supabase
6. Log sync event

---

### 6.3 Conflict Resolution

| Scenario | Resolution |
|----------|------------|
| Same field modified in both | Odoo wins (source of truth for finance) |
| Record deleted in Odoo | Soft delete in Supabase (`deleted_at`) |
| Record deleted in Supabase | No action in Odoo (audit trail) |
| Lookup fails | Create placeholder, flag for review |

---

## 7. Webhook Configuration

### 7.1 Odoo Webhooks

Configure in Odoo via `base_automation` or custom module:

```python
# Expense sheet webhook
{
    'name': 'Sync Expense Sheet to Supabase',
    'model_id': 'hr.expense.sheet',
    'trigger': 'on_write',
    'url': 'https://n8n.insightpulseai.com/webhook/odoo-expense-sheet',
    'fields': ['state', 'total_amount', 'approval_date'],
}
```

### 7.2 Supabase Edge Functions

```typescript
// supabase/functions/sync-to-odoo/index.ts
Deno.serve(async (req) => {
    const { record, type, table } = await req.json();

    // Route to appropriate handler
    switch (table) {
        case 'rates.rate_cards':
            return syncRateCardToOdoo(record, type);
        case 'expense.cash_advances':
            return syncCashAdvanceToOdoo(record, type);
        default:
            return new Response('Unknown table', { status: 400 });
    }
});
```

---

## 8. Error Handling

### 8.1 Retry Strategy

| Error Type | Retry | Max Attempts | Backoff |
|------------|-------|--------------|---------|
| Network timeout | Yes | 3 | Exponential |
| Rate limit | Yes | 5 | Fixed 60s |
| Validation error | No | — | — |
| Not found | No | — | Log and skip |

### 8.2 Dead Letter Queue

Failed syncs are logged to `logs.sync_failures`:

```sql
CREATE TABLE logs.sync_failures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,  -- 'odoo' or 'supabase'
    target TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    error_message TEXT NOT NULL,
    attempts INTEGER DEFAULT 1,
    last_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 9. Monitoring

### 9.1 Sync Health Dashboard

Key metrics:
- Sync latency (p50, p95, p99)
- Sync success rate
- Dead letter queue depth
- Record count delta (Odoo vs Supabase)

### 9.2 Alerts

| Alert | Condition | Channel |
|-------|-----------|---------|
| Sync failure spike | >10 failures in 5 min | Mattermost |
| High latency | p95 > 30s | Mattermost |
| Queue backup | DLQ > 100 items | Mattermost + Email |

---

## 10. Related Documents

- [INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](../docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md)
- [DB_TARGET_ARCHITECTURE.md](../db/DB_TARGET_ARCHITECTURE.md)
- [Engine Specs](../engines/) — Engine YAML definitions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial release |
