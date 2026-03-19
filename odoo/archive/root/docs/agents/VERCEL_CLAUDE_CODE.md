# Vercel Claude Code via AI Gateway

> Route Claude Code (and all Anthropic SDK calls) through the Vercel AI Gateway
> for centralized observability, rate-limit management, and spend control.

---

## Why use Vercel AI Gateway

| Problem | AI Gateway solution |
|---------|---------------------|
| No visibility into Claude Code token usage | Logs every request with token counts, latency, model |
| Per-developer API keys scattered across machines | One gateway key per team; individual keys revocable |
| Hard to enforce model tier or spend limits | Gateway-level rate limits, model allow-lists |
| No audit trail for agent-generated changes | Request logs in Vercel dashboard for compliance |

---

## Environment variables

Set these on every machine running Claude Code or in any Vercel project using the Anthropic SDK:

```bash
# Route all Anthropic SDK calls through Vercel AI Gateway
ANTHROPIC_BASE_URL=https://ai-gateway.vercel.sh

# Vercel AI Gateway key (team scope — from vercel.com/[team]/~/ai-gateway/api-keys)
ANTHROPIC_AUTH_TOKEN=<ai-gateway-key>

# Leave ANTHROPIC_API_KEY empty — the gateway authenticates; direct key not needed
ANTHROPIC_API_KEY=
```

**Important**: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` are distinct from `ANTHROPIC_API_KEY`.
The SDK uses `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` for gateway routing; it falls back to
`ANTHROPIC_API_KEY` for direct API access. Leave `ANTHROPIC_API_KEY` empty to enforce gateway-only routing.

---

## Setting up the gateway

1. Go to `vercel.com/[your-team]/~/ai-gateway`
2. Create a new API key (scope: team or project)
3. Copy the key — you will only see it once
4. Add to `.env.local` (local) or Vercel project env vars (deployed)

---

## Claude Code CLI configuration

For the Claude Code CLI (`claude`), set env vars in your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export ANTHROPIC_BASE_URL=https://ai-gateway.vercel.sh
export ANTHROPIC_AUTH_TOKEN=<ai-gateway-key>
export ANTHROPIC_API_KEY=
```

Reload: `source ~/.zshrc`

Verify routing: Claude Code logs show `ai-gateway.vercel.sh` in request traces when `--verbose` is used.

---

## ops-console integration

The ops-console does **not** call Claude Code directly in client code.
All Anthropic SDK usage is server-side, through the AI Gateway:

```typescript
// apps/ops-console/lib/ai-client.ts (example — only on server)
import Anthropic from '@anthropic-ai/sdk'

// Picks up ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN from env
const anthropic = new Anthropic()
```

Environment variables for Vercel project settings:

| Variable | Value | Server/Client |
|----------|-------|---------------|
| `ANTHROPIC_BASE_URL` | `https://ai-gateway.vercel.sh` | Server only |
| `ANTHROPIC_AUTH_TOKEN` | AI Gateway key | Server only |
| `ANTHROPIC_API_KEY` | (empty) | — |

Never add `NEXT_PUBLIC_` prefix to these variables.

---

## Observability (what you get)

Via Vercel dashboard → AI Gateway:
- Request count per model per day
- Token input/output per request
- Latency (p50, p95, p99)
- Error rate by error type
- Cost estimate (based on published model pricing)

---

## Model allow-list (recommended)

Lock Claude Code to specific model tiers via AI Gateway policy:

| Tier | Model | Use case |
|------|-------|---------|
| Standard | `claude-haiku-4-5-20251001` | Quick edits, completions |
| Power | `claude-sonnet-4-6` | Primary development model |
| Max | `claude-opus-4-6` | Architecture decisions, complex PRs |

---

## Related

| File | Purpose |
|------|---------|
| `agents/claude/CLAUDE_CODE_POLICY.md` | Claude Code usage policy for this repo |
| `apps/ops-console/.env.agent.example` | Template env file for agent-enabled deployments |
| `docs/ops/VERCEL_MONOREPO.md` | ops-console project configuration |
