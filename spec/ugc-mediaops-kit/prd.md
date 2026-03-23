# Product Requirements Document: ugc-mediaops-kit

## Product Definition

Open-source infrastructure for agency UGC and generative media workflows: brief → ingest → generate/edit → polish → export → evaluate.

The project focuses on the **finishing workflow layer** between generation and publishing — the part that turns raw or AI-generated assets into finished, platform-ready content.

## Problem

AI can generate assets, but agencies still need a repeatable finishing workflow to make content publish-ready across platforms. The bottleneck is not raw generation — it is the last mile of formatting, branding, QA, export packaging, and publish handoff.

## Product

Open-source infra/tooling for:

- Creative brief intake and job schemas
- Provider routing across Gemini / Imagen / fal / OpenAI multimodal
- Asset/job orchestration with queue/webhook patterns
- Brand preset enforcement
- Platform export packaging
- QA/eval before publish
- Publishing adapter interfaces
- Post-publish analytics normalization

## Users

- Agency ops teams
- Creator studios
- Media workflow engineers
- Internal content ops teams

## Non-Goals

- DAM replacement
- Full PM/project management system
- Full billing/pricing system
- Full publishing SaaS
- Consumer-facing creative app
- Generic "AI image generator" product

## Open-Source Boundary

### Open-source (publish)

- Brief/job schemas
- Provider broker interfaces
- Pipeline runner
- Brand preset engine
- Platform export profiles
- QA/eval framework
- Analytics/report schema
- Publish adapter interfaces
- Example workflows

### Closed/commercial (keep private)

- W9 customer workspace
- Billing/pricing logic
- Proprietary brand presets
- Internal benchmarks
- Private approval/admin flows
- Studio occupancy/scheduling economics
- Sales/ops admin surfaces
- Local studio execution processes

## Provider Policy

- **Gemini direct:** Fast stills, conversational editing, concepting
- **Imagen:** Premium-quality stills, logos, brand-critical visuals
- **fal.ai:** Mixed-media (video, voice, music, SFX), queue-based production
- **OpenAI multimodal:** Understanding, evaluation, extraction, review, QA

See `docs/architecture/CREATIVE_PROVIDER_POLICY.md` for full policy.

## Workflow Backbone

1. **Capture / Ingest** — Accept brief, footage, AI-generated assets
2. **Generate / Edit** — Provider-routed generation and editing
3. **AI Polish** — Caption cleanup, style transfer, enhancement
4. **Brand Presets** — Apply brand guidelines, enforce consistency
5. **Platform Exports** — Platform-specific format packaging
6. **QA / Eval** — Automated quality checks before publish
7. **Publish Handoff** — Schedule, approve, deliver to platforms
8. **Analytics + Next Steps** — Performance tracking, next-brief recommendations

## MVP Sequence

### MVP 0.1 — Schemas + Pipeline Manifests

- `CreativeBrief` schema
- `AssetJob` schema
- `BrandPreset` schema
- `ExportProfile` schema
- CLI/service: read brief → create jobs → write manifests → route to providers → store status

### MVP 0.2 — Polish / Export / QA

- Caption cleanup hook
- Typography/style preset validator
- Aspect-ratio export packager
- QA report generator
- Publish package output

### MVP 0.3 — Analytics + Recommendation Loop

- Normalized analytics schema
- Retention / CTR report format
- Recommendation engine contract for next brief
- Benchmark/eval runner

## Real-World Anchor

This project is abstracted from W9 Studio's operating workflow:

- Real physical studio node (508.25 sqm, La Fuerza Compound, Makati City)
- Operationalized user journey: Book → Record → AI-Assist Edit → Brand & Platform Formatting → Schedule & Publish → Weekly Report
- Product promise: "Shoot at 9AM. Publish the same day."
- Roadmap toward exportable W9 Node blueprint, shared AI playbooks, and template marketplace

## SSOT References

- Surface taxonomy: `docs/architecture/ASSISTANT_SURFACES.md`
- Creative provider policy: `docs/architecture/CREATIVE_PROVIDER_POLICY.md`
- Provider SSOT: `ssot/creative/provider_policy.yaml`
- W9 Studio spec: `spec/w9-studio-copilot/prd.md`

---

*Last updated: 2026-03-23*
