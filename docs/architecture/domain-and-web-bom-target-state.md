# Domain & Web Bill of Materials — Target State

> **Locked:** 2026-04-15
> **Authority:** this file for domain/web target state.
> **Companion:** [`docs/architecture/azure-bom-target-state.md`](./azure-bom-target-state.md) (Azure resource target state)
> **Doctrine:** **one shared Azure web platform serving four domains.** Not four unrelated deployments.

---

## Domain role map

```
www.insightpulseai.com       = primary brand + product marketing root
erp.insightpulseai.com       = authenticated product ingress + product landing
prismalab.insightpulseai.com = vertical tool/app microsite (interactive product, not brochure)
www.w9studio.net             = booking / commerce microsite
```

---

## Runtime classes (2 only)

The real architectural split is **two runtime classes**, not four:

| Class | Used by | Characteristic |
|---|---|---|
| **A — content / marketing** | `www.insightpulseai.com`, `www.w9studio.net` | SSR/static, forms → shared API |
| **B — interactive / product** | `erp.insightpulseai.com`, `prismalab.insightpulseai.com` | Public shell + authenticated or anonymous product backend |

---

## Shared edge BOM (one for all four domains)

| Item | Target | Note |
|---|---|---|
| Azure Front Door Premium | 1 | global entry, routing, TLS, WAF, redirects, caching |
| WAF policy | 1 | host/path-specific rules |
| Custom domains | 4 | `www.insightpulseai.com`, `erp.insightpulseai.com`, `prismalab.insightpulseai.com`, `www.w9studio.net` |
| Managed certs | 4 | via AFD (preferred) or ACA where AFD can't reach |
| Diagnostics | 1 | shared sink to Log Analytics + App Insights |

Cloudflare → Azure DNS transition remains; Azure DNS is authoritative, Front Door is the application edge.

---

## Shared platform BOM

| Item | Target |
|---|---|
| Entra tenant | 1 authority |
| Auth app path | 1 (for `erp.insightpulseai.com` only) |
| Key Vault | 1 shared (`kv-ipai-dev`) for web/runtime secrets |
| Static asset storage | 1 shared boundary |
| Forms / queue / API layer | 1 shared — serves demo requests, booking inquiries, form submits, tool job submissions |
| App Insights | 3–4 (one per major surface family) |

---

## Shared delivery BOM

| Item | Target |
|---|---|
| Monorepo | 1 web workspace |
| CI/CD | Azure Pipelines only |
| Infra | Bicep-managed |
| Promotion path | preview → staging → prod |
| Release controls | gates + feature flags where needed |

---

## Surface-by-surface BOM

### 1. `www.insightpulseai.com` — company root

**Role:** primary brand + product marketing + conversion surface.

**Hosting:**
- lightweight SSR/static web app
- CMS-lite or content-in-repo
- public anonymous
- forms → shared API/queue

**BOM:**
```
1 web app/static surface
1 App Insights instance
shared edge/WAF/certs
shared forms backend
```

---

### 2. `erp.insightpulseai.com` — product ingress

**Role:** `public product shell + authenticated application entry`.

Today it looks marketing-led; target state is actual product boundary.

**Hosting:**
- public product shell (marketing + demo CTA)
- authenticated route → Odoo / Pulser runtime
- reverse-routed / session-aware edge behavior

**BOM:**
```
1 public web surface
1 authenticated ingress path
1 ACA-backed Odoo/Pulser runtime
1 App Insights instance
shared edge/WAF/certs
```

---

### 3. `prismalab.insightpulseai.com` — interactive vertical app

**Role:** tool-led vertical product surface — **not brochure**.

Live surface today exposes:
- Clarify Question
- Search PubMed
- PRISMA diagram
- Review type
- Ask PrismaLab AI
- No-account-required usage
- Export flow

**This upgrades PrismaLab from "microsite" to real app surface.**

**Hosting:**
- SSR/static marketing shell
- tool execution API (backend)
- optional retrieval / AI backend (grounded)
- export / result generation
- analytics funnel tracking

