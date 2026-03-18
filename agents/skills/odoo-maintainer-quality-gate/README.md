# odoo-maintainer-quality-gate

Judge skill — validate OCA module adoption against maintainer quality standards before inclusion in install baseline.

## When to use
- OCA module adoption is proposed
- addons.manifest.yaml is being updated
- Quality gate review for module inclusion

## Key rule
Stable minimum for production, Mature for critical path modules. Never adopt without
test install on a disposable database. Never adopt modules with Enterprise dependencies.
Every adoption must be documented in addons.manifest.yaml with repo, tier, and provenance.
This is a judge skill — elevated thresholds for accuracy (0.98) and policy adherence (0.99).

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
- `config/addons.manifest.yaml`
