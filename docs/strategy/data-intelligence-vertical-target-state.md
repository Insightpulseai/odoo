# Data Intelligence Vertical — Target State

> **Locked:** 2026-04-15
> **Authority:** this file (vertical strategy + competitive map)
> **Doctrine companion:** [`docs/strategy/smartly-quilt-capability-map.md`](./smartly-quilt-capability-map.md)
> **Memory anchor:** `project_smartly_quilt_capability_strategy.md`

---

## Position

```
Two products on one stack:
  W9                              = Smartly-like wedge (commercial booking, creative ops)
  data-intelligence + agent-platform + PrismaLab = Quilt-like wedge (research/audience intel + tools)
  Odoo                            = SoR underneath both
```

Build for **Azure partner integration later**. Every service we ship should be a candidate for the [Azure Partner Solutions](https://learn.microsoft.com/en-us/azure/partner-solutions/partners) catalog.

---

## Competitive reference set

| Reference | Role | What we adopt | What we don't |
|---|---|---|---|
| **Smartly.io** | Adtech / creative-ops automation | Workflow patterns, creative-batch UX, performance feedback loops | Their cost basis, ad-platform-only scope |
| **Quilt.ai** | Culture intelligence / audience research | Audience-mining patterns, LLM-grounded insight generation, narrative structure | Closed APIs, no Azure-native deployment story |
| **Cannes Lions Marketing Assistant** ([marketingassistant.lions.co](https://marketingassistant.lions.co/en)) | Industry-curated marketing knowledge assistant | RAG over a curated corpus, conversational UX, "ask the canon" pattern | Single-corpus lock-in |
| **dataintelligence.ro** | Romania data intelligence services | Service-tier packaging, PH-equivalent localization model | RO-only positioning |
| **PrismaLab (ours)** | Research-methods tool surface (PRISMA, PubMed, PICO, Cochrane) | Already shipped — see [`docs/architecture/domain-and-web-bom-target-state.md`](../architecture/domain-and-web-bom-target-state.md) | — |

---

## PH-localized "data intelligence" wedge

dataintelligence.ro shows the model: **service-led + tool-led + grounded-AI**, packaged for one country market.

Our PH version:

```
Domain:    data-intelligence.insightpulseai.com  (or dataintelligence.ph if domain available)
Surface:   PrismaLab pattern (interactive product) + curated corpora
Localization: PH-specific data sources (PSA, BSP, BIR, NEDA, DTI)
Pricing:   Service tier + Tool tier + AI tier
Auth:      Anonymous tools (no account) + paid API/export tier
Tech:      same Bicep/ACA/Foundry stack as PrismaLab
```

This is **not** a duplicate of PrismaLab — it's the broader-than-research analog (marketing, audience, business intelligence) for the PH market.

---

## Capability map (Smartly + Quilt + Cannes + dataintelligence.ro → IPAI)

### Smartly-like (commercial workflow automation)

| Smartly capability | IPAI surface | Anchor |
|---|---|---|
| Creative batch automation | W9 booking + production workflow | `www.w9studio.net` |
| Asset management | Odoo `documents` + Foundry Document Intelligence | `addons/ipai/ipai_document_*` |
| Performance feedback loop | Pulser agent feedback intel | `agent-platform/prisma-assistant/` |
| Cross-channel publishing | Meta CAPI + Odoo connectors | `addons/ipai/ipai_*_connector/` |

### Quilt-like (audience / culture intelligence)

| Quilt capability | IPAI surface | Anchor |
|---|---|---|
| Audience clustering | Databricks ML on `dbw-ipai-dev` | `data-intelligence/` |
| Cultural narrative mining | Foundry-grounded RAG over PH corpora | `agent-platform/prisma-assistant/` |
| Trend reports | Power BI / Fabric semantic model | TBD (PBI Pro post-trial) |
| Insight delivery | PrismaLab tool pattern | `prismalab.insightpulseai.com` |

### Cannes Lions Marketing Assistant-like (curated knowledge assistant)

| Cannes capability | IPAI surface | Anchor |
|---|---|---|
| RAG over curated marketing canon | Foundry + AI Search index over PH-localized corpus | `srch-ipai-dev` |
| Conversational UX | Pulser systray + chat surface | `addons/ipai/ipai_odoo_copilot` |
| Citation-first answers | PrismaLab "Ask PrismaLab AI" pattern | `prismalab.insightpulseai.com` |

### dataintelligence.ro-like (service + tool packaged for one market)

| Capability | IPAI surface |
|---|---|
| Service tier (consultancy) | InsightPulseAI advisory engagements |
| Tool tier (self-serve) | PrismaLab + future PH-localized tools |
| AI tier (grounded assistant) | Pulser + Foundry agent service |
| Localization | PH data sources, BIR/PSA/BSP integrations |

---

## Build sequence (Phase plan)

### Phase 1 — Confirm wedges (live, ~30 days from 2026-04-15)
- W9 booking microsite + Odoo Appointment (in flight, see [`docs/runbooks/zoho-bookings-to-odoo-cutover.md`](../runbooks/zoho-bookings-to-odoo-cutover.md))
- PrismaLab interactive surface live
- 4-domain web platform consolidated per [`docs/architecture/domain-and-web-bom-target-state.md`](../architecture/domain-and-web-bom-target-state.md)

### Phase 2 — PH data intelligence wedge (60–90 days)
- Stand up PH-localized tool corpus (PSA, BSP, BIR public datasets)
- Build 3–5 self-serve tools modeled on PrismaLab pattern (e.g. PH industry classifier, BIR rate calculator, PSA geographic explorer)
- Foundry-grounded "Ask PH Data Intelligence" assistant
- Service tier productization (engagement packages)

### Phase 3 — Azure partner-ready (120–180 days)
- All services architected for Azure SaaS multitenant pattern (per [`docs/architecture/multitenant-saas-target-state.md`](../architecture/multitenant-saas-target-state.md))
- Marketplace listing readiness (consumption metering, tenant isolation, MI auth)
- Partner Center co-sell readiness

---

## Anti-pattern guard

**Do not build:**
- A standalone Smartly clone (we don't have ad-platform integrations or budget)
- A standalone Quilt clone (we don't have the audience-data partnerships)
- Generic "marketing AI assistant" without a curated corpus
- A multi-country expansion before PH wedge proves out

**Do build:**
- The thinnest viable IPAI surface that captures one Smartly + Quilt + Cannes + dataintelligence.ro pattern element each
- PH-localized first
- Azure-native + partner-ready from day one

---

## Workspace identity inventory (current state, 2026-04-15)

| Workspace | Domain | Users | Notes |
|---|---|---|---|
| Zoho Workspace | `insightpulseai.com` | 2 active (`finance@`, `business@` aka Jake) | Mail SMTP authority per `mail_settings.yaml` |
| Google Workspace | `w9studio.net` | 1 active (W9 Studio admin) | Identity per `feedback_w9_google_workspace_integration.md`. Calendar/comms/docs |

Both feed the **interactive product surface** identity model in [`docs/architecture/domain-and-web-bom-target-state.md`](../architecture/domain-and-web-bom-target-state.md).

---

## References

- [Smartly.io](https://www.smartly.io/) — adtech wedge reference
- [Quilt.ai](https://www.quilt.ai/) — culture intelligence reference
- [Cannes Lions Marketing Assistant](https://marketingassistant.lions.co/en) — curated knowledge assistant pattern
- [dataintelligence.ro](https://dataintelligence.ro/) — service+tool+AI packaging reference (PH equivalent target)
- [Azure Partner Solutions](https://learn.microsoft.com/en-us/azure/partner-solutions/partners)
- [Azure SaaS multitenant architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)
- [Azure multitenant solution checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
- [Common Data Model](https://learn.microsoft.com/en-us/common-data-model/creating-schemas)
- [Azure Resource Manager management](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/)
- [Odoo Industries](https://www.odoo.com/es_ES/all-industries)
- [OCA repos](https://github.com/orgs/OCA/repositories)
- [Databricks PG dump-restore for OLTP projects](https://learn.microsoft.com/en-us/azure/databricks/oltp/projects/pg-dump-restore)

---

*Last updated: 2026-04-15*
