# Pulser Assistant — Surface Design Across 4 Domains + Teams

> **Locked:** 2026-04-15
> **Authority:** this file (Pulser Copilot UX design per surface)
> **Companions:**
> - [`domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md) — 4 domains + 2 runtime classes
> - [`multitenant-saas-target-state.md`](./multitenant-saas-target-state.md) — tenancy model
> - [`capability-source-map.md`](./capability-source-map.md) — upstream composition
> - [`../skills/stack-build-map.md`](../skills/stack-build-map.md) — agent-building track
> - [`pulser-product-packaging.md`](../strategy/pulser-product-packaging.md)
>
> **Reference templates:** [Azure AI app templates gallery](https://azure.github.io/awesome-azd/) (azd — 64 templates)
> **Teams integration:** [Teams Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.ms-teams-vscode-extension)

---

## The 4 web surfaces + Teams — Pulser UX by surface

Each domain has a different buyer journey. Pulser must adapt UX per surface — **same agent, different skins, different affordances.**

| Surface | Role | Pulser UX shape | Primary use case |
|---|---|---|---|
| `www.insightpulseai.com` | Marketing root | Floating chat widget + lead capture | "Tell me about IPAI" → demo scheduling |
| `erp.insightpulseai.com` | Authenticated product | Full systray + chat panel inside Odoo | Finance / project / compliance workflows |
| `prismalab.insightpulseai.com` | Research tool app | Tool-specific assistants + grounded Q&A | "Ask PrismaLab AI" + artifact preview |
| `www.w9studio.net` | Booking microsite | Lightweight chat for booking + FAQ | Studio inquiry / package explainer |
| **Teams / M365 Copilot** | Internal + client delivery | Teams-native agent via Teams Toolkit | Cross-surface reach for M365 customers |

---

## Surface 1 — `www.insightpulseai.com` (marketing root)

### UX pattern

- Bottom-right **floating chat widget** (collapsed by default)
- Triggers: homepage CTA, pricing page, case studies
- Outputs: answers + demo booking deep-link → `book.insightpulseai.com/appointment`

### Build pattern (consume + thin wrapper)

```
Upstream azd template:
  "Get Started with Chat" (353 forks, 241 stars)
  Simple chat app deployed to ACA — matches our pattern exactly

Adopt mode:  clone_as_reference
Compose:
  - Pulser API (we already have ipai_pulser_api via ACA)
  - JS widget (new, lightweight; no React per OWL doctrine — vanilla JS here since it's not Odoo)
  - Keyless auth via Entra MI
  - Session persistence in Redis (when we enable) OR client-side only (MVP)
  - Lead capture → POSTs to shared forms API (per web BOM plane)
```

### Scope (thin)

- Anonymous users
- No deep domain knowledge — scope to IPAI positioning / pricing / demos
- Intent: qualify → book demo → hand off

### What it should NOT do

- No PHI/finance queries (wrong surface)
- No document uploads (save for erp.*)
- No multi-turn agent orchestration (save for erp.*)

---

## Surface 2 — `erp.insightpulseai.com` (authenticated product)

This is the **primary Pulser surface** — where the work happens.

### UX pattern

- **Odoo systray icon** (top-right of Odoo UI) — opens chat drawer
- **Chatter integration** on every record (sale.order, account.move, project.task, etc.) — record-context-aware
- **Inline artifacts** when Pulser emits structured output (per [`ipai_artifact_preview`](#) module proposal)

### Build pattern (already 80% there — compose existing `ipai_*`)

```
Already exists:
  addons/ipai/ipai_ai_copilot          — Pulser copilot core
  addons/ipai/ipai_odoo_copilot        — Odoo-specific copilot
  addons/ipai/ipai_ai_channel_actions  — channel-level actions
  addons/ipai/ipai_ai_platform         — platform-level surface
  addons/ipai/ipai_copilot_actions     — action registry
  addons/ipai/ipai_mail_plugin_bridge  — bridges to M365 mail

To build (remaining):
  addons/ipai/ipai_artifact_preview    — inline rendering (per artifact-preview doc)
  .claude/skills/pulser-odoo-grounded  — authoring guide for Odoo-context tools
```

### Reference templates (azd)

| Template | What to learn |
|---|---|
| `Azure AI Basic App Sample | Python` (241 forks) | Foundry hub+project+chat in ACA |
| `Get started with AI agents` (558 forks) | Agent Service + Search retrieval |
| `Securely authenticate and access your GenAI app with managed identity` (139 forks) | Keyless MI pattern (matches our doctrine) |
| `Multi Agent Custom Automation Engine` (774 stars) | Multi-agent orchestration with AutoGen — **reference only**, we use Agent Framework |
| `Monitor GenAI models with Arize AI` | Pattern for production monitoring |

### Scope (deep)

- Authenticated users scoped to tenant (`company_id`)
- Pulser has full access to Odoo models via `ipai-odoo-mcp`
- Record-level context injected into every call
- Artifact rendering inline (Mermaid, HTML dashboards, code)
- Multi-turn workflows (close cadence, BIR filing prep, expense liquidation)

### What to also display

- Tool calls visible to user (transparency)
- Approval gates for mutating actions (per policy-gated doctrine)
- Evidence pack links (for compliance trails)
- Cost telemetry per conversation (tenant-scoped, tagged)

---

## Surface 3 — `prismalab.insightpulseai.com` (research tool app)

This is the **"Ask PrismaLab AI" pattern** — tool-specific + grounded over research corpus.

### UX pattern

- Per-tool assistant (one for Clarify Question, one for PRISMA diagram, one for PubMed, etc.)
- **Shared "Ask PrismaLab AI" panel** — grounded over PRISMA 2020 + Cochrane + Harrer corpus (per [`prismalab_rag_corpus.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/prismalab_rag_corpus.md) memory)
- **Artifact outputs** — PRISMA flow diagrams as Mermaid, PICO tables as Markdown, PubMed results as citeable lists

