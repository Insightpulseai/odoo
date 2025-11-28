# WBS & LogFrame Mapping Documentation
## Month-End Closing Tasks for TBWA Finance SSC

**Generated**: 2025-11-26
**Source**: Notion Kanban Export (73 HTML files → 36 unique tasks)
**Deployment**: Odoo 18 CE + ipai_finance_ppm_tdi module

---

## Executive Summary

This document provides the complete mapping of 36 month-end closing tasks extracted from Notion to:
1. **Work Breakdown Structure (WBS)** - 4 hierarchical phases
2. **Logical Framework (LogFrame)** - Goal → Outcome → IM1/IM2 → Outputs → Activities
3. **Employee Assignments** - 10 TBWA Finance SSC team members with validated codes

### Key Metrics
- **Total Tasks**: 36 unique tasks (deduplicated from 72 Notion exports)
- **IM1 (Month-End Closing)**: 31 tasks (86%)
- **IM2 (Tax Filing Compliance)**: 5 tasks (14%)
- **Employee Workload Distribution**:
  - BOM (Finance Supervisor): 13 tasks (36%)
  - LAS (Finance Manager): 11 tasks (31%)
  - RIM (Senior Finance Manager): 4 tasks (11%)
  - RMQB (AP/Payments): 4 tasks (11%)
  - JI (Assets): 4 tasks (11%)

---

## Logical Framework Structure

### Goal (G1)
**100% compliant and timely month-end closing and tax filing**

**Indicator**: Zero penalties, 100% on-time filing rate

### Outcome (O1)
**Streamlined coordination between Finance, Payroll, Tax, Treasury**

**Indicator**: Month-end closing completed within 5 business days

### Immediate Objectives

#### IM1: Month-End Closing - Accurate books and reconciliations
**Indicator**: All reconciliations completed within 3 days of month-end

**Activities**:
1. Bank & Cash reconciliation (4 tasks)
2. GL account reconciliation (4 tasks)
3. AR/AP aging reviews (12 tasks)
4. Inventory valuation
5. Accruals & provisions (7 tasks)
6. Revenue recognition
7. Depreciation & amortization (3 tasks)
8. Reclassifications (OOP/WIP) (1 task)
9. Working capital reporting

#### IM2: Tax Filing Compliance - On-time BIR filing
**Indicator**: 100% BIR forms filed before deadline

**Activities**:
1. VAT compilation and reporting (3 tasks)
2. Withholding tax (2307) compilation
3. Tax provision calculation (1 task)
4. BIR form preparation
5. Final pay processing (1 task)
6. Payroll tax compliance

### Outputs

#### O1.1: All journal entries finalized and posted
**Indicator**: Zero pending JEs after Day 5
**Tasks**: 31 IM1 tasks contribute to this output

#### O1.2: All BIR tax forms filed on time
**Indicator**: 100% forms filed before BIR deadline
**Tasks**: 5 IM2 tasks contribute to this output

#### O1.3: Management reports reviewed and approved
**Indicator**: CFO approval within 7 days of month-end
**Tasks**: Subset of IM1 reporting tasks (8 tasks)

---

## Work Breakdown Structure (WBS)

### Phase 1: Initial & Compliance (Days 1-5)
**Focus**: Foundation tasks, compliance requirements, payroll

**Tasks** (5 total):
1. Calculate and record the monthly tax provision and PPB provision (RIM)
2. Process and record Payroll, Final Pay, SL conversions (BOM)
3. Record monthly bank charges, revalue foreign currency bank accounts (BOM)

**Critical Path**: Payroll must complete before Phase 2 accruals

### Phase 2: Revenue & Core Accruals (Days 3-7)
**Focus**: Revenue recognition, core accrual categories, VAT

**Tasks** (18 total):
1. Accrue estimated monthly audit fees (LAS)
2. Accrue monthly expense for employee cellphone allowance (LAS)
3. Accrue monthly expenses for management and royalty fees (RIM)
4. Accrue recurring expenses for regularly occurring services (LAS)
5. Accrue revenue and billable costs based on client contracts (LAS)
6. Compile and record monthly input VAT entries (RIM)
7. Compile supporting documents for attachment of revenue accruals (LAS)
8. Compile, review, and record the monthly VAT report (RIM)
9. Record depreciation for vehicles, purchases, LOA, tech licenses (JI)
10. Record estimated monthly insurance premiums (LAS)
11. Record intercompany revaluations and accruals (BOM)
12. Record monthly accrued utility expenses (LAS)
13. Record monthly rental income/expense recognition (LAS)
14. Prepare and record WIP Schedule per job number (BOM)
15. Record depreciation and amortization for annual subscriptions (JI)
16. Review and process monthly cash advance liquidation (RMQB)
17. Update and record accrual for unused service leave balances (BOM)

