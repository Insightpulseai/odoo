# Tasks: odoo-settings-as-code

## Completed

- [x] T-01 Create `config/odoo/settings.yaml` with managed config parameters
- [x] T-02 Create `scripts/odoo/apply_settings.py` (idempotent, dry-run, verify)
- [x] T-03 Create `docs/contracts/ODOO_SETTINGS_CONTRACT.md` (C-15)
- [x] T-04 Create `config/odoo/auth_providers.yaml` (Supabase OIDC only)
- [x] T-05 Create `scripts/odoo/apply_auth_providers.py`
- [x] T-06 Update `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` with C-15 and C-16

## Pending

- [ ] T-07 Create `scripts/ci/check_settings_ssot_drift.sh`
  - Secret-scan gate: fail if settings.yaml contains non-placeholder secret
  - web.base.url cross-check against DNS SSOT
- [ ] T-08 Create `.github/workflows/odoo-settings-guard.yml`
  - Triggers on `config/odoo/**` path
  - Runs T-07 script
  - Run `apply_settings.py --dry-run` against a test Odoo instance (if available)
- [ ] T-09 First apply to production
  ```bash
  ODOO_URL=https://erp.insightpulseai.com \
  ODOO_DB=odoo_prod \
  ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD \
  python scripts/odoo/apply_settings.py --dry-run
  # Review diff, then:
  python scripts/odoo/apply_settings.py
  ```
- [ ] T-10 First apply auth providers to production
  - Requires `ODOO_OIDC_SUPABASE_CLIENT_ID` + `ODOO_OIDC_SUPABASE_CLIENT_SECRET` in
    container env vars (set after Supabase OIDC app is created)
- [ ] T-11 Supabase OIDC app creation (depends on C-03 JWT Trust Contract)
  - Create OIDC provider entry in Supabase
  - Set `ODOO_OIDC_SUPABASE_CLIENT_ID` / `CLIENT_SECRET` in container
