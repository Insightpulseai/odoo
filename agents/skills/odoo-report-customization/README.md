# odoo-report-customization

Customizes PDF reports, QWeb report templates, and operational print surfaces in Odoo CE 18.

## When to use
- A custom report layout or additional content is needed
- An existing report needs extra fields or sections
- A new printable document is required
- Report rendering needs fixing or reformatting

## Key rule
Always use inherited QWeb templates to extend existing reports. Never replace core report templates.
Use `t-esc` for escaped output and test rendering with actual data on a disposable database.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo18-coding.md`
