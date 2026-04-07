# W9 Studio — Wix-to-Azure/Odoo Salvage Matrix

> **Decision**: Wix is dead (deprecated 2026-04-02). This matrix classifies every Wix-origin asset.
> **Target**: Azure Container Apps (frontend) + Odoo 18 (system of record).

---

## Status Quo

| Surface | Where | Status |
|---------|-------|--------|
| Public landing page | `ipai-w9studio-dev` ACA, `w9studio.net` via AFD | **LIVE** (Fluent 2, no Wix deps) |
| DNS | Azure DNS zone `w9studio.net` | **LIVE** (NS cutover done) |
| Wix site | 6 sites under `jgtolentino.rn@gmail.com` | **DEAD** — revoke API keys |
| Wix Velo code | `/private/tmp/io.landing/src/` | **DISCARD** (empty stubs) |
| Wix types/config | `/private/tmp/io.landing/.wix/` | **DISCARD** |

---

## Salvage Classification

### KEEP — Reuse as-is

| Asset | Source | Target | Notes |
|-------|--------|--------|-------|
| Landing page HTML | `w9studio-fluent.html` (153 KB) | Already deployed to ACA | Fluent 2, zero Wix deps |
| Hero video | `hero.mp4` (5.3 MB) | ACA static serve | In container |
| Room renders | `render-{studio,lounge,dressing,meeting}.png` | ACA static serve | In container, used as OG image |
| Rate tables | Embedded in HTML (11 price points) | Odoo product catalog + HTML | Publish-safe, competitor names removed |
| Room/spec data | Embedded in HTML (442 sqm, 4 rooms) | Odoo resources + HTML | Dimension-normalized (24.15m x 18m) |
| FAQ intents | Embedded in HTML | Pulser grounding corpus | 10+ Q&A pairs |
| Booking form fields | `{name, email, phone, serviceNeeded, preferredDate, message}` | Odoo CRM lead form | Schema from `inquiries.jsw` |
| Pulser eval dataset | `agents/evals/w9-pulser/w9-pulser-eval-v1.jsonl` | Pulser CI/eval | 25 scenarios + 74-scenario user set |
| Pulser spec bundle | `spec/w9studio-pulser-assistant/` (4 files) | Pulser agent build | Constitution, PRD, plan, tasks |
| Copy patches | Memory: `project_w9studio_publish_readiness.md` | Content governance | Publish-safe assertions |
| OG/SEO metadata | In HTML `<head>` | Already live | OG, Twitter Card, JSON-LD, LLM meta |
| Google Sign-In client | `916601142061-f7j0sh49utn78fpm3oikr7eu72lrrpsa` | OAuth for W9 booking auth | W9 GCP project, web type |

### ADAPT — Light rework needed

| Asset | Source | Target | Adaptation |
|-------|--------|--------|------------|
| Inquiry form schema | `inquiries.jsw` field list | Odoo `crm.lead` fields | Map `serviceNeeded` → Odoo tag, `preferredDate` → lead field, drop wixData |
| Parallax/scroll logic | HTML `<script>` (requestAnimationFrame) | Keep in HTML | Already framework-free, no Wix deps |
| Section reveal animations | HTML IntersectionObserver code | Keep in HTML | Pure vanilla JS |
| Room card grid | HTML Fluent card components | Keep in HTML | Already Fluent 2 native |
| Contact form validation | HTML `required` + JS validation | Keep + wire to Odoo JSON-RPC | Replace `sendInquiry()` with Odoo endpoint |
| Payment provider logos | SVG icons in HTML | Keep in HTML | Already real brand logos (GCash, Maya, PayPal) |
| Google Calendar integration | `W9_CONFIG.google` in HTML | Wire to Odoo calendar | API key + OAuth flow |
| Floor plan interactive | HTML/CSS grid + hover states | Keep in HTML | Pure CSS, no Wix deps |

### REWRITE — Rebuild natively in Odoo/Azure

