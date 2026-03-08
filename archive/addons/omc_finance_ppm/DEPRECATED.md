# DEPRECATED — omc_finance_ppm

> **Deprecated**: 2026-03-09
> **Replaced by**: `data/finance_seed/` (canonical seed CSVs + import scripts)

This archived Odoo 18 module (`omc_finance_ppm`) contained legacy XML seed data
for the Finance PPM WBS. It has been superseded by the normalized CSV-based seed
data at `data/finance_seed/`.

## Migration

| Old (archive) | New (canonical) |
|----------------|-----------------|
| `data/ppm_seed_finance_wbs_2025_2026.xml` | `data/finance_seed/03_project.task.month_end.csv` + `04_project.task.bir_tax.csv` |
| `data/ppm_seed_users.xml` | `data/finance_seed/update_tasks_after_import.py` |
| `data/project_data.xml` | `data/finance_seed/02_project.project.csv` |
| `data/logframe_seed.xml` | `data/finance_seed/01_project.tags.csv` |

Do not use any files from this directory for new deployments.
