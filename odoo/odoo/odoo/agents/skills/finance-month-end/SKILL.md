---
name: finance-ssc-month-end
description: Automates month-end closing procedures for TBWA Finance SSC
version: 1.0.0
author: InsightPulse AI
tags: [finance, accounting, month-end, closing]
---

# Finance SSC Month-End Closing

## Overview

This skill guides Claude through the complete month-end closing process for TBWA Finance SSC. It provides structured workflows, validation checks, and automated task management for the closing cycle.

## Prerequisites

- Access to Odoo 18 CE via MCP (`odoo-mcp` server)
- Supabase connection for audit logging
- n8n workflows for automation triggers
- Mattermost integration for notifications

## Capabilities

This skill enables:
- Generating month-end task checklists
- Validating closing readiness
- Running pre-close checks
- Coordinating team activities
- Generating status reports
- Automating journal entries
- Producing management reports

## Workflow Steps

### Phase 1: Pre-Close (Day 1-3)

1. **Data Validation**
   ```
   Use Odoo MCP to verify:
   - All vendor invoices posted (account.move where move_type='in_invoice' and state='draft')
   - All customer invoices issued
   - Bank statements downloaded
   - Petty cash reconciled
   ```

2. **Reconciliation Checks**
   ```
   Query intercompany accounts:
   - Match debit/credit across companies
   - Flag unmatched transactions
   - Generate reconciliation report
   ```

3. **Open Items Review**
   ```
   Identify items needing action:
   - Open purchase orders > 30 days
   - Unapproved expenses
   - Pending journal entries
   ```

### Phase 2: Close Activities (Day 4-5)

1. **Standard Journal Entries**
   ```
   Generate entries for:
   - Accrued expenses (payroll, utilities, rent)
   - Prepaid amortization (insurance, subscriptions)
   - Depreciation (run schedule via n8n)
   ```

2. **Bank Reconciliation**
   ```
   For each bank account:
   - Import latest statement
   - Match transactions
   - Flag outstanding items
   - Document reconciling items
   ```

3. **Trial Balance Review**
   ```
   Generate and analyze:
   - Compare to prior period
   - Identify variances > 10%
   - Document explanations
   ```

### Phase 3: Reporting (Day 6-7)

1. **Financial Statements**
   ```
   Generate standard reports:
   - Balance Sheet
   - Income Statement
   - Cash Flow (quarterly)
   ```

2. **Variance Analysis**
   ```
   For each significant variance:
   - Calculate amount and percentage
   - Identify root cause
   - Document explanation
   ```

3. **Management Report**
   ```
   Compile:
   - Executive summary
   - KPI dashboard
   - Significant items
   - Recommendations
   ```

## Automation Triggers

| Command | Action |
|---------|--------|
| `/month-end start` | Initialize new closing period |
| `/month-end status` | Show current progress |
| `/month-end tasks` | List pending tasks |
| `/month-end report` | Generate status report |
| `/month-end close` | Request period lock |

## Validation Rules

### Pre-Close Checks

```python
checks = [
    ("All invoices posted", "No draft invoices in period"),
    ("Bank reconciled", "All accounts balanced"),
    ("Intercompany matched", "Zero net IC balance"),
    ("Accruals posted", "Standard accruals complete"),
    ("Depreciation run", "Asset schedule current"),
]
```

### Close Criteria

- All Phase 2 tasks completed
- Trial balance balanced
- Variances documented
- Manager approval obtained
- No blocking errors

## MCP Tool Usage

### Search for Draft Invoices

```json
{
  "tool": "odoo_search",
  "params": {
    "model": "account.move",
    "domain": [
      ["move_type", "in", ["in_invoice", "out_invoice"]],
      ["state", "=", "draft"],
      ["date", ">=", "2026-01-01"],
      ["date", "<=", "2026-01-31"]
    ]
  }
}
```

### Generate Trial Balance

```json
{
  "tool": "odoo_execute",
  "params": {
    "model": "account.report",
    "method": "get_report_values",
    "args": ["trial_balance", {"date_from": "2026-01-01", "date_to": "2026-01-31"}]
  }
}
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Unbalanced entries | Review and correct before proceeding |
| Missing approvals | Escalate to Finance Director |
| System unavailable | Retry in 15 minutes, notify #system-health |
| Data discrepancy | Document and flag for investigation |

## Output Format

### Status Report Template

```markdown
# Month-End Status Report
**Period**: January 2026
**Status**: In Progress
**Completion**: 65%

## Task Summary
| Phase | Total | Complete | Pending |
|-------|-------|----------|---------|
| Pre-Close | 10 | 8 | 2 |
| Close | 8 | 3 | 5 |
| Reporting | 5 | 0 | 5 |

## Blocking Issues
- [ ] Bank statement pending for Account XYZ

## Next Steps
1. Complete bank reconciliation
2. Post depreciation entry
3. Generate trial balance
```

## Related Skills

- [BIR Tax Filing](../bir-tax-filing/SKILL.md)
- [Expense Processing](../expense-processing/SKILL.md)

## Changelog

- **v1.0.0** (2026-01-06): Initial release
