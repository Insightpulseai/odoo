# Shell Ops Policy

## Safety Rules

- NEVER use `self.env.cr.commit()` — ORM manages transactions
- NEVER execute `self.env.cr.execute("DROP ...")` or any DDL
- NEVER mutate context directly — use `with_context()`
- Shell is for inspection and debugging, not bulk data modification
- Close shell cleanly after use (exit() or Ctrl+D)

## Database Access

- Shell operations only on odoo_dev and test_<module> databases
- Never open shell against odoo_staging or odoo from dev machines
- Use `--no-http` flag when running scripted shell (prevents port conflicts)

## Scripted Execution

- Prefer piping scripts via stdin over interactive shell for reproducibility
- Script output should be printed to stdout (not written to files without explicit paths)
- Scripts should be idempotent — safe to re-run without side effects

## Data Inspection Best Practices

- Use `search([], limit=10)` to avoid loading entire tables
- Use `read(['field1', 'field2'])` to limit field loading
- Use `mapped('field')` for extracting single fields from recordsets
- Use `filtered(lambda r: ...)` for in-memory filtering

## Logging

- Log shell script execution in evidence directory when part of debugging workflow
- Include database name and timestamp in logs
