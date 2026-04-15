# Plan — Pulser Inline Visualization Engine
`.specify/plan.md`
Rev: 2026-04-15 | Status: READY FOR TASKS

---

## Tech stack

| Layer | Choice | Version |
|---|---|---|
| Language | Python | 3.12 |
| Agent framework | Microsoft Agent Framework (MAF) | latest |
| Foundry inference | Azure AI Foundry | `ipai-copilot-resource` |
| Chart generation | gpt-5.3-codex via Code Interpreter | — |
| Chart library (console/Odoo) | Chart.js | 4.4.1 (cdnjs) |
| Queue | Azure Service Bus | `sb-ipai-dev-sea` |
| Blob storage | Azure Blob Storage | `stipaidevagent` |
| Odoo module | Odoo 18 CE + OCA | 18.0 |
| Frontend | React + TypeScript | 18 + 5 |
| Schema validation | ajv CLI | 8.x |
| Testing | pytest + React Testing Library | — |
| CI/CD | Azure Pipelines | `azure-pipelines/` |

---

## Project structure

```
agent-platform/
  renderers/
    __init__.py
    foundry_renderer.py      # F-004: Code Interpreter → PNG → blob
    teams_renderer.py        # F-005: viz_payload → Adaptive Card JSON
    odoo_renderer.py         # F-006: viz_payload → QWeb HTML string
    console_renderer.py      # F-007: viz_payload → React prop JSON
    queue_worker.py          # F-008: Service Bus consumer
    viz_payload.py           # F-001: VizPayload dataclass + builder
    cli.py                   # pulser-viz CLI entry point
  tests/
    contract/
      test_viz_payload_schema.py
    unit/
      test_bank_recon_viz_payload.py
      test_finance_close_viz_payload.py
      test_tax_guru_viz_payload.py
      test_ap_invoice_viz_payload.py
      test_doc_intel_viz_payload.py
      test_pulser_viz_payload.py
      test_ces_viz_payload.py
      test_scout_viz_payload.py
      test_teams_renderer.py
      test_foundry_renderer.py
    integration/
      test_end_to_end_render.py
      test_queue_worker.py

platform/
  contracts/
    viz-payload.schema.json  # F-001: JSON Schema draft-07

odoo/addons/ipai/
  ipai_viz_chatter/          # F-006: Odoo delta module
    __manifest__.py
    models/
      viz_log.py             # log of viz renders in Odoo
    views/
      viz_log_views.xml
    static/
      src/
        js/
          viz_chatter.js     # Chart.js init in chatter
    templates/
      viz_templates.xml      # QWeb templates for all 7 viz_types
    security/
      ir.model.access.csv
    tests/
      test_viz_chatter.py

web/src/components/viz/      # F-007: React components
  VizRenderer.tsx
  KpiCardGrid.tsx
  LineChart.tsx
  BarChart.tsx
  GroupedBarChart.tsx
  DonutChart.tsx
  Sparkline.tsx
  InsightPills.tsx
  viz.types.ts               # TypeScript types mirroring viz_payload schema
  viz.test.tsx               # React Testing Library tests

infra/azure/agent/
  viz-renderer-job.bicep     # F-008: ACA Job for async renderer

azure-pipelines/
  viz-renderer.yml           # CI: schema validate → test → build → deploy
```

---

## Public contracts (CLI interfaces)

```bash
# Validate a payload against schema
pulser-viz validate --payload payload.json
# stdout: {"valid": true} | {"valid": false, "errors": [...]}

# Render for a specific target
pulser-viz render --payload payload.json --target teams    # → stdout: adaptive_card.json
pulser-viz render --payload payload.json --target odoo     # → stdout: html_string
pulser-viz render --payload payload.json --target chart    # → stdout: {"blob_url": "https://..."}

# Run the queue worker
pulser-viz worker --connection-string $SERVICE_BUS_CONN

# Health check
pulser-viz health  # → stdout: {"status": "ok", "foundry": "ok", "storage": "ok", "queue": "ok"}
```

---

## Phase sequence (strict — predecessor/successor)

```
Phase 0: Contract  →  Phase 1: Core  →  Phase 2: Renderers  →  Phase 3: Integration
```

**Phase 0 — Contract (prerequisite for all phases)**
- [ ] `viz-payload.schema.json` published
- [ ] Schema CI gate added to `viz-renderer.yml`
- SUCCESSOR: Phase 1

**Phase 1 — Core library**
- [ ] `viz_payload.py` — VizPayload dataclass, builder functions, emit()
- [ ] `build_viz_payload()` in all 8 agent skill modules
- PREDECESSOR: Phase 0
- SUCCESSOR: Phase 2

**Phase 2 — Renderers (parallel after Phase 1)**
- [ ] T-004: `foundry_renderer.py` + chart style tokens
- [ ] T-005: `teams_renderer.py` + Adaptive Card templates
- [ ] T-006: `ipai_viz_chatter` Odoo module
- [ ] T-007: React viz components
- PREDECESSOR: Phase 1
- SUCCESSOR: Phase 3

**Phase 3 — Async pipeline + integration**
- [ ] T-008: Service Bus queue worker + ACA Job
- [ ] Integration tests end-to-end
- PREDECESSOR: Phase 2 (all four renderers complete)

---

## Key design decisions

**Decision 1: Async render, not inline blocking**
Agents return text immediately. Chart generation (up to 8s) runs async via Service Bus.
Client polls `cosmos-ipai-dev` for `blob_url`. This keeps agent response latency < 1s.

**Decision 2: One payload, three renderers**
Teams, Odoo, and console consume identical `viz_payload`. No target-specific agent code.
Renderer selection happens in the queue worker based on `session.render_targets`.

**Decision 3: PNG for Teams, Chart.js for Odoo/console**
Teams Adaptive Cards render `Image` elements reliably via blob URL.
Odoo chatter and React console render Chart.js natively — no PNG needed, faster.
Foundry Code Interpreter only runs for Teams renders (or explicit `force_png` flag).

**Decision 4: Chart.js from cdnjs CDN in Odoo**
No webpack/bundler integration with Odoo 18 CE static pipeline needed.
Chart.js 4.4.1 UMD from `https://cdnjs.cloudflare.com` — CORS and CSP approved.

**Decision 5: IPAI design tokens in chart renderer**
All charts use TBWA-derived palette: black (#1A1A1A), yellow (#FFD100), teal (#1D9E75),
coral (#D85A30), blue (#378ADD). Enforced in `foundry_renderer.py` system prompt.

---

## Failure modes and mitigations

| Failure | Detection | Mitigation |
|---|---|---|
| Foundry Code Interpreter timeout | DLQ after 3 retries | Fallback: KPI text only, no chart |
| `stipaidevagent` upload fails | Exception in worker | Retry with backoff; DLQ after 3 |
| Teams Adaptive Card schema invalid | Teams rejects card | Fallback: plain text message |
| Odoo module install failure | `ir.module.module` error | Rollback migration; alert via App Insights |
| Service Bus queue depth > 1000 | Alert rule in `appi-ipai-dev-agent-sea` | Scale out worker ACA Job replicas |
| Schema validation failure | CI gate blocks deploy | Fix payload builder before merge |
