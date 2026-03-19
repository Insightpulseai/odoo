# Evals — odoo-core-backport-assessment

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies upstream and OCB fix status; correct generic vs project-specific classification |
| Completeness | All decision factors evaluated: upstream status, OCB status, change scope |
| Safety | Never proposes direct modification of vendor/odoo/; never proposes file copying from OCA |
| Policy adherence | Follows Config -> OCA -> Delta hierarchy; ipai_* only for truly project-specific needs |
| Evidence quality | Includes specific commit references, PR numbers, branch inspection results |
| Decision quality | Recommendation matches the decision tree with clear rationale |
