# Product Requirements Document: W9 Studio / Studio Copilot

## Product Definition

W9 Studio is a creative finishing and media operations product. Studio Copilot is the AI assistant embedded within W9 Studio.

The product center of gravity is **turning raw or AI-generated assets into finished, publish-ready content**. The bottleneck is post-production; W9's value is the last-mile finishing layer.

## Surface Classification

Studio Copilot is one of five canonical assistant surfaces. See `docs/architecture/ASSISTANT_SURFACES.md`.

- **Role:** Creative finishing / mediaops assistant
- **Scope:** Authenticated, workflow-driven
- **Product name:** W9 Studio (Studio Copilot is the assistant inside it)
- **Not:** A generic social-media chatbot, not an ERP copilot, not a "generate a pretty image" tool

## Goal

Create a workflow-driven creative assistant that:

- Guides users through the six-stage finishing pipeline
- Applies brand presets and platform-specific export profiles
- Brokers across generation providers based on task type
- Supports same-day-publish workflows
- Provides analytics and next-brief feedback

## Non-Goals

- Replacing professional creative tools (Premiere, After Effects, Figma)
- Building a standalone social media management SaaS
- Generic image generation without finishing/brand context
- Merging into Diva Copilot or Odoo Copilot UX
- Autonomous publishing without human confirmation

## Workflow Backbone

### Stage 1: Capture / Ingest

- Accept brief, footage, AI-generated assets
- Parse brief for brand, audience, platform targets
- Validate asset formats and quality

### Stage 2: AI Polish

- Enhancement, cleanup, upscaling
- Style transfer and adaptation
- Copy generation and refinement

### Stage 3: Brand Presets

- Apply brand guidelines (colors, typography, logo placement)
- Enforce brand consistency across assets
- Template-driven layouts

### Stage 4: Platform Exports

- Platform-specific format packaging (Instagram, TikTok, LinkedIn, YouTube, etc.)
- Aspect ratio, duration, and format compliance
- Metadata and caption generation

### Stage 5: Scheduling / Publish Handoff

- Schedule across platforms
- Approval gate before publish
- Handoff to platform APIs or manual publish queue

### Stage 6: Analytics + Next Steps

- Post-publish performance tracking
- Content performance insights
- Next-brief recommendations based on what worked

## Generation Policy

| Task Type | Provider | Notes |
|-----------|----------|-------|
| Stills (fast) | Gemini direct | Quick edits, iterations |
| Stills (premium) | Imagen | High-quality generation |
| Mixed media / video / audio | fal | Video, audio, multimodal |
| Multimodal review / eval / extraction | OpenAI | Quality assessment, content review |

Provider selection is task-driven, not user-selected. The copilot picks the right provider based on the job.

## Personas

### Creative Lead

Needs fast turnaround from brief to published content with brand consistency.

### Content Producer

Needs multi-platform export, scheduling, and performance feedback.

### Brand Manager

Needs brand preset enforcement, approval gates, and consistency auditing.

## Execution Architecture

### Control Flow

1. Intake brief in Studio surface
2. Create job manifest
3. Trigger n8n workflow
4. n8n submits to fal queue endpoint (header auth + JSON payload)
5. fal returns generated assets
6. Studio QA/eval runs (OpenAI multimodal)
7. Export package created (platform-specific)
8. Publish/schedule handoff
9. Analytics written back to governed data plane (Databricks Bronze/Silver/Gold)

### n8n → fal Integration

- Use queue URL from fal model's API tab
- Header auth: `Authorization: Key YOUR_FAL_KEY`
- JSON body from model payload documentation
- Poll for completion or webhook callback

### Open-Source Layer

The reusable infrastructure under this workflow is published as `ugc-mediaops-kit`. See `spec/ugc-mediaops-kit/prd.md`.

## SSOT References

- Surface taxonomy: `docs/architecture/ASSISTANT_SURFACES.md`
- Machine-readable: `ssot/agents/assistant_surfaces.yaml`
- Creative provider policy: `docs/architecture/CREATIVE_PROVIDER_POLICY.md`
- Provider SSOT: `ssot/creative/provider_policy.yaml`
- OSS layer: `spec/ugc-mediaops-kit/`

---

*Last updated: 2026-03-23*
