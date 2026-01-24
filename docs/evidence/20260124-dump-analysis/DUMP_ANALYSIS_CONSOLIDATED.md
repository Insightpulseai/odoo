# Consolidated Dump Analysis — Engineering Upgrade Roadmap

**Date**: 2026-01-24
**Analyst**: Claude Agent (Opus 4.5)
**Target Stack**: odoo-ce (Supabase + Vercel + GitHub + MCP/Pulser agents)

---

## DUMP 1: DeepSeek OCR React + FastAPI Scaffold

### Summary (5 bullets)
- Full-stack scaffold: React+TS+Tailwind frontend + FastAPI backend + Docker Compose
- Mock OCR API with typed Pydantic models (Box, OcrResponse)
- Bounding box overlay rendering on uploaded images
- Structured response: `raw_model_response` + `metadata` separation
- Environment-driven API base URL (`VITE_API_BASE`)

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **Typed API contracts (Pydantic)** | Prevents runtime type errors, enables OpenAPI auto-gen | `supabase/functions/*/index.ts` - add Zod schemas |
| 2 | **Raw response + metadata separation** | Debug visibility without polluting main response | All Edge Functions should return `{data, meta, debug}` |
| 3 | **Mock-first development** | UI development unblocked before backend ready | Add mock mode to MCP tools |
| 4 | **Overlay coordinate system** | Visual debugging for spatial AI tasks | Relevant for doc-ocr engine |
| 5 | **Docker Compose dev parity** | Local mirrors prod topology | Already have; validate it matches |

### Gaps / Risks
- No authentication on `/api/ocr/image` endpoint
- No rate limiting or file size validation
- Mock coordinates use hardcoded 1000x600 space (not actual image dims)
- No error schema (just string messages)
- No health check beyond `/healthz`
- No structured logging or trace IDs

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Add Zod schemas to Edge Functions**
```bash
# File: supabase/functions/_shared/schemas.ts
# Add typed request/response contracts
```

```typescript
// supabase/functions/_shared/schemas.ts
import { z } from "zod";

export const ApiResponseSchema = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    data: dataSchema,
    meta: z.object({
      request_id: z.string(),
      timestamp: z.string(),
      latency_ms: z.number(),
    }),
    debug: z.record(z.unknown()).optional(),
  });

export const ErrorResponseSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.unknown()).optional(),
  }),
  meta: z.object({
    request_id: z.string(),
    timestamp: z.string(),
  }),
});
```

**Verification:**
```bash
cd supabase/functions && npx tsc --noEmit
```

**2. Add request_id to all Edge Function responses**
```typescript
// Pattern for all Edge Functions
const request_id = crypto.randomUUID();
const start = Date.now();

// ... function logic ...

return new Response(JSON.stringify({
  data: result,
  meta: { request_id, timestamp: new Date().toISOString(), latency_ms: Date.now() - start }
}), { headers: { "Content-Type": "application/json", "X-Request-ID": request_id } });
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Mock mode for MCP tools**
```bash
# File: mcp/servers/odoo-erp-server/src/mock.ts
# Add MOCK_MODE env var support
```

```typescript
// mcp/servers/odoo-erp-server/src/config.ts
export const MOCK_MODE = process.env.MOCK_MODE === "true";

