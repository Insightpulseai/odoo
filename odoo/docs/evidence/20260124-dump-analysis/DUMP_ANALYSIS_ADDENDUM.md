# Dump Analysis Addendum — OCR Engines + Ops Workbench

**Date**: 2026-01-24
**Continuation of**: `DUMP_ANALYSIS_CONSOLIDATED.md`

---

## DUMP 5: PaddleOCR + VLM Router Architecture

### Summary (5 bullets)
- Keep PaddleOCR as deterministic baseline for `plain_ocr` and `find` modes
- Route to VLM (DeepSeek) only for `describe` and `freeform` modes
- Fallback pattern: if primary engine fails, try secondary
- Normalized coordinates (0..1) for device-independent overlays
- Engine selection is mode-driven, not random

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **Router pattern for OCR** | Cost control + determinism for simple tasks | Doc-OCR engine in MCP |
| 2 | **Fallback chain** | Resilience when primary engine fails | All external API integrations |
| 3 | **Normalized boxes (0..1)** | Device-independent rendering | Mobile/web overlay components |
| 4 | **Mode-based routing matrix** | Clear decision boundaries | `route_engine()` function pattern |
| 5 | **PaddleOCR for cost/latency** | VLM is expensive; baseline should be cheap | Default engine selection |

### Gaps / Risks
- No timeout handling on engine calls
- No circuit breaker for repeated failures
- Fallback error context could be lost
- No A/B testing or canary routing
- Mobile offline case not addressed in router

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Add engine routing to doc-ocr MCP server**
```typescript
// mcp/servers/doc-ocr-server/src/router.ts
type Mode = "plain_ocr" | "describe" | "find" | "freeform";
type Engine = "paddle" | "vlm";

interface RouteResult {
  primary: Engine;
  fallback: Engine;
}

export function routeEngine(mode: Mode): RouteResult {
  switch (mode) {
    case "plain_ocr":
      return { primary: "paddle", fallback: "vlm" };
    case "find":
      return { primary: "paddle", fallback: "vlm" };
    case "describe":
    case "freeform":
      return { primary: "vlm", fallback: "paddle" };
    default:
      return { primary: "paddle", fallback: "vlm" };
  }
}
```

**2. Add fallback wrapper**
```typescript
// mcp/servers/doc-ocr-server/src/fallback.ts
export async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  ctx: { traceId: string }
): Promise<T & { fallback_used?: boolean; primary_error?: string }> {
  try {
    return await primary();
  } catch (e) {
    console.log(JSON.stringify({
      trace_id: ctx.traceId,
      event: "fallback_triggered",
      error: String(e),
    }));
    const result = await fallback();
    return { ...result, fallback_used: true, primary_error: String(e) };
  }
}
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Circuit breaker for engine health**
```typescript
// mcp/servers/doc-ocr-server/src/circuit-breaker.ts
interface CircuitState {
  failures: number;
  lastFailure: number;
  open: boolean;
}

const circuits = new Map<string, CircuitState>();

export function isCircuitOpen(engine: string, threshold = 5, resetMs = 60000): boolean {
  const state = circuits.get(engine);
  if (!state) return false;
  if (state.open && Date.now() - state.lastFailure > resetMs) {
    // Half-open: allow one attempt
    state.open = false;
    return false;
  }
  return state.open;
}

export function recordFailure(engine: string, threshold = 5): void {
  const state = circuits.get(engine) ?? { failures: 0, lastFailure: 0, open: false };
  state.failures++;
  state.lastFailure = Date.now();
  if (state.failures >= threshold) {
    state.open = true;
  }
  circuits.set(engine, state);
}

