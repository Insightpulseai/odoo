# odoo-core-backport-assessment

Assess whether a change belongs in extension code (ipai_*) or community-core backport (OCB) — decision gate for patch vs extension.

## When to use
- Bug fix needed in core Odoo behavior
- Upstream fix exists but is not in the current version
- Community patch is proposed for adoption

## Key rule
Never modify `vendor/odoo/` directly. Prefer OCB backport for generic fixes, ipai_* override
for project-specific changes. Never copy OCA files into `addons/ipai/` — use `_inherit` overrides.

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