// In tool handlers:
if (MOCK_MODE) {
  return getMockResponse(toolName, args);
}
```

**Verification:**
```bash
MOCK_MODE=true npm run test:integration
```

#### (c) Strategic Refactor (1-2 months)

**1. Unified API response envelope across all services**
- Standardize `{data, meta, debug?, error?}` envelope
- Add OpenAPI spec generation from Zod schemas
- Integrate with Supabase client types

---

## DUMP 2: Vibe Coding Critique → Workflow Controls

### Summary (5 bullets)
- Critique of rapid-build tools (Replit, Lovable, Manus, Base44)
- Core argument: speed without structure leads to "one change breaks everything"
- Missing in vibe coding: version control, branching, dev/prod separation, release process
- Recommended stack: Firebase + GitHub + Cursor (structured + fast)
- Key insight: "Most vibe coders need better workflow, not faster building"

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **Branch protection is non-negotiable** | Prevents accidental prod breaks | `.github/workflows/`, branch rules |
| 2 | **DEV vs PROD environment separation** | Test before you break users | Supabase branching, Vercel preview |
| 3 | **Release gates before merge** | CI must pass, not optional | `all-green-gates.yml` |
| 4 | **Rollback strategy must exist** | Recovery when things go wrong | Tagged releases, migration rollback |
| 5 | **"Building fast is easy; stable wins"** | Long-term mindset over demo velocity | Culture + CI enforcement |

### Gaps / Risks
- The critique is philosophical, not implementation-specific
- Firebase recommendation doesn't map to Supabase stack
- No mention of database migration rollback
- No mention of feature flags for gradual rollout
- Assumes solo dev workflow (no team PR review process)

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Verify branch protection rules**
```bash
gh api repos/jgtolentino/odoo-ce/branches/main/protection | jq '.required_status_checks, .required_pull_request_reviews'
```

**Expected output:**
- `required_status_checks.strict: true`
- `required_pull_request_reviews.required_approving_review_count: >= 1`

**If missing, set:**
```bash
gh api -X PUT repos/jgtolentino/odoo-ce/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["ci-odoo-ce","spec-kit-enforce"]}' \
  -f required_pull_request_reviews='{"required_approving_review_count":1}'
```

**2. Add pre-push hook for local CI**
```bash
# File: .githooks/pre-push
cat > .githooks/pre-push << 'EOF'
#!/bin/bash
set -e
echo "Running local CI checks..."
./scripts/ci_local.sh
EOF
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Supabase preview branches for PRs**
Already configured per dashboard. Verify:
```bash
# Check if preview branch exists for current PR
gh pr view --json headRefName | jq -r '.headRefName'
# Supabase should auto-create preview for PRs touching supabase/
```

**2. Add release tagging workflow**
```yaml
# .github/workflows/release-tag.yml
name: Release Tag
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '*.md'

jobs:
  tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get next version
        id: version
        run: |
          LAST=$(git tag -l 'v*' --sort=-v:refname | head -n1 || echo "v0.0.0")
          NEXT=$(echo $LAST | awk -F. '{print $1"."$2"."$3+1}')
          echo "version=$NEXT" >> $GITHUB_OUTPUT
      - name: Create tag
        run: |
          git tag ${{ steps.version.outputs.version }}
          git push origin ${{ steps.version.outputs.version }}
```

#### (c) Strategic Refactor (1-2 months)

**1. Feature flags system**
```sql
-- supabase/migrations/YYYYMMDD_feature_flags.sql
CREATE SCHEMA IF NOT EXISTS flags;

CREATE TABLE flags.features (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  enabled BOOLEAN DEFAULT false,
  rollout_pct INT DEFAULT 0 CHECK (rollout_pct BETWEEN 0 AND 100),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION flags.is_enabled(feature_name TEXT, user_id UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
  SELECT CASE
    WHEN NOT EXISTS (SELECT 1 FROM flags.features WHERE name = feature_name) THEN false
    WHEN (SELECT enabled FROM flags.features WHERE name = feature_name) = false THEN false
    WHEN user_id IS NULL THEN true
    ELSE (SELECT rollout_pct FROM flags.features WHERE name = feature_name) > (abs(hashtext(user_id::text)) % 100)
  END;
$$ LANGUAGE sql STABLE;
```

---

## DUMP 3: Agentic AI Production Guide → Agent Runtime

