# CHANGELOG -- Odoo Copilot on Azure

All notable changes to the Odoo Copilot agent and its Odoo module are documented here.

Versioning follows the runtime-contract.md (C-30) release ladder.

## [2.0.0] - 2026-03-15 -- Advisory Release

### Agent

- System prompt upgraded to v2.0.0: scope-boundary enforcement, context-awareness, RBAC-awareness, advisory disclaimers, live-data claim suppression.
- Temperature reduced from 1.0 to 0.4 for factual grounding.
- Top P adjusted from 1.0 to 0.9.
- Evaluation pack: 30/30 pass (eval-20260315-full-final). ADVISORY_RELEASE_READY.

### Odoo Module (ipai_odoo_copilot 18.0.3.0.0)

- Dual-backend gateway controller (Azure OpenAI direct + custom gateway).
- SSE streaming endpoint (`/ipai/copilot/stream`).
- Conversation model with company-scoped access checks.
- Audit model with event logging.
- Rate limiting (20 req/min/user).
- Systray UI with markdown rendering.
- Context builder service (record, company, user, tax contexts).

### Contracts

- Runtime contract C-30 v1.3.0 established.
- Context envelope contract v1.0.0.
- Retrieval grounding contract v1.0.0 (Phase 2B, not active).
- Telemetry contract v1.0.0 (Phase 2C, not active).
- Guardrails v1.0.0 (G-1 through G-6).
- Tooling matrix v1.0.0 (8 read-only tools defined, 0 wired).
- Publish policy v1.0.0 with 4-level ladder.

## [1.0.0] - 2026-03-03 -- Internal Prototype

### Agent

- Initial agent created in Foundry project `data-intel-ph`.
- Agent ID: `asst_45er4aG28tFTABadwxEhODIf`.
- Model: gpt-4.1 (serverless).
- System prompt v0.1.0: basic advisory prompt.
- No tools, no knowledge sources, no evaluations.

## [0.1.0] - 2026-03-23 -- Stage 3 Azure Wiring

### Infrastructure

- gpt-4.1 model contract deployed to oai-ipai-dev.
- odoo-docs-kb index created in srch-ipai-dev (26 chunks, HNSW 1536d cosine).
- RBAC: Search Index Data Reader + Cognitive Services OpenAI User assigned.
- Foundry connections: CognitiveSearch + AzureOpenAI.
- ipai-copilot-endpoint scoring URI verified operational.
- ipai-copilot-gateway env vars wired to gpt-4.1.
- Retrieval smoke test passed (grounded results, score 7.33).
