# Evals — odoo-security-acl-rules

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Groups have correct hierarchy; ACL rows cover all models; record rule domains are valid |
| Completeness | Every model has at least one ACL row; all 4 CRUD columns present; multi-company rules where needed |
| Safety | No full CRUD to public/portal without justification; Portal/Internal exclusivity respected |
| Policy adherence | ACL ID pattern followed; security XML first in manifest; no core security file edits |
| Evidence quality | Install log and access test results on disposable DB captured |
| Upgrade safety | Security definitions are additive; no core group modifications |