### Summary (5 bullets)
- 8 foundational agent patterns: ReAct, Reflection, Tool Use, Planning, Multi-agent, CodeAct, ReWOO, Routing
- Critique: frameworks add opacity; build thin runtime with strong observability
- Decision matrix: framework for MVP, custom for production
- "Minimal viable agent": 1 agent, small tool set, loop until done, few LLM calls
- Key insight: "You can't scale what you can't measure" — eval infrastructure is critical

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **ReWOO for independent tool calls** | Plan upfront, parallel execute, token-efficient | MCP coordinator batch mode |
| 2 | **ReAct for dependent tool calls** | Stepwise observation when order matters | Default agent loop |
| 3 | **Typed tool contracts** | Deterministic dispatch, testable | `mcp/servers/*/tools/` |
| 4 | **Structured logging from day one** | Every LLM call, tool call, decision logged | Supabase `mcp_jobs.job_events` |
| 5 | **Eval harness is not optional** | Regression gates, quality measurement | `evals/` directory pattern |
| 6 | **Router pattern** | Intent → specialized agent/workflow | MCP coordinator routing |
| 7 | **Libraries over frameworks** | Pydantic/Zod for validation, plain code for orchestration | Current approach validates |
| 8 | **Trace IDs everywhere** | Correlate across services | `X-Request-ID` header propagation |

### Gaps / Risks
- No concrete eval framework provided (just "build one")
- ReWOO requires knowing tool independence upfront
- Multi-agent coordination complexity underestimated
- No mention of cost tracking per agent run
- No mention of timeout/circuit breaker patterns

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Add trace ID propagation to MCP coordinator**
```typescript
// mcp/coordinator/src/middleware/tracing.ts
import { randomUUID } from "crypto";

export function withTracing(handler: Function) {
  return async (req: Request, ...args: unknown[]) => {
    const traceId = req.headers.get("X-Trace-ID") ?? randomUUID();
    const spanId = randomUUID().slice(0, 8);

    // Inject into context
    const ctx = { traceId, spanId, startTime: Date.now() };

    try {
      const result = await handler(req, ...args, ctx);
      return result;
    } finally {
      console.log(JSON.stringify({
        trace_id: traceId,
        span_id: spanId,
        duration_ms: Date.now() - ctx.startTime,
        // ... other fields
      }));
    }
  };
}
```

**2. Add tool call logging to job_events**
```sql
-- Already exists in mcp_jobs schema, verify usage:
INSERT INTO mcp_jobs.job_events (job_id, event_type, payload)
VALUES ($1, 'tool_call', jsonb_build_object(
  'tool', $2,
  'args', $3,
  'result', $4,
  'duration_ms', $5
));
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Implement ReWOO batch execution mode**
```typescript
// mcp/coordinator/src/loops/rewoo.ts
interface ToolPlan {
  tool: string;
  args: Record<string, unknown>;
  depends_on?: string[]; // IDs of other planned calls
}

export async function executeReWOO(
  plan: ToolPlan[],
  toolRegistry: ToolRegistry,
  ctx: TraceContext
): Promise<Map<string, ToolResult>> {
  const results = new Map<string, ToolResult>();
  const pending = [...plan];

  while (pending.length > 0) {
    // Find executable (no unresolved dependencies)
    const executable = pending.filter(p =>
      !p.depends_on?.some(dep => !results.has(dep))
    );

    if (executable.length === 0 && pending.length > 0) {
      throw new Error("Circular dependency in tool plan");
    }

    // Execute in parallel
    const batch = await Promise.all(
      executable.map(async (p) => {
        const result = await toolRegistry.execute(p.tool, p.args, ctx);
        return { id: p.tool, result };
      })
    );

    // Store results, remove from pending
    batch.forEach(({ id, result }) => {
      results.set(id, result);
      const idx = pending.findIndex(p => p.tool === id);
      if (idx >= 0) pending.splice(idx, 1);
    });
  }

  return results;
}
```

**2. Create eval harness scaffold**
```bash
mkdir -p evals/{cases,runners,reports}

cat > evals/cases/sample.jsonl << 'EOF'
{"id":"ocr-001","input":{"image":"fixtures/invoice.png","mode":"find","prompt":"total amount"},"expected":{"contains":"$1,234.56"}}
{"id":"agent-001","input":{"task":"create project","params":{"name":"Test"}},"expected":{"status":"completed","has_id":true}}
EOF

