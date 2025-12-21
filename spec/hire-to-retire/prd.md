# Hire-to-Retire Process - Product Requirements

## Overview

End-to-end employee lifecycle management from hiring to retirement/separation, with DOLE statutory compliance and internal SLA tracking.

## Process Phases

### Phase 1: Hiring
- Staffing need identification
- Requisition submission and approval
- Budget approval (FSS)
- Candidate selection and offer
- Employee master data creation

### Phase 2: First Pay
- Payroll master setup
- 7-day eligibility check (internal SLA)
- Include in current payroll run
- First salary disbursement

### Phase 3: Active Employment
- Salary changes
- Promotions/transfers
- Leave management
- Performance reviews
- Training records

### Phase 4: Clearance
- Exit request/resignation
- Offboarding ticket creation
- Parallel clearance collection:
  - HR clearance
  - Finance clearance (advances, reimbursements)
  - IT clearance (access revocation, asset return)
  - Admin clearance (IDs, keys, badges)
- Leave balance calculation
- Clearance completion milestone

### Phase 5: Last Pay (Final Pay)
- Final pay calculation:
  - Pro-rated salary
  - Leave credit conversion (VL + SL)
  - 13th month (pro-rated)
  - Pending reimbursements
  - Less: Advances, asset charges, taxes
- FSS Director approval
- Payment execution
- COE issuance (≤3 days from request)
- Employee status update: Terminated

## SLA Requirements

| Requirement | Type | Deadline | Trigger |
|-------------|------|----------|---------|
| Final Pay | Statutory | ≤30 days | Separation date |
| Final Pay | Internal | ≤7 days | Clearance completed |
| COE | Statutory | ≤3 days | Employee request |
| Clearance | Internal | ≤5 biz days | Last working day |

## Final Pay Components

### Additions
- Pro-rated basic salary (up to LWD)
- Unused leave credit conversion
- 13th month pay (pro-rated)
- Approved reimbursements
- Other benefits due

### Deductions
- Outstanding cash advances
- Unreturned asset value
- Tax adjustments (BIR)
- Government contributions (SSS, PhilHealth, Pag-IBIG)

### Leave Conversion Formula
```
Daily Rate = Monthly Basic / 22 work days
VL Conversion = VL Balance × Daily Rate
SL Conversion = SL Balance × Daily Rate (if policy allows)
Total = VL Conversion + SL Conversion
```

## Success Metrics

| Metric | Target |
|--------|--------|
| Final Pay within 7 days | 95%+ |
| COE within 3 days | 100% |
| Clearance within 5 days | 90%+ |
| Zero DOLE complaints | 100% |
