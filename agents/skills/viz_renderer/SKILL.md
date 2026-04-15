---
name: viz-renderer
description: >
  IPAI meta-skill for Pulser inline visualizations. Single payload-first contract
  (viz_payload JSON) consumed by all Pulser agents to emit charts, KPI cards, and
  insight pills. Three render targets: Teams Adaptive Cards, Odoo QWeb HTML,
  ops-console React. Use when any Pulser agent (Scrum Master, Finance PPM, BIR,
  Bank Recon, Scout, Ces, PrismaLab, Tax Guru) needs to emit inline data
  visualization. All domain skills depend on this meta-skill; none reimplement
  rendering.
---

# Viz Renderer — IPAI Meta-Skill

## Purpose

Meta-skill that owns the `viz_payload` contract and render pipeline. Every Pulser
agent that emits visualizations depends on this skill; none implement their own
renderer.

**Architecture:** one contract, three render targets, N emitting agents.

## Scope

- **Odoo version:** 18.0 CE (render target for `view_mode="list,form"`)
- **OCA-first:** yes — uses `ipai_odoo_copilot` chatter widget for Odoo render
- **`ipai_*` delta:** no — meta-skill lives at agent-platform layer
- **Azure resources:**
  - Foundry `ipai-copilot-resource` (East US 2) — `gpt-5.3-codex` via Code Interpreter for PNG/SVG generation
  - Blob `stipaidevagent` — chart artifact storage
  - Service Bus `sb-ipai-dev-sea` — async render queue (`viz-render` topic)
  - Key Vault `kv-ipai-dev-sea` — Teams/Odoo credentials
  - App Insights `appi-ipai-platform-sea` — render latency metrics
- **Agents served:**
  - `scrum_master` — sprint analytics
  - `tax_guru` — tax calc validation cards
  - `bank_recon` — reconciliation donuts + discrepancy pills
  - `finance_close` — D+5 progress tracker
  - `finance_ppm` — project profitability + cash flow
  - `ap_invoice` / `ar_collections` — aging buckets + DSO trends
  - `doc_intel` — extraction confidence KPIs
  - `scout_analytics` — brand share + SOV
  - `ces_campaign` — campaign KPIs + channel mix
  - `prismalab` — PRISMA flow + forest/funnel plots
  - `pulser` (orchestrator) — cross-domain dashboards

## Prerequisites

- [ ] `ipai-agent-platform` loaded (for MAF patterns)
- [ ] `ipai-resource-map` loaded (for Foundry/Blob/SB names)
- [ ] Spec bundle `spec/pulser-inline-viz/` accessible (contract source of truth)

## Vision (the UX IPAI is building)

**"Claude.ai artifact panel + Notion AI + Databricks Genie + SAP Joule + M365 Copilot
(Finance / Project Operations) — all consolidated into Pulser-in-Odoo, agentic."**

Each reference product gives us one capability Pulser must match:

| Reference | What IPAI borrows |
|---|---|
| **Claude.ai** | Inline artifact generation (charts, docs, code) in chat, with preview + edit + save |
| **Notion AI** | Workspace-aware agent grounded in internal docs (our spec bundles + SSOT + doctrine) |
| **Databricks Genie** | Natural-language data Q&A against governed data (Scout + Finance gold layers) |
| **SAP Joule** | Enterprise AI assistant with RBAC-aware data access |
| **M365 Copilot for Finance** | Recon, Collections, Expense agents inside the system of record |
| **M365 Copilot for Project Operations** | Services-ERP copilot (timesheets, WIP, invoicing, profitability) |

Pulser is the consolidated answer — one agent surface, one identity, one policy gate,
embedded in Odoo (system of record) + Teams (collaboration) + ops-console (ops view).

## Sandboxed artifact generation (CRITICAL architectural directive)

**Generate → Preview → Save** — every artifact runs in a sandbox before committing to
Odoo. Model: Claude.ai artifacts panel, but embedded in Odoo chatter.

