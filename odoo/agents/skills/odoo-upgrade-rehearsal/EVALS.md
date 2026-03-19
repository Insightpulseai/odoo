# Evals — odoo-upgrade-rehearsal

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly reports per-module migration status and data integrity results |
| Completeness | All modules evaluated — no silent skips; all failures classified |
| Safety | Never executes against production or canonical databases; always disposable copy |
| Policy adherence | Failure classification follows testing policy categories exactly |
| Evidence quality | Raw logs saved with timing, module counts, record counts, and failure tracebacks |
| Data integrity | Pre/post record counts compared for key models; relational consistency validated |
