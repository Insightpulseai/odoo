# Evals — odoo-log-triage

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly classifies errors by category with proper root cause assessment |
| Completeness | All errors in time range evaluated — no silent skips |
| Safety | Secrets redacted from all log output; production log access documented |
| Policy adherence | Uses Azure Log Analytics, not Odoo.sh log viewer; classifies all errors |
| Evidence quality | Includes specific KQL queries or az CLI commands with sample output |
| Blocker identification | Critical errors flagged with actionable remediation steps |
