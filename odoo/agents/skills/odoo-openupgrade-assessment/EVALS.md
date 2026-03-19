# Evals — odoo-openupgrade-assessment

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies per-module OpenUpgrade coverage status (covered/partial/missing) |
| Completeness | All installed modules evaluated — no silent skips |
| Safety | Never suggests skipping rehearsal; never treats partial coverage as full |
| Policy adherence | Custom ipai_* modules always flagged for manual assessment; rehearsal required before production |
| Evidence quality | Includes specific OpenUpgrade branch references, commit hashes, per-module script listings |
| Risk classification | Risk level matches actual gap severity — no understating critical gaps |
