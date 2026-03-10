# Archive Manifest — data/finance_seed/

| Field | Value |
|-------|-------|
| **Original Path** | `data/finance_seed/` |
| **Archived At** | 2026-02-16 |
| **Reason** | superseded |
| **Canonical Replacement** | `data/seed/finance_ppm/tbwa_smp/` |
| **Branch** | `claude/deploy-finance-ppm-odoo19-LbLm4` |

## Archived Files

| File | Canonical Equivalent |
|------|---------------------|
| `01_project.tags.csv` | `data/seed/finance_ppm/tbwa_smp/tags.csv` |
| `02_project.project.csv` | `data/seed/finance_ppm/tbwa_smp/projects.csv` |
| `03_project.task.month_end.csv` | `data/seed/finance_ppm/tbwa_smp/tasks_month_end.csv` |
| `04_project.task.bir_tax.csv` | `data/seed/finance_ppm/tbwa_smp/tasks_bir_tax.csv` |
| `05_logframe.csv` | `data/seed/finance_ppm/tbwa_smp/logframe.csv` |

## Notes

These CSV files were created during the Finance PPM deployment on this branch.
They were superseded by the canonical seed root at `data/seed/finance_ppm/tbwa_smp/`
which adds a normalized `team_directory.csv` with Tier column and consolidates
all seed data under one SSOT location.

Content is identical to canonical — only the directory structure changed.
