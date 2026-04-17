# Vertical Boundaries — Capability, Runtime, and Delivery Split

> **Status**: canonical · **Last updated**: 2026-04-14 · **Authority**: SSOT for vertical ownership
>
> The IPAI platform is split into **three bounded capability domains** on top of **one shared platform spine**. Verticals differ by data models, runtimes, workflows, connectors, and output schemas — **not** by brand, design system, or agent runtime.

---

## 1. Doctrine

### One shared foundation, three verticals

```text
Pulser / Odoo Finance       = transaction vertical
Ads / Market Intelligence   = intelligence + activation vertical
Research / Strategy         = retrieval + synthesis vertical
```

Not:

```text
three brands with different colors
```

But:

```text
three bounded capability domains with different data models, runtimes, and delivery surfaces
on a single shared platform spine.
```

### Design system alignment

Tenant token overlays live at `design/foundations/tenants/*.tokens.json`. Mapping:

| Vertical                  | Token overlay        | Vertical key              |
| ------------------------- | -------------------- | ------------------------- |
| Pulser / Odoo Finance     | `pulser.tokens.json` | `pulser-odoo-finance`     |
| Ads / Market Intelligence | `ads.tokens.json`    | `ads-market-intelligence` |
| Research / Strategy       | `ipai.tokens.json`   | `research-strategy`       |

**Design system is shared**, not forked. Differences live in brand ramp, emphasis color, density/posture, component tone, and editorial feel — never in separate component libraries.

---

## 2. Vertical 1 — Pulser / Odoo Finance

**Role**: transaction + finance-agent vertical.

### Owns

- Odoo business objects and workflows
- Finance parity modules (account, AR, AP, bank reconciliation, fixed assets)
- Collections, dunning, aging
- BIR/tax automation (2307, eBIRForms, eFPS, ePAY, eAFS)
- Approvals tied to accounting truth
- Reconciliation agents, payment-match agents

### Canonical repos / directories

- `odoo`
- `agent-platform`
- `platform`
- `automations`

### Suggested paths

```text
odoo/addons/ipai/ipai_finance_*/
odoo/addons/ipai/ipai_bir_*/
agent-platform/finance/
platform/finance/
automations/finance/
```

### System of record

- `odoo` (Odoo DB)

### Do NOT put here

- Market-intel pipelines
- Ad-platform orchestration
- Research workspace corpus logic

---

## 3. Vertical 2 — Ads / Market Intelligence

**Role**: signal + activation + campaign-intelligence vertical.

### Owns

- AI Answer Share
- Digital Health
- Creator Graph
- Promo Radar
- Media / creative performance intelligence
- Microsoft Advertising + Meta + Google Ads connector layer
- Actioning into campaign workflows (pause, budget, audience)

### Canonical repos / directories

- `data-intelligence`
- `agent-platform`
- `platform`
- `automations`
- `web`

### Suggested paths

```text
data-intelligence/marketing/
agent-platform/marketing/
platform/advertising/
platform/customer-intelligence/
automations/advertising/
web/apps/ads-copilot/
```

### System of record

- `data-intelligence` — derived intelligence, enrichments, scores
- `platform` — normalized contracts, shared schemas
- `odoo` — **only** for commercial/project follow-through (billing, SOWs, receivables)

### Do NOT put here

- Finance ledger logic
- BIR workflows
- Generic research archive management as primary concern

---

## 4. Vertical 3 — Research / Strategy

**Role**: retrieval + synthesis + evidence-pack vertical.

### Owns

- Cited research assistant (LIONS-like)
- Evidence packs (PRISMA, systematic review, meta-analysis)
- Strategy briefs
- Workspace memory for planners / strategists
- Retrieval corpora and source governance
- PrismaLab-style structured review / research flows

### Canonical repos / directories

- `agent-platform`
- `platform`
- `web`
- `docs`
- `data-intelligence` — **only** for supporting semantic / index pipelines

### Suggested paths

```text
agent-platform/research/
platform/research/
web/apps/research-assistant/
docs/research/
data-intelligence/research-index/
```

### System of record

- `platform` — schemas, contracts, citation infrastructure
- `data-intelligence/research-index/` — indexed corpora
- Not `odoo`, unless a brief crosses the boundary into a commercial project or engagement artifact

### Do NOT put here

- Ad delivery logic
- ERP posting logic
- Production media execution logic

---

## 5. Shared platform spine (build once, not per vertical)

