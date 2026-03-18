# odoo-security-acl-rules

Defines security groups, ACLs, and record rules for Odoo CE 19 module security.

## When to use
- A new model is created and needs access control definitions
- Access control changes are required for an existing module
- Multi-company record rules are needed
- A security audit flags missing ACLs on a model

## Key rule
Every model must have at least one ACL row in `ir.model.access.csv` with all 4 CRUD columns.
Portal and Internal User groups are mutually exclusive in Odoo 19. Security XML must be listed
first in `__manifest__.py` data section.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo19-coding.md`
