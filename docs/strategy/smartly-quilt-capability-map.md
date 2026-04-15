# Smartly + Quilt Capability Map

> **Locked:** 2026-04-15
> **Memory anchor:** `project_smartly_quilt_capability_strategy.md`
> **Authority:** this file (canonical reference for Smartly/Quilt-led IPAI wedge)
> **Companion:** [`data-intelligence-vertical-target-state.md`](./data-intelligence-vertical-target-state.md) (broader vertical incl. Cannes Lions + dataintelligence.ro PH)

---

## Position

```
Two products on one stack:
  W9                              = Smartly-like wedge
  data-intelligence + agent-platform + PrismaLab = Quilt-like wedge
  Odoo                            = SoR underneath both
```

---

## Capability mapping

### Smartly-like wedge (W9 Studio commercial workflow)

| Smartly capability | IPAI surface | Anchor |
|---|---|---|
| Creative batch automation | W9 booking + production workflow | `www.w9studio.net` |
| Asset management | Odoo `documents` + Foundry Document Intelligence | `addons/ipai/ipai_document_*` |
| Performance feedback loop | Pulser feedback intel | `agent-platform/` |
| Cross-channel publishing | Meta CAPI + Odoo connectors | `addons/ipai/ipai_*_connector/` |
| Booking + scheduling | Odoo CE 18 `appointment` + OCA recurrence | `addons/ipai/ipai_web_branding/data/appointment_types.xml` |

### Quilt-like wedge (data intelligence + audience research)

| Quilt capability | IPAI surface | Anchor |
|---|---|---|
| Audience clustering | Databricks ML on `dbw-ipai-dev` | `data-intelligence/` |
| Cultural narrative mining | Foundry-grounded RAG over PH corpora | `agent-platform/prisma-assistant/` |
| Trend reports | Power BI / Fabric semantic model | TBD post PBI Pro procurement |
| Insight delivery | PrismaLab tool pattern | `prismalab.insightpulseai.com` |
| API for partners | FastAPI + Foundry agent service | `addons/ipai/ipai_ops_api/` |

---

## Phased build (60/120/180 day)

### 60 days
- Confirm W9 booking live (Odoo Appointment + Google Workspace calendar)
- Confirm PrismaLab tools live (PRISMA, PubMed search, PICO clarifier)
- 4-domain web platform consolidated per [`domain-and-web-bom-target-state.md`](../architecture/domain-and-web-bom-target-state.md)

### 120 days
- PH data intelligence wedge live (3–5 self-serve tools + grounded assistant)
- Pulser feedback intel feeding W9 production workflow
- Audience clustering ML pipeline on Databricks
- Power BI semantic model live (post trial→Pro)

### 180 days
- Azure SaaS multitenant pattern fully implemented
- Marketplace listing readiness
- Partner Center co-sell readiness
- Repeat-customer retention + telemetry

---

## Anti-pattern guard

- Don't replicate Smartly's adtech-platform integrations — we don't have the Meta/Google/TikTok Ads partnerships
- Don't replicate Quilt's audience-data partnerships — we don't have Brandwatch/Crimson Hexagon equivalents
- Build the **thinnest viable surface** that captures one pattern element each
- PH-localized first; multi-country expansion only after wedge proves out

---

## References

- [Smartly.io](https://www.smartly.io/)
- [Quilt.ai](https://www.quilt.ai/)
- See [`data-intelligence-vertical-target-state.md`](./data-intelligence-vertical-target-state.md) for extended set (Cannes Lions Marketing Assistant, dataintelligence.ro)

---

*Last updated: 2026-04-15*
