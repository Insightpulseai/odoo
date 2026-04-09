# odoo-xml-structure-check

Verify XML files follow Odoo conventions — file naming, XML ID patterns, record formatting,
data file organization, and Odoo 18 specific rules.

## When to use
- XML file creation or modification
- View definitions (form, list, search, kanban)
- Data files (cron, sequences, templates)
- Security files (groups, ACLs, record rules)
- Manifest data key ordering review

## Key rule
Odoo 18 renamed `tree` to `list` globally. All new code must use `list`. XML IDs must
follow naming conventions (`_view_form`, `_view_list`, `_action`, `_menu`). Data files
in the manifest must be ordered: security groups, ACLs, data, views. ACL CSV files
must have all 4 CRUD columns with proper ID patterns.

## Cross-references
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `~/.claude/rules/odoo18-coding.md`
