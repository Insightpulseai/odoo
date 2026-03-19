# Evals — odoo-code-review-judge

> Elevated thresholds — this is a judge skill and the primary quality gate.

| Dimension | Threshold | Pass criteria |
|-----------|-----------|--------------|
| Accuracy | 0.98 | Correctly identifies all coding guideline violations with correct rule citations |
| Completeness | — | All checklist categories evaluated — no silent skips across structure, Python, XML, transactions, extendability, exceptions, CSS, JS |
| Safety | 0.99 | Never approves code with cr.commit() without justification; never approves broad exception catches; never approves direct core patching |
| Policy adherence | 0.99 | All violations mapped to the correct guideline rule; Odoo 19 breaking changes flagged (tree→list, groups_id→group_ids) |
| Evidence quality | — | Every violation includes exact file path, line number, and the offending code line |
| False negative rate | < 0.02 | Critical violations (cr.commit, bare except, core patching) must never be missed |
| False positive rate | < 0.05 | Correct patterns must not be flagged as violations |
