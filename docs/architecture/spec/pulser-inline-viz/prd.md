# PRD — Pulser Inline Visualization Engine
**Product:** InsightPulseAI (IPAI) — Pulser Agent Platform
**Feature:** Inline chart, KPI card, and data visualization output
**Version:** 1.0.0
**Date:** 2026-04-15
**Owner:** Jake Tolentino (Founder/CTO, InsightPulseAI)
**Status:** APPROVED — spec-kit bundle

---

## Problem statement

Pulser agents (Tax Guru, Bank Recon, AP Invoice, Finance Close, Doc Intel, Pulser) currently
return text-only responses. The Ask Ces and Suqi Analytics web apps (Vercel — deprecated)
demonstrate that users want inline chart rendering, KPI cards, competitive insight panels,
and sparkline trend views directly inside their workspace — not as separate dashboard tabs.

The parity target: **whatever Ask Ces and Suqi Analytics show on screen, Pulser must be
able to produce inline** — in Microsoft Teams (Adaptive Cards), in Odoo chatter
(QWeb HTML), and in the ops-console web app (React).

---

## Goals

1. Pulser agents emit structured `viz_payload` JSON alongside text answers.
2. Three render targets consume identical payloads: Teams, Odoo, ops-console.
3. Chart types: line, bar, grouped bar, donut, sparkline, KPI card, insight pill.
4. Data sources: `ipai-odoo-mcp` (Odoo), Scout tables (pg-ipai-odoo platform schema),
   Ces campaign tables, Databricks Gold via Fabric.
5. Zero new infrastructure: reuse `ipai-copilot-resource` (Foundry Code Interpreter),
   `stipaidevagent` (chart PNG/SVG blob storage), `sb-ipai-dev-sea` (async render queue).
6. Render pipeline SLA: < 3 seconds for KPI cards, < 8 seconds for chart PNGs.

---

## Non-goals (v1.0)

- Native Power BI embed (use Fabric Data Agent MCP instead — separate feature)
- Mobile Odoo app chart rendering
- Real-time streaming chart updates (polling only in v1)
- D3 choropleth geographic maps (v2)

---

## Users and surfaces

| User | Surface | Primary need |
|---|---|---|
| Khalil Veracruz (Finance Director) | Teams + Odoo | Period-close KPI summary inline |
| Finance team (TBWA\SMP) | Teams bot | DSO/DPO sparklines in chat |
| TBWA account planners | Ask Ces web app | Campaign SOV bar charts, Lions pipeline |
| Retail intelligence team | Suqi Analytics | Transaction trend lines, brand share donut |
| Jake (CTO) | ops-console | All agent run metrics + Odoo health |

---

## Success metrics

| Metric | Target |
|---|---|
| KPI card render time (p95) | < 3 seconds end-to-end |
| Chart PNG render time (p95) | < 8 seconds end-to-end |
| Payload schema validation pass rate | 100% |
| Teams Adaptive Card render compatibility | Teams Desktop + Web + Mobile |
| Odoo chatter render compatibility | Odoo 18 CE web client |
| Chart types covered | 7 (line, bar, grouped bar, donut, sparkline, KPI card, insight pill) |
| Agent integration coverage | 6/6 (all provisioned agents) |

---

## Constraints

- Azure-native only: no Vercel, no Cloudflare, no n8n
- All secrets in `kv-ipai-dev-sea`
- Chart outputs stored in `stipaidevagent` blob, served via AFD `afd-ipai-dev`
- Foundry Code Interpreter: `ipai-copilot-resource`, project `ipai-copilot`, East US 2
- PG Flex: `pg-ipai-odoo`, host `pg-ipai-odoo.postgres.database.azure.com`
- CI/CD: Azure Pipelines only — GitHub Actions FORBIDDEN
- OCA-first module hierarchy; `ipai_*` delta modules only where CE+OCA cannot cover
