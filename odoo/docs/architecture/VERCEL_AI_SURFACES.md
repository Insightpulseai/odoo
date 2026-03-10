# Vercel AI Surfaces Contract

**Status**: Active
**SSOT registrations**: `ssot/integrations/vercel-agent.yaml`, `ssot/integrations/vercel-ai-gateway.yaml`
**References**:
- Vercel Agent: https://vercel.com/agent
- Vercel AI Gateway: https://vercel.com/ai-gateway

---

## Overview

Two distinct Vercel AI surfaces are in use:

| Surface | Purpose | Role in this repo |
|---------|---------|-------------------|
| **Vercel Agent** | GitHub PR review assistant | Advisory — findings forwarded to `ops.advisor_findings` |
| **Vercel AI Gateway** | Unified LLM routing endpoint | Execution surface — all server-side model calls route through it |

Neither surface is an SSOT. Both are registered as execution surfaces in `ssot/integrations/` to
satisfy Rule 9 of the SSOT Platform Rules (cross-domain changes require a contract doc).

---

## Vercel Agent

### What It Is

Vercel Agent is an AI assistant invoked via `@vercel` mentions in GitHub pull request comments.
It performs automated code review with awareness of Vercel-specific deployment patterns: framework
detection, environment variable usage, build configuration, and edge runtime constraints.

### Invocation Pattern

```
# In a GitHub PR comment:
@vercel check this deployment config
@vercel will this build on Edge Runtime?
```

### Advisory-Only Policy

Vercel Agent output is **advisory only**. It does not gate merges and its suggestions carry no
higher authority than a human reviewer comment.

Agent findings that identify actionable issues are forwarded to the internal ops advisor pipeline:

```
Vercel Agent suggestion
  → ops.advisor_findings (Supabase table)
    → reviewed by on-call engineer
      → actioned if valid, dismissed with note if not
```

Agent suggestions MUST NOT be auto-applied without human review. No automation reads Agent output
and applies code changes.

### Scope Boundary

Vercel Agent has read access to the pull request diff and may reference Vercel documentation.
It does not have write access to the repository, does not deploy, and does not modify Vercel
project settings.

---

## Vercel AI Gateway

### What It Is

Vercel AI Gateway is a single HTTPS endpoint that proxies requests to multiple LLM providers
(OpenAI, Anthropic, Mistral, Google, Cohere, and others). It provides:

- **Unified billing**: All provider costs consolidated in one Vercel dashboard
- **Observability**: Request/response logging, latency, token counts, cost per call
- **Provider failover**: Configurable fallback chains (e.g. GPT-4o → Claude 3.5 Sonnet)
- **Rate limiting**: Per-route and per-user quotas configurable without code changes

### Integration Pattern

All server-side LLM calls in `apps/*` and `packages/*` MUST route through the Gateway:

```typescript
// Correct — route through AI Gateway
const response = await fetch(process.env.VERCEL_AI_GATEWAY_URL + "/openai/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.VERCEL_AI_GATEWAY_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "gpt-4o",
    messages: [...],
  }),
});

// Incorrect — direct provider call (bypasses observability + billing)
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
```

### Observability: Logging to `ops.run_events`

Every Gateway call that produces a business event MUST be logged to `ops.run_events` with the
following fields:

| Field | Source | Notes |
|-------|--------|-------|
| `provider` | `"openai"` / `"anthropic"` / etc. | Provider name extracted from Gateway response headers |
| `model` | `"gpt-4o"` / `"claude-3-5-sonnet-20241022"` / etc. | Model ID from response body |
| `request_id` | `x-vercel-ai-request-id` response header | Gateway-assigned trace ID |
| `cost_usd` | `x-vercel-ai-cost` response header (if available) | Decimal USD; null if not provided |
| `input_tokens` | `usage.prompt_tokens` | From provider response |
| `output_tokens` | `usage.completion_tokens` | From provider response |
| `surface` | `"vercel-ai-gateway"` | Constant; identifies the execution surface |
| `run_id` | Caller-assigned UUID | Links to the parent `ops.runs` row |

### Plan Compatibility

Vercel AI Gateway is available on **all Vercel plans**, including Hobby and Pro. Enterprise is not
required. The Gateway is enabled by default for any Vercel project; no additional opt-in is needed.

---

## Key Boundary Rules

### Gateway API Key Must Never Reach the Client Bundle

`VERCEL_AI_GATEWAY_API_KEY` is a **server-only secret**. It must never appear in:

- Client-side JavaScript bundles (`app/` or `pages/` directory code that runs in the browser)
- `next.config.js` `publicRuntimeConfig` or any `NEXT_PUBLIC_*` environment variable
- `vercel.json` (values are not stored in files — see Vercel Monorepo Contract)
- Any log output (CI logs, Supabase Edge Function logs, browser console)

The Gateway URL (`VERCEL_AI_GATEWAY_URL`) may be exposed client-side only if Vercel provides a
purpose-built client SDK that handles authentication on the server side. Direct key exposure is
always forbidden.

### Agent Output Is Advisory, Not Authoritative

Vercel Agent comments on PRs do not constitute approval. The Vercel Agent:

- Cannot merge PRs
- Cannot trigger deployments
- Cannot modify `ssot/vercel/projects.yaml` or any SSOT file
- Cannot create GitHub issues or assign reviewers

Any action taken as a result of an Agent suggestion requires a human approval step in the PR
review process.

---

## Secrets Management

| Secret | Store | Access pattern |
|--------|-------|----------------|
| `vercel_ai_gateway_api_key` | Supabase Vault + Vercel environment variables | Server-side only; never client bundle |
| `vercel_ai_gateway_url` | Vercel environment variables | Server-side preferred; client-safe if using client SDK |
| Vercel Agent credentials | Managed by Vercel (no team-owned secret) | Installed as GitHub App; no manual key management |

Secret identifiers (not values) are registered in `ssot/secrets/registry.yaml` under the
`vercel-ai` consumer group.

Retrieve at runtime:

```typescript
// In a Vercel Serverless Function or Edge Function
const gatewayUrl = process.env.VERCEL_AI_GATEWAY_URL;     // injected by Vercel
const gatewayKey = process.env.VERCEL_AI_GATEWAY_API_KEY;  // injected by Vercel; never log this
```

---

## SSOT Registration

Both surfaces are registered as execution surfaces (not SSOT) in `ssot/integrations/`:

```yaml
# ssot/integrations/vercel-agent.yaml
surface: vercel-agent
role: advisory
authority: false          # not authoritative — findings are advisory only
output_sink: ops.advisor_findings
invocation: "@vercel in GitHub PR comments"

# ssot/integrations/vercel-ai-gateway.yaml
surface: vercel-ai-gateway
role: llm-routing
authority: false          # not SSOT — gateway is an execution surface
log_sink: ops.run_events
secret_store: supabase-vault + vercel-env
plan_requirement: any     # available on all Vercel plans
```

---

## Reference

- Vercel Agent: https://vercel.com/agent
- Vercel AI Gateway: https://vercel.com/ai-gateway
- Monorepo contract: `docs/architecture/VERCEL_MONOREPO_CONTRACT.md`
- Secrets SSOT: `ssot/secrets/registry.yaml`
- `ops.run_events` schema: `supabase/migrations/` (search `run_events`)
- `ops.advisor_findings` schema: `supabase/migrations/` (search `advisor_findings`)
