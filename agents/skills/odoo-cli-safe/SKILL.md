# Odoo CLI Safe Skill

## Purpose

Run Odoo module operations (install, update, test) in non-interactive mode.
Designed for containerized Odoo 18 CE environments.

## Preconditions

- `odoo` binary available (inside container or on PATH)
- Database connection configured (env vars or odoo.conf)
- Target database exists and is accessible

## Allowed operations

### Read-only
- `odoo --modules` — list available modules
- `odoo scaffold <module>` — generate module skeleton
- `odoo cloc` — count lines of code

### Controlled write (always with --stop-after-init)
- `odoo -d <db> -i <modules> --stop-after-init --no-http` — install modules
- `odoo -d <db> -u <modules> --stop-after-init --no-http` — update modules
- `odoo -d <db> --init base --stop-after-init --no-http` — initialize database

### Testing
- `odoo -d test_<module> -i <module> --test-enable --stop-after-init --no-http`
- Test databases must use `test_` prefix (never prod/dev databases)

## Disallowed operations

- `odoo shell` — interactive REPL, not skill-compatible
- Long-running server without `--stop-after-init` (use deployment, not skill)
- Operations against `odoo` (prod) database without explicit confirmation
- Direct SQL execution
- `--database` pointing at production without `ODOO_SAFE_ALLOW_PROD=1`

## Output contract

- Module install/update logs to stdout
- Exit code 0 = success, non-zero = failure
- Check logs for `ERROR` or `CRITICAL` lines

## Verification contract

```bash
# After module install:
curl -sf http://localhost:8069/web/health
# Expected: HTTP 200

# After module install via Container App Job:
az containerapp job execution show -n <job> -g <rg> \
  --job-execution-name <exec> --query "properties.status" -o tsv
# Expected: "Succeeded"
```

## Odoo 18 API changes

### post_init_hook signature
Odoo 18 uses `post_init_hook(cr, registry)` signature.
The `cr` parameter is a database cursor.

```python
# Odoo 18
def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
```