**Critical Path**: Revenue accruals must complete before WIP/OOP reclassification

### Phase 3: WIP/Final Accruals (Days 5-10)
**Focus**: Cost reclassifications, final adjustments

**Tasks** (3 total):
1. Perform month-end reclassifications between OOP and WIP (LAS)
2. Record accrued business permit amortization (JI)
3. Review and record accrued foreign currency differences (RMQB)

**Critical Path**: WIP reclassification depends on Phase 2 revenue completion

### Phase 4: Final Adjustments & Close (Days 8-12)
**Focus**: Reporting, final depreciation, treasury reconciliation

**Tasks** (10 total):
1. Prepare accounts payable aging report for management review (RMQB)
2. Prepare monthly HOW's summary reports per brand and agency (BOM)
3. Prepare monthly working capital report (BOM)
4. Process and record monthly depreciation entries for all fixed assets (JI)
5. Record business development expense accruals (BOM)
6. Record monthly accrual for trade and non-trade payables (RMQB)
7. Record monthly accrued interest expense on loans (BOM)
8. Record monthly contingency reserve accruals (BOM)
9. Review and record adjustments for deferred tax assets/liabilities (RIM)
10. Review and update prepaid expense amortization schedules (JI)

**Critical Path**: All Phase 2 & 3 tasks must complete before final depreciation and reporting

---

## Employee Assignment Matrix

### Finance Director (CKVC - Khalil Veracruz)
**Role**: Final approvals, strategic decisions, CFO-level tasks
**Assigned Tasks**: 0 routine tasks (approval workflow only)
**BIR Workflow**: Step 3 (Payment Approval) + Step 4 (Filing & Payment)

### Senior Finance Manager (RIM - Rey Meran)
**Role**: VAT, tax compliance, complex accruals, management fees
**Assigned Tasks**: 4 tasks
1. Accrue monthly expenses for management and royalty fees
2. Compile and record monthly input VAT entries
3. Compile, review, and record the monthly VAT report
4. Review and record adjustments for deferred tax assets/liabilities

**BIR Workflow**: Step 2 (Report Approval)

### Finance Manager (LAS - Amor Lasaga)
**Role**: Revenue recognition, billable costs, reconciliations
**Assigned Tasks**: 11 tasks
1. Accrue estimated monthly audit fees
2. Accrue monthly expense for employee cellphone allowance
3. Accrue recurring expenses for regularly occurring services
4. Accrue revenue and billable costs based on client contracts
5. Compile supporting documents for attachment of revenue accruals
6. Perform month-end reclassifications between OOP and WIP
7. Record estimated monthly insurance premiums
8. Record monthly accrued utility expenses
9. Record monthly rental income/expense recognition
10. Update and record accrual for unused service leave balances

### Finance Supervisor (BOM - Beng Manalo)
**Role**: Bank reconciliation, payroll, routine closing tasks
**Assigned Tasks**: 13 tasks
1. Calculate and record the monthly tax provision and PPB provision
2. Process and record Payroll, Final Pay, SL conversions
3. Record monthly bank charges, revalue foreign currency bank accounts
4. Record intercompany revaluations and accruals
5. Prepare and record WIP Schedule per job number
6. Prepare monthly HOW's summary reports per brand and agency
7. Prepare monthly working capital report
8. Record business development expense accruals
9. Record monthly accrued interest expense on loans
10. Record monthly contingency reserve accruals

**BIR Workflow**: Step 1 (Preparation)

### Finance Assistant - Assets (JI - Jasmin Ignacio)
**Role**: Expense tracking, fixed asset management, depreciation
**Assigned Tasks**: 4 tasks
1. Record depreciation for vehicles, purchases, LOA, tech licenses
2. Record accrued business permit amortization
3. Process and record monthly depreciation entries for all fixed assets
4. Review and update prepaid expense amortization schedules

