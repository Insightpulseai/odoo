# Agent Rules — Canonical Map

> This document is the **repo SSOT** for agent governance artifacts.
> Local rule files (`~/.claude/rules/`) are **runtime projections**, not repo-owned truth.

---

## Architecture

```
Repo-owned (committed, reviewable, CI-gatable)
├── docs/kb/agent-skills/*/SKILL.md     ← agent skill definitions
├── config/addons.manifest.yaml          ← OCA module governance data
├── docs/agents/ODOO_CLOUD_DEVOPS_AGENT_SKILLS.md ← DevOps skill catalog
├── ssot/agents/rules-manifest.yaml      ← rule registry (machine-readable)
└── this file                            ← canonical map

Local projections (per-developer, not committed)
├── ~/.claude/rules/odoo19-coding.md     ← Odoo 19 coding conventions
└── ~/.claude/rules/oca-governance.md    ← OCA module governance rules
```

## Key Principle

**Repo artifacts are SSOT. Local rule files are projections.**

The `~/.claude/rules/` files are loaded automatically by Claude Code at session start.
They exist for agent ergonomics — not as the source of truth. If a rule file
contradicts a repo artifact, the repo artifact wins.

---

## Repo-Owned Artifacts

### SKILL.md Files (`docs/kb/agent-skills/`)

8 skill definitions following Microsoft Agent Framework SKILL.md convention:

| Skill | Category | Priority | Lines |
|-------|----------|----------|-------|
| `odoo-module-development` | backend | critical | ~344 |
| `odoo-orm-patterns` | backend | critical | ~456 |
| `odoo-views-and-actions` | backend | high | ~451 |
| `odoo-testing` | qa | high | ~135 |
| `odoo-frontend` | frontend | high | ~50 |
| `odoo-api-integration` | integration | high | ~66 |
| `oca-module-porting` | devops | medium | ~39 |
| `ipai-module-conventions` | platform | critical | ~60 |

### Addons Manifest (`config/addons.manifest.yaml`)

35 OCA repos, tiered 0–9, with must-have module lists, profiles, and bundles.
Machine-validated by `scripts/odoo/validate_addons_manifest.py`.

### DevOps Skills (`docs/agents/ODOO_CLOUD_DEVOPS_AGENT_SKILLS.md`)

Cloud DevOps skill catalog — monitoring, deployment, backup, scaling patterns.

---

## Local Projections

### `~/.claude/rules/odoo19-coding.md`

**Source**: Distilled from upstream Odoo 19 coding guidelines + repo conventions.
**Content**: Model class order, naming conventions, ORM rules, translation patterns, Odoo 19 breaking changes.
**Sync expectation**: Manual. Regenerate from upstream docs if Odoo 19 guidelines change.
**Not committed** because it applies to all Odoo projects, not just this repo.

### `~/.claude/rules/oca-governance.md`

**Source**: Distilled from OCA must-have lists + `config/addons.manifest.yaml`.
**Content**: Maturity levels, quality gates, porting workflow, adoption thresholds.
**Sync expectation**: Manual. Update when manifest changes materially.
**Not committed** because it applies to all Odoo projects, not just this repo.

---

## Sync Contract

| Artifact | Owner | Location | Sync |
|----------|-------|----------|------|
| SKILL.md files | Repo | `docs/kb/agent-skills/` | CI-gatable |
| Addons manifest | Repo | `config/addons.manifest.yaml` | CI-validated |
| DevOps skills | Repo | `docs/agents/` | Manual review |
| Coding rules | Local | `~/.claude/rules/odoo19-coding.md` | Manual, upstream-derived |
| OCA governance | Local | `~/.claude/rules/oca-governance.md` | Manual, manifest-derived |

If a local rule contradicts the repo, the repo wins. Period.