**BOM:**
```
1 web app surface (marketing shell + tool frontend)
1 backend API for tools
1 job/queue path for tool execution (async)
1 App Insights instance
optional AI Search + Foundry grounded retrieval
shared edge/WAF/certs
```

**PrismaLab internal split:**
```
marketing shell
+ free tool frontend
+ tool execution backend
+ optional grounded AI / retrieval layer
```

---

### 4. `www.w9studio.net` — booking microsite

**Role:** commercial booking + sales microsite.

Live today: studio descriptions, rate cards, shoot types, inquiry form.

**Hosting:**
- lightweight SSR/static site
- booking inquiry form flow
- optional calendar / inventory later (Odoo Appointment per [`addons/ipai/ipai_web_branding/data/appointment_types.xml`](../../addons/ipai/ipai_web_branding/data/appointment_types.xml))
- payment link or CRM handoff, not full custom commerce

**BOM:**
```
1 web app/static surface
1 booking API/form handler
1 CRM/queue handoff
1 App Insights instance
shared edge/WAF/certs
```

---

## Consolidation pattern

### Do **not**
- 4 separate app stacks
- 4 separate observability stacks
- 4 separate edge stacks
- 4 separate CI/CD pipelines with different conventions

### Do
- 1 edge
- 1 identity pattern
- 1 shared observability model
- 1 shared delivery model
- 4 app surfaces
- 2 runtime classes

---

## Desired Azure-side BOM (summary)

```
Edge:
  - 1 Azure Front Door Premium
  - 1 WAF policy
  - 4 custom domains

Runtime:
  - 1 ACA environment for product/runtime apps
  - 1 Odoo/Pulser runtime behind erp.insightpulseai.com
  - 1 PrismaLab tool runtime (ACA or smaller app)
  - 2 lightweight web surfaces (root + w9)

Shared services:
  - 1 Key Vault
  - 1 Log Analytics workspace family
  - 3-4 App Insights (per surface family)
  - 1 storage account for static/upload
  - 1 queue/API layer for forms/booking/demo/tool submissions

Delivery:
  - 1 Azure Pipelines web delivery lane
  - 1 Bicep web/edge module set
  - 1 tag contract (per ssot/azure/tagging-standard.yaml)
```

---

## Recommended repo mapping

```
web/
  apps/
    insightpulse-site/       # www.insightpulseai.com
    prisma-tools/            # prismalab.insightpulseai.com (tool frontend)
    w9-booking/              # www.w9studio.net
    erp-shell/               # erp.insightpulseai.com public shell

platform/
  forms/                     # shared form/demo submit API
  lead-routing/              # CRM handoff
  exports/                   # PrismaLab export generation

agent-platform/
  prisma-assistant/          # PrismaLab AI grounded retrieval

infra/
  azure/
    frontdoor/               # shared AFD + WAF
    web/                     # web app bicep modules
    aca/                     # ACA envs and apps
    monitoring/              # App Insights + LA
    tags/main.bicep          # canonical tag module
```

---

## Bottom line

```
www.insightpulseai.com       = root site (marketing)
erp.insightpulseai.com       = product ingress (interactive)
prismalab.insightpulseai.com = tool-backed vertical app (interactive)
www.w9studio.net             = booking microsite (marketing)

Desired BOM = one shared edge + two runtime classes + four domain surfaces
```

PrismaLab is an **interactive product surface**, not a microsite — because of the tool layer.

---

## Enforcement

- **Azure Policy:** forbids new hostnames outside the four canonical domains without an exemption.
- **Bicep validation:** every new web app must declare its surface (`system: web`, `domain: <canonical>`, `workload: marketing|erp-shell|prisma-tools|w9-booking`).
- **App Insights:** resources not tagged with `system=web` cannot route to the web App Insights family.
- **Azure Pipelines:** promotion gates per surface; PrismaLab + ERP gated with extra interactive-class checks.

---

*Last updated: 2026-04-15*
