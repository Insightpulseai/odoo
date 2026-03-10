# Finance Seed Data

Production-ready seed data for **Month-End Close**, **BIR Tax Filing**, and **Expense Management** projects.

## Quick Start

```bash
# Import all seed data via XML-RPC
python3 import_all.py <username> <password>

# Or use the shell wrapper
./import_finance_seed.sh
```

## Files

| File | Model | Records | Description |
|------|-------|---------|-------------|
| `01_project.tags.csv` | project.tags | 36 | Phase tags (I-IV) + Category tags + BIR form tags |
| `02_project.project.csv` | project.project | 2 | Month-End Close + BIR Tax Filing projects |
| `03_project.task.month_end.csv` | project.task | 36 | Month-end closing tasks organized by 4 phases |
| `04_project.task.bir_tax.csv` | project.task | 33 | BIR tax filings for 2026 with deadlines |
| `05_expense_categories.csv` | product.product | 18 | Expense categories (travel, meals, office, training, comms) |
| `06_approval_thresholds.csv` | *(reference)* | 11 | Approval rules by amount threshold (for ipai_approvals) |
| `update_tasks_after_import.py` | - | - | Post-import script to assign users |
| `import_finance_seed.sh` | - | - | Shell script to run full import |

## Import Sequence

```
1. Tags (phase + category + BIR form types)
2. Projects (Month-End Close, BIR Tax Filing)
3. Month-End Close tasks (36 tasks in 4 phases)
4. BIR Tax Filing tasks (33 tasks for 2026)
5. Expense Categories (18 products with can_be_expensed)
6. Approval Thresholds (11 rules — reference data, no Odoo model)
```

## Month-End Close Task Phases

| Phase | Tasks | Focus Area |
|-------|-------|------------|
| Phase I | 6 | Initial entries & Compliance (Payroll, Tax, Rent, Accruals) |
| Phase II | 6 | Accruals & Amortization (Corporate, Insurance, Treasury) |
| Phase III | 12 | WIP Management (Client Billings, CA Liquidations, OOP) |
| Phase IV | 12 | Final Adjustments (VAT, Reclassifications, Reports) |

## BIR Tax Filing Schedule (2026)

| Form | Frequency | Deadline |
|------|-----------|----------|
| 1601-C | Monthly | 10th of following month |
| 0619-E | Monthly | 20th of following month |
| 2550Q | Quarterly | 25 days after quarter end |
| 1601-EQ | Quarterly | Last day of month after quarter |
| 1702-RT | Annual | April 15 |

## Expense Categories (from Supabase consolidation)

| Group | Categories | GL Range |
|-------|-----------|----------|
| Travel | Airfare, Lodging, Ground Transport, Parking, Mileage | 6100-xx |
| Meals | Client, Team, Individual | 6200-xx |
| Office | Supplies, Computer, Software, Books | 6300-xx |
| Training | Courses, Conferences, Memberships | 6400-xx |
| Communications | Phone/Internet, Shipping | 6500-xx |
| Other | Miscellaneous | 6900-00 |

## Post-Import: Assign Users

After importing, run the update script to assign users:

```bash
python3 update_tasks_after_import.py \
  --url https://erp.insightpulseai.com \
  --db odoo \
  --user admin \
  --password YOUR_PASSWORD
```

Or use `--dry-run` to preview changes:

```bash
python3 update_tasks_after_import.py \
  --url https://erp.insightpulseai.com \
  --db odoo \
  --user admin \
  --password YOUR_PASSWORD \
  --dry-run
```

## User Assignments (from Spreadsheet)

| Phase | Preparer | Reviewer | Approver |
|-------|----------|----------|----------|
| Phase I | RIM | RIM/CKVC | CKVC |
| Phase II | BOM | RIM | CKVC |
| Phase III | JPAL/LAS | BOM/RIM | CKVC |
| Phase IV | JLI/RMQB/JAP/JRMO | JPAL/LAS/RIM | CKVC |
| BIR Tax | BOM | RIM | CKVC |

## Audit

Run the seed audit to validate completeness:

```bash
python3 scripts/finance_ppm_seed_audit.py
```

Expected thresholds: tags >= 36, projects >= 2, month-end tasks >= 36, BIR tasks >= 33, expense categories >= 18, approval rules >= 11.

## Related Files

- Module: `addons/ipai/ipai_finance_ppm/`
- Audit script: `scripts/finance_ppm_seed_audit.py`
- Archive (deprecated): `archive/addons/omc_finance_ppm/`
- Supabase seed (deprecated): `supabase/seeds/002_finance_seed.sql`
