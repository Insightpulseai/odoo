# Evals — odoo-staging-validation

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly reports test pass/fail counts and classifies failures |
| Completeness | All modules tested — no silent skips; all failures classified |
| Safety | Never uses production database; disposable test DBs only |
| Policy adherence | Failure classification follows testing policy; evidence log cited |
| Evidence quality | Includes test command output, classification table, and log file path |
| Blocker identification | Real defects and regressions flagged as blockers with context |
