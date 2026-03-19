# Evals — odoo-dev-to-staging-promotion

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly verifies CI status, developer evidence, and staging deploy state |
| Completeness | All promotion prerequisites checked — CI, evidence, blockers, rollback path |
| Safety | Never promotes with failing checks; never skips staging; rollback documented |
| Policy adherence | Requires developer persona evidence; uses GitHub PR flow and ACA |
| Evidence quality | Includes promotion trace, revision IDs, backup timestamps |
| Blocker identification | Open blockers surfaced and promotion halted until resolved |
