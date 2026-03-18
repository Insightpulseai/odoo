# Evals — odoo-staging-to-production-promotion

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly verifies all prerequisites and deployment state |
| Completeness | All checklist items evaluated — tester, admin, rollback, bake-time |
| Safety | Never deploys without backup; never skips bake-time; rollback documented |
| Policy adherence | Requires cross-persona evidence; uses ACA and Azure PG, not Odoo.sh |
| Evidence quality | Includes deployment trace, monitoring snapshots, bake-time metrics |
| Blocker identification | Bake-time failures trigger immediate rollback with evidence |