### The 3-phase flow

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. GENERATE (sandboxed, outside Odoo DB)                             │
│    - Pulser agent emits viz_payload                                  │
│    - Foundry Code Interpreter runs chart code in isolated container  │
│    - PNG/SVG/HTML written to stipaidevagent (staging path)           │
│    - Service Bus 'viz-preview' topic notifies Odoo                   │
│                                                                      │
│ 2. PREVIEW (Odoo chatter side-panel, not committed)                  │
│    - Sandboxed iframe in chatter renders blob_url preview            │
│    - User sees chart + KPIs + insight pills inline                   │
│    - Actions: [Approve] [Edit payload] [Regenerate] [Discard]        │
│    - Nothing written to ir.attachment yet                            │
│                                                                      │
│ 3. SAVE (committed to Odoo as ir.attachment + linked artifact)       │
│    - User clicks Approve                                             │
│    - Safe Outputs vets final payload                                 │
│    - Blob moved from staging path → canonical path                   │
│    - ir.attachment created, linked to active record (move/project/…) │
│    - Optionally published: mail.message body, evidence pack, etc.    │
└──────────────────────────────────────────────────────────────────────┘
```

### Sandbox boundaries

| Boundary | What runs in sandbox | What stays outside |
|---|---|---|
| **Compute** | Chart-gen code (Python in Foundry Code Interpreter container) | Odoo ORM, PG DB, Key Vault |
| **Network** | No outbound from chart sandbox except to `stipaidevagent` staging container | All other Azure resources |
| **Storage** | Staging blob path: `stipaidevagent/viz-staging/<session>/<payload_id>.*` | Production blob path: `stipaidevagent/viz/<payload_id>.*` — only after save |
| **Identity** | Sandbox MI: `id-ipai-viz-sandbox-dev` with RBAC on staging container ONLY | Approved artifacts elevated via `id-ipai-viz-renderer-dev` |
| **DB writes** | None from sandbox | Only after user approve: Odoo `ir.attachment.create()` |

### Sandbox implementation (Odoo side)

```python
# addons/ipai/ipai_odoo_copilot/models/ipai_viz_session.py
class IpaiVizSession(models.Model):
    _name = 'ipai.viz.session'
    _description = 'Sandboxed viz preview before save'

    name = fields.Char()
    agent_run_id = fields.Char()  # FK to overlay agent.agent_runs
    payload_id = fields.Char(required=True)
    viz_type = fields.Selection([...])
    staging_blob_url = fields.Char()  # sandbox location
    preview_html = fields.Html()
    state = fields.Selection([
        ('generating', 'Generating'),
        ('preview', 'Awaiting user review'),
        ('approved', 'Approved — saving'),
        ('saved', 'Saved'),
        ('discarded', 'Discarded'),
        ('failed', 'Failed'),
    ], default='generating')
    attachment_id = fields.Many2one('ir.attachment')
    owner_record_model = fields.Char()  # e.g., 'account.move'
    owner_record_id = fields.Integer()
    safe_outputs_decision = fields.Char()  # allow/redact/block

    def action_approve(self):
        # 1. Safe Outputs vet
        # 2. Move blob staging → canonical path
        # 3. Create ir.attachment
        # 4. Link to owner record
        # 5. Post to chatter via mail.message
        # 6. Log to agent.artifacts (overlay DBML)
        pass

    def action_discard(self):
        # 1. Delete staging blob
        # 2. Update state
        # 3. Log audit.audit_events
        pass
```

### Odoo chatter widget (preview UI)

`addons/ipai/ipai_odoo_copilot/static/src/js/viz_sandbox_widget.js` — Owl.js component
that:
- Subscribes to `ipai.viz.session` records in `preview` state
- Renders the staging blob in an iframe with `sandbox="allow-scripts allow-same-origin"`
- Shows Approve / Edit / Regenerate / Discard buttons
- On Approve → RPC to `action_approve()`

### Documents module integration (canonical landing)

**All saved artifacts MUST also appear in Odoo Documents module** (`/odoo/action-<dms_id>` — action ID is environment-specific, e.g., `action-1367` on `localhost:8069`). Not just as orphan attachments on arbitrary records.

**Why:** Users need ONE place to find all Pulser-generated artifacts — searchable, filterable, shareable. Documents module is the canonical DMS UX. CE 18 has no native Documents app (Enterprise-only), so IPAI uses **OCA `dms`** (already submodule'd at `addons/oca/dms/`).

**Integration model (CE/OCA-first, no new custom module):**

```python
# On action_approve(), in addition to ir.attachment.create():
def _save_to_documents(self):
    """Save sandbox artifact to Odoo Documents (OCA dms) for canonical discovery."""
    dms_directory = self.env['dms.directory'].search([
        ('name', '=', f"Pulser/{self.tenant_slug}/{self.agent_run_id}/{self.create_date:%Y-%m}"),
    ], limit=1) or self._create_pulser_directory()

    dms_file = self.env['dms.file'].create({
        'name': f"{self.viz_type}-{self.payload_id}.{self.mime_suffix}",
        'directory_id': dms_directory.id,
        'attachment_id': self.attachment_id.id,  # links to existing ir.attachment
        # IPAI metadata — queryable in Documents search
        'tag_ids': [
            self.env.ref('ipai_odoo_copilot.tag_pulser_generated').id,
            self.env.ref(f'ipai_odoo_copilot.tag_agent_{self.agent_name}').id,
            self.env.ref(f'ipai_odoo_copilot.tag_viz_{self.viz_type}').id,
        ],
    })
    return dms_file
