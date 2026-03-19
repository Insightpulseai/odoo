# Production DB Runtime Fix — 2026-03-13

## Summary

Fixed broken Odoo login page at `erp.insightpulseai.com`. Two root causes:

1. **Missing `db_name` in Azure config**: `config/azure/odoo.conf` relied on an `ODOO_DB` env var that was never set in ACA and isn't a standard Odoo Docker entrypoint mapping. Without `db_name` or `dbfilter`, Odoo redirected to `/web/database/selector` which showed "database manager disabled" (due to `list_db=False`).

2. **Missing `web.base.url`**: Azure Front Door forwarded the ACA internal FQDN as the Host header, causing Odoo to auto-detect the wrong base URL for assets.

## Changes Applied

### Config Files (committed to main)

| File | Change |
|------|--------|
| `config/azure/odoo.conf` | Added `db_name = odoo`, `dbfilter = ^odoo$`, `web.base.url = https://erp.insightpulseai.com` |
| `config/prod/odoo.conf` | Changed `odoo_prod` → `odoo` for db_name and dbfilter |
| `infra/azure/modules/front-door.bicep` | Added optional `originHostHeader` override |
| `infra/azure/parameters/front-door-prod.parameters.json` | Added `originHostHeader: erp.insightpulseai.com` to odoo-web origin |

### ACA Runtime (applied live)

| Change | Detail |
|--------|--------|
| Container command | Updated from `-d odoo_prod` to `-d odoo --db-filter '^odoo$'` |
| Active revision | `ipai-odoo-dev-web--0000020` with 100% traffic |
| Old revisions | `0000015`, `0000017`, `0000018`, `0000019` deactivated |

## Verification Results

| Check | Result |
|-------|--------|
| `/web/health` | HTTP 200 |
| `/web/login` | HTTP 200 (was 303 redirect before fix) |
| CSS bundle (`web.assets_frontend.min.css`) | HTTP 200, 478KB |
| Lazy JS bundle (`web.assets_frontend_lazy.min.js`) | HTTP 200, 1.8MB |
| Minimal JS bundle (`web.assets_frontend_minimal.min.js`) | HTTP 500 (pre-existing asset compilation issue) |
| Session info | Valid, CSRF tokens functional |
| Fresh login POST | HTTP 200 with valid CSRF |
| Favicon | HTTP 200 |

## Residual Issues

1. **`web.assets_frontend_minimal.min.js` returns 500**: This is an asset compilation defect, likely caused by a broken JS/QWeb/SCSS file in an installed addon. Not related to the DB routing fix.

2. **`odoo_prod` database still exists**: Contains legacy production data. Must be compared against `odoo` before deletion.

3. **Key Vault password mismatch**: `odoo-pg-password` secret in Key Vault doesn't match the PG server admin password. Needs alignment.

## Commits

- `5e79173441` — fix(deploy): add web.base.url and originHostHeader for Azure Front Door
- `b47f87cc97` — fix(deploy): add db_name to Azure odoo.conf
- `38e504d7fc` — fix(deploy): correct db_name to 'odoo' per canonical database model
