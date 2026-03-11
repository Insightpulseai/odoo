[ROLE] Coding agent in cloud IDE/CI runner. Execute, test, deploy, validate end-to-end with no manual UI.
[GOAL] Turn `spec/mappings/concur_to_odoo19_ce_oca_ipai.yaml` into an executable build plan: modules, configs, ingestion, and validation.
[CONSTRAINTS] No UI steps; idempotent; validate against actual addons path and installed modules; mark unknowns as TODO.
[OUTPUT FORMAT]

1. Brief execution plan (3–5 bullets)
2. Apply commands
3. Test commands
4. Deploy/migration commands
5. Validation commands
6. Rollback strategy

Deliverables:

- Repo changes: IPAI glue skeleton modules + scripts
- Verification: Odoo module installability checks + smoke flows via RPC
