# Skill: fal.ai — Generative Media Inference Platform

source: https://fal.ai/docs
extracted: 2026-03-15
applies-to: agents, ops-platform, lakehouse

## What it is
Unified API for 1,000+ generative media models (image, video, audio, 3D, speech).
Serverless model deployment (your own models, same infra).
Compute: dedicated GPU instances (H100 SXM, 8×H100) for training/fine-tuning.

## When to use (decision matrix)

| Workload | Use |
|---|---|
| Call hosted model (SDXL, Sora-class, etc.) | Model API via `fal_client.subscribe()` |
| Deploy custom/fine-tuned model as endpoint | fal Serverless (`fal.App` class) |
| Training run, fine-tuning, batch ETL on GPU | fal Compute (hourly, SSH) |
| Real-time streaming output | WebSocket endpoint |
| Async queue (long jobs) | `queue.fal.run` + webhook |

## Core API pattern (async queue — preferred for IPAI)

```
POST https://queue.fal.run/{model-id}
Authorization: Key $FAL_KEY
→ returns request_id
→ poll or webhook on completion
```

## fal.App serverless pattern

```python
class MyModel(fal.App):
    machine_type = "GPU-H100"
    min_concurrency = 0   # scale to zero
    max_concurrency = 10

    def setup(self):           # runs once per runner (warm)
        self.model = load()

    @fal.endpoint("/")
    def generate(self, prompt: str):
        return self.model(prompt)
```

## SSOT/SOR mapping
- fal is NEITHER SSOT nor SOR — it is a stateless compute layer
- Job state (request_id, status, result_url) → `ops.runs` + `ops.run_events` (Supabase SSOT)
- Outputs (images, video, audio) → Supabase Storage with metadata in Postgres
- Model registry (which fal model ID maps to which IPAI capability) → `ops.model_registry`

## Integration pattern for IPAI

```
User request (ops-console / web)
  → Supabase Edge Function (ops-platform)
      → enqueue to ops.inference_jobs (Supabase Queue)
  → Edge Function worker
      → POST queue.fal.run/{model-id}
      → store request_id in ops.runs
  → Webhook from fal → Edge Function
      → update ops.run_events (completed/failed)
      → write output URL to Supabase Storage
      → emit Realtime event to ops-console
```

## Gaps / watch
- No native multi-tenant RLS — auth is API-key only; enforce tenant isolation at Edge Function layer
- Shared mode (`app_auth="shared"`) — callers pay own usage; useful for portal surfaces
- Cold starts: use `min_concurrency=1` for latency-sensitive paths; `concurrency_buffer` for spikes
- Secrets required: `FAL_KEY` in Azure Key Vault
