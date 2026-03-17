# Synthetic Data Generation Specification

> Only for gaps not covered by public datasets.
> Every synthetic record is labeled: `ref` prefixed `SYNTH_`, `note` contains `[SYNTHETIC]`.
> Reference: `docs/seed/SEED_DATA_STRATEGY.md`

---

## 1. PH Customer Partners (8,000 records)

**Generator**: `Faker('fil_PH')` + custom distributions

```python
# scripts/seed/generate_ph_partners.py
from faker import Faker
fake = Faker('fil_PH')

# Schema
{
    "ref": f"SYNTH_CUST_{i:06d}",
    "name": fake.name(),
    "email": fake.email(),
    "phone": fake.phone_number(),       # +639xx format
    "mobile": fake.phone_number(),
    "street": fake.street_address(),
    "city": weighted_choice(PH_CITIES),  # NCR-heavy
    "state_id": mapped_province(),       # PH provinces
    "country_id": "base.ph",
    "company_type": weighted_choice(["person", "company"], [0.7, 0.3]),
    "vat": fake.ssn() if is_company else False,  # TIN format
    "customer_rank": 1,
    "lang": "en_US",
    "note": "[SYNTHETIC] Generated for demo/testing purposes",
}
```

**Distributions**:
- 70% individual (`person`), 30% company
- Geographic: NCR 55%, CALABARZON 15%, Central Luzon 10%, Cebu 8%, Davao 5%, others 7%
- 3% missing phone, 1% duplicate email (intentional for dedup testing)
- 0.5% invalid addresses (testing error handling)

---

## 2. PH Vendor Partners (500 records)

**Generator**: `Faker('fil_PH')` + industry distribution

```python
{
    "ref": f"SYNTH_VEND_{i:04d}",
    "name": fake.company(),
    "company_type": "company",
    "supplier_rank": 1,
    "customer_rank": 0,
    "vat": generate_ph_tin(),
    "payment_term_id": weighted_choice([immediate, net15, net30, net60], [0.1, 0.3, 0.4, 0.2]),
    "note": "[SYNTHETIC]",
}
```

**Industry distribution**: IT services 25%, Office supplies 20%, Logistics 15%, Marketing 10%, Food/catering 10%, Utilities 10%, Professional services 10%

---

## 3. Purchase Orders (2,000 records)

**Generator**: PyDataFaker + custom Odoo fields

**Row counts**: 2,000 POs with avg 2.5 lines = 5,000 PO lines

**Date range**: 2025-01-01 to 2026-03-15, uniform with slight seasonality (higher in Q1/Q3)

**Status distribution**:
| Status | % | Count |
|--------|---|-------|
| `purchase` (confirmed) | 50% | 1,000 |
| `done` (received) | 30% | 600 |
| `draft` | 10% | 200 |
| `cancel` | 10% | 200 |

**Amount distribution**:
- Mean: ₱45,000
- Median: ₱25,000
- Min: ₱500
- Max: ₱2,000,000
- Std dev: ₱80,000
- Skew: right (long tail of large POs)

**Dependencies**:
- `partner_id` → random vendor from `SYNTH_VEND_*`
- `product_id` → random product from product catalog
- `date_order` → within date range
- `date_planned` → date_order + payment_term days

---

## 4. Vendor Bills (3,000 records)

Derived from purchase orders:
- 80% of confirmed POs generate 1 bill
- 20% of confirmed POs generate 2 bills (partial delivery)
- Additional 200 standalone bills (utilities, rent, subscriptions)

**Amount**: Matches PO line totals ± 2% (rounding, adjustments)

---

## 5. PH Payroll (3,600 payslips)

**Generator**: Custom PH payroll calculator

**Scope**: 300 employees × 12 months (2025-04 to 2026-03)

**Per payslip lines (7 avg)**:
1. Basic Pay (`wage` from `hr.contract`)
2. SSS Deduction (5% EE, cap at ₱35,000 base)
3. PhilHealth Deduction (2.5% EE, base ₱10K-₱100K)
4. Pag-IBIG Deduction (2% EE, cap at ₱5,000 base)
5. Withholding Tax (TRAIN law progressive)
6. Net Pay (computed)
7. 13th Month Pay (December only, = basic pay)

