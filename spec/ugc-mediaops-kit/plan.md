# Implementation Plan: ugc-mediaops-kit

## Reference Runtime Split

| Plane | Service | Role |
|-------|---------|------|
| Media generation | fal.ai | Image, video, audio, utility transforms |
| Workflow orchestration | n8n | Trigger, poll, handoff, status update |
| Analytics / data products | Databricks | Bronze/Silver/Gold creative ops telemetry |
| BI consumption | Fabric / Power BI | Campaign KPIs, performance reporting |
| Understanding / eval | OpenAI multimodal | QA, review, extraction, scoring |
| Alternate generation | Gemini / Imagen | Stills, editing, premium brand assets |

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
9. Analytics written back to governed data plane

### n8n → fal Integration

- Use queue URL from fal model's API tab
- Header auth: `Authorization: Key YOUR_FAL_KEY`
- JSON body copied from model payload documentation
- Poll for completion or use webhook callback

## Bronze/Silver/Gold Output Model

| Tier | Content |
|------|---------|
| **Bronze** | Raw briefs, prompts, assets, render logs, provider responses |
| **Silver** | Normalized jobs, metadata, QC signals, export manifests |
| **Gold** | Campaign-ready KPIs, creative performance summaries, recommendation outputs |

## fal Integration Layers

fal is not one undifferentiated API. See `docs/architecture/FAL_INTEGRATION_STRATEGY.md` for full details.

| Layer | fal Surface | OSS Module | Phase |
|-------|------------|------------|-------|
| 1. Generation | Model APIs | `packages/provider-broker-fal` | v0.1 |
| 2. Orchestration | n8n integration | `packages/workflow-runner` | v0.1 |
| 3. Platform ops | Platform APIs | `packages/platform-ops-fal` | v0.2 |
| 4. Custom deploy | CLI + Python SDK | Deferred | v0.3+ |

**Rule:** Generation goes through Model APIs. Platform APIs are for metadata/pricing/usage/analytics/queue/logs/keys/billing — never for executing model calls.

## OSS Module Structure

### Package 1: schemas

- `creative_brief.schema.json`
- `asset_job.schema.json`
- `brand_preset.schema.json`
- `export_profile.schema.json`
- `publish_plan.schema.json`
- `performance_report.schema.json`

### Package 2: provider-broker-fal

Wraps **Model APIs** only. Normalizes model IDs, submits jobs, maps responses to internal schema.

Methods:

| Job | fal Model |
|-----|-----------|
| `still.generate.fast` | `nano-banana-2` |
| `still.generate.premium` | `nano-banana-pro` |
| `still.edit.brand` | `flux-pro/kontext` |
| `still.generate.fallback` | `gpt-image-1.5` |
| `video.generate.premium` | `kling-video/v3/pro/image-to-video` |
| `video.generate.transition` | `kling-o3-image-to-video-pro` |
| `video.generate.google` | `veo-3.1` |
| `video.generate.fast` | `ltx-2.3/image-to-video/fast` |
| `video.extend` | `ltx-2.3/extend-video` |
| `asset.remove_background` | `pixelcut/background-removal` |
| `asset.upscale` | `seedvr/upscale/image` |
| `asset.to_lottie` | `omnilottie/image-to-lottie` |
| `asset.to_svg` | `vecglypher/image-to-svg` |

### Package 3: workflow-runner

Methods:

| Method | Role |
|--------|------|
| `createJobFromBrief` | Parse brief → create job manifest |
| `submitFalJob` | Submit to fal queue endpoint |
| `pollFalJob` | Poll for completion |
| `collectArtifacts` | Collect and store outputs |
| `runQaChecks` | Execute QA/eval pipeline |
| `buildExportPack` | Create platform-specific export package |
| `emitPublishPayload` | Hand off to publish/schedule |

Orchestration: n8n first (submit/poll/callback), custom runner later.

### Package 6: platform-ops-fal (v0.2)

Wraps **Platform APIs** for operational visibility. Not for generation.

Methods:

| Method | Platform API |
|--------|-------------|
| `searchModels` | Model metadata/search |
| `getModelPricing` | Model pricing |
| `estimateCost` | Pricing calculation |
| `getUsage` | Usage tracking |
| `getAnalytics` | Usage analytics |
| `getQueueSize` | Serverless queue metrics |
| `getServerlessMetrics` | Serverless performance |
| `getLogs` | Serverless logs |
| `listKeys` / `createKey` / `deleteKey` | API key lifecycle |
| `getBillingUsage` | Billing/FOCUS reports |

### Package 4: brand-preset-engine

- Config-driven rules: fonts, colors, lower thirds, title safe area, aspect ratios, subtitle style, watermark rules
- Platform-specific preset profiles

### Package 5: qa-evals

- Caption completeness check
- Aspect-ratio readiness check
- Brand-preset compliance check
- Title/thumbnail consistency check
- Missing output variants check
- Dead-air / hook / pacing heuristics

## fal Production Policy

- Use hosted model queue endpoints first for v1
- Use `fal deploy` only when custom app logic, stable endpoint IDs, region/env control, or private auth needed
- Default production auth for custom apps: private
- Prefer rolling rollout strategy

## MVP Build Order

1. **MVP 0.1** — Schemas + provider broker + manifest CLI
2. **MVP 0.2** — Polish/export/QA pipeline
3. **MVP 0.3** — Analytics schema + recommendation loop

## Examples to Ship

- `creator_shortform/` — Single creator, shoot-to-publish same day
- `agency_batch_campaign/` — Multi-asset batch generation for campaign
- `studio_same_day_publish/` — W9-style full pipeline

---

*Last updated: 2026-03-23*