cat > evals/runners/run_evals.ts << 'EOF'
import { readFileSync } from "fs";

interface EvalCase {
  id: string;
  input: Record<string, unknown>;
  expected: Record<string, unknown>;
}

async function runEvals(casesFile: string) {
  const cases: EvalCase[] = readFileSync(casesFile, "utf-8")
    .split("\n")
    .filter(Boolean)
    .map(line => JSON.parse(line));

  const results = [];
  for (const c of cases) {
    const result = await executeCase(c);
    results.push({ ...c, result, pass: checkExpected(result, c.expected) });
  }

  console.log(JSON.stringify({ total: cases.length, passed: results.filter(r => r.pass).length, results }, null, 2));
}

// TODO: Implement executeCase and checkExpected
EOF
```

#### (c) Strategic Refactor (1-2 months)

**1. Full agent observability dashboard**
- Supabase view aggregating `mcp_jobs.jobs` + `job_runs` + `job_events`
- Metrics: success rate, latency p50/p95/p99, token usage, cost
- Alerts: failure rate > 10%, latency spike, DLQ growth

```sql
-- supabase/migrations/YYYYMMDD_agent_observability_views.sql
CREATE OR REPLACE VIEW mcp_jobs.agent_metrics_hourly AS
SELECT
  date_trunc('hour', created_at) AS hour,
  source,
  job_type,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'completed') AS completed,
  COUNT(*) FILTER (WHERE status = 'failed') AS failed,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) * 1000) AS avg_duration_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (updated_at - created_at)) * 1000) AS p95_duration_ms
FROM mcp_jobs.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY 1, 2, 3;
```

---

## DUMP 4: Kubernetes Service Discovery → Deploy Topology

### Summary (5 bullets)
- Services provide stable DNS + virtual IP for ephemeral Pods
- Label selectors are the contract between Service and Pods
- Service types: ClusterIP (internal), NodePort (basic external), LoadBalancer (cloud)
- DNS discovery: `service-name.namespace.svc.cluster.local`
- Headless Services for StatefulSets (per-pod DNS)

### High-Value Takeaways

| # | Takeaway | Why It Matters | Where It Fits |
|---|----------|----------------|---------------|
| 1 | **DNS-based discovery is default** | No hardcoded IPs, dynamic resolution | Docker Compose service names |
| 2 | **Label selector = contract** | Mismatch = zero endpoints | docker-compose.yml service labels |
| 3 | **Health endpoints required** | K8s probes; also good for any deploy | All services need `/healthz` |
| 4 | **Headless for stateful** | Direct pod addressing | PostgreSQL, Redis if scaled |
| 5 | **EndpointSlices over Endpoints** | Scalable backend | Future-proofing |

### Gaps / Risks
- odoo-ce currently uses Docker Compose, not K8s
- K8s concepts don't directly translate to Supabase Edge Functions
- Overengineering risk if K8s not actually needed
- NetworkPolicy not relevant without K8s

### Upgrade Proposals

#### (a) Immediate Quick Wins (1-2 days)

**1. Standardize health endpoints across all services**
```bash
# Verify existing health endpoints
grep -r "healthz\|health\|ready" docker-compose.yml deploy/docker-compose.yml
```

**Pattern to apply:**
```yaml
# docker-compose.yml healthcheck pattern
services:
  odoo-core:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

**2. Add health endpoint to all Edge Functions**
```typescript
// supabase/functions/_shared/health.ts
export function handleHealth(req: Request): Response | null {
  if (new URL(req.url).pathname === "/healthz") {
    return new Response(JSON.stringify({ ok: true, ts: Date.now() }), {
      headers: { "Content-Type": "application/json" }
    });
  }
  return null;
}

// Usage in each function:
const healthResponse = handleHealth(req);
if (healthResponse) return healthResponse;
```

#### (b) Medium Upgrades (1-2 weeks)

