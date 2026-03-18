# Evals — odoo-xml-structure-check

| Dimension | Threshold | Pass criteria |
|-----------|-----------|--------------|
| Accuracy | 0.95 | Correctly identifies file naming violations, XML ID pattern violations, deprecated tree views, and ACL format issues |
| Completeness | — | All XML dimensions evaluated — file naming, XML IDs, formatting, manifest ordering, Odoo 19 deprecations, ACL format |
| Safety | 0.99 | Never approves deprecated tree views in Odoo 19 code; never approves ACL files with missing CRUD columns |
| Policy adherence | — | Violations mapped to correct convention rule; Odoo 19 breaking changes (tree→list, groups_id→group_ids) always flagged |
| Evidence quality | — | Every violation includes file path, line number, the offending XML, and the expected correction |
| Upgrade safety | — | Odoo 19 specific deprecations identified with blocking/non-blocking classification |
