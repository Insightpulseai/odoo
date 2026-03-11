# Plan: odoo-settings-as-code

## Files

| File | Action | Status |
|------|--------|--------|
| `config/odoo/settings.yaml` | Create SSOT YAML | ✅ Done |
| `scripts/odoo/apply_settings.py` | Create idempotent XML-RPC applier | ✅ Done |
| `docs/contracts/ODOO_SETTINGS_CONTRACT.md` | Create C-15 contract | ✅ Done |
| `config/odoo/auth_providers.yaml` | Create OAuth provider SSOT | ✅ Done |
| `scripts/odoo/apply_auth_providers.py` | Create provider applier | ✅ Done |
| `spec/odoo-settings-as-code/` | This spec bundle | ✅ Done |
| `scripts/ci/check_settings_ssot_drift.sh` | Secret-scan CI gate | ⬜ Pending |
| `.github/workflows/odoo-settings-guard.yml` | CI workflow | ⬜ Pending |

## Architecture

```
config/odoo/settings.yaml          ← SSOT (edit this)
config/odoo/auth_providers.yaml    ← SSOT for OAuth providers
        │
        ▼
scripts/odoo/apply_settings.py     ← idempotent applier (XML-RPC)
scripts/odoo/apply_auth_providers.py
        │
        ▼
Odoo DB: ir.config_parameter, auth.oauth.provider  ← derived cache
        │
        ▼ (optional)
ops.platform_events (Supabase)     ← audit trail for setting changes
```

## Risks

| Risk | Mitigation |
|------|------------|
| Apply script sets a param that breaks Odoo | `--dry-run` shows diff before apply; verify step after |
| YAML checked in with a secret | CI secret-scan gate (R-02) |
| `web.base.url` diverges from DNS | CI guard compares `settings.yaml` vs `subdomain-registry.yaml` |
| OAuth provider model differs in Odoo 19 | `apply_auth_providers.py` does `fields_get` introspection and fails fast if schema mismatch |