**Salary distribution**:

| Band | Monthly (PHP) | % Employees | Count |
|------|--------------|-------------|-------|
| Entry | 18,000-25,000 | 25% | 75 |
| Junior | 25,000-40,000 | 30% | 90 |
| Mid | 40,000-70,000 | 25% | 75 |
| Senior | 70,000-120,000 | 15% | 45 |
| Executive | 120,000-300,000 | 5% | 15 |

**Seasonality**:
- 13th month in December
- Overtime spikes in March (BIR filing) and December (year-end)
- 2-3% employees on leave each month (reduced pay)

**Anomalies for testing**:
- 5 employees with mid-year salary adjustments
- 3 employees terminated mid-year (final pay computation)
- 2 employees hired mid-year (pro-rated)
- 1 employee with back-pay correction

---

## 6. Expenses (1,000 records)

**Generator**: Faker + weighted categories

**Date range**: 2025-01-01 to 2026-03-15

**Category distribution**:

| Category | % | Avg Amount (PHP) |
|----------|---|-----------------|
| Transportation | 25% | 1,500 |
| Meals | 20% | 800 |
| Office Supplies | 15% | 3,000 |
| Communication | 10% | 1,200 |
| Training | 10% | 15,000 |
| Travel | 10% | 25,000 |
| Representation | 5% | 5,000 |
| Miscellaneous | 5% | 2,000 |

**Status distribution**: 60% approved, 20% submitted, 10% draft, 5% refused, 5% paid

**Dependencies**: `employee_id` → random from `hr.employee`

**Anomalies**:
- 3% over policy limit (>₱50,000 single expense)
- 2% missing receipts
- 1% duplicate submissions

---

## 7. CRM Pipeline (5,000 opportunities)

**Generator**: Faker + stage funnel

**Date range**: 2025-01-01 to 2026-03-15

**Funnel conversion**:
```
New (100%) → Qualified (65%) → Proposition (45%) → Negotiation (30%) → Won (20%)
                                                                    → Lost (10%)
```

**Revenue distribution** (expected_revenue):
- Mean: ₱250,000
- Median: ₱80,000
- Min: ₱5,000
- Max: ₱10,000,000
- Log-normal distribution

**Win rate**: 20% overall, varying by:
- Source: Referral 35%, Inbound 22%, Outbound 12%
- Segment: Enterprise 15%, Mid-market 25%, SMB 30%
- Quarter: Q4 highest (25%), Q1 lowest (15%)

**Sales cycle (days to close)**:
- Enterprise: 90-180 days
- Mid-market: 30-90 days
- SMB: 7-30 days

**Dependencies**:
- `partner_id` → random customer partner
- `team_id` → random sales team
- `user_id` → random salesperson

---

## 8. Project Tasks (500 records)

**Composition**:
- 53 existing BIR tasks (from `ipai_finance_close_seed`)
- 20 existing month-end tasks (from `ipai_finance_workflow`)
- 9 existing project seed tasks
- 418 synthetic operational tasks

**Synthetic task categories**:

| Category | Count | Project |
|----------|-------|---------|
| Sprint tasks (engineering) | 200 | Software Development |
| Marketing campaigns | 50 | Marketing Operations |
| Client onboarding | 40 | Client Services |
| Infrastructure | 30 | DevOps/Infra |
| Compliance/audit | 30 | Compliance |
| Design/creative | 30 | Design |
| Documentation | 20 | Documentation |
| Training | 18 | HR/Training |

**Status distribution**: 40% done, 25% in-progress, 20% todo, 10% cancelled, 5% blocked

**Date range**: Created 2025-01 to 2026-03, deadlines spread over same range

---

## 9. Subscriptions (200 records)

**Generator**: Custom subscription lifecycle

**Types**:
| Type | % | Monthly (PHP) | Billing Cycle |
|------|---|--------------|---------------|
| SaaS subscription | 40% | 5,000-50,000 | Monthly |
| Maintenance contract | 25% | 10,000-100,000 | Annual |
| Support plan | 20% | 3,000-30,000 | Monthly |
| License | 15% | 20,000-200,000 | Annual |

