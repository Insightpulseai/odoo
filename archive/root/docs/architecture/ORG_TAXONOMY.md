# Organization Repository Taxonomy

> SSOT: `ssot/github/org_repos.yaml`
> CI Guard: `.github/workflows/org-taxonomy-guard.yml`
> Last updated: 2026-03-05

---

## Tier System

| Tier | Label | Purpose | Naming Convention |
|------|-------|---------|-------------------|
| 0 | Governance / Templates | Org-wide policies, golden paths | `.github`, `template-*`, `planning-*` |
| 1 | Platform Primitives | Runtime services, infra, MCP | `odoo`, `ops-platform`, `mcp-*`, `agent-*`, `edge` |
| 2 | Operator UX | Internal tools, dashboards | `ops-*` |
| 3 | Product Apps | Customer-facing surfaces | `web-*`, `app-*`, `ui-*` |
| 4 | Experimental / Labs | Non-prod, learning, demos | `labs-*` |

## Naming Rules

1. **Boring names**: repo names describe function, not brand
2. **Prefix indicates tier**: `ops-` (operator), `labs-` (experimental), `web-` (marketing), `ui-` (design library)
3. **No abbreviations** unless universally understood (CRM, MCP, UI)
4. **Renames are tracked**: `pending_renames` in `org_repos.yaml` queues renames before execution

## Categories

| Category | Description |
|----------|-------------|
| `governance` | Org-wide policies, templates, roadmap |
| `primitive` | Core platform services (ERP, Supabase, MCP, agents) |
| `console` | Internal operator dashboards and tools |
| `product` | Customer-facing applications |
| `ui` | Design systems and component libraries |
| `lab` | Experimental, learning, demos |

## Data Classification

| Level | Description |
|-------|-------------|
| `public` | Open-source or marketing content |
| `internal` | Internal tooling, not customer data |
| `restricted` | Contains or accesses production data, secrets references, PII |

## Lifecycle States

| State | Description |
|-------|-------------|
| `active` | In production use |
| `incubating` | Under development, not yet production |
| `deprecated` | Scheduled for removal or archival |
| `archived` | Read-only, no further changes |

## What Gets Published

Only **deployable containers** are published to GHCR:

| Image | Source Repo | Status |
|-------|------------|--------|
| `ghcr.io/insightpulseai/odoo` | odoo | active |
| `ghcr.io/insightpulseai/ops-console` | ops-console | active |

Internal Python/TS libraries stay as `packages/` inside their parent repo until a second repo genuinely depends on them.

## CI Enforcement

The `org-taxonomy-guard.yml` workflow validates:

1. Every repo in `org_repos.yaml` has: `tier`, `category`, `lifecycle`, `data_classification`
2. No repo appears without all required fields
3. Category values match the allowed set
4. Tier values are 0-4

Validator: `scripts/ci/validate_org_taxonomy.py`