| Capability | Wix Origin | New Target | Notes |
|------------|-----------|------------|-------|
| Booking/inquiry capture | Wix Bookings + `W9Inquiries` collection | Odoo `crm.lead` + `calendar.event` | Odoo 18 CRM is the SoR |
| Availability display | Wix Bookings calendar widget | Odoo calendar API → HTML widget | Read Odoo resource availability |
| Room/package recommendation | Manual Wix page sections | Pulser assistant (AI) + Odoo product catalog | Agent-driven recommendation |
| Recurring booking workflow | Wix manual process | Odoo subscription / recurring events | `sale_subscription` or custom |
| Lead → Quote → Invoice | No Wix equivalent | Odoo CRM → Sale → Invoice pipeline | Native Odoo flow |
| Customer portal | Wix Members area | Odoo website portal | `/my/` routes |
| Email notifications | Wix Automations | Odoo mail templates + Zoho SMTP | `mail.template` on lead stage change |
| Pulser chat widget | Concept only | Azure Copilot Gateway → HTML embed | `ipai-copilot-gateway` ACA |

### DISCARD — Sunk cost, do not carry forward

| Asset | Path | Reason |
|-------|------|--------|
| Wix Velo page stubs | `src/pages/*.js` (12 files) | All empty `$w.onReady` boilerplate |
| Wix backend modules | `src/backend/*.jsw` (3 files) | `wixData` imports, Wix-specific runtime |
| Wix type definitions | `.wix/types/` (10+ dirs) | Wix Editor X type stubs |
| Wix config | `wix.config.json`, `jsconfig.json` | Wix CLI configuration |
| Wix package deps | `package.json`, `package-lock.json`, `node_modules/` | Wix dev dependencies |
| Old non-Fluent HTML | `w9studio.html` (30 KB) | Superseded by `w9studio-fluent.html` |
| Wix DNS coupling | `ns6.wixdns.net`, `ns7.wixdns.net` | Azure DNS is live |
| Wix API keys | Account `c169c522-...` | Revoke after this salvage |
| Wix MCP server | `mcp__wix__*` tools | No longer needed |
| `src/backend/permissions.json` | Wix backend permissions | Wix-specific ACL model |
| `src/backend/setupCollections.jsw` | Wix Data collection setup | Replaced by Odoo models |
| `src/backend/manageServices.jsw` | Wix Bookings service mgmt | Replaced by Odoo calendar/CRM |
| `src/backend/http-functions.js` | Wix HTTP endpoints | Replaced by Odoo controllers |

---

## Go-Forward Architecture

```
┌─────────────────────────────────────────────────┐
│                   Public Web                     │
│  w9studio.net → AFD → ipai-w9studio-dev (ACA)   │
│  Static HTML (Fluent 2) + Pulser widget embed    │
└──────────────────────┬──────────────────────────┘
                       │ JSON-RPC / REST
┌──────────────────────┴──────────────────────────┐
│               Odoo 18 (System of Record)         │
│  erp.insightpulseai.com                          │
│  CRM leads · Calendar · Products · Invoicing     │
│  ipai_google_workspace (Gmail addon)             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────┐
│              Azure Services                      │
│  Copilot Gateway · Key Vault · Document AI       │
│  Zoho SMTP · Azure DNS · AFD (TLS/WAF)          │
└─────────────────────────────────────────────────┘
```

---

## Minimal Rebuild Scope (6 items)

| # | Deliverable | Owner | Status |
|---|-------------|-------|--------|
| 1 | W9 landing page | ACA `ipai-w9studio-dev` | **DONE** — live at `w9studio.net` |
| 2 | Rates page | Embedded in landing page | **DONE** — 11 price points |
| 3 | Booking inquiry flow | Odoo CRM lead capture | **TODO** — wire HTML form → Odoo JSON-RPC |
| 4 | Pulser chat widget | Copilot Gateway embed | **TODO** — spec exists, runtime not wired |
| 5 | Odoo lead → quote workflow | Odoo CRM → Sale → Invoice | **TODO** — native Odoo config |
| 6 | Availability integration | Odoo calendar → HTML widget | **TODO** — read-only calendar API |

---

## Cleanup Actions

- [ ] Revoke Wix API keys for account `c169c522-8188-4fc5-a7c4-8dcce7700ef6`
- [ ] Remove `.wix/`, `src/`, `node_modules/`, `package*.json`, `jsconfig.json`, `wix.config.json`, `w9studio.html` from `/private/tmp/io.landing/`
- [ ] Remove Wix MCP server from Claude Code config (if configured)
- [ ] Archive Wix account (6 sites) — no active use after deprecation

---

*Created: 2026-04-02*
*Authority: This file supersedes all prior Wix migration plans.*