**1. Service dependency graph documentation**
```bash
# Generate from docker-compose
cat > scripts/gen_service_graph.sh << 'EOF'
#!/bin/bash
echo "digraph services {"
docker compose config --format json | jq -r '
  .services | to_entries[] |
  .key as $svc |
  (.value.depends_on // {} | keys[]) as $dep |
  "  \"\($svc)\" -> \"\($dep)\";"
'
echo "}"
EOF
chmod +x scripts/gen_service_graph.sh
./scripts/gen_service_graph.sh > docs/architecture/SERVICE_GRAPH.dot
```

#### (c) Strategic Refactor (1-2 months)

**1. K8s migration prep (only if scaling requires it)**
- Document current Docker Compose topology
- Create Helm chart scaffold mirroring compose
- Add Kustomize overlays for dev/staging/prod

*Note: Only pursue if Docker Compose becomes a bottleneck. Current stack is appropriate for scale.*

---

## CONSOLIDATED THEMES

| # | Theme | Source Dumps | Priority |
|---|-------|--------------|----------|
| 1 | **Typed contracts everywhere** | 1, 3 | P0 |
| 2 | **Structured logging + trace IDs** | 1, 3 | P0 |
| 3 | **Branch protection + release gates** | 2 | P0 |
| 4 | **Eval harness for agents** | 3 | P1 |
| 5 | **Mock mode for development** | 1 | P1 |
| 6 | **Health endpoints standardization** | 4 | P1 |
| 7 | **ReWOO batch execution** | 3 | P2 |
| 8 | **Feature flags system** | 2 | P2 |

---

## TARGET END-STATE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Production Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GitHub (PR + CI Gates)                                                 │
│       │                                                                  │
│       ├── Branch Protection (main)                                       │
│       ├── Required Checks: [ci-odoo-ce, spec-kit-enforce, evals]        │
│       └── Auto-tag on merge                                              │
│                                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│   │   Vercel    │    │  Supabase   │    │   Odoo CE   │                │
│   │  (Frontend) │    │  (Backend)  │    │   (ERP)     │                │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                │
│          │                  │                  │                        │
│          └────────┬─────────┴─────────┬────────┘                        │
│                   │                   │                                  │
│            ┌──────▼──────┐    ┌───────▼───────┐                         │
│            │     MCP     │    │   mcp_jobs    │                         │
│            │ Coordinator │◄──►│  (Job Queue)  │                         │
│            └──────┬──────┘    └───────────────┘                         │
│                   │                                                      │
│     ┌─────────────┼─────────────┐                                       │
│     │             │             │                                        │
│ ┌───▼───┐   ┌─────▼─────┐  ┌────▼────┐                                  │
│ │ ReAct │   │   ReWOO   │  │ Router  │                                  │
│ │ Loop  │   │  (Batch)  │  │ (Intent)│                                  │
│ └───┬───┘   └─────┬─────┘  └────┬────┘                                  │
│     │             │             │                                        │
│     └─────────────┴─────────────┘                                       │
│                   │                                                      │
│            ┌──────▼──────┐                                               │
│            │ Tool Registry│ ← Typed contracts (Zod)                     │
│            │ + Trace IDs  │ ← Structured logging                        │
│            └──────────────┘                                              │
│                                                                          │
│   Observability: trace_id → job_events → metrics_hourly → alerts        │
│   Evals: cases.jsonl → run_evals.ts → CI gate                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PRIORITIZED BACKLOG

### P0 — Critical (This Week)

| Item | Effort | Risk | Files |
|------|--------|------|-------|
| Add Zod schemas to Edge Functions | 4h | Low | `supabase/functions/_shared/schemas.ts` |
| Add trace ID to all responses | 2h | Low | `supabase/functions/*/index.ts` |
| Verify branch protection rules | 1h | Low | GitHub API |
| Add pre-push hook | 1h | Low | `.githooks/pre-push` |

### P1 — Important (Next 2 Weeks)

