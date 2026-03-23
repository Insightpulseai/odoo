# W9 Studio Copilot -- PRD

> Product requirements for the Studio Copilot assistant surface.

---

## Product Summary

W9 Studio is a creative finishing platform. Studio Copilot is its embedded AI assistant that orchestrates the generation-to-publish pipeline using provider-brokered models.

**Target user:** Creative operators, brand managers, marketing teams.
**Value proposition:** Reduce time from brief to published content by orchestrating AI generation, brand compliance, and platform export in one workspace.

---

## Functional Requirements

### FR-1: Provider-Brokered Generation

- Support multiple generation providers via adapter interface
- Default routing: Gemini (fast stills), Imagen (premium stills), fal (mixed media), OpenAI (understanding/eval)
- Provider selection based on task type, quality tier, and modality
- Fallback chain when primary provider is unavailable

### FR-2: Brand Preset Management

- Create, store, and apply brand presets (colors, fonts, templates, tone)
- Presets are workspace-scoped (`workspace_id`)
- Apply presets to generation prompts and post-processing
- Version presets with change history

### FR-3: Creative Pipeline Orchestration

- Ingest assets from upload, brief, or AI generation
- Apply AI polish (enhancement, style transfer, brand alignment)
- Generate platform-specific exports (dimensions, format, metadata)
- Queue for review/approval before publish

### FR-4: Platform Export

- Export to standard social/web formats (1080x1080, 1920x1080, 9:16, etc.)
- Include platform-specific metadata (alt text, captions, hashtags)
- Batch export for multi-platform campaigns
- Export manifest with audit trail

### FR-5: Publish Handoff

- Integration with scheduling tools (n8n workflows)
- Approval gate before publish (human confirmation required)
- Calendar view of scheduled content
- Post-publish performance signal ingestion (analytics loop)

### FR-6: Workspace Isolation

- All assets, presets, and history scoped to `workspace_id`
- `workspace_id` validated against `customer_tenant_id`
- No cross-workspace data leakage
- Workspace-level RBAC (owner, editor, viewer)

---

## Non-Functional Requirements

### NFR-1: Latency

- Generation request acknowledgment: < 2s
- Fast still generation (Gemini): < 10s
- Premium still generation (Imagen): < 30s
- Video generation (fal): async with webhook, < 5min

### NFR-2: Observability

- All generation calls logged with provider, model, latency, cost estimate
- Audit trail for brand preset changes
- Publish event logging with approval chain

### NFR-3: Security

- No tenant data in public surfaces
- Provider API keys managed via Azure Key Vault
- Generation outputs stored in workspace-scoped storage

---

## Out of Scope (v1)

- Direct Odoo record access (use A2A handoff to Odoo Copilot)
- Analytics dashboards (use Genie)
- Auto-publish without human confirmation
- Custom model fine-tuning
- Video editing beyond generation + trim

---

## Dependencies

- Creative provider policy: `docs/architecture/CREATIVE_PROVIDER_POLICY.md`
- Tenancy model: `docs/architecture/TENANCY_MODEL.md`
- fal model shortlist: `ssot/creative/provider_policy.yaml#fal_v01_model_shortlist`

---

*Last updated: 2026-03-24*
