# Evals — odoo-ci-validation

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies passing and failing status checks with proper classification |
| Completeness | All required checks evaluated — no silent skips |
| Safety | Never marks CI as passing when checks fail; never bypasses hooks |
| Policy adherence | Test failures classified per testing policy; uses GitHub Actions, not Odoo.sh |
| Evidence quality | Includes gh CLI commands, workflow run IDs, and test log excerpts |
| Blocker identification | Real defects flagged as blockers; env issues documented but non-blocking |
