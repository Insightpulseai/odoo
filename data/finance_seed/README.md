# Finance Seed Data

Production-ready seed data for **Month-End Close** and **BIR Tax Filing** projects.

## Quick Start

```bash
# Option 1: Run import script (recommended)
./import_finance_seed.sh

# Option 2: Install Odoo module (includes holidays)
docker compose exec odoo-core odoo -d odoo_core -u ipai_finance_close_seed
```

## Files

| File | Model | Records | Description |
|------|-------|---------|-------------|
| `01_project.tags.csv` | project.tags | 36 | Phase tags (I-IV) + Category tags + BIR form tags |
| `02_project.project.csv` | project.project | 2 | Month-End Close + BIR Tax Filing projects |
| `03_project.task.month_end.csv` | project.task | 36 | Month-end closing tasks organized by 4 phases |
| `04_project.task.bir_tax.csv` | project.task | 33 | BIR tax filings for 2026 with deadlines |
| `update_tasks_after_import.py` | - | - | Post-import script to assign users |
| `import_finance_seed.sh` | - | - | Shell script to run full import |

## Import Sequence

```
1. Tags (phase + category + BIR form types)
2. Projects (Month-End Close, BIR Tax Filing)
3. Month-End Close tasks (36 tasks in 4 phases)
4. BIR Tax Filing tasks (33 tasks for 2026)
5. (Optional) Update tasks with user assignments
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

## Alternative: SQL Direct Update

For faster tag assignment without XML-RPC:

```sql
-- Connect to database
docker exec -i $(docker ps -q -f name=db) psql -U odoo -d odoo_core << 'SQL'

-- Assign Phase I tag to tasks with [I.
UPDATE project_task SET tag_ids = array_append(tag_ids,
  (SELECT id FROM project_tags WHERE name = 'Phase I: Initial & Compliance'))
WHERE name LIKE '[I.%';

-- Repeat for Phase II, III, IV...
SQL
```

## Troubleshooting

### "External ID not found"
Import in correct order: tags -> projects -> tasks

### Tags not appearing
Check if tags were created:
```sql
SELECT name FROM project_tags WHERE name LIKE 'Phase%';
```

### Users not found
Ensure users exist in Odoo with exact names. The update script uses `ilike` for partial matching.

## Related Files

- Module: `addons/ipai/ipai_finance_close_seed/`
- Original templates: `data/import_templates/`
- Scripts: `scripts/seed_finance_close_from_xlsx.py`
