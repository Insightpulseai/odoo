# odoo-shell-debug

Provides runtime debugging via Azure Container App shell access. Inspect container state, run Odoo shell commands, diagnose runtime issues.

## When to use
- Runtime issue requires container inspection
- Module installation state needs verification
- Database connection debugging
- ORM query investigation for diagnosis

## Key rule
Shell access is read-only on production. Never modify production data or install/uninstall modules via shell. Document every session.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-developer.md`
- `.claude/rules/infrastructure.md`
