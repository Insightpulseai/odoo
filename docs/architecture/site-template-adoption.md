# Public Site → Azure AI Template Adoption

**Status**: canonical
**Authority**: [ssot/web/site-template-adoption.yaml](../../ssot/web/site-template-adoption.yaml)
**Related**: [agent-framework-adoption.md](agent-framework-adoption.md), [identity-architecture.md](identity-architecture.md)

---

## Decision

Four surfaces, four distinct roles. Three receive Azure AI template adoption;
one is the Odoo ERP runtime entrypoint (no template adoption). One template
per site, not one for all. Templates are **reference inputs**, not production
repo topology.

| Site | Role | Baseline | Owning repo |
|---|---|---|---|
| [erp.insightpulseai.com](https://erp.insightpulseai.com) | Production Odoo ERP entrypoint (transactional system-of-record) | **No template** — Odoo CE 18 + OCA + `ipai_*` | [addons/](../../addons/) |
| [www.insightpulseai.com](https://www.insightpulseai.com) | Flagship platform / product front door | `Get started with AI agents` | [web/apps/ipai-landing](../../web/apps/ipai-landing) (existing) |
| [prismalab.insightpulseai.com](https://prismalab.insightpulseai.com) | Domain-specific AI workspace (PRISMA / evidence / research) | `Get started with AI agents` + multimodal/doc patterns | `web/apps/prismalab` (evolve from existing `web/apps/prismalab-gateway`) |
| [www.w9studio.net](https://www.w9studio.net) | Studio / creative commercial site | `Get Started with Chat` | `web/apps/w9studio-site` (new; design tokens already at `design/tokens/w9studio.tokens.json`) |

**ERP routing rule**: when user intent references "ERP", "Odoo", "back
office", or "transactional system", the canonical URL is
`https://erp.insightpulseai.com/`. Other shells link to it, integrate with
it, or call into it — never replace its role.

---

## Boundary contract

```
web/apps/<site>/                     UI, routing, auth UX, attachment upload UX
            ↓  HTTP API
agent-platform/src/agent_platform/   runtime, orchestration, retrieval, providers, tool execution
            ↓  loads config
agents/                              prompts, personas, judges, eval scenarios, tool metadata
            ↓  consumes tokens from
design/                              tokens, brand assets, component library
```

**Rule**: `web/apps/*` never imports `agent_framework` or runs an agent
runtime locally. It calls into `agent-platform` HTTP APIs. Prompts and
personas live in `agents/`, not duplicated inside each site repo.

---

## Per-site adaptation

### 1. `www.insightpulseai.com` — flagship platform

**Template base**: `Get started with AI agents`
**Frontend reference**: `microsoft-foundry/foundry-agent-webapp`
**App path**: [web/apps/ipai-landing](../../web/apps/ipai-landing) (exists — evolve in place)

**Adaptation targets**:
- Branded marketing + platform entry
- Product entry points: Odoo Copilot, data intelligence, AI operations, industry accelerators
- Optional Entra-authenticated demo workspace backed by `agent-platform`

**Do not**:
- Leave as a generic "upload docs and chat" demo
- Hardwire sample knowledge/index logic into the site repo
- Run agent runtime inside the web app (call `agent-platform` APIs instead)

---

### 2. `prismalab.insightpulseai.com` — domain workspace

**Template base**: `Get started with AI agents`
**Secondary references**:
- `Multi-modal Content Processing` (ingestion patterns)
- `Document Generation and Summarization` (output synthesis patterns)
**Workflow inspiration only** (do not copy UI):
- `Healthcare Agent Orchestrator`
**App path**: `web/apps/prismalab` (evolve from existing `web/apps/prismalab-gateway`)

**Adaptation targets**:
- Document-heavy research/evidence workflows
- Grounded answers with citations
- Attachment ingestion: PDF, Word, Excel, images
- Structured extraction via Azure Document Intelligence
- PRISMA-compliant systematic review outputs (see `.claude/skills/prismalab-*`)

**Ingestion path**:
```
web/apps/prismalab (upload widget)
  → agent-platform/src/agent_platform/attachments/pipeline.py
  → agent-platform/src/agent_platform/tools/docintel/extract.py
  → agent-platform/src/agent_platform/retrieval/grounding.py
  → grounded response w/ citations back to UI
```

---

### 3. `www.w9studio.net` — studio / creative

**Template base**: `Get Started with Chat`
**Optional UX inspiration only**:
- `Creative Writing Assistant Python` (tone/style controls)
- `GenAI chat frontend with debug/restyle/revisit` (iteration UX)
**App path**: `web/apps/w9studio-site` (new)

**Existing scaffolding to leverage**:
- [design/w9studio/](../../design/w9studio/) — brand assets
- [design/tokens/w9studio.tokens.json](../../design/tokens/w9studio.tokens.json) — design tokens
- [spec/w9-studio-copilot/](../../spec/w9-studio-copilot/) — existing spec bundle

**Adaptation targets**:
- Marketing site
- Services showcase
- Optional lead intake + light creative assistant demo

**Do not**:
- Adopt agent-heavy orchestration templates as base
- Match the runtime complexity of `ipai-landing` or `prismalab`
- Start with Entra auth as primary (public site, no standing auth)

---

## Deferred templates (do not use as first-base)

These are useful as architecture references, not starting points for the
three public surfaces:

- `Multi Agent Custom Automation Engine Solution Accelerator` — too opinionated
- `Container Migration Solution Accelerator` — wrong domain
- `Release Manager Assistant` — internal only; already used in `agent-platform/agents/release-manager/`
- `Real-Time Intelligence for Operations` — specialized ops dashboard
- `Home Banking Assistant` — irrelevant domain
- `Prior Authorization Multi-Agent Solution Accelerator` — healthcare-specific

---

## microsoft-foundry org as reference, not template

The `microsoft-foundry` GitHub org is **reference material** — samples,
labs, starter apps, demos, event assets. Do **not** mirror its repo layout
into InsightPulseAI. See the upstream crosswalk in
[agent-framework-adoption.md §Appendix A](agent-framework-adoption.md).

---

## Adoption order

| Phase | Scope | Blocking |
|---|---|---|
| 1 | Evolve `web/apps/ipai-landing` toward `Get started with AI agents` shape. Call into `agent-platform` HTTP API. Wire Entra OIDC for optional demo workspace. | `agent-platform` runtime API must exist (follow-up Python-skeleton PR) |
| 2 | Build out `web/apps/prismalab` on `Get started with AI agents` base. Add attachment ingestion pipeline. Ship PRISMA-compliant output flow. | phase 1 + `agent_platform.attachments.pipeline` + `agent_platform.tools.docintel` |
| 3 | Scaffold `web/apps/w9studio-site` on `Get Started with Chat` base. Import tokens from `design/tokens/w9studio.tokens.json`. Optional lead intake widget. | phase 1 (shared shell patterns) |

---

## Non-goals

- Not forking Azure AI template repos.
- Not mirroring `microsoft-foundry` repo layout.
- Not running agent runtime inside `web/apps/`.
- Not duplicating prompts or personas across `web/apps/` (definitions live in `agents/`).
- Not hardcoding sample knowledge or index fixtures into site repos.

---

## References

- SSOT: [ssot/web/site-template-adoption.yaml](../../ssot/web/site-template-adoption.yaml)
- Agent framework adoption: [agent-framework-adoption.md](agent-framework-adoption.md)
- Identity authorities: [identity-architecture.md](identity-architecture.md)
- PRISMA skills: `.claude/skills/prismalab-*`
- Existing apps: [web/apps/ipai-landing](../../web/apps/ipai-landing), [web/apps/prismalab-gateway](../../web/apps/prismalab-gateway)
- Design tokens (W9): [design/tokens/w9studio.tokens.json](../../design/tokens/w9studio.tokens.json)
