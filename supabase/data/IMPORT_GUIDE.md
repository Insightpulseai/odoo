# Month-End Closing Tasks Import Guide

## Overview

This directory contains seed data for 37 month-end closing tasks to be imported into Odoo Finance PPM module.

**Files**:
- `month_end_closing_tasks.csv` - CSV format for Odoo UI import
- `month_end_closing_tasks.sql` - SQL INSERT statements for direct database import

## Prerequisites

### 1. Finance PPM Module Installed
```bash
ssh root@159.223.75.148
docker exec -it odoo-core odoo -d odoo_core -u ipai_finance_ppm --stop-after-init
```

### 2. Project Created
Create "Month-end closing" project in Odoo:
- Navigate to: **Projects** → **Create**
- Name: `Month-end closing`
- Save

### 3. Finance Users Created
Ensure these users exist with correct email logins:

| Code | Name | Email | Role |
|------|------|-------|------|
| CKVC | Khalil Veracruz | ckveracruz@tbwaphilippines.com | Director |
| RIM | Rey Meran | rmeran@tbwaphilippines.com | Manager |
| BOM | Beng Manalo | bmanalo@tbwaphilippines.com | Supervisor |
| LAS | Amor Lasaga | alasaga@tbwaphilippines.com | Staff |
| RMQB | Sally Brillantes | sbrillantes@tbwaphilippines.com | Staff |
| JMSM | Joana Maravillas | jmaravillas@tbwaphilippines.com | Staff |
| JAP | Jinky Paladin | jpaladin@tbwaphilippines.com | Staff |
| JPAL | Jerald Loterte | jloterte@tbwaphilippines.com | Staff |
| JLI | Jasmin Ignacio | jignacio@tbwaphilippines.com | Staff |
| JRMO | Jhoee Oliva | joliva@tbwaphilippines.com | Staff |
| CSD | Cliff Dejecacion | cdejecacion@tbwaphilippines.com | Staff |

**Create users**:
1. Navigate to: **Settings** → **Users & Companies** → **Users** → **Create**
2. Fill in name, email (as login), and assign Finance Manager/User access rights
3. Repeat for all 11 users

## Import Method 1: Odoo UI Import (Recommended)

### Step 1: Navigate to Import Screen
1. Go to **Settings** → **Technical** → **Import/Export** → **Import**
2. Select model: **project.task** (Tasks)

### Step 2: Upload CSV
1. Click **Upload File**
2. Select `month_end_closing_tasks.csv`
3. Verify column mapping:
   - `name` → Task Name
   - `finance_code` → Finance Code
   - `finance_category` → Finance Category
   - `finance_deadline_type` → Finance Deadline Type
   - `reviewer_id/login` → Reviewer (by email)
   - `approver_id/login` → Approver (by email)
   - `prep_duration` → Preparation Duration
   - `review_duration` → Review Duration
   - `approval_duration` → Approval Duration
   - `project_id/name` → Project (by name)
   - `is_finance_ppm` → Is Finance PPM

### Step 3: Test Import
1. Click **Test** (dry run)
2. Verify no errors
3. Expected: 37 records to import

### Step 4: Execute Import
1. Click **Import**
2. Wait for completion
3. Verify success message

### Step 5: Verify Import
1. Navigate to: **Projects** → **Month-end closing**
2. Click **Tasks** smart button
3. Expected: 37 tasks visible
4. Filter by **Finance PPM Tasks** to see only Finance tasks
5. Verify task categories, reviewers, approvers are correctly assigned

## Import Method 2: Direct SQL Import

### Step 1: Copy SQL File to Server
```bash
scp data/month_end_closing_tasks.sql root@159.223.75.148:/tmp/
```

### Step 2: Execute SQL via Docker
```bash
ssh root@159.223.75.148
docker exec -i odoo-postgres psql -U odoo -d odoo_core < /tmp/month_end_closing_tasks.sql
```

### Step 3: Verify Import
```bash
docker exec odoo-postgres psql -U odoo -d odoo_core -c \
  "SELECT COUNT(*) FROM project_task WHERE is_finance_ppm = TRUE AND finance_category IS NOT NULL;"
```

**Expected output**: 37

## Task Categories Breakdown

| Category | Task Count | Description |
|----------|------------|-------------|
| Accruals & Expenses | 2 | Expense accruals and reconciliation |
| Payroll & Personnel | 4 | Payroll processing and benefits |
| Tax & Provisions | 4 | Tax calculations and provisions |
| Bank Reconciliation | 3 | Bank account reconciliations |
| AR/AP Reconciliation | 4 | Receivables and payables reconciliation |
| Fixed Assets & Depreciation | 3 | Asset register and depreciation |
| Journal Entries & Adjustments | 4 | Adjusting entries and revaluations |
| Financial Reporting | 5 | Financial statements and reports |
| GL Reconciliation | 4 | General ledger reconciliations |
| Month-end Close Process | 4 | Final review and period close |
| **Total** | **37** | |

## Approval Workflow

All tasks follow 3-stage workflow:
1. **Preparation**: Assigned to finance staff (1 day)
2. **Review**: Assigned to Supervisor/Manager (0.5 day)
3. **Approval**: Assigned to Manager/Director (0.5 day)

**Total per task**: 2 days (1.0 + 0.5 + 0.5)

## Post-Import Verification Checklist

- [ ] 37 tasks imported successfully
- [ ] All tasks linked to "Month-end closing" project
- [ ] All tasks have `is_finance_ppm = TRUE`
- [ ] Finance codes assigned correctly (CKVC, RIM, BOM, etc.)
- [ ] Reviewer IDs mapped to correct users
- [ ] Approver IDs mapped to correct users
- [ ] Durations set correctly (Prep=1.0, Review=0.5, Approval=0.5)
- [ ] All 10 task categories present
- [ ] No duplicate tasks

## Troubleshooting

### Error: Project "Month-end closing" not found
**Solution**: Create the project first via Odoo UI (see Prerequisites #2)

### Error: User with email 'xxx@tbwaphilippines.com' not found
**Solution**: Create the missing user (see Prerequisites #3)

### Error: Field 'finance_code' does not exist
**Solution**: Ensure Finance PPM module is upgraded successfully:
```bash
docker exec -it odoo-core odoo -d odoo_core -u ipai_finance_ppm --stop-after-init
```

### Import shows 0 records created
**Possible causes**:
1. CSV encoding issue (ensure UTF-8)
2. Column mapping mismatch (verify mappings in Step 2)
3. Duplicate detection (check if tasks already exist)

## Next Steps After Import

1. **Assign due dates**: Set month-end closing deadline and let system calculate prep/review/approval dates
2. **Enable cron jobs**: Activate Finance PPM cron job for daily task generation
3. **Configure notifications**: Set up Mattermost webhook for deadline alerts
4. **Create logframe links**: Link tasks to Finance Logframe objectives

## Related Documentation

- Finance PPM Module: `/addons/ipai/ipai_finance_ppm/README.md`
- BIR Schedule Seed Data: `/addons/ipai/ipai_finance_ppm/data/finance_bir_schedule_seed.xml`
- Deployment Summary: `/claudedocs/DEPLOYMENT_SUMMARY.md`
