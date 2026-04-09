# odoo-module-scaffolding

Creates new Odoo CE 19 module structure with correct directory layout, manifest, init files, security stubs, and README.

## When to use
- A new custom module is required for an ipai_* feature
- A spec bundle references a module that does not yet exist
- A PR introduces a new directory under addons/ipai/

## Key rule
Every new module must follow the `ipai_<domain>_<feature>` naming convention, use LGPL-3 license,
version `19.0.x.y.z`, and declare only CE-compatible dependencies. The manifest must be valid Python
and the security CSV must include all 4 CRUD columns.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo18-coding.md`