```

**Folder structure (per dms.directory tree):**

```
/Pulser Workspace/
  /<tenant_slug>/                          ← tenant isolation (mirrors res.company)
    /scrum_master/                          ← per-agent folder
      /2026-04/                             ← monthly rollup
        sprint-burndown-<uuid>.png
        velocity-<uuid>.svg
        dora-kpis-<uuid>.png
    /bank_recon/
      /2026-04/
        reconciliation-donut-<uuid>.png
        discrepancy-pills-<uuid>.json
    /tax_guru/
      /2026-Q1/                             ← tax periods for BIR
        2307-summary-<uuid>.png
        2550m-kpis-<uuid>.svg
    /finance_ppm/
      /2026-04/
        project-profitability-<uuid>.png
    /prismalab/
      /<research-project-key>/              ← per research project
        prisma-flow-<uuid>.svg
        forest-plot-<uuid>.svg
    /ces_campaign/
      /<campaign-key>/                      ← per campaign
        kpi-cards-<uuid>.png
        channel-mix-donut-<uuid>.png
    /sora_creative/
      /<brief-key>/                         ← per creative brief
        vertical-9x16-<uuid>.mp4
        storyboard-<uuid>.png
```

**Tags (queryable in Documents search):**

- `pulser-generated` — any artifact from Pulser
- `agent:<name>` — filter by source agent (scrum_master, bank_recon, tax_guru, etc.)
- `viz:<type>` — filter by viz_type (kpi_cards, line_chart, prisma_flow, etc.)
- `tenant:<slug>` — tenant isolation
- `period:<YYYY-MM>` — monthly rollups
- `classification:<level>` — internal / confidential / restricted
- `approved` / `published` / `archived` — lifecycle state

**URL routing (action-1367 pattern — env-specific):**

- Documents landing: `/odoo/action-<dms_id>` (equivalent of Documents app)
- Filtered Pulser view: `/odoo/action-<dms_id>?tag=pulser-generated`
- Per-agent: `/odoo/action-<dms_id>?tag=agent:scrum_master`
- Per-tenant: `/odoo/action-<dms_id>?tag=tenant:tbwa-smp`

The action ID (1367 on localhost) varies per environment — **reference it by xml_id** (e.g., `ipai_odoo_copilot.action_pulser_workspace` or `dms.action_dms_files`), never by numeric ID in code.

**Access permissions:**

- `dms.directory` group: `ipai_odoo_copilot.group_pulser_user` (read); `ipai_odoo_copilot.group_pulser_admin` (write/delete)
- Row-level per tenant: `res.company` match via `ir.rule` on `dms.directory` and `dms.file`
- Share links: Pulser artifacts can be shared externally only if `classification IN ('public','internal')` — CONFIDENTIAL and RESTRICTED cannot be share-linked

**What this replaces:**

- `ir.attachment` orphans scattered across `account.move`, `project.project`, etc. — now findable in ONE Documents view
- Ad-hoc screenshot sharing via Slack/Teams — now via Documents share links with audit trail
- "Where did Pulser save that chart yesterday?" — now a tag filter in Documents search

### Artifact types saved after approval

| Artifact | Saved to | Owner linkage | Documents folder |
|---|---|---|---|
| Chart PNG/SVG | `ir.attachment` + `agent.artifacts` + `dms.file` | Active record (move / project / partner / etc.) | `/Pulser Workspace/<tenant>/<agent>/<YYYY-MM>/` |
| Report PDF | `ir.attachment` (mimetype PDF) + `dms.file` | Active record or evidence pack | `/Pulser Workspace/<tenant>/<agent>/<YYYY-MM>/reports/` |
| Excel export | `ir.attachment` (mimetype XLSX) + `dms.file` | Active record | `/Pulser Workspace/<tenant>/<agent>/<YYYY-MM>/exports/` |
| Teams Adaptive Card JSON | Posted to Teams channel (no Odoo save) | — | — (ephemeral) |
| ops-console preview | React component rendered in-app | Session only | — (ephemeral) |
| Sora video | `creative.video_generations` (overlay) + `ir.attachment` + `dms.file` | Active campaign / record | `/Pulser Workspace/<tenant>/sora_creative/<brief-key>/` |
| gpt-image-1.5 still | `creative.image_generations` + `ir.attachment` + `dms.file` | Active brief / campaign | `/Pulser Workspace/<tenant>/sora_creative/<brief-key>/` |
| PRISMA flow SVG | `research.prisma_flow_snapshots` (overlay) + `ir.attachment` + `dms.file` | Active research project | `/Pulser Workspace/<tenant>/prismalab/<research-project-key>/` |

## The canonical contract

See `spec/pulser-inline-viz/spec.md` §F-001 for the authoritative schema.

Every Pulser agent output that includes a visualization MUST include a
`viz_payload` JSON object alongside the text answer:

```jsonc
{
  "$schema": "https://ipai.internal/viz-payload/v1",
  "id": "<uuid>",
  "agent": "<agent-name>",
  "title": "<card/chart title>",
  "subtitle": "<optional sub-label>",
  "viz_type": "kpi_cards|line_chart|bar_chart|grouped_bar|donut_chart|sparkline|insight_pills|prisma_flow|forest_plot",
  "generated_at": "<ISO-8601 timestamp>",
  "kpi_cards": [...],         // when viz_type=kpi_cards
  "chart": {...},             // when viz_type is any chart type
  "insight_pills": [...],     // optional on any type
  "blob_url": "<stipaidevagent url>",  // for PNG/SVG artifacts
  "accessibility": {...}      // WCAG alt-text for screen readers
}
```

Schema file: `platform/contracts/viz-payload.schema.json`
CI gate: `azure-pipelines/viz-renderer.yml` (T001)

## Render targets (three, identical contract)

| Target | Consumer | How |
|---|---|---|
| **Teams** | Microsoft Teams channel | Adaptive Card JSON generated from payload; renders natively |
| **Odoo** | Odoo chatter message | QWeb HTML string injected into `mail.message` body |
| **ops-console** | React ops dashboard | Chart.js component with payload passed as prop |

**All three targets consume IDENTICAL payload.** No divergence allowed — if Teams renders one way and Odoo another, the bug is in the renderer, not the payload.

## Reuse patterns (the actual meta-skill value)

### Pattern A — Scrum Master (board analytics)

```python
payload = {
    "id": uuid4(), "agent": "scrum_master",
    "title": "Sprint Burn-Down — R1-Foundation-30d",
    "viz_type": "sparkline",
    "chart": {
        "x": ["day-1", "day-2", "day-3", "day-4", "day-5"],
        "y": [42, 38, 35, 31, 27],  # remaining SP
        "target_line": [42, 37, 33, 28, 24],  # ideal burn
    },
    "insight_pills": [
        {"label": "On track", "severity": "info"},
        {"label": "4 items added mid-sprint", "severity": "warning"},
    ],
    "accessibility": {"alt": "Sprint burn-down sparkline showing 27 SP remaining vs 24 ideal"}
}
```

### Pattern B — Finance PPM (project profitability)

```python
payload = {
    "agent": "finance_ppm",
    "title": "Project Profitability — Q2 FY2026",
    "viz_type": "grouped_bar",
    "chart": {
        "x_categories": ["TBWA-SMP-Feb", "TBWA-SMP-Mar", "TBWA-SMP-Apr"],
        "series": [
            {"name": "Revenue",        "values": [480000, 520000, 580000]},
            {"name": "Cost",           "values": [310000, 340000, 370000]},
            {"name": "Gross Margin",   "values": [170000, 180000, 210000]},
        ],
        "currency": "PHP"
    },
    "kpi_cards": [
        {"label": "Avg margin %", "value": "36%", "trend": "up", "delta": "+2.1pp"},
        {"label": "On-budget projects", "value": "8/11", "trend": "stable"},
    ]
}
```

### Pattern C — Bank Recon (reconciliation status)

```python
payload = {
    "agent": "bank_recon",
    "title": "Bank Reconciliation — Apr 2026",
    "viz_type": "donut_chart",
    "chart": {
        "segments": [
            {"label": "Auto-matched", "value": 1247, "color": "success"},
            {"label": "Suggested match (needs review)", "value": 58, "color": "warning"},
            {"label": "Unreconciled", "value": 23, "color": "danger"},
        ]
    },
    "insight_pills": [
        {"label": "3 duplicate payments detected", "severity": "warning", "action_url": "odoo://..."},
        {"label": "1 FX adjustment needed", "severity": "info"},
    ]
}
```

### Pattern D — BIR 2307 (withholding cert summary)

```python
payload = {
    "agent": "tax_guru",
    "title": "BIR 2307 — Q1 FY2026",
    "viz_type": "kpi_cards",
    "kpi_cards": [
        {"label": "Total WHT", "value": "PHP 285,430", "trend": "up"},
        {"label": "Certs issued", "value": "142"},
        {"label": "Pending review", "value": "7", "severity": "warning"},
        {"label": "Quarter submission date", "value": "2026-04-30"},
    ]
}
```

### Pattern E — Scout Analytics (brand share)

```python
payload = {
    "agent": "scout_analytics",
    "title": "Brand Share — Beverages, Luzon, Q1",
    "viz_type": "grouped_bar",
    "chart": {
        "x_categories": ["Jan", "Feb", "Mar"],
        "series": [
            {"name": "Brand A",  "values": [23.4, 24.1, 25.0]},
            {"name": "Brand B",  "values": [19.2, 18.8, 18.1]},
            {"name": "Brand C",  "values": [15.3, 15.5, 16.2]},
        ],
        "unit": "%"
    },
    "insight_pills": [
        {"label": "Brand A gained 1.6pp", "severity": "info"},
        {"label": "Brand B declining 3 months", "severity": "warning"},
    ]
}
```

### Pattern F — Ces Campaign (multi-channel KPIs)

```python
payload = {
    "agent": "ces_campaign",
    "title": "Campaign KPIs — Summer 2026",
    "viz_type": "kpi_cards",
    "kpi_cards": [
        {"label": "SOV",    "value": "27%",       "trend": "up",   "delta": "+4pp"},
        {"label": "GRP",    "value": "342",       "trend": "up"},
        {"label": "CTR",    "value": "2.1%",      "trend": "up"},
        {"label": "ROAS",   "value": "3.8x",      "trend": "up"},
    ]
}
```

### Pattern G — PrismaLab (PRISMA 2020 flow)

```python
payload = {
    "agent": "prismalab",
    "title": "PRISMA 2020 Flow — H. pylori BQT vs CLR SR",
    "viz_type": "prisma_flow",
    "prisma_counts": {
        "identification_db": 1842,
        "identification_other": 47,
        "duplicates_removed": 623,
        "screened": 1266,
        "excluded_title_abstract": 1104,
        "full_text_assessed": 162,
        "excluded_full_text": 131,
        "included_qualitative": 31,
        "included_quantitative": 23
    },
    "blob_url": "https://stipaidevagent.../prisma-<id>.svg"
}
```

### Pattern H — PrismaLab (forest plot / meta-analysis)

```python
payload = {
    "agent": "prismalab",
    "title": "Forest Plot — Odds Ratio, Random Effects",
    "viz_type": "forest_plot",
    "forest_data": {
        "studies": [
            {"name": "Smith 2019",  "or": 1.32, "ci_low": 1.08, "ci_high": 1.62, "weight": 12.4},
            {"name": "Jones 2021",  "or": 1.18, "ci_low": 0.95, "ci_high": 1.46, "weight": 18.7},
            # ...
        ],
        "overall_effect": {"or": 1.24, "ci_low": 1.11, "ci_high": 1.39, "i2": 32.1, "tau2": 0.008}
    },
    "blob_url": "https://stipaidevagent.../forest-<id>.svg"
}
```

## Viz types — canonical enum (extend via schema PR)

| Enum value | Use case | Render engines |
|---|---|---|
| `kpi_cards` | 2-6 key metrics with trend arrows | Teams Adaptive / Odoo QWeb / Chart.js |
| `line_chart` | Time series single line | All three |
| `bar_chart` | Single-series bars (aging buckets, category breakdowns) | All three |
| `grouped_bar` | Multi-series bars (YoY comparison, brand share over time) | All three |
| `donut_chart` | Part-to-whole (reconciliation status, channel mix) | All three |
| `sparkline` | Inline trend (burn-down, daily activity) | All three |
| `insight_pills` | AI-generated observations with severity + action | Teams / Odoo (text badges) |
| `prisma_flow` *(domain)* | PRISMA 2020 study selection diagram | Foundry Code Interpreter → SVG |
| `forest_plot` *(domain)* | Meta-analysis effect sizes with CI | Foundry Code Interpreter → SVG |
| `funnel_plot` *(domain)* | Publication bias assessment | Foundry Code Interpreter → SVG |

**Adding new viz type:** edit `platform/contracts/viz-payload.schema.json` + add fixture in `tests/fixtures/viz_payloads/` + bump `$schema` minor version. **No new skill needed.**

## Odoo conventions (enforced)

- Views: `<list>` always — never `<tree>`
- Odoo render target uses `mail.message` chatter; QWeb HTML is scoped (no inline JS)
- `ipai_odoo_copilot` module's chatter widget consumes the payload

## Azure conventions (enforced)

- CI/CD: Azure Pipelines only (`azure-pipelines/viz-renderer.yml`)
- Never: GitHub Actions, DockerHub, Vercel
- Blob: `stipaidevagent` — never Azure Blob public containers
- Identity: `DefaultAzureCredential` → `ManagedIdentityCredential` in prod
- Auth: agent identity `id-ipai-agent-viz-renderer-dev` with RBAC on Foundry + Blob + SB

## Artifact paths

| Output | Target path |
|---|---|
| Contract | `platform/contracts/viz-payload.schema.json` |
| Spec bundle | `spec/pulser-inline-viz/` |
| Test fixtures | `tests/fixtures/viz_payloads/*.json` (one per viz_type) |
| Renderer service | `agent-platform/services/viz-renderer/` |
| Odoo render widget | `addons/ipai/ipai_odoo_copilot/static/src/js/viz_widget.js` |
| Teams Adaptive Card generator | `agent-platform/services/viz-renderer/teams/` |
| ops-console React component | `web/ops-console/src/components/VizRenderer.tsx` |
| Rendered chart artifacts | `stipaidevagent/viz/<payload_id>.{png,svg}` |
| CI pipeline | `azure-pipelines/viz-renderer.yml` |

## Related skills (consumers)

**Direct consumers** — each emits `viz_payload` and depends on this meta-skill:

- `scrum-master` — sprint burn-down / velocity / DORA KPIs
- `tax-guru` (BIR) — WHT summary cards
- `bank-recon` — reconciliation donut + discrepancy pills
- `finance-close` — D+5 progress tracker
- `finance-ppm` — project profitability + cash flow
- `ap-invoice` / `ar-collections` — aging buckets + DSO
- `doc-intel` — extraction confidence KPIs
- `scout-analytics` (Suqi) — brand share + SOV
- `ces-campaign` (Ask Ces) — campaign KPIs + channel mix
- `prismalab` — PRISMA flow + forest/funnel plots

**Pairs with:** `ipai-agent-platform`, `ipai-resource-map`, `ipai-odoo-platform` (for Odoo render target), `librarian-indexer` (for skill drift alignment)

**ADO area path:** `InsightPulseAI\ControlPlane` (payload schema) + `InsightPulseAI\DeliveryEng` (renderer service)

**ADO epic parent:** "[OBJ-003] Foundry Agent Runtime & Copilot" (#3)

## Trigger routing (for Librarian v3 §5)

```yaml
viz_renderer:
  keywords:
    - "chart"
    - "KPI"
    - "dashboard"
    - "visualization"
    - "burn-down"
    - "sparkline"
    - "donut"
    - "forest plot"
    - "PRISMA"
    - "viz_payload"
    - "inline chart"
  load: [viz-renderer, ipai-agent-platform, ipai-resource-map]
  note: "Meta-skill. Load alongside the domain skill that emits the payload."
```

## Safe-action contracts

Viz Renderer is READ-ONLY relative to business data — it transforms payloads into
render artifacts. Does NOT mutate Odoo records or ADO work items.

| Action | Approval band | Auto-execute? |
|---|---|---|
| Render Teams/Odoo/React from valid payload | `l1_no_approval` | ✅ yes |
| Persist chart PNG/SVG to `stipaidevagent` | `l1_no_approval` | ✅ yes |
| Publish Adaptive Card to Teams channel | `l1_no_approval` (per-channel rate limit) | ✅ yes |
| Inject QWeb HTML into Odoo `mail.message` | `l1_no_approval` | ✅ yes |
| Extend `viz_payload` schema with new viz_type | `l3_dual_review` | ❌ human PR only |

## Safe Outputs vetting

Every render runs through `agent.safe_output_events`:

- **Secrets redaction:** payload fields are scanned for PAT/password/API-key patterns
- **PII classification:** customer names, TINs, bank accounts are redacted unless payload
  has `data_classification: internal|confidential` AND audience includes entity owner
- **Content safety:** insight_pills text runs Microsoft Content Safety (hate/sexual/violence/self-harm)
- **Rate limit:** max 10 renders per channel per hour (Teams / Slack)
- **C2PA provenance:** for charts generated by Foundry Code Interpreter (`gpt-5.3-codex`), preserve provenance metadata in the blob

## Success metrics (self-tracking via `agent.eval_run_metrics`)

- Render latency: p50 < 2s, p99 < 8s
- Payload schema validation pass rate: 100% (CI gate blocks non-conforming)
- Render target parity: Teams/Odoo/React produce visually-equivalent output (golden-file tests)
- Consumer adoption: number of domain skills emitting `viz_payload` per quarter
  (target R2: 4, R3: 8, R4: 12)
- Zero divergence: same payload produces identical chart across 3 targets (diff tests)

## Migration path (from existing single-purpose viz code)

1. **R2 gate:** Scrum Master + Bank Recon + Finance Close emit `viz_payload` (3 consumers)
2. **R3 gate:** Add AP/AR, BIR Tax Guru, Finance Close, Scout Analytics (4 more)
3. **R4 gate:** Add PrismaLab (prisma_flow + forest_plot), Ces Campaign, PPM (3 more)
4. **Post-GA:** deprecate any remaining domain-specific viz code

## Anti-patterns (DO NOT)

- **Don't reimplement rendering** in a domain skill. Always emit `viz_payload` and let Viz Renderer handle the three targets.
- **Don't add viz types inline** in a domain skill. Extend the schema via PR to `platform/contracts/viz-payload.schema.json`.
- **Don't bypass Safe Outputs** for "internal-only" payloads. Every render is vetted.
- **Don't render in the emitting agent's runtime.** Push to `sb-ipai-dev-sea` render queue; consumer writes to `stipaidevagent`; agents get the `blob_url`.
- **Don't use Chart.js on the Teams side or Adaptive Cards on the Odoo side.** Three render targets, three engines, one payload.
- **Don't log payload bodies to App Insights** — may contain PII. Log only metadata (agent, viz_type, latency, tenant_id).

## Evidence contract

Every render produces an evidence row in `agent.agent_runs`:

- `run_id`, `tenant_id`, `agent` (emitting agent), `viz_type`, `render_targets[]`
- Latency per target (Teams / Odoo / React)
- Safe Outputs decision (`allow` / `redact` / `block`)
- Blob URL(s)
- Consumer: links to the emitting `agent.agent_runs.id`

## Anchors

- `spec/pulser-inline-viz/` — spec bundle (contract authority)
- `platform/contracts/viz-payload.schema.json` — JSON Schema (to be authored in T001)
- `agents/skills/scrum_master/SKILL.md` — first consumer, already references this meta-skill
- `addons/ipai/ipai_odoo_copilot/` — Odoo chatter widget (to be extended with viz_widget.js)
- `agent-platform/services/viz-renderer/` — renderer service (to be built)
- `docs/architecture/reference-adaptations/pulser-inline-viz.md` — design rationale (to be written)
- CLAUDE.md — doctrine (Azure-native, OCA-first, Safe Outputs mandatory)
