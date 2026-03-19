# Archive Manifest — artifacts/data/ipai_finance_ppm_directory.csv

| Field | Value |
|-------|-------|
| **Original Path** | `artifacts/data/ipai_finance_ppm_directory.csv` |
| **Archived At** | 2026-02-16 |
| **Reason** | superseded |
| **Canonical Replacement** | `data/seed/finance_ppm/tbwa_smp/team_directory.csv` |
| **Branch** | `claude/deploy-finance-ppm-odoo19-LbLm4` |

## Notes

Original directory CSV had 5 columns: Code, Name, Email, Role, Company.
Canonical replacement adds a **Tier** column (Director, Senior Manager, Manager, Analyst)
and is located under the unified seed SSOT root.

Differences:
- Original: no Tier column
- Canonical: adds Tier column with values {Director, Senior Manager, Manager, Analyst}
- Content (9 employees): identical
- JPAL role: Finance Analyst (correct in both)
