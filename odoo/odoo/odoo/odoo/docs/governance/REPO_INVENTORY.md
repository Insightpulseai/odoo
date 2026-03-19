# Repository Inventory

## Purpose

This document records the current repository estate and the desired classification for each repo.

Update this file whenever a repository is:
- created
- renamed
- reclassified
- archived
- restored

---

## Classification table

| Repo | Visibility | Desired type | Lifecycle | Owner | Canonical purpose | Action |
|---|---|---|---|---|---|---|
| .github | Private | control-plane | active | TBD | org-wide governance, templates, workflows | keep and harden |
| odoo | Public | runtime | active | TBD | ERP runtime and module delivery | keep and harden |
| web | Private | runtime | active | TBD | product web surfaces | keep and harden |
| infra | Private | control-plane | active | TBD | IaC and cloud infrastructure | keep and harden |
| ops-platform | Private | control-plane | active | TBD | Supabase control plane / SSOT / automations | keep and harden |
| lakehouse | Private | runtime | active | TBD | data/lakehouse platform | keep and harden |
| design-system | Internal | shared-library | active | TBD | tokens, components, brand assets | keep and harden |
| templates | Private | template | active | TBD | repo and starter templates | keep and harden |
| agents | Public | shared-library | active | TBD | reusable agent definitions/patterns | keep and harden |
| template-factory | Private archive | archive | archived | TBD | historical template factory work | document/archive |
| plugin-marketplace | Private archive | archive | archived | TBD | historical marketplace plugin concept | document/archive |
| plugin-agents | Private archive | archive | archived | TBD | historical agents plugin concept | document/archive |
| dev-environment | Private archive | archive | archived | TBD | historical dev environment repo | document/archive |
| ops-console | Private archive | archive | archived | TBD | historical ops console repo | review for migration |
| app-crm | Internal archive | archive | archived | TBD | historical CRM app repo | document/archive |
| learn | Private archive | archive | archived | TBD | historical learning repo | document/archive |
| fluent-owl | Internal archive | archive | archived | TBD | historical UI experiment repo | document/archive |
| roadmap | Public archive | archive | archived | TBD | historical roadmap repo | replace with org projects/docs |
| mcp-core | Internal archive | archive | archived | TBD | historical MCP core repo | review for migration |
| fin-ops | Internal archive | archive | archived | TBD | historical fin-ops repo | review for migration |
| app-landing | Internal archive | archive | archived | TBD | historical landing repo | document/archive |
| demo-repository | Private archive | archive | archived | TBD | GitHub demo repo | document/archive |

---

## Cross-reference

This inventory aligns with `docs/architecture/ORG_TAXONOMY.md` (tier system) and the SSOT platform rules in `.claude/rules/ssot-platform.md`. The tier system defines operational tiers (0-4); this inventory defines governance classification (type + lifecycle).

| Tier (ORG_TAXONOMY) | Governance type (this doc) |
|---|---|
| Tier 0 — Governance/Templates | control-plane, template |
| Tier 1 — Platform Primitives | runtime |
| Tier 2 — Operator UX | runtime |
| Tier 3 — Product Apps | runtime |
| Tier 4 — Experimental/Labs | shared-library, archive |

---

## Rules

### Active repos
Every active repo must have:
- owner
- README
- taxonomy
- linkage to project system
- release classification if deployable

### Archived repos
Every archived repo must have:
- archive rationale
- note on whether canonical logic was migrated
- pointer to replacement repo/doc if applicable