### Build pattern

```
Already deployed:
  ipai-prismalab-gateway (ACA, already live per memory prismalab_gateway_deployed)
  srch-ipai-dev — AI Search index `prismalab-rag-v1`
  4 RAG sources: R skills, PRISMA 2020, Cochrane, Harrer

To build:
  Tool-specific assistant skills per PrismaLab tool
  (.claude/skills/prismalab-* entries, one per tool)
```

### Reference templates (azd)

| Template | Fit |
|---|---|
| `RAG chat with Azure AI Search + Python` (5.4K forks, 7.6K stars) | **Exact match** — we already do this |
| `RAG chat on PostgreSQL` (950 forks, 487 stars) | For corpus stored in PG |
| `VoiceRAG with Realtime API` (352 forks, 554 stars) | Future: voice for PrismaLab |
| `Entity extraction with Azure OpenAI structured outputs` (77 stars) | For PICO / PRISMA data extraction |
| `Multi-modal GenAI experience: Q&A on uploaded images` (222 stars) | For paper screenshots / figures |

### Scope

- **Anonymous allowed** per existing positioning (no account required)
- Tenant context optional (only for export/saving)
- Tool-specific system prompts + grounding
- Citation-first responses (PRISMA 2020 + Cochrane refs)

---

## Surface 4 — `www.w9studio.net` (booking microsite)

### UX pattern