| Item | Effort | Risk | Files |
|------|--------|------|-------|
| Create eval harness scaffold | 8h | Medium | `evals/` |
| Add mock mode to MCP tools | 4h | Low | `mcp/servers/*/src/mock.ts` |
| Standardize health endpoints | 4h | Low | `supabase/functions/_shared/health.ts` |
| Add release tagging workflow | 2h | Low | `.github/workflows/release-tag.yml` |
| Service dependency graph | 2h | Low | `scripts/gen_service_graph.sh` |

### P2 — Strategic (Next Month)

| Item | Effort | Risk | Files |
|------|--------|------|-------|
| ReWOO batch execution | 16h | Medium | `mcp/coordinator/src/loops/rewoo.ts` |
| Feature flags system | 8h | Medium | `supabase/migrations/` |
| Agent observability views | 8h | Low | `supabase/migrations/` |
| Full observability dashboard | 16h | Medium | Supabase + Vercel |

---

## EXECUTION PLAN

### Week 1 (P0 items)

```bash
# Day 1-2: Typed contracts
mkdir -p supabase/functions/_shared
# Create schemas.ts with Zod contracts
# Update 3-5 Edge Functions to use schemas

# Day 3: Trace IDs
# Add X-Request-ID header to all Edge Function responses
# Update mcp_jobs insert to include trace_id

# Day 4: Branch protection
gh api repos/jgtolentino/odoo-ce/branches/main/protection | jq .
# Configure if missing

# Day 5: Pre-push hook
cat > .githooks/pre-push << 'EOF'
#!/bin/bash
set -e
./scripts/ci_local.sh
EOF
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

**Verification:**
```bash
# Schemas compile
cd supabase/functions && npx tsc --noEmit

# Trace IDs present
curl -sI https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/healthz | grep -i x-request-id

# Branch protection active
gh api repos/jgtolentino/odoo-ce/branches/main/protection | jq '.required_status_checks'

# Pre-push works
git stash && git stash pop  # No-op to test hook path
```

### Week 2-3 (P1 items)

```bash
# Eval harness
mkdir -p evals/{cases,runners,reports}
# Create sample cases and runner script

# Mock mode
# Add MOCK_MODE env var support to MCP servers

# Health endpoints
# Create shared health.ts, apply to all functions

# Release tagging
# Add .github/workflows/release-tag.yml
```

**Verification:**
```bash
# Evals run
npm run evals -- --cases evals/cases/sample.jsonl

# Mock mode works
MOCK_MODE=true npm run test:mcp

# Health endpoints respond
for fn in copilot-chat ipai-copilot sync-odoo-modules; do
  curl -sS "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/$fn/healthz" | jq .ok
done
```

### Month 2 (P2 items)

- Implement ReWOO in MCP coordinator
- Deploy feature flags migration
- Create agent observability views
- Build dashboard (Supabase + Vercel)

---

## CI/CD GATES

Add to `.github/workflows/all-green-gates.yml`:

```yaml
jobs:
  schema-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: cd supabase/functions && npx tsc --noEmit

  eval-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run evals -- --cases evals/cases/regression.jsonl --threshold 0.95

  trace-id-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          grep -r "X-Request-ID" supabase/functions/*/index.ts || exit 1
```

---

## ROLLBACK STRATEGY

| Component | Rollback Method |
|-----------|-----------------|
| Supabase migrations | `supabase db reset` to last known good, or manual `DROP`/`ALTER` |
| Edge Functions | `supabase functions deploy <fn> --version <prev>` |
| Vercel frontend | Instant rollback via Vercel dashboard or `vercel rollback` |
| MCP servers | Revert commit, redeploy container |
| Feature flags | `UPDATE flags.features SET enabled = false WHERE name = $1` |

---

## DONE CHECKLIST

- [ ] All Edge Functions return `{data, meta}` envelope with `request_id`
- [ ] `X-Request-ID` header present on all API responses
- [ ] Branch protection requires CI pass before merge
- [ ] Pre-push hook runs `ci_local.sh`
- [ ] Eval harness exists with ≥10 test cases
- [ ] Health endpoint responds 200 on all services
- [ ] Release tags auto-created on merge to main
- [ ] Trace IDs correlate across MCP coordinator → job_events