export function recordSuccess(engine: string): void {
  circuits.set(engine, { failures: 0, lastFailure: 0, open: false });
}
```

---

## DUMP 6: PaddleOCR + LandingAI ADE Integration

### Summary (5 bullets)
- LandingAI ADE (`landingai-ade` pip package) for structured document extraction
- PaddleOCR for offline/cost-control/fallback
- ADE returns "chunks" (structured markdown), tables, fields
- Single API with `engine` query param for routing
- ADE requires `VISION_AGENT_API_KEY` environment variable

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **ADE for schema extraction** | Tables, fields, layout awareness | Invoice/receipt processing |
| 2 | **Paddle for baseline** | Fast, cheap, deterministic | Default engine |
| 3 | **Engine interface pattern** | Pluggable, testable | `OCREngine` protocol |
| 4 | **Chunks output format** | Structured markdown for downstream | RAG ingestion, indexing |
| 5 | **`engine` param on API** | Client chooses, server routes | `/api/ocr?engine=paddle|landingai` |

### Gaps / Risks
- ADE API key management (secrets rotation)
- ADE rate limits and pricing not documented
- `agentic-doc` repo marked legacy; ensure using correct package
- PaddleOCR dependency pinning is complex (CPU/GPU variants)
- No batch processing for ADE (single doc per call)

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Add `VISION_AGENT_API_KEY` to .env.example**
```bash
# .env.example addition
# LandingAI ADE (Agentic Document Extraction)
VISION_AGENT_API_KEY=your_landingai_api_key_here
```

**2. Create engine config in Supabase secrets**
```sql
-- Store engine configs in vault (not plain env)
-- Use Supabase Vault for production secrets
INSERT INTO vault.secrets (name, secret, description)
VALUES ('VISION_AGENT_API_KEY', 'sk-xxx', 'LandingAI ADE API key')
ON CONFLICT (name) DO NOTHING;
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Implement OCR engine edge function**
```typescript
// supabase/functions/doc-ocr/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

type Engine = "paddle" | "landingai" | "auto";

interface OcrRequest {
  engine: Engine;
  mode: string;
  prompt?: string;
}

serve(async (req) => {
  const url = new URL(req.url);
  const engine = (url.searchParams.get("engine") ?? "auto") as Engine;
  const mode = url.searchParams.get("mode") ?? "plain_ocr";

  // Route based on engine
  if (engine === "landingai" || (engine === "auto" && mode === "describe")) {
    return await callLandingAI(req);
  }
  return await callPaddleBackend(req);
});

async function callLandingAI(req: Request): Promise<Response> {
  const apiKey = Deno.env.get("VISION_AGENT_API_KEY");
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "VISION_AGENT_API_KEY not configured" }), { status: 500 });
  }
  // TODO: Implement ADE API call
  return new Response(JSON.stringify({ engine: "landingai", chunks: [] }));
}

async function callPaddleBackend(req: Request): Promise<Response> {
  // TODO: Proxy to PaddleOCR backend service
  return new Response(JSON.stringify({ engine: "paddle", text: "", boxes: [] }));
}
```

---

## DUMP 7: Ops Workbench Schema (Databricks-like Layer)

### Summary (5 bullets)
- `ops` schema: `job_defs`, `runs`, `run_events`, `artifacts`
- Implements job queue pattern: queued → running → succeeded/failed
- Event log for observability (`run_events` with phase/level)
- Artifacts stored in Supabase Storage with metadata in DB
- RLS: deny-all by default, service_role only writes

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **Job queue in Postgres** | No external queue dependency | Complements `mcp_jobs` |
| 2 | **Run events = observability** | Phase-level logging (claim/download/parse/persist) | Debugging pipeline failures |
| 3 | **Artifacts with storage_ref** | Metadata in DB, files in Storage | Document processing outputs |
| 4 | **Job definitions** | Reusable pipeline templates | `doc-ingest`, `invoice-extract`, etc. |
| 5 | **Claim pattern** | FOR UPDATE SKIP LOCKED for concurrency | High-throughput processing |

### Gaps / Risks
- Simple claim (no SKIP LOCKED) won't scale
- No retry logic with exponential backoff
- Artifacts bucket creation manual (not in migration)
- No dead letter queue for permanent failures
- `ops` schema overlaps with existing `mcp_jobs` schema

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Evaluate overlap with existing `mcp_jobs` schema**
```sql
-- Compare schemas
\dt mcp_jobs.*
\dt ops.*

-- Decision: merge into mcp_jobs or keep separate?
-- Recommendation: EXTEND mcp_jobs rather than create ops
```

