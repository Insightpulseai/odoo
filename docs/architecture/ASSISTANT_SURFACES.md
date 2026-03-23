# Assistant Surfaces — Product Taxonomy

> Three distinct assistant surfaces on one shared runtime plane. No mega-copilot.

---

## 1. Canonical Surfaces

| Surface | Role | Scope |
|---------|------|-------|
| **Odoo Copilot** | ERP / transactional assistant | Authenticated, record-aware |
| **Diva Copilot** | Orchestration / routing / schema assistant | Authenticated, cross-domain |
| **Studio Copilot** | Creative finishing / mediaops assistant (W9 Studio) | Authenticated, workflow-driven |
| **Genie** | Conversational analytics | Authenticated, query-provenance |
| **Document Intelligence Assistant** | Document review and extraction | Authenticated, page/field-anchored |

These are separate product surfaces, not modes of one assistant.

## 2. Surface Doctrine

- Each surface has a **distinct grounding model**
- Each surface has a **distinct permission boundary**
- No single "mega-copilot" UX — users interact with the surface that matches their job
- System prompts are **separate and versioned independently**
- Naming must not blur boundaries: Diva is not "everything," Odoo Copilot is not public-facing, Studio is not a generic chatbot

## 3. Grounding Model by Surface

### Odoo Copilot

- **Lane 1:** Odoo runtime context (active record, company, user role, locale)
- **Lane 2:** Curated Odoo 19 docs KB (`odoo-docs-kb` index)
- **Lane 3:** Bounded web retrieval (allowed domains only, max 3 per query)

Primary jobs: explain ERP state, summarize records, answer module/config questions, guide workflows, draft actions, eventually execute tightly scoped actions after confirmation.

Launch posture: internal beta, trusted users, read-only advisory first.

### Diva Copilot

- **Routing shell** across modes, not a domain expert itself
- Routes to: Strategy, Odoo, Tax Guru, Capability, Governance
- Assembles context per mode from KB segments
- Classifies intent → picks mode → assembles context → routes

Primary jobs: classify intent, pick the right mode, assemble context, route to specialist.

What it must not become: a fake "knows everything" assistant, the direct analytics engine, the document-review UI, the studio finishing UI.

### Studio Copilot (W9 Studio)

- **Workflow backbone:**
  1. Capture / Ingest (brief, footage, AI-generated assets)
  2. AI Polish
  3. Brand Presets
  4. Platform Exports
  5. Scheduling / Publish handoff
  6. Analytics + Next Steps

- **Generation policy:**
  - Stills (fast): Gemini direct
  - Stills (premium): Imagen
  - Mixed media / video / audio: fal
  - Multimodal review / eval / extraction: OpenAI

Product center of gravity: turn raw or AI-generated assets into **finished, publish-ready content**. The bottleneck is post-production; W9's value is the last-mile finishing layer.

### Genie

- Conversational analytics surface
- Semantic layer + live queries + provenance
- Not a general-purpose copilot
- Citation model: query provenance (shows what data was queried and how)

### Document Intelligence Assistant

- Document-first review and extraction
- Page/field anchored (not free-form chat)
- Human-in-the-loop with confidence thresholds
- Extraction → structured data → Odoo record mapping
- Not merged into Diva or Studio UI

## 4. Shared Runtime Plane

All five surfaces share a common substrate:

| Capability | Shared |
|-----------|--------|
| Identity / permission scope | Entra ID + managed identities |
| Tool registry | Foundry Agent Service |
| Retrieval policy | Azure AI Search (per-surface indexes) |
| Audit / traces | `ipai.copilot.audit` + App Insights |
| Evals | Per-surface eval packs with distinct thresholds |
| Provider brokering | Azure OpenAI (gpt-4.1) + per-surface model overrides |
| Design system | Fluent 2 components |

The runtime plane provides infrastructure. The surfaces provide distinct user experiences.

## 5. Naming Rules

### Use

- **Odoo Copilot** — the ERP assistant
- **Diva Copilot** — the orchestration/routing shell
- **W9 Studio** — the product name
- **Studio Copilot** — the assistant inside W9
- **Genie** — the analytics surface
- **Document Intelligence** — the extraction/review surface

### Avoid

- Calling everything "Diva"
- Calling Genie a "copilot"
- Calling the public landing assistant "Odoo Copilot" (that is the Marketing Assistant per `MARKETING_ASSISTANT_DOCTRINE.md`)
- Making Studio Copilot sound like a generic social-media chatbot
- Using "Foundry" as a user-facing brand for every assistant surface

---

## 5. Shared Substrate by Plane

| Plane | Service | Role |
|-------|---------|------|
| ERP | Odoo runtime + Odoo Copilot | Transactional SoR, record-aware assistance |
| Schema / orchestration | Diva Copilot | Cross-surface routing, goal/governance context |
| Creative / media | Studio Copilot + fal + Gemini/Imagen | Finishing pipeline, provider-brokered generation |
| Data intelligence | Databricks lakehouse + Fabric/Power BI + Genie | Medallion analytics, semantic BI, governed data Q&A |
| Automation | n8n | Workflow orchestration, trigger/poll/handoff |
| Governance | Entra ID, Key Vault, Azure Monitor, Purview, GitHub, Azure DevOps | Identity, secrets, observability, catalog, CI/CD |

---

## 6. Domain Intelligence Shells

Each domain vertical composes from the same three planes:

| Domain | Diva (Intelligence) | Odoo (Execution) | Studio (Creative) |
|--------|-------------------|-------------------|-------------------|
| Marketing | Customer 360, campaign intelligence | CRM, campaigns, partners | Campaign creative, social content |
| Media | Audience analytics, content intelligence | Scheduling, rights, revenue | Content production, platform export |
| Retail | Inventory analytics, demand forecasting | POs, inventory, sales | Product visuals, catalog |
| Financial Ops | Risk/compliance/efficiency analytics | Journals, invoices, tax, close | Financial reports (rare) |

See `docs/architecture/DOMAIN_INTELLIGENCE_SHELLS.md` for the full doctrine.

---

## SSOT References

- Machine-readable: `ssot/agents/assistant_surfaces.yaml`
- Odoo Copilot: `ssot/agents/diva_copilot.yaml` (odoo mode)
- Diva Copilot: `ssot/agents/diva_copilot.yaml` (all modes)
- Tenancy model: `ssot/architecture/tenancy_model.yaml`
- A2A interop: `docs/architecture/A2A_INTEROP.md`
- AgentOps doctrine: `docs/architecture/AGENTOPS_DOCTRINE.md`
- Retrieval policy: `docs/architecture/RETRIEVAL_AND_MEMORY_POLICY.md`
- Go-live matrix: `docs/architecture/GO_LIVE_MATRIX.md`
- Domain shells: `docs/architecture/DOMAIN_INTELLIGENCE_SHELLS.md`
- Marketing Assistant: `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md`
- Runtime authority: `docs/architecture/AI_RUNTIME_AUTHORITY.md`

---

*Last updated: 2026-03-24*
