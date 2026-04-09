# fal Integration Strategy

> Architecture for `ugc-mediaops-kit` fal integration, separated by fal's documented API surfaces.

---

## Core Principle

fal is **not one undifferentiated API**. It has four distinct integration layers, and each maps to a different module in the OSS project.

| Layer | fal Surface | OSS Module | When |
|-------|------------|------------|------|
| 1. Generation | Model APIs | `packages/provider-broker-fal` | v0.1 (now) |
| 2. Orchestration | Examples (n8n, Next.js) | `packages/workflow-runner` | v0.1 (now) |
| 3. Platform ops | Platform APIs | `packages/platform-ops-fal` | v0.2 (after jobs flow) |
| 4. Custom deploy | CLI + Python SDK | Deferred | v0.3+ (when justified) |

---

## Layer 1: Model APIs — Generation

Used for actual generation/edit job execution. Wrapped inside `packages/provider-broker-fal`.

### What it does

- Submit generation/edit jobs to fal model endpoints
- Normalize model IDs and payloads to internal schema
- Handle async queue semantics for long-running media work
- Map provider-specific responses to standard `AssetJob` results

### Methods

| Job | fal Model |
|-----|-----------|
| `still.generate.fast` | `nano-banana-2` |
| `still.generate.premium` | `nano-banana-pro` |
| `still.edit.brand` | `flux-pro/kontext` |
| `video.generate.premium` | `kling-video/v3/pro/image-to-video` |
| `video.generate.fast` | `ltx-2.3/image-to-video/fast` |
| `video.extend` | `ltx-2.3/extend-video` |
| `asset.remove_background` | `pixelcut/background-removal` |
| `asset.upscale` | `seedvr/upscale/image` |

### Implementation

- Start with **client libraries** for model calls from the app
- fal positions client libraries as the primary lane for calling fal AI models from applications
- Do not start with custom deployed fal apps

---

## Layer 2: Workflow Orchestration — n8n

Used for submit/poll/callback/handoff flows. n8n is the first orchestration lane.

### What it does

- Brief intake trigger
- Queue submit to fal model endpoints
- Poll for completion or handle webhook callbacks
- Asset state transitions
- QA/eval gate
- Publish handoff
- Analytics handoff to governed data plane

### n8n → fal Pattern

fal documents "Using fal within an n8n workflow" as a first-class integration example:

1. Use the queue URL from the fal model's API tab
2. Set header auth: `Authorization: Key YOUR_FAL_KEY`
3. Copy JSON body from model payload documentation
4. Poll for completion or configure webhook callback

### Why n8n first

- Already deployed in the stack (`n8n.insightpulseai.com`)
- fal explicitly supports n8n as an integration pattern
- No custom code needed for basic submit/poll/collect flows
- Can be extended with custom nodes later

---

## Layer 3: Platform APIs — Observability

Used for metadata, pricing, usage, analytics, queue monitoring, and billing. Wrapped by `packages/platform-ops-fal`.

**Important:** Platform APIs are for operations visibility, not for executing model calls. fal explicitly states: "For actual generation, use Model APIs."

### Methods

| Method | Platform API Category |
|--------|----------------------|
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

### When to add

Only after generation jobs are flowing through Layer 1. Do not build the observability wrapper before the generation pipeline works.

---

## Layer 4: Custom Deploy — Deferred

Used for persistent wrapped endpoints with custom pre/post-processing. Built with fal CLI + Python SDK.

### When to use

- Stable wrapped endpoint ID needed
- Custom preprocessing/postprocessing around model calls
- Isolated staging/prod environments required
- Region or machine type control needed
- Unified wrapper around multiple underlying model calls

### When NOT to use

- v0.1 (use hosted model queue endpoints instead)
- Simple submit/poll flows (n8n handles this)
- Single-model calls (client library is sufficient)

### Deploy policy

When custom deploy is needed:

- Default auth: **private**
- Prefer **rolling** rollout strategy for zero-downtime
- Use `fal deploy` CLI for remote cloud builds
- Configure machine type and region per endpoint

---

## Implementation Order

### Phase 1 — Model APIs + n8n (v0.1)

- Wire `packages/provider-broker-fal` with client libraries
- Wire n8n workflow templates for submit/poll/collect
- Ship schemas + basic pipeline

### Phase 2 — Platform API observability (v0.2)

- Add `packages/platform-ops-fal` for usage/pricing/analytics
- Wire cost estimation into job planning
- Add queue monitoring for production visibility

### Phase 3 — Custom deploy (v0.3+)

- Only if hosted model endpoints are insufficient
- Build custom fal serverless apps for wrapped workflows
- Deploy with CLI, manage with Platform APIs

---

## Grant Alignment

This architecture strengthens the fal grant story because it directly maps to fal's documented surfaces:

- **Model APIs** → generation execution (the core value)
- **n8n integration** → workflow orchestration (fal's own example)
- **Platform APIs** → operational visibility (cost/usage/analytics)
- **CLI/SDK deploy** → custom serverless apps (when justified)

The OSS project open-sources the **schema, broker, runner, ops, and eval** layers on top of these surfaces.

---

## SSOT References

- Creative provider policy: `docs/architecture/CREATIVE_PROVIDER_POLICY.md`
- Provider SSOT: `ssot/creative/provider_policy.yaml`
- OSS spec: `spec/ugc-mediaops-kit/`

---

*Last updated: 2026-03-23*
