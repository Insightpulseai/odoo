# W9 Studio Copilot -- Implementation Plan

> Phased delivery plan for the Studio Copilot assistant surface.

---

## Phase 1: Provider Adapter Foundation

**Goal:** Establish the provider broker interface and connect first-wave providers.

- Implement provider adapter contract (`gemini | imagen | fal | openai | fallback`)
- Connect Gemini direct for fast still generation
- Connect fal queue endpoint for mixed media
- Implement provider health check and fallback chain
- Wire Azure Key Vault for provider credentials

**Exit criteria:** Generate a still image via Gemini and a video clip via fal from a single workspace.

## Phase 2: Workspace and Brand Presets

**Goal:** Workspace isolation and brand preset management.

- Implement `workspace_id` scoping for all assets
- Create brand preset CRUD (colors, fonts, templates)
- Apply presets to generation prompts
- Workspace RBAC (owner, editor, viewer)

**Exit criteria:** Two workspaces with different brand presets produce visually distinct outputs from the same prompt.

## Phase 3: Creative Pipeline

**Goal:** End-to-end generation-to-export pipeline.

- Asset ingest (upload + AI generation)
- AI polish step (enhancement, brand alignment)
- Platform export formatting (multi-format, multi-dimension)
- Export manifest with audit trail

**Exit criteria:** Brief -> generation -> polish -> export produces a publish-ready asset package.

## Phase 4: Publish Handoff

**Goal:** Approval and scheduling workflow.

- Approval gate (human confirmation required)
- n8n workflow integration for scheduling
- Calendar view of scheduled content
- Post-publish analytics signal ingestion

**Exit criteria:** Content moves from generation through approval to scheduled publish with full audit trail.

## Phase 5: Eval and Release

**Goal:** Studio Copilot eval pack and staging validation.

- Create eval pack (generation quality, brand compliance, export accuracy)
- Establish staging baseline
- Internal beta with trusted creative operators
- Iterate based on feedback

**Exit criteria:** Eval pack passes staging gate (score > 0.70). Internal beta active.

---

## Mapping to Existing Specs

| Spec | Relationship |
|------|-------------|
| `spec/fluent-designer-agent/` | UI/UX design system for Studio surfaces |
| `spec/landing-ai/` | Public landing page (not Studio itself) |
| `spec/copilot-target-state/` | Overarching copilot family target state |

---

*Last updated: 2026-03-24*
