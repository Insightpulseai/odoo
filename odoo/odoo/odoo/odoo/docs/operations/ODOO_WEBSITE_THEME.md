# Odoo Website Theme — Operations Runbook

> **SSOT**: `ssot/website/theme.yaml`
> **Apply**: `scripts/odoo/apply_website_theme.py`
> **Verify**: `scripts/odoo/verify_website_theme.sh`
> **Evidence**: `docs/evidence/odoo/theme_apply_<UTC-stamp>.json`

---

## Current state (2026-02-27)

| Website | ID | Theme | Status |
|---------|----|-------|--------|
| My Website | 1 | `cts_theme_rozz` (Theme Rozz) | Active |

---

## Apply (idempotent)

Port 8069 is firewalled externally. Run over SSH from the prod host:

```bash
ssh root@178.128.112.214 \
  "ODOO_URL=http://localhost:8069 \
   ODOO_DB=odoo_prod \
   ODOO_ADMIN_LOGIN=admin \
   ODOO_ADMIN_PASSWORD=<from keychain> \
   python3 /opt/odoo/repo/scripts/odoo/apply_website_theme.py --env prod"
```

**Dry-run** (no writes):

```bash
ssh root@178.128.112.214 \
  "ODOO_URL=http://localhost:8069 ODOO_DB=odoo_prod \
   ODOO_ADMIN_LOGIN=admin ODOO_ADMIN_PASSWORD=<pw> \
   python3 /opt/odoo/repo/scripts/odoo/apply_website_theme.py --env prod --dry-run"
```

Exit codes: `0` = no-op (already correct), `2` = dry-run diff found, `1` = error.

---

## Verify (frontend proof)

```bash
scripts/odoo/verify_website_theme.sh https://erp.insightpulseai.com
```

Asserts these markers are present in the homepage HTML:
- `about_theme_rozz`
- `services_theme_rozz`
- `cts_theme_rozz/static`

Exit `0` = PASS. Exit `1` = markers absent.

---

## Changing the theme

1. Edit `ssot/website/theme.yaml` — update `theme_module` (and `theme_id` hint).
2. Install the new theme module if not already installed:
   ```bash
   ssh root@178.128.112.214 "docker exec odoo-prod odoo \
     -c /etc/odoo/odoo.conf \
     --db_host=... --db_port=25060 --db_user=doadmin --db_password=<pw> \
     --db_sslmode=require -d odoo_prod \
     -i <new_theme_module> --stop-after-init --no-http"
   ```
3. Run the applier: `apply_website_theme.py --env prod`
4. Run the verifier: `verify_website_theme.sh`
5. Commit the updated SSOT file.

---

## Evidence artifacts

Each successful apply run writes a JSON artifact:

```
docs/evidence/odoo/theme_apply_<YYYYMMDDTHHMMSSZ>.json
```

Fields: `stamp`, `env`, `ssot_file`, `module` (id/name/state),
`before` (website_id/theme_id/theme_name), `after` (theme_id), `changed`.

---

## How the theme activation works

Installing a theme module (`odoo -i cts_theme_rozz`) registers it in
`ir.module.module` with `state=installed`. This does **not** automatically
apply it to a website — it just makes it available.

Activation requires writing `website.theme_id = <module_id>` on the
`website.website` record. Odoo CE 19 stores this as a Many2one to
`ir.module.module`. The write triggers Odoo's internal `_force_theme()`
which installs theme-specific views and assets.

The SSOT + apply script pattern prevents the common failure mode:
module installed but theme never activated (`theme_id = False`).

---

## Notes

- `website.theme_id` is a Many2one to `ir.module.module` (not `website.theme`)
  in Odoo CE 19. Do not use `website.theme` model (EE only).
- The applier script uses the same XML-RPC pattern as `apply_settings.py`.
- Port 8069 must not be exposed publicly — always use SSH tunnel or run
  the script directly on the server.
