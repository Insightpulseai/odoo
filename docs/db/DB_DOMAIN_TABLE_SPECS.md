# Domain Table Specs (Conceptual)

This document lists canonical table specs (columns, types, PKs, salient FKs) for the major domains. These are **specs only** (no CREATE TABLE statements).

---

## Pattern Notes (Applies to All Tables)

- `tenant_id uuid NOT NULL` when table is tenant-scoped
- `company_id uuid` optional for legal entity separation
- `created_at timestamptz DEFAULT now()`, `updated_at timestamptz DEFAULT now()`
- PK: `id uuid DEFAULT gen_random_uuid()` unless Odoo numeric IDs required; record Odoo ID as `odoo_id integer` when needed

---

## Core Schema

### core.tenant
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| company_id | uuid FK | References core.company |
| slug | text UNIQUE | |
| name | text NOT NULL | |
| plan | text | |
| region | text | |
| metadata | jsonb | |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### core.company
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| name | text NOT NULL | |
| legal_name | text | |
| metadata | jsonb | |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### core.app_user
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| auth_user_id | uuid | References auth.users.id |
| email | text | |
| display_name | text | |
| phone | text | |
| metadata | jsonb | |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### core.role
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| code | text UNIQUE NOT NULL | |
| name | text NOT NULL | |
| description | text | |
| created_at | timestamptz | |

### core.tenant_membership
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid NOT NULL FK | |
| app_user_id | uuid NOT NULL FK | |
| role_id | uuid FK | |
| is_owner | boolean | |
| created_at | timestamptz | |

---

## SaaS Schema

### saas.plan
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| slug | text UNIQUE | |
| name | text | |
| price_cents | integer | |
| billing_interval | text | monthly/yearly |
| features | jsonb | |
| created_at | timestamptz | |

### saas.subscription
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid FK | References core.tenant |
| plan_id | uuid FK | References saas.plan |
| status | text | active/past_due/cancelled |
| start_at | timestamptz | |
| expires_at | timestamptz | |
| seats | integer | |

---

## CRM Schema

### crm.partner
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| name | text | |
| email | text | |
| phone | text | |
| partner_type | text | person/company |
| odoo_partner_id | integer | Optional Odoo mapping |

---

## Sales Schema

### sales.order
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| partner_id | uuid FK | References crm.partner |
| state | text | |
| total_amount | numeric | |
| currency | text | |
| order_date | date | |

---

## Finance Schema

### finance.move
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| journal_id | uuid | |
| date | date | |
| ref | text | |

### finance.move_line
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| move_id | uuid FK | References finance.move |
| account_id | uuid | |
| debit | numeric | |
| credit | numeric | |
| partner_id | uuid | |

---

## Inventory Schema

### inventory.product
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| name | text | |
| default_code | text | SKU |
| uom_id | uuid | |
| category_id | uuid | |

---

## Expense Schema

### expense.expense_report
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| employee_id | uuid | References core.app_user |
| name | text | |
| status | text | |
| total_amount | numeric | |
| currency | text | |
| submitted_at | timestamptz | |
| approver_id | uuid | |

### expense.expense_line
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| report_id | uuid FK | References expense.expense_report |
| category_id | uuid | |
| amount | numeric | |
| date | date | |
| merchant | text | |
| receipt_url | text[] | |

---

## MCP / Agent Schema

### mcp.agents
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| slug | text | |
| name | text | |
| default_model | text | |
| routing_config | jsonb | |

---

## Gold Schema

### gold.docs
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| company_id | uuid | |
| source_uri | text | |
| title | text | |
| content_text | text | |
| metadata | jsonb | |

### gold.doc_chunks
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| doc_id | uuid FK | References gold.docs |
| chunk_no | integer | |
| content | text | |
| embedding | vector | |

---

## Projects Schema

### projects.project
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| tenant_id | uuid | |
| name | text | |
| code | text | |
| status | text | |
| start_date | date | |
| end_date | date | |

### projects.task
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| name | text | |
| assigned_to | uuid | |
| status | text | |
| due_date | date | |
