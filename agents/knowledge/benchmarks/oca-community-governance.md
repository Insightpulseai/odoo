# OCA Community Governance — Benchmark Reference

## Source

OCA GitHub org pinned repos and odoo-community.org resources.

## Purpose

OCA repos and resources serve as the benchmark layer for upgrade, maintenance,
and repo governance — NOT runtime architecture or product SoR.

## Six Benchmark Surfaces

### 1. OpenUpgrade — Upgrade/Migration Path Benchmark

Open source upgrade path for Odoo. Provides migration scripts per module per
version jump. Used as the benchmark for assessing upgrade readiness, identifying
coverage gaps, and planning migration script inventory.

- Repo: `OCA/OpenUpgrade`
- Role: upgrade_path_benchmark

### 2. OCB (Odoo Community Backports) — Backport/Patch Discipline Benchmark

Community-maintained fork of Odoo core with backported fixes. Provides the
benchmark for deciding whether a change belongs in extension code (ipai_*) or
should be sourced from community-core backports.

- Repo: `OCA/OCB`
- Role: community_backport_benchmark

### 3. maintainer-tools — Maintainer Conventions and Repo Quality Benchmark

Tooling for OCA maintainers: manifest validation, README generation, pre-commit
hooks, CI configuration. Benchmark for repository quality standards and module
conformance gates.

- Repo: `OCA/maintainer-tools`
- Role: maintainer_conventions_benchmark

### 4. oca-github-bot — Repo Automation and CI Governance Benchmark

Bot that automates OCA repository workflows: branch creation, migration issue
generation, CI triggering, merge policies. Benchmark for understanding and
aligning custom CI/automation patterns.

- Repo: `OCA/oca-github-bot`
- Role: repo_automation_benchmark

### 5. repo-maintainer-conf — Branch/Series Standardization Benchmark

Configuration repository defining branch generation rules, series support
policies, and CI tooling requirements per Odoo version. Benchmark for
branch-series governance.

- Repo: `OCA/repo-maintainer-conf`
- Role: series_branch_standardization_benchmark

### 6. odoo-community.org docs/how-to/code — Community Documentation Reference

Published OCA documentation including coding guidelines, contribution workflows,
migration how-tos, and maintainer guides. Benchmark for community documentation
and implementation reference.

- Source: odoo-community.org
- Role: community_documentation_benchmark

## Canonical Split

| Domain | Benchmark source |
|--------|-----------------|
| Odoo.sh roles | Delivery persona benchmark |
| Odoo developer how-tos | Implementation skill benchmark |
| Odoo coding guidelines | Code-quality/eval benchmark |
| OCA repos + resources | Community maintenance, upgrade, and repo-governance benchmark |

## Persona Strengthening (Not New Personas)

OCA benchmark skills bind to existing Odoo personas rather than creating new ones:

| Persona | Strengthening from OCA benchmarks |
|---------|----------------------------------|
| odoo-developer | OpenUpgrade awareness, OCB-aware patch discipline |
| odoo-tester | Migration rehearsal, upgrade validation |
| odoo-release-manager | Series/branch readiness, migration issue readiness |
| odoo-platform-admin | Upgrade cutover/recovery discipline |
| odoo-delivery-judge | OCA conformance, upgrade safety, maintainer-quality gate |

## Cross-References

- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
