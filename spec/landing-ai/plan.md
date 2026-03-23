# Implementation Plan: Landing AI (Public Assistant)

## Runtime Template Baseline

- **Foundry template baseline:** Get Started with AI Chat
- **Deployment shape:** Azure Container Apps
- **Goal:** Public docs-grounded assistant with telemetry and explicit advisory boundary
- **Non-goal:** Autonomous multi-agent orchestration

## Design Doctrine

The public landing assistant follows `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md`:

- Public, documentation-grounded product guide
- Explicit provenance on every response
- Zero tenant access
- CTA-oriented (docs, pricing, demo, trial, contact)
- Separate system prompt from authenticated assistants

## Implementation Phases

### Phase 1 — Chat Surface

- Deploy chat widget on landing pages
- Wire to Azure OpenAI (gpt-4.1) via copilot gateway
- Ground responses in approved public documentation corpus
- Add first-use capability disclosure
- Add source labels per response

### Phase 2 — Retrieval

- Create public-docs KB index (separate from odoo-docs-kb)
- Index: product docs, architecture pages, pricing, FAQ, release notes
- Retrieval order: page-specific → docs corpus → pricing/FAQ → labeled web fallback
- No tenant/workspace data retrieval

### Phase 3 — Telemetry & Trust

- Instrument with App Insights
- Add persistent accuracy notice
- Add per-answer feedback controls
- Measure response quality baseline

## Model Baseline

- **Primary public model:** `gpt-5-mini`
- **Escalation model:** `gpt-5.4`

The landing assistant prioritizes throughput, cost efficiency, and stable public advisory behavior. More complex synthesis and higher-risk product-positioning turns may escalate to `gpt-5.4`.

**Note:** `gpt-4.1` is the current deployed model. Migration to GPT-5 tier as deployments become available.

## Provider Baseline

- **Primary path:** Current public assistant provider contract
- **Allowed secondary path:** Gemini API via `@google/genai`

Use Gemini only for:

- Public advisory mode
- Docs/pricing/architecture Q&A
- Experiments and A/B testing
- Optional search-heavy public workflows

Do not use Gemini for tenant-aware or write-capable product surfaces.

## Public Assistant Tool Policy

- **No direct MCP action tools enabled**
- Docs-grounded only
- Public advisory mode
- No tenant access
- No actions

## Rules

- Public assistant answers from approved public sources only
- No tenant/customer data access from marketing surface
- Every answer exposes source class
- Technical questions answered before sales qualification
- Public-web search must be labeled when used
- Marketing and authenticated assistant system prompts are separate

---

*Last updated: 2026-03-23*
