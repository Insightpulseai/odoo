# Allowed Operations — Odoo CLI

## Read-only (always safe)

- `odoo --modules` — list available modules
- `odoo scaffold <name> <path>` — generate module skeleton
- `odoo cloc -d <db>` — count lines of code
- `odoo --version` — show version

## Controlled write (requires --stop-after-init)

- `odoo -d <db> -i <modules> --stop-after-init --no-http` — install modules
- `odoo -d <db> -u <modules> --stop-after-init --no-http` — update modules

## Testing (disposable databases only)

- `odoo -d test_<module> -i <module> --test-enable --stop-after-init --no-http`
- Database name must start with `test_`

## Blocked by default

- `odoo shell` — interactive REPL
- Long-running server mode (no --stop-after-init)
- Production database without ODOO_SAFE_ALLOW_PROD=1
- Direct SQL execution

## Database naming rules

| Database | Usage | Skill access |
|----------|-------|-------------|
| `odoo` | Production | Blocked unless ODOO_SAFE_ALLOW_PROD=1 + --stop-after-init |
| `odoo_dev` | Development | Allowed with --stop-after-init |
| `test_*` | Testing | Unrestricted (disposable) |
