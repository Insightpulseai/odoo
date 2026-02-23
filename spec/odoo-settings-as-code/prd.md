# PRD: odoo-settings-as-code

## Problem

Odoo settings drift silently between environments. A checkbox toggled in the Odoo UI
does not appear in git. There is no way to reproduce a production configuration from
the repo alone. Onboarding a new environment requires manual UI work.

## Goal

Every Odoo `ir.config_parameter` value that matters for platform governance is stored
in a YAML file, applied by an idempotent script, and verified by CI.

## Out of scope

- Odoo module install state (handled by `desired_modules.yml` + `install-ce-apps.sh`)
- Mail server configuration (handled by `mail_settings.yaml` + `apply_mail_settings.py`)
- Identity / auth provider configuration (handled by `auth_providers.yaml` + `apply_auth_providers.py`)
- Enterprise / IAP features (CE-only stack)

## Success criteria

1. `config/odoo/settings.yaml` contains all managed config parameters.
2. `scripts/odoo/apply_settings.py --dry-run` exits 0 in a fresh install (no diff).
3. `scripts/odoo/apply_settings.py --verify-only` exits 0 in production.
4. CI gate (`odoo-settings-guard.yml`) blocks secrets in `settings.yaml`.
5. `web.base.url` in `settings.yaml` equals the `erp` subdomain in DNS SSOT.
6. `auth_signup.invitation_scope = "b2b"` is enforced and cannot be overridden without
   a spec change.

## Non-functional requirements

- Apply script must complete in < 10 seconds (only writes changed values).
- No new Python dependencies beyond stdlib + `pyyaml` + `xmlrpc.client` (both already present).
