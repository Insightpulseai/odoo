# Creative Provider Policy

> Provider routing doctrine for creative/media surfaces. Generation vs understanding split is mandatory.

---

## Canonical Rule

**Use OpenAI to understand, evaluate, extract, route, and assist.**
**Use Gemini / Imagen / fal to generate, depending on modality and quality tier.**

---

## Provider Doctrine

| Provider | Primary Role | When to Use |
|----------|-------------|-------------|
| **Gemini direct** | Fast conversational image generation and editing | Default for speed, iteration, editing, concepting |
| **Imagen** | Premium-quality stills, logos, product visuals, style-critical creative | When image quality is critical (Google's own guidance) |
| **fal.ai** | Mixed-media pipelines: video, voice, music, SFX, multi-model orchestration | UGC video/audio, batch media, queue-based production |
| **OpenAI multimodal** | Understanding, evaluation, extraction, review | QA, evals, document intelligence, captioning, scoring |

---

## Surface Assignment

### Landing Creative Studio

- **Primary:** Gemini direct
  - Default model: `gemini-2.5-flash-image` (Nano Banana)
  - Premium escalate: `gemini-3-pro-image-preview` (Nano Banana Pro)
- **Secondary:** Imagen (quality-critical stills only)
- **fal enabled:** false (unless video/audio generation added to public studio)
- **OpenAI role:** optional multimodal QA, captioning, tagging

### Agency Workspace

- **Architecture:** Provider broker (not single-provider lock-in)
- **Stills / editing:** Gemini direct
- **Premium brand key art / logos / product visuals:** Imagen
- **UGC video / motion / voice / music / SFX:** fal.ai
- **Judge / eval / orchestration:** OpenAI multimodal

### Batch Asset Generation

- **Fast image-only batches:** Gemini direct (`gemini-2.5-flash-image`)
- **Premium still-image batches:** Imagen (`imagen-4` family)
- **Mixed-media batches:** fal.ai (async queue + webhook)

---

## OpenAI Multimodal Role

OpenAI is the preferred multimodal **understanding and evaluation** layer. It is not the default generation provider.

### Primary jobs

- Vision and document understanding
- OCR-adjacent extraction
- PDF parsing and multimodal RAG
- Image evaluation and creative quality review
- Speech/transcript processing
- Multimodal assistant orchestration
- Asset captioning, tagging, and summarization

### Non-primary jobs

OpenAI should not replace:

- Gemini direct for fast conversational image generation
- Imagen for premium-quality stills
- fal for mixed-media generation pipelines

### Surface-specific OpenAI roles

| Surface | OpenAI Jobs |
|---------|-------------|
| Landing Creative Studio | Multimodal QA, captioning, public assistant understanding |
| Agency Workspace | Judge/eval, multimodal understanding, asset review, routing |
| Document Intelligence | Vision/document understanding, OCR extraction, PDF-to-RAG |
| Creative Review | Output scoring, post-generation classification, approval support |

---

## fal.ai v0.1 Model Shortlist

Do not expose the entire fal catalog. Use this curated set:

### Images

| Model | Role |
|-------|------|
| `nano-banana-2` | Default fast generation/editing |
| `nano-banana-pro` | Premium generation/editing |
| `flux-pro/kontext` | Reference-edit / transform |
| `gpt-image-1.5` | High-fidelity fallback |

### Video

| Model | Role |
|-------|------|
| `kling-video/v3/pro/image-to-video` | Default premium UGC video |
| `kling-o3-image-to-video-pro` | Start/end-frame transition |
| `veo-3.1` | Google premium video |
| `ltx-2.3/image-to-video/fast` | Fast batch video |
| `ltx-2.3/extend-video` | Video extension |

### Utilities

| Model | Role |
|-------|------|
| `pixelcut/background-removal` | Background removal |
| `seedvr/upscale/image` | Upscaling |
| `omnilottie/image-to-lottie` | Motion graphics export |
| `vecglypher/image-to-svg` | Vector/logo/glyph |

---

## fal Production Policy

- Use hosted model queue endpoints first for v1
- Use `fal deploy` only when you need custom app logic, stable endpoint IDs, region/env control, or private auth
- Default production auth for custom deployed fal apps: **private**
- Prefer **rolling** rollout strategy for zero-downtime revisions
- n8n can call fal queue endpoints directly with header auth and JSON payloads

---

## Secondary Provider Policy

### Gemini API

Gemini is allowed as a secondary provider for public, advisory-only, non-tenant-aware surfaces (landing-page assistants, prototype research helpers). It is not the primary runtime/control plane for authenticated or governed assistants.

### Provider Adapter Contract

Landing and studio applications should implement a provider adapter interface:

```
provider = gemini | foundry | fal | openai | fallback
```

One assistant contract, one disclosure policy, one citation/provenance policy — regardless of provider.

---

## SSOT References

- Machine-readable: `ssot/creative/provider_policy.yaml`
- Assistant surfaces: `../agents/ASSISTANT_SURFACES.md`
- Model tiering: `docs/architecture/AI_RUNTIME_AUTHORITY.md`

---

*Last updated: 2026-03-23*