- Simple **chat bubble** for booking inquiries
- Scripted flows: "book a studio," "get rates," "ask about packages"
- Handoff to Odoo `appointment` for actual booking (per [`booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md))

### Build pattern (minimal)

```
Reuse: same widget pattern as Surface 1 (marketing)
Different system prompt: W9 Studio context + booking intent
Backend: Pulser + ipai_odoo_copilot scoped to W9 company_id
Booking handoff: POST to /appointment URL deep-link
```

### Reference templates (azd)

| Template | Fit |
|---|---|
| `Serverless GenAI assistant using function calling` (42 stars) | Function calling pattern for "book a slot" |
| `Customer Chatbot Solution Accelerator` (27 stars) | Orchestrator + specialized agents |

### Scope (thin)

- Booking-intent only
- Rates + availability Q&A
- No deep workflow

---

## Surface 5 — Microsoft Teams + M365 Copilot

This is the **enterprise delivery surface** — especially for M365-heavy customers (TBWA\SMP once signed).

### UX pattern

- Pulser as **Teams app** (added to a user's or team's Teams client)
- **Adaptive Cards** for rich in-Teams responses
- **Context passing** — click a Teams message → Pulser picks up context
- **Single-tenant deployment** per customer (one app per M365 tenant)

### Build pattern — Teams Toolkit is the canonical path

```
Tool:     Teams Toolkit for VS Code (TeamsDevApp.ms-teams-vscode-extension)
Backend:  Reuse existing ipai_agent / ipai_mail_plugin_bridge patterns
Auth:     Entra app registration per customer tenant (not per-user)
Storage:  Adaptive Cards JSON manifest + bot service backing
Hosting:  ACA (same pattern as other Pulser surfaces)
```

### Teams Toolkit unlocks

- Scaffolding for Teams apps (manifest.json, Adaptive Cards, bot hosting)
- Local dev tunnel
- M365 developer tenant for testing
- Deployment to Azure Bot Service + ACA backend
- Integration with Graph API for user context, calendar, mail

### Reference templates (azd)

| Template | Fit |
|---|---|
| **`AI application with SharePoint knowledge and actions`** (13 stars, 22 forks) | ⭐ **Closest match** — Foundry SDK + Copilot Retrieval API over SharePoint |
| `Healthcare Agent Orchestrator` (188 stars) | Multi-agent with M365 + Teams integration |
| `Home Banking Assistant` (32 stars) | Agent Framework + Foundry pattern |
| `AI Toolkit for VS Code + samples` (already in register) | Dev-time for Teams |

### Scope (customer-specific)

- Separate Teams app per customer tenant
- Tenant-scoped Entra app registration
- M365 user context → Pulser agent with tenant boundaries
- Adaptive Cards for common workflows (expense approval, BIR filing status, close progress)

### Guardrails

- No cross-tenant queries (tenant app boundary)
- Pulser uses customer's Entra for user identity, but IPAI MI for backend Foundry calls
- Policy gates enforced per Pulser doctrine

---

## Common Pulser architecture across all 5 surfaces

```
┌────────────────────────────────────────────────────────────────┐
│  Surface-specific UI (5 flavors)                               │
│    • Web widget (surfaces 1, 4)                                │
│    • Odoo systray + chatter (surface 2)                        │
│    • PrismaLab tool panels (surface 3)                         │
│    • Teams app + Adaptive Cards (surface 5)                    │
├────────────────────────────────────────────────────────────────┤
│  Pulser API (ACA) — shared across all surfaces                 │
│    • ipai-pulser-api container                                 │
│    • Tenant-scoped auth via Entra OIDC                         │
│    • Policy-gated execution                                    │
│    • Surface dispatcher (routes by surface context)            │
├────────────────────────────────────────────────────────────────┤
│  Pulser core (microsoft/agent-framework)                       │
│    • Planner / router                                          │
│    • Specialist agents (Tax Guru, Recon, Advisory, etc.)       │
│    • Tool adapters via MCP                                     │
│    • Memory (pluggable — tenant-scoped)                        │
├────────────────────────────────────────────────────────────────┤
│  Foundry                                                       │
│    • ipai-copilot-resource (AIServices, East US 2)             │
│    • gpt-4.1, text-embedding-3-small, gpt-4o-mini              │
│    • AI Search for grounded retrieval                          │
│    • Content Safety filter                                     │
├────────────────────────────────────────────────────────────────┤
│  MCP servers                                                   │
│    • ipai-odoo-mcp (Odoo data plane — surface 2)               │
│    • Future: odoo-mcp-server per capability-source-map P0 gap  │
│    • Azure MCP (via microsoft/azure-skills plugin)             │
│    • Foundry MCP (via microsoft/azure-skills plugin)           │
│    • Teams MCP (for surface 5, via Teams Toolkit scaffolding)  │
└────────────────────────────────────────────────────────────────┘
```

---

## What to build vs what to consume (per surface)

| Surface | What to build | What to consume |
|---|---|---|
| www.insightpulseai.com | Thin JS widget + system prompt | `Get Started with Chat` azd template pattern |
| erp.insightpulseai.com | `ipai_artifact_preview` module + OWL widget | Existing `ipai_*` modules + Odoo CE `web_editor` |
| prismalab.insightpulseai.com | Tool-specific skills + RAG corpus maintenance | `ipai-prismalab-gateway` already live + AI Search |
| www.w9studio.net | System prompt + appointment handoff | Same widget as Surface 1 + Odoo `appointment` |
| Teams / M365 | Teams app manifest + Adaptive Cards library | Teams Toolkit + Azure Bot Service + existing Pulser API |

---

## Build order (which surface ships first)

Per ship gates + customer priority:

1. **Surface 2 (erp.*)** — primary; already 80% live via existing `ipai_*` modules. Remaining: `ipai_artifact_preview` (~3 days)
2. **Surface 3 (prismalab.*)** — already live; tool-specific skill authoring (~2 days per tool)
3. **Surface 1 (www.*)** — marketing widget (~3 days; follows Get Started with Chat template)
4. **Surface 4 (w9studio.*)** — thin variant of Surface 1 (~1 day after Surface 1)
5. **Surface 5 (Teams)** — customer-triggered only (when TBWA\SMP or similar M365 customer signs). ~2 weeks

---

## Design principles

### 1. Same agent, different skin

Pulser is ONE agent stack. Surface differences are **system prompt + UI skin + tool allowlist**, never forks of the agent.

### 2. Tenant-scoped always

Every surface carries tenant context from token → middleware → agent → tool calls.

### 3. Progressive disclosure

Surface 1 = lightest (public, no auth).
Surface 5 = deepest (full M365 integration).
Don't cram Surface 2 features into Surface 1.

### 4. Artifact preview where it adds value

Surfaces 2 + 3 + 5 support artifacts.
Surfaces 1 + 4 don't — artifact preview is overkill for marketing/booking.

### 5. Build only the delta

- Widget (1, 4) — ~500 LOC JS
- Odoo module (2) — ~500 LOC Python + OWL
- PrismaLab skills (3) — skill definitions only, no new module
- Teams app (5) — ~1000 LOC TS + Adaptive Cards JSON

Total new build: ~2000 LOC across 5 surfaces. Everything else is composition.

---

## Reference templates to mine (from azure.github.io/awesome-azd)

Priority order for pattern mining:

1. **`Get Started with Chat`** — Surface 1 + 4 base pattern
2. **`Azure AI Basic App Sample | Python`** — Surface 2 reference
3. **`RAG chat with Azure AI Search + Python`** — Surface 3 (already matches our pattern)
4. **`AI application with SharePoint knowledge and actions`** — Surface 5 closest match
5. **`Securely authenticate with managed identity`** — keyless MI reference for all surfaces
6. **`Get started with AI agents`** — Agent Service pattern for multi-agent features
7. **`Multi-modal Content Processing`** — document Q&A patterns for Surface 3

### Reject / skip

- `Multi-Agent Custom Automation Engine` — uses AutoGen (rejected in register)
- Anything with GHA deploy workflow — strip and replace with Azure Pipelines
- Anything that uses `OPENAI_API_KEY` — adapt to Foundry + MI

---

## Teams Toolkit specific recommendations

Per [Teams Toolkit docs](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.ms-teams-vscode-extension):

### What to adopt

- Teams app scaffolding (manifest.json format, icon/branding)
- Adaptive Cards library (JSON schema + rendering)
- Local dev tunnel (for testing against real M365)
- M365 developer tenant access

### What to adapt

- Deploy via Azure Pipelines (not the GHA templates scaffolded by default)
- Use our Entra MI pattern (not app-only keys)
- Backend in ACA (not Azure Bot Service alone — use both: Bot Service for Teams channel + ACA for logic)

### Required register addition

```yaml
- upstream: OfficeDev/TeamsFx
  purpose: Teams Toolkit for VS Code + CLI (Teams app scaffolding)
  adopt_mode: consume_directly
  internal_owner: agent-platform
  guardrails:
    - Deploy via Azure Pipelines, not the bundled GHA templates
    - Use Entra MI for backend auth, not app keys
  last_verified: 2026-04-15
```

---

## Anti-patterns

| Don't | Why |
|---|---|
| Build a different agent per surface | Violates "same agent, different skin" |
| Use OpenAI API keys in any surface | Doctrine — MI + Foundry only |
| Skip tenant scoping on Surface 1 | Even anonymous users must be tenant-tagged for cost attribution |
| Build React components for Surface 2 | Odoo uses OWL natively |
| Deploy Teams app with bundled GHA workflow | Doctrine — Azure Pipelines sole CI |
| Cross-tenant queries in Surface 5 | Teams app is single-tenant scoped |
| Build every surface at once | Ship order matters; Surface 2 first (primary revenue) |

---

## Success criteria per surface

- **Surface 1** — 30% of visitors open chat; 15% book demo via chat
- **Surface 2** — 80% of finance-team actions go through Pulser within 90 days of go-live
- **Surface 3** — 3x increase in tool completion rate vs. non-AI baseline
- **Surface 4** — 20% of booking inquiries resolved by chat before human touch
- **Surface 5** — Customer retention within M365 without forcing them into our ERP UI

---

## References

Internal:
- [`docs/architecture/domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md) — 4 domains + runtime classes
- [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md)
- [`docs/architecture/booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md)
- [`docs/architecture/planner-surface-microsoft-parity.md`](./planner-surface-microsoft-parity.md)
- [`docs/skills/stack-build-map.md`](../skills/stack-build-map.md) — 4 tracks
- [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) — register v2
- Existing modules: `ipai_ai_copilot`, `ipai_odoo_copilot`, `ipai_ai_platform`, `ipai_ai_channel_actions`, `ipai_copilot_actions`, `ipai_mail_plugin_bridge`
- Memory: `prismalab_gateway_deployed`, `prismalab_rag_corpus`, `pulser_agent_classification`

External:
- [Azure AI app templates gallery (awesome-azd)](https://azure.github.io/awesome-azd/) — 64 templates
- [Teams Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.ms-teams-vscode-extension)
- [Teams Toolkit docs](https://learn.microsoft.com/microsoftteams/platform/toolkit/)
- [Adaptive Cards](https://adaptivecards.io/)
- [Microsoft Graph API](https://learn.microsoft.com/graph/)

---

## Bottom line

```
5 surfaces, 1 Pulser agent, 1 Foundry backend, 1 MCP ecosystem.
Surface differences = system prompt + UI skin + tool allowlist.
Build order = Surface 2 (ERP) → 3 (PrismaLab) → 1 (marketing) → 4 (W9) → 5 (Teams).
Total new build across 5 surfaces: ~2000 LOC.
Consume upstream: 64 azd templates + Teams Toolkit + existing ipai_* modules.
```

---

*Last updated: 2026-04-15*