### Shared repos

- `platform`
- `agent-platform`
- `automations`
- `infra`
- `.github`
- `docs`

### Shared responsibilities

```text
platform/
  auth/
  tenants/
  exports/
  citations/
  audit/
  workspace-memory/

agent-platform/
  runtime/
  policies/
  safe-outputs/
  tool-registry/
  orchestration/

automations/
  schedulers/
  sync/
  reporting/
  refresh/

infra/
  azure/
  identity/
  pipelines/
  monitoring/
```

---

## 6. What stays shared vs. what is separated

### Shared (one implementation serves all three verticals)

- Auth (Entra ID, managed identity)
- Tenancy (`res.company` + tenant tokens)
- Agent runtime (Pulser custom engine + MAF)
- Policy / safe outputs (3-tier defense)
- Observability (Application Insights, Log Analytics)
- CI/CD (Azure Pipelines)
- Export contracts
- Memory primitives
- Citation infrastructure
- Design system foundations

### Separated (per-vertical implementation)

- Domain models
- Workflows
- UI apps (separate app bundles, shared Fluent components)
- Prompts / skills
- Source connectors
- Output schemas
- Tenant token overlays (brand ramp + posture)

---

## 7. Repo-aware one-line mapping

```text
Pulser Finance  -> odoo + agent-platform + platform + automations
Ads / Intel     -> data-intelligence + platform + agent-platform + web + automations
Research        -> agent-platform + platform + web + docs (+ supporting data-intelligence)
```

---

## 8. Anti-drift rules

Do **NOT** create:

- ❌ A separate repo per vertical
- ❌ A separate agent runtime per vertical
- ❌ A separate auth model per vertical
- ❌ A separate design system per vertical
- ❌ A separate CI/CD per vertical

Do create:

- ✅ **One shared platform spine**
- ✅ **Three domain verticals** on top of it
- ✅ **Three tenant token overlays** expressing visual/posture differences
- ✅ **Three UI app bundles** (or route bundles) consuming shared components

---

## 9. Cross-vertical handoffs

Verticals routinely hand artifacts to each other. These are the sanctioned paths:

| From → To                     | Artifact              | Handoff mechanism                                                       |
| ----------------------------- | --------------------- | ----------------------------------------------------------------------- |
| Research → Ads                | Strategy brief        | `platform/exports/` brief JSON → ads-copilot campaign seeder            |
| Ads → Pulser (Odoo)           | Campaign commercials  | `automations/sync/` posts media invoices into Odoo AP                   |
| Pulser (Odoo) → Ads           | Budget / spend caps   | `platform/advertising/` reads approved budgets, enforces at connector   |
| Research → Pulser (Odoo)      | Engagement proposal   | Brief → `sale.order` draft in Odoo CRM                                  |
| Ads → Research                | Campaign learnings    | `data-intelligence/research-index/` ingests post-campaign findings      |

**Rule**: all cross-vertical handoffs go through `platform/` contracts. No direct vertical-to-vertical imports.

---

## 10. Ownership & escalation

| Vertical                  | Primary owner       | Escalation domain                                |
| ------------------------- | ------------------- | ------------------------------------------------ |
| Pulser / Odoo Finance     | Finance platform    | Accounting truth, BIR compliance, audit          |
| Ads / Market Intelligence | Data platform       | Signal quality, connector SLAs, activation safety |
| Research / Strategy       | Knowledge platform  | Source integrity, citation accuracy, privacy     |
| Shared spine              | Platform engineering | Runtime, auth, observability, CI/CD              |

---

## 11. Cross-references

- `design/foundations/tenants/*.tokens.json` — tenant token overlays (3 verticals)
- `design/README.md` — design system doctrine
- `CLAUDE.md` §"Engineering Execution Doctrine" — reuse-first, thinnest `ipai_*` delta
- `CLAUDE.md` §"Cross-Repo Invariants" items 9, 12, 14 (Databricks governance, Power BI consumption, Stateless agents)
- `.claude/rules/ssot-platform.md` — SSOT platform rules
- Memory `feedback_yes_partial_no_layering_doctrine.md` — YES/PARTIAL/NO capability map
- Memory `feedback_four_plane_architecture_doctrine.md` — Transaction / Data / Agent / Delivery planes
- Memory `project_smartly_quilt_capability_strategy.md` — Smartly/Quilt wedge positioning

---

*This document is SSOT for vertical ownership. Changes require PR review by platform engineering.*
