# Tasks: ugc-mediaops-kit

## MVP 0.1 — Schemas + Pipeline Manifests

- [ ] Define `CreativeBrief` JSON schema
- [ ] Define `AssetJob` JSON schema
- [ ] Define `BrandPreset` JSON schema
- [ ] Define `ExportProfile` JSON schema
- [ ] Define `PublishPlan` JSON schema
- [ ] Define `PerformanceReport` JSON schema
- [ ] Build provider broker interface (Gemini / Imagen / fal / OpenAI)
- [ ] Build fal adapter with queue/webhook support
- [ ] Build Gemini adapter with Nano Banana model routing
- [ ] Build manifest CLI: read brief → create jobs → write manifests → route → status
- [ ] Create example: `creator_shortform/`
- [ ] Write README.md with project positioning and architecture overview

## MVP 0.2 — Polish / Export / QA

- [ ] Build caption cleanup hook
- [ ] Build typography/style preset validator
- [ ] Build aspect-ratio export packager (TikTok, Reels, Shorts, YouTube, 1:1, 16:9, 9:16)
- [ ] Build QA report generator
- [ ] Build publish package output formatter
- [ ] Build n8n workflow template for fal queue integration
- [ ] Create example: `agency_batch_campaign/`

## MVP 0.2.5 — Platform Ops (fal Platform APIs)

- [ ] Build `packages/platform-ops-fal` wrapper
- [ ] Implement `searchModels` — model metadata/search
- [ ] Implement `getModelPricing` — pricing lookup
- [ ] Implement `estimateCost` — cost estimation for job planning
- [ ] Implement `getUsage` — usage tracking
- [ ] Implement `getAnalytics` — usage analytics
- [ ] Implement `getQueueSize` — queue monitoring
- [ ] Implement `getServerlessMetrics` — performance metrics
- [ ] Implement `getLogs` — serverless logs
- [ ] Implement key lifecycle — `listKeys` / `createKey` / `deleteKey`
- [ ] Implement `getBillingUsage` — billing/FOCUS reports
- [ ] Wire cost estimation into job planning workflow

## MVP 0.3 — Analytics + Recommendation Loop

- [ ] Define normalized analytics schema (retention, CTR, hook performance)
- [ ] Build performance report generator
- [ ] Build recommendation engine contract for next brief
- [ ] Build benchmark/eval runner
- [ ] Create example: `studio_same_day_publish/`

## Cross-Cutting

- [ ] Write `docs/architecture/OVERVIEW.md`
- [ ] Write `docs/architecture/PROVIDER_POLICY.md`
- [ ] Write `docs/architecture/BRAND_PRESETS.md`
- [ ] Write `docs/architecture/EXPORT_PROFILES.md`
- [ ] Write `docs/architecture/QA_EVALS.md`
- [ ] Create platform export presets (TikTok, Reels, Shorts, YouTube longform)
- [ ] Create example brand preset YAML
- [ ] Set up CI for schema validation
- [ ] License: choose OSS license (MIT or Apache 2.0)

## Grant Application

- [ ] Create public repo skeleton on GitHub
- [ ] Draft grant email to grants@fal.ai
- [ ] Attach repo link + W9 proof materials
- [ ] Submit application

---

*Last updated: 2026-03-23*
