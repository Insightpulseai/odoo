# ipai_month_end - Product Requirements

## Overview

Month-end closing automation module for Odoo 18 CE, providing SAP Advanced Financial Closing (AFC) feature parity at zero licensing cost.

## Cost Comparison

| Item | SAP AFC | ipai_month_end |
|------|---------|----------------|
| Software License | $50,000+/year | $0 (AGPL-3) |
| SAP S/4HANA Required | Yes (~$200K+) | No |
| Implementation | $100K-500K | $10K-30K |
| 5-Year TCO | $500K-1M+ | <$50K |

## Feature Mapping

### 1. Templates (100% Parity)
- `ipai.month.end.task.template` model
- Phase I-IV grouping
- Task dependencies (M2M)
- RACI assignments
- Workday offset scheduling

### 2. Task Lists (100% Parity)
- Generate task list from templates
- Holiday-aware workday calculation
- Release workflow (draft → in_progress)
- Process workflow (Prep → Review → Approve)

### 3. Approval Workflow (100% Parity)
- Multi-level approval
- Audit trail with timestamps
- State machine: pending → in_progress → review → done

### 4. Notifications (95% Parity)
- Odoo mail.thread integration
- Daily overdue alerts (ir.cron)
- Activity scheduling
- Email notifications

### 5. Monitoring (100% Parity)
- Progress computed field
- Overdue tracking
- Dashboard integration
- Superset SQL support

## Task Template Structure

```python
class MonthEndTaskTemplate(models.Model):
    _name = "ipai.month.end.task.template"

    name = fields.Char(required=True)
    sequence = fields.Integer()
    phase = fields.Selection([
        ("I", "Initial & Compliance"),
        ("II", "Accruals & Amortization"),
        ("III", "WIP"),
        ("IV", "Final Adjustments & Close"),
    ])
    prep_user_id = fields.Many2one("res.users")
    review_user_id = fields.Many2one("res.users")
    approve_user_id = fields.Many2one("res.users")
    prep_day_offset = fields.Integer()  # -6 = 6 days before close
    depends_on_ids = fields.Many2many("ipai.month.end.task.template")
    odoo_model = fields.Char()  # e.g., "account.move"
    oca_module = fields.Char()  # e.g., "account_asset_management"
```

## 36-Task Template Library

### Phase I: Initial & Compliance
1. Update PH holiday calendar
2. Validate SSS/PhilHealth/Pag-IBIG submissions
3. Prepare BIR 2307 withholding certificates
4. Reconcile bank statements

### Phase II: Accruals & Amortization
5. Accrue salaries and wages
6. Accrue professional fees
7. Accrue utilities
8. Process prepaid amortization
9. Process asset depreciation

### Phase III: WIP
10. Review WIP projects
11. Recognize project revenue
12. Close completed projects

### Phase IV: Final Adjustments & Close
13. Post intercompany entries
14. Foreign currency revaluation
15. Reconcile control accounts
16. Generate trial balance
17. Close period in GL

## Success Metrics

| Metric | Target |
|--------|--------|
| Feature Parity | 98%+ |
| Task Completion Rate | 100% by close date |
| Overdue Tasks | 0 at month-end |
| Close Cycle Time | ≤5 working days |