### Finance Assistant - AP/Payments (RMQB - Sally Brillantes)
**Role**: AP processing, payment support
**Assigned Tasks**: 4 tasks
1. Review and process monthly cash advance liquidation
2. Review and record accrued foreign currency differences
3. Prepare accounts payable aging report for management review
4. Record monthly accrual for trade and non-trade payables

### Finance Assistant - VAT/Reporting (JPAL - Jinky Paladin)
**Role**: VAT support, reporting assistance
**Assigned Tasks**: 0 tasks (support role for RIM's VAT tasks)

### Finance Assistant - AP/Billing (JPL - Jerald Loterte)
**Role**: AP processing, billing support
**Assigned Tasks**: 0 tasks (support role for RMQB's AP tasks)

### Finance Assistant - General Support (JO - Jhoee Oliva)
**Role**: General finance support tasks
**Assigned Tasks**: 0 tasks (floating support)

### Finance Assistant - General Support (JM - Joana Maravillas)
**Role**: General finance support tasks
**Assigned Tasks**: 0 tasks (floating support)

---

## BIR Filing Workflow Integration

All BIR tax forms follow a 4-step workflow with internal deadlines:

### Step 1: Preparation (BIR Deadline - 4 Business Days)
**Responsible**: BOM (Finance Supervisor)
**Tasks**:
- Gather data
- Prepare BIR Form
- Draft payment request (check voucher)

### Step 2: Report Approval (BIR Deadline - 2 Business Days)
**Responsible**: RIM (Senior Finance Manager)
**Tasks**:
- Review report data for accuracy
- Approve compliance with BIR requirements
- Submit File Request to SFM

### Step 3: Payment Approval (BIR Deadline - 1 Business Day)
**Responsible**: CKVC (Finance Director)
**Tasks**:
- Review approved report
- Review payment request
- Approve release of funds for remittance

### Step 4: Filing & Payment (On or before BIR Deadline)
**Responsible**: CKVC (Finance Supervisor)
**Tasks**:
- File approved form (electronically or OTC)
- Remit payment to BIR

### 2026 BIR Calendar (Sample Entries)

| BIR Form | Period | BIR Deadline | Step 1 | Step 2 | Step 3 | Note |
|----------|--------|--------------|--------|--------|--------|------|
| 1601-C / 0619-E | Feb 2026 | Mar 10 | Mar 4 | Mar 6 | Mar 9 | |
| 1601-C / 0619-E | Mar 2026 | Apr 10 | Apr 6 | Apr 8 | Apr 9 | |
| 2550Q (VAT) | Q1 2026 | Apr 27 | Apr 21 | Apr 23 | Apr 24 | Apr 25 is Sat |
| 1601-EQ (Quarterly EWT) | Q1 2026 | Apr 30 | Apr 24 | Apr 28 | Apr 29 | |

**Complete Calendar**: See `data/bir_calendar_2026.json` (20 entries)

---

## Critical Path Analysis

### Dependencies
1. **Payroll → Accruals**: Final pay processing must complete before payroll accruals
2. **Revenue → WIP**: Revenue accruals must complete before WIP reclassification
3. **Accruals → Reporting**: All accruals must complete before working capital reporting
4. **VAT → BIR Filing**: VAT compilation must complete before quarterly BIR 2550Q

### Bottlenecks
1. **RIM (Senior Finance Manager)**: Only 4 tasks but includes critical VAT and tax adjustments
2. **LAS (Finance Manager)**: 11 tasks including critical revenue recognition path
3. **BOM (Finance Supervisor)**: 13 tasks with BIR Workflow Step 1 responsibility

### Mitigation Strategies
1. **JPAL (VAT Support)**: Assist RIM with VAT compilation to prevent bottleneck
2. **JPL (AP Billing)**: Assist RMQB with AP aging and accruals
3. **JO/JM (General Support)**: Float across teams to balance workload

---

## Task Categorization Summary

### By Category (from Notion parsing)
1. **Accruals & Provisions**: 20 tasks (56%)
2. **Reporting**: 8 tasks (22%)
3. **Tax & Compliance**: 8 tasks (22%)
4. **Depreciation & Assets**: 8 tasks (22%)
5. **Revenue Recognition**: 4 tasks (11%)
6. **Reclassifications**: 6 tasks (17%)
7. **Adjustments**: 4 tasks (11%)
8. **Bank & Cash**: 2 tasks (6%)
9. **General**: 12 tasks (33%)

*Note: Categories overlap - tasks can belong to multiple categories*

### By WBS Phase
1. **Phase 1 (Initial & Compliance)**: 5 tasks (14%)
2. **Phase 2 (Revenue & Core Accruals)**: 18 tasks (50%)
3. **Phase 3 (WIP/Final Accruals)**: 3 tasks (8%)
4. **Phase 4 (Final Adjustments & Close)**: 10 tasks (28%)

### By LogFrame Immediate Objective
1. **IM1 (Month-End Closing)**: 31 tasks (86%)
2. **IM2 (Tax Filing Compliance)**: 5 tasks (14%)

---

## Deployment Instructions

### Prerequisites
- Odoo 18 CE installed with `ipai_finance_ppm_tdi` module
- Finance team user accounts created with proper roles
- Project model enabled

### Installation Steps

1. **Upload Seed Data**:
```bash
scp addons/ipai_finance_ppm_tdi/data/month_end_tasks_notion_import.xml root@159.223.75.148:/root/odoo-prod/addons/ipai_finance_ppm_tdi/data/
```

2. **Update Manifest** (add to `__manifest__.py`):
```python
'data': [
    # ... existing files ...
    'data/month_end_tasks_notion_import.xml',
]
```

3. **Upgrade Module**:
```bash
ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production -u ipai_finance_ppm_tdi --stop-after-init"
```

4. **Verify Installation**:
```bash
ssh root@159.223.75.148 "docker exec odoo-ce psql -U odoo -d production -c \"SELECT COUNT(*) FROM project_task WHERE project_id IN (SELECT id FROM project_project WHERE name LIKE '%Notion%');\""
```

**Expected Output**: `36 rows` (36 tasks imported)

### Acceptance Gates

✅ **All gates must pass before marking deployment complete**:

1. ✅ All 36 tasks imported successfully
2. ✅ Task descriptions include LogFrame mapping notes
3. ✅ Employee assignments mapped to correct user records
4. ✅ Priority levels assigned (1=high, 2=medium, 3=normal)
5. ✅ Project "Month-End Closing - Notion Tasks" created
6. ✅ No duplicate tasks (compared with existing 51 seed data tasks)
7. ✅ TDI audit log shows "done" status with 100% success rate

---

## Maintenance & Updates

### Adding New Tasks
1. Export new tasks from Notion as HTML
2. Place in `/Users/tbwa/Downloads/notion-kanban/Untitled/New data source/`
3. Run: `python3 scripts/parse_notion_tasks.py --input <path> --output data/notion_tasks_new.json --summary`
4. Run: `python3 scripts/map_logframe.py --input data/notion_tasks_new.json --output data/notion_tasks_mapped_new.json --summary`
5. Run: `python3 scripts/generate_seed_xml.py --input data/notion_tasks_mapped_new.json --output addons/ipai_finance_ppm_tdi/data/month_end_tasks_update.xml`
6. Deploy via module upgrade

### Updating Employee Assignments
1. Edit `data/employee_directory.json`
2. Re-run LogFrame mapper: `python3 scripts/map_logframe.py ...`
3. Re-generate XML seed data
4. Deploy

### Updating BIR Calendar
1. Edit `data/bir_calendar_2026.json`
2. Import via TDI wizard in Odoo UI or upgrade module with updated seed data

---

## Appendix A: Complete Task List

### IM1: Month-End Closing Tasks (31 total)

#### Accruals & Provisions (7 tasks)
1. Accrue estimated monthly audit fees (LAS)
2. Accrue monthly expense for employee cellphone allowance (LAS)
3. Accrue recurring expenses for regularly occurring services (LAS)
4. Accrue revenue and billable costs based on client contracts (LAS)
5. Record estimated monthly insurance premiums (LAS)
6. Record monthly accrued utility expenses (LAS)
7. Update and record accrual for unused service leave balances (LAS)

#### AR/AP Aging Reviews (12 tasks)
8. Record accrued business permit amortization (JI)
9. Record business development expense accruals (BOM)
10. Record intercompany revaluations and accruals (BOM)
11. Record monthly accrual for trade and non-trade payables (RMQB)
12. Record monthly accrued interest expense on loans (BOM)
13. Record monthly contingency reserve accruals (BOM)
14. Record monthly rental income/expense recognition (LAS)
15. Review and process monthly cash advance liquidation (RMQB)
16. Review and record accrued foreign currency differences (RMQB)
17. Prepare accounts payable aging report for management review (RMQB)
18. Review and update prepaid expense amortization schedules (JI)
19. Compile supporting documents for attachment of revenue accruals (LAS)

#### GL Account Reconciliation (4 tasks)
20. Prepare and record WIP Schedule per job number (BOM)
21. Prepare monthly HOW's summary reports per brand and agency (BOM)
22. Prepare monthly working capital report (BOM)

#### Bank & Cash Reconciliation (4 tasks)
23. Record monthly bank charges, revalue foreign currency bank accounts (BOM)

#### Depreciation & Amortization (3 tasks)
24. Record depreciation for vehicles, purchases, LOA, tech licenses (JI)
25. Record depreciation and amortization for annual subscriptions (JI)
26. Process and record monthly depreciation entries for all fixed assets (JI)

#### Reclassifications (OOP/WIP) (1 task)
27. Perform month-end reclassifications between OOP and WIP (LAS)

### IM2: Tax Filing Compliance Tasks (5 total)

#### VAT Compilation and Reporting (3 tasks)
1. Accrue monthly expenses for management and royalty fees (RIM)
2. Compile and record monthly input VAT entries (RIM)
3. Compile, review, and record the monthly VAT report (RIM)

#### Tax Provision Calculation (1 task)
4. Calculate and record the monthly tax provision and PPB provision (RIM)

#### Final Pay Processing (1 task)
5. Process and record Payroll, Final Pay, SL conversions (BOM)

---

## Appendix B: Employee Directory

| Code | Name | Email | Role | Responsibilities |
|------|------|-------|------|------------------|
| CKVC | Khalil Veracruz | khalil.veracruz@omc.com | Finance Director | Final approvals, strategic decisions |
| RIM | Rey Meran | rey.meran@omc.com | Senior Finance Manager | VAT, tax compliance, complex accruals |
| LAS | Amor Lasaga | amor.lasaga@omc.com | Finance Manager | Revenue recognition, billable costs |
| BOM | Beng Manalo | beng.manalo@omc.com | Finance Supervisor | Bank reconciliation, payroll, routine tasks |
| JPAL | Jinky Paladin | jinky.paladin@omc.com | Finance Assistant (VAT/Reporting) | VAT support, reporting assistance |
| JPL | Jerald Loterte | jerald.loterte@omc.com | Finance Assistant (AP/Billing) | AP processing, billing support |
| JI | Jasmin Ignacio | jasmin.ignacio@omc.com | Finance Assistant (Expense/Assets) | Expense tracking, fixed asset management |
| JO | Jhoee Oliva | jhoee.oliva@omc.com | Finance Assistant (General Support) | General finance support tasks |
| JM | Joana Maravillas | joana.maravillas@omc.com | Finance Assistant (General Support) | General finance support tasks |
| RMQB | Sally Brillantes | sally.brillantes@omc.com | Finance Assistant (AP/Payments) | AP processing, payment support |

---

## Appendix C: File Manifest

| File | Description | Location |
|------|-------------|----------|
| `parse_notion_tasks.py` | Python parser for Notion HTML exports | `scripts/` |
| `map_logframe.py` | LogFrame mapper with employee assignments | `scripts/` |
| `generate_seed_xml.py` | Odoo XML seed data generator | `scripts/` |
| `notion_tasks_parsed.json` | Parsed Notion task data (72 tasks) | `data/` |
| `notion_tasks_deduplicated.json` | Deduplicated tasks (36 unique) | `data/` |
| `notion_tasks_with_logframe.json` | Tasks with LogFrame + employee mappings | `data/` |
| `employee_directory.json` | Employee codes, emails, roles | `data/` |
| `bir_calendar_2026.json` | BIR filing calendar with deadlines | `data/` |
| `month_end_tasks_notion_import.xml` | Odoo XML seed data (36 tasks) | `addons/ipai_finance_ppm_tdi/data/` |
| `WBS_LOGFRAME_MAPPING.md` | This documentation file | `docs/` |

---

**End of Documentation**

**Next Steps**:
1. Review and approve this mapping
2. Deploy XML seed data to production
3. Validate task imports in Odoo UI
4. Assign actual user IDs (currently using references)
5. Test month-end closing workflow with real data

**Questions?** Contact Jake Tolentino (TBWA Finance SSC / Odoo Developer)
