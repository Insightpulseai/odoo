# Evals — odoo-transaction-safety

| Dimension | Threshold | Pass criteria |
|-----------|-----------|--------------|
| Accuracy | 0.98 | Correctly identifies all cr.commit(), raw SQL, context mutations, and undocumented sudo() calls |
| Completeness | — | All transaction-related patterns scanned — no silent skips |
| Safety | 0.99 | Never approves cr.commit() without explicit justification; never misses context mutation |
| Policy adherence | — | Violations mapped to correct guideline rule; migration vs business logic context correctly assessed |
| Evidence quality | — | Every violation includes exact file path, line number, and the offending code line |
| False negative rate | < 0.02 | cr.commit() and context mutation must never be missed |
| Context sensitivity | — | Correctly distinguishes migration scripts (where raw SQL may be acceptable) from business logic (where ORM is required) |