**2. Add artifact tracking to mcp_jobs**
```sql
-- supabase/migrations/YYYYMMDD_mcp_jobs_artifacts.sql
CREATE TABLE IF NOT EXISTS mcp_jobs.artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES mcp_jobs.jobs(id) ON DELETE CASCADE,
  kind TEXT NOT NULL, -- markdown, json, table, image, export
  name TEXT NOT NULL,
  storage_ref JSONB NOT NULL, -- {bucket, path, content_type, bytes, sha256}
  meta JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS artifacts_job_id_idx ON mcp_jobs.artifacts(job_id);
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Add claim RPC with SKIP LOCKED**
```sql
-- supabase/migrations/YYYYMMDD_mcp_jobs_claim_rpc.sql
CREATE OR REPLACE FUNCTION mcp_jobs.claim_next_job(
  p_worker_id TEXT,
  p_job_types TEXT[] DEFAULT NULL
)
RETURNS mcp_jobs.jobs AS $$
DECLARE
  claimed_job mcp_jobs.jobs;
BEGIN
  SELECT * INTO claimed_job
  FROM mcp_jobs.jobs
  WHERE status = 'queued'
    AND (p_job_types IS NULL OR job_type = ANY(p_job_types))
  ORDER BY priority DESC, created_at ASC
  FOR UPDATE SKIP LOCKED
  LIMIT 1;

  IF claimed_job.id IS NOT NULL THEN
    UPDATE mcp_jobs.jobs
    SET status = 'running',
        claimed_by = p_worker_id,
        claimed_at = NOW(),
        updated_at = NOW()
    WHERE id = claimed_job.id;

    -- Refresh the row
    SELECT * INTO claimed_job FROM mcp_jobs.jobs WHERE id = claimed_job.id;
  END IF;

  RETURN claimed_job;
END;
$$ LANGUAGE plpgsql;
```

**2. Add job definitions table to mcp_jobs**
```sql
-- supabase/migrations/YYYYMMDD_mcp_jobs_defs.sql
CREATE TABLE IF NOT EXISTS mcp_jobs.job_defs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  default_config JSONB DEFAULT '{}',
  steps JSONB DEFAULT '[]', -- ["parse", "split", "extract"]
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Seed default job definitions
INSERT INTO mcp_jobs.job_defs (slug, name, description, steps)
VALUES
  ('doc-ingest', 'Document Ingest', 'Parse documents into structured chunks', '["parse", "split", "extract"]'),
  ('invoice-extract', 'Invoice Extraction', 'Extract fields from invoices', '["parse", "extract"]'),
  ('ocr-batch', 'OCR Batch', 'Batch OCR processing', '["ocr"]')
