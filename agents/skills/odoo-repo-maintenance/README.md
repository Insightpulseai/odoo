# odoo-repo-maintenance

Validate OCA addon repository conformance — manifest standards, CI configuration, pre-commit hooks, README generation.

## When to use
- New module added to addons manifest
- CI failure on OCA repository
- Maintainer review cycle
- pre-commit configuration update

## Key rule
Never modify OCA source directly. Modules below Stable maturity must not be used in
production. Submodule pins older than 30 days require justification. README must be
generated via oca-gen-addon-readme, never hand-edited.

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
