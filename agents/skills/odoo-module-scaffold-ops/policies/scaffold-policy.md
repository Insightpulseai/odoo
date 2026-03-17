# Module Scaffold Policy

## Naming Rules

- All custom modules must start with `ipai_` prefix
- Pattern: `ipai_<domain>_<feature>`
- Domain must be a recognized business domain (finance, ai, auth, bir, hr, crm, etc.)
- Feature must be specific and descriptive
- No generic names like `ipai_utils` or `ipai_common` without justification

## OCA-First Rule

- Before scaffolding a new module, check if OCA provides equivalent functionality
- If OCA module exists: create a thin `ipai_*` bridge/override, not a full reimplementation
- Document why OCA alternative was insufficient if creating from scratch

## Manifest Requirements

- Version: `19.0.x.y.z` (always starts with 19.0)
- License: `LGPL-3` (CE-only rule)
- Dependencies: minimal and explicit (no transitive dependency assumptions)
- Data order: security groups -> ACLs -> data -> views
- No Enterprise module dependencies
- No odoo.com IAP dependencies

## Quality Gates

- Module must install cleanly in disposable test database
- `ir.model.access.csv` must be present with all 4 CRUD columns
- Model classes must follow attribute order per odoo19-coding.md
- Module must not conflict with existing IPAI or OCA modules

## Location Rules

- Custom modules: `addons/ipai/` only
- Never place modules at addons root
- Never place modules in addons/oca/ (that is vendor territory)
- Never modify vendor/odoo/ addons
