# W9 Studio Copilot -- Tasks

> Task checklist with status.

---

## Phase 1: Provider Adapter Foundation

- [ ] Define provider adapter interface contract
- [ ] Implement Gemini direct adapter (gemini-2.5-flash-image)
- [ ] Implement fal queue adapter (async + webhook)
- [ ] Implement Imagen adapter (imagen-4 family)
- [ ] Implement OpenAI multimodal adapter (understanding/eval)
- [ ] Wire Azure Key Vault for provider API keys
- [ ] Implement provider health check and fallback chain
- [ ] Smoke test: generate still via Gemini from workspace

## Phase 2: Workspace and Brand Presets

- [ ] Implement workspace_id scoping model
- [ ] Workspace RBAC (owner, editor, viewer)
- [ ] Brand preset CRUD API
- [ ] Preset application to generation prompts
- [ ] Workspace isolation validation (no cross-workspace leakage)

## Phase 3: Creative Pipeline

- [ ] Asset ingest: upload endpoint
- [ ] Asset ingest: AI generation trigger
- [ ] AI polish step: enhancement + brand alignment
- [ ] Platform export: multi-format renderer
- [ ] Export manifest with audit trail
- [ ] Batch export for multi-platform campaigns

## Phase 4: Publish Handoff

- [ ] Approval gate implementation
- [ ] n8n workflow integration for scheduling
- [ ] Calendar view API
- [ ] Post-publish analytics signal ingestion

## Phase 5: Eval and Release

- [ ] Create eval pack (generation quality, brand compliance, export accuracy)
- [ ] Establish staging baseline metrics
- [ ] Internal beta deployment
- [ ] Iterate based on feedback
- [ ] Promote to limited_ga after 7-day SLO pass

---

*Last updated: 2026-03-24*
