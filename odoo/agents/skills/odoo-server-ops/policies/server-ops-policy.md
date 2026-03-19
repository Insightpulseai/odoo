# Server Ops Policy

## Database Selection Rules

- `odoo_dev` for development (default for local/devcontainer)
- `odoo_staging` for staging rehearsal
- `odoo` for production (never accessed directly from dev machines)
- `test_<module>` for testing (disposable)
- Never use production database for development or testing

## Dev Mode Rules

- `--dev=xml,reload,qweb` for active development (auto-reload on code changes)
- Never use `--dev` flags in production
- `--dev=all` includes werkzeug debugger — never expose publicly

## Worker Configuration

- `--workers=0` for development (single-threaded, easier debugging)
- `--workers=2-4` for production-like local testing
- Production worker count determined by container resources
- `--proxy-mode` required when behind a reverse proxy (Azure Front Door)

## Addons Path Rules

- Core addons always first in path (vendor/odoo/addons or /opt/odoo/addons)
- IPAI custom addons second
- OCA addons third
- Never include paths that do not exist (causes startup warnings)
- Never modify vendor/odoo/ — upstream mirror is read-only

## Security

- Never expose Odoo dev server to public internet
- Never use `--db_password` with actual passwords in command line (use config file or env vars)
- `--list-db=False` in production to prevent database enumeration
