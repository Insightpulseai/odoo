[ROLE] Coding agent in cloud IDE/CI runner. Execute, test, deploy, validate end-to-end with no manual UI.
[GOAL] Implement PH month-end close + tax compliance "pack" using Odoo 19 CE + OCA + minimal IPAI glue.
[CONSTRAINTS] No UI steps; use shell/scripts/configs/APIs; idempotent; do not invent module names—mark TODOs.
[OUTPUT FORMAT]

1. Brief execution plan (3–5 bullets)
2. Apply commands
3. Test commands
4. Deploy/migration commands
5. Validation commands
6. Rollback strategy

Scope:

- Use `spec/taxonomy/philippines_tax.yaml` as the locale overlay.
- Generate: tax schedules, completeness checks (tax tags, TIN presence), audit trail bundle.
- Prefer data templates + minimal glue modules rather than new ORM models.
