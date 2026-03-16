# Constitution: odoo-settings-as-code

> Non-negotiable governance rules for this feature.
> Any implementation that violates a rule here is invalid regardless of other merits.

---

## Rules

### R-01 — Config YAML is SSOT, Odoo DB is derived
The Odoo DB `ir.config_parameter` table is a **cache** of the YAML file.
If they differ, the YAML wins. The DB is updated by `apply_settings.py`.

### R-02 — No secrets in YAML
`config/odoo/settings.yaml` must contain only key names and non-secret values.
Passwords, tokens, and API keys are always `${ENV_VAR}` placeholders or absent.
CI must enforce this with a secret-scan step.

### R-03 — Odoo is never the identity SSOT
`auth_signup.invitation_scope` must be `"b2b"` (invitation-only) in all environments.
Supabase Auth owns the invite flow. No Odoo setting may re-enable free signup.

### R-04 — No module toggles in settings.yaml
Settings that install modules belong in `config/odoo/desired_modules.yml`.
`settings.yaml` manages only `ir.config_parameter` values.

### R-05 — Idempotent apply
`apply_settings.py` must be safe to run multiple times.
It reads current values, diffs, and only writes parameters that differ.
It never deletes a key not in its managed set.

### R-06 — Verify after apply
Every apply run must be followed by a verification pass that reads back the values
and confirms they match the desired state. Exit 1 if any mismatch.

### R-07 — web.base.url must match DNS SSOT
`web.base.url` in `settings.yaml` must equal the `erp` subdomain in
`infra/dns/subdomain-registry.yaml`. If they diverge, CI fails.