ON CONFLICT (slug) DO NOTHING;
```

#### (c) Strategic Refactor (1-2 months)

**1. Full document processing pipeline**
- Integrate ADE + PaddleOCR as job step executors
- Add Delta/Parquet export step for Databricks
- Build Workbench UI for runs/artifacts/review

---

## UPDATED CONSOLIDATED THEMES

| # | Theme | Source Dumps | Priority |
|---|-------|--------------|----------|
| 1 | Typed contracts everywhere | 1, 3 | P0 |
| 2 | Structured logging + trace IDs | 1, 3, 7 | P0 |
| 3 | Branch protection + release gates | 2 | P0 |
| 4 | Engine routing with fallback | 5, 6 | P1 |
| 5 | Eval harness for agents | 3 | P1 |
| 6 | Circuit breaker for external APIs | 5 | P1 |
| 7 | Job artifacts tracking | 7 | P1 |
| 8 | Claim RPC with SKIP LOCKED | 7 | P1 |
| 9 | ReWOO batch execution | 3 | P2 |
| 10 | Document processing pipeline | 6, 7 | P2 |

---

## UPDATED TARGET ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Document Processing Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input Sources (Mobile, Web, API)                                       │
│       │                                                                  │
│       ▼                                                                  │
│   ┌────────────────────────────────────────┐                            │
│   │         /api/ocr?engine=...            │                            │
│   │         Supabase Edge Function         │                            │
│   └────────────────┬───────────────────────┘                            │
│                    │                                                     │
│          ┌─────────┴─────────┐                                          │
│          │   Engine Router   │                                          │
│          │  (mode → engine)  │                                          │
│          └────────┬──────────┘                                          │
│                   │                                                      │
│     ┌─────────────┼─────────────┐                                       │
│     │             │             │                                        │
│     ▼             ▼             ▼                                        │
│ ┌───────┐   ┌─────────┐   ┌─────────┐                                   │
│ │Paddle │   │LandingAI│   │ VLM/    │                                   │
│ │  OCR  │   │   ADE   │   │DeepSeek │                                   │
│ └───┬───┘   └────┬────┘   └────┬────┘                                   │
│     │            │             │                                         │
│     └────────────┴─────────────┘                                        │
│                   │                                                      │
│                   ▼                                                      │
│   ┌────────────────────────────────────────┐                            │
│   │            mcp_jobs Queue              │                            │
│   │  - jobs (queued → running → done)      │                            │
│   │  - job_runs (execution history)        │                            │
│   │  - job_events (phase-level logs)       │                            │
│   │  - artifacts (storage_ref + metadata)  │                            │
│   └────────────────┬───────────────────────┘                            │
│                    │                                                     │
│                    ▼                                                     │
│   ┌────────────────────────────────────────┐                            │
│   │         Supabase Storage               │                            │
│   │  - chunks.jsonl                        │                            │
│   │  - tables.parquet                      │                            │
│   │  - extracted_fields.json               │                            │
│   └────────────────────────────────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ADDITIONAL BACKLOG ITEMS

### P1 — Important (Next 2 Weeks)

| Item | Effort | Risk | Files |
|------|--------|------|-------|
| Engine router in Edge Function | 4h | Low | `supabase/functions/doc-ocr/` |
| Fallback wrapper with logging | 2h | Low | `supabase/functions/_shared/fallback.ts` |
| Circuit breaker for engines | 4h | Medium | `supabase/functions/_shared/circuit-breaker.ts` |
| Add artifacts table to mcp_jobs | 2h | Low | `supabase/migrations/` |
| Add claim_next_job RPC | 2h | Low | `supabase/migrations/` |

### P2 — Strategic (Next Month)

| Item | Effort | Risk | Files |
|------|--------|------|-------|
| LandingAI ADE integration | 16h | Medium | `supabase/functions/doc-ocr/` |
| PaddleOCR backend service | 16h | Medium | `apps/paddle-ocr-service/` |
| Document Workbench UI | 24h | Medium | `apps/control-room/` |
| Delta/Parquet export step | 8h | Medium | `supabase/functions/export-delta/` |

---

## DECISION: mcp_jobs vs ops schema

**Recommendation**: Extend `mcp_jobs` rather than create parallel `ops` schema.

**Rationale**:
1. `mcp_jobs` already has jobs + job_runs + job_events
2. Adding `artifacts` + `job_defs` keeps single source of truth
3. Avoids confusion about which queue to use
4. Existing observability (metrics views) applies automatically

**Migration path**:
```sql
-- Add missing tables to mcp_jobs (not ops)
-- mcp_jobs.artifacts
-- mcp_jobs.job_defs
-- Update existing jobs table with job_def reference if needed
```

---

## DONE CHECKLIST (Updated)

- [ ] All Edge Functions return `{data, meta}` envelope with `request_id`
- [ ] Engine router implemented with mode → engine mapping
- [ ] Fallback wrapper logs to job_events
- [ ] Circuit breaker prevents cascading failures
- [ ] `mcp_jobs.artifacts` table exists with storage_ref
- [ ] `mcp_jobs.job_defs` table exists with step definitions
- [ ] `claim_next_job()` RPC uses SKIP LOCKED
- [ ] `VISION_AGENT_API_KEY` in .env.example and Vault