**Lifecycle states**: 60% active, 15% churned, 10% trial, 10% paused, 5% expired

**Churn pattern**: Higher in months 3, 6, 12 (common churn points)

---

## 10. Agent Task Logs (10,000 records — Supabase)

**Generator**: Custom agent simulation

**Target**: `supabase.agent.task_log`

```sql
CREATE TABLE agent.task_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent.session(id),
    agent_name TEXT NOT NULL,        -- 'advisory', 'router', 'ops', 'actions'
    tool_name TEXT,                   -- 'odoo_create_task', 'search_knowledge', etc.
    intent TEXT NOT NULL,             -- 'bir_filing_query', 'expense_approval', etc.
    status TEXT NOT NULL,             -- 'completed', 'failed', 'timeout', 'escalated'
    input_tokens INT,
    output_tokens INT,
    latency_ms INT,
    error_message TEXT,
    odoo_record_ref TEXT,            -- linked Odoo record if applicable
    created_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB,
    is_synthetic BOOLEAN DEFAULT true
);
```

**Distribution**:
| Agent | % | Avg Latency (ms) |
|-------|---|-------------------|
| advisory | 40% | 2,500 |
| router | 25% | 500 |
| ops | 20% | 3,000 |
| actions | 15% | 4,500 |

**Status**: 85% completed, 8% failed, 4% timeout, 3% escalated

**Intent categories**: BIR queries 20%, expense management 15%, report generation 15%, task creation 12%, knowledge search 12%, document processing 10%, schedule management 8%, other 8%

**Anomalies**:
- 5% with latency > 10s (slow queries)
- 2% with token count > 4000 (long conversations)
- 1% with error cascades (3+ failures in same session)

---

## 11. Milestones & KPIs (50+100 records)

### Milestones (hand-authored)

| Milestone | Project | Target Date | Status |
|-----------|---------|-------------|--------|
| Q1 2025 BIR Filing Complete | BIR Returns | 2025-04-15 | done |
| EE Parity 50% | Platform Development | 2025-06-30 | in_progress |
| Lakehouse MVP | Data Intelligence | 2025-09-30 | planned |
| Agent Platform v1 | Agent Platform | 2025-12-31 | planned |
| EE Parity 80% | Platform Development | 2026-06-30 | planned |

### KPIs (Plane projection — synthetic)

| KPI | Target | Actual | Period |
|-----|--------|--------|--------|
| Monthly Active Users | 500 | varies | Monthly |
| Revenue (PHP) | ₱5M/mo | varies | Monthly |
| Support Ticket Resolution Time | <4hrs | varies | Weekly |
| Agent Task Completion Rate | >90% | varies | Weekly |
| BIR Filing Compliance | 100% | 100% | Quarterly |

---

## 12. Multi-Company Behavior

All synthetic records respect company isolation:

| Company | % of Records | Currency | Fiscal Year |
|---------|-------------|----------|-------------|
| InsightPulse AI | 60% | PHP | Jan-Dec |
| IPAI Digital | 25% | PHP | Jan-Dec |
| IPAI Retail | 10% | PHP | Jan-Dec |
| TBWA\SMP | 5% | PHP | Jan-Dec |

Inter-company transactions: 50 synthetic invoices between companies (testing multi-company reconciliation).

---

## 13. Null/Error Conditions for Pipeline Testing

| Condition | % | Purpose |
|-----------|---|---------|
| Missing phone number | 3% of partners | Test data quality checks |
| Duplicate email | 1% of partners | Test deduplication |
| Invalid date (future invoice date) | 0.5% of invoices | Test validation rules |
| Negative quantity | 0.1% of order lines | Test constraint checks |
| Zero-amount invoice | 0.3% of invoices | Test edge cases |
| Orphaned payment (no invoice) | 0.2% of payments | Test reconciliation |
| Circular department hierarchy | 1 record | Test infinite loop prevention |
| Unicode in names | 2% of partners | Test encoding (Filipino diacritics) |
| Very long description | 0.5% of tasks | Test field truncation |
| Backdated entries | 1% of journal entries | Test period lock |

---

*All synthetic data is clearly labeled and non-identifying.*
*Last updated: 2026-03-17*
