# Vercel AI Gateway + Observability — Team Plan Constraints

## TL;DR

| Feature | Team Plan | Notes |
|---------|-----------|-------|
| AI Gateway | ✅ Available | $5/mo included credits; PAYG after |
| Base Observability | ✅ Available | Retention and limits apply |
| Observability Plus | ❌ Not available | Pro/Enterprise owners only |

## AI Gateway (Team — available)

AI Gateway is available on **all plans** including Team. Every Vercel team account
gets **$5/month of included AI Gateway credits**; beyond that, token cost is
passed through at zero markup (including BYOK — Bring Your Own Key).

### Capability coverage (Team)

- Unified endpoint for 100+ models (OpenAI, Anthropic, Mistral, etc.)
- Image generation, video generation, web search
- Usage tracking and budget controls
- Zero data retention option
- Observability within the Gateway (request logs, latency, token usage)

### Environment contract (ops-console)

```
Server-only (never in NEXT_PUBLIC_*):
  AI_GATEWAY_API_KEY       — Vercel AI Gateway key
  OPENAI_API_KEY           — fallback if Gateway key absent

Client-safe:
  NEXT_PUBLIC_ENABLE_AI_QUERIES — "true" if either key is present
```

Route all model calls through the Gateway endpoint:

```
https://ai-gateway.vercel.sh/v1
```

Use the standard OpenAI-compatible `chat.completions.create` API with model
strings in `provider/model` format:

```
anthropic/claude-haiku-4-5-20251001
openai/gpt-4o-mini
```

Source: `apps/ops-console/app/api/ai/sql/route.ts`

## Base Observability (Team — available with limits)

Base Observability is available on all plans. Team plan includes:

- Web Analytics
- Speed Insights (Core Web Vitals)
- Logs (limited retention)
- Function logs

Retention limits are shorter than Pro/Enterprise. Exact current limits are shown
in the Vercel dashboard (they can change with plan updates).

## Observability Plus (Team — NOT available)

Observability Plus is an upgrade available only to **Pro and Enterprise** owners.
It is not available on Team. You cannot enable Plus while staying on Team.

### "Plus-equivalent" for Team (ops.* SSOT approach)

If you need deeper observability without upgrading, mirror events into Supabase:

```
ops.run_events       — deploy/approval/anomaly events
ops.ai_usage         — AI Gateway token usage (write from API route)
ops.deploy_history   — deployment outcomes + durations
```

Then surface these in ops-console dashboards (no external vendor required).

**Pattern:**

```
Vercel function (server route)
  └─ AI Gateway call
       └─ on completion: INSERT into ops.ai_usage via Supabase service role
            └─ ops-console /settings page reads usage aggregates
```

## Getting the AI Gateway key

1. Go to `vercel.com/[team]/~/ai-gateway/api-keys`
2. Create a key scoped to `tbwa/odooops-console` (or team-wide)
3. Store locally: `security add-generic-password -s "ai-gateway-api-key" -a "$USER" -w`
4. Generate `.env.local`: `./scripts/secrets/gen-env-local.sh`
5. Push to Vercel: `echo "$KEY" | vercel env add AI_GATEWAY_API_KEY production`

## Cross-references

- `docs/ops/SUPABASE_VERCEL.md` — env var sync contract
- `docs/ops/SUPABASE_N8N.md` — ops automation plane
- `apps/ops-console/app/api/ai/sql/route.ts` — AI Gateway integration code
- `scripts/secrets/keychain-setup.sh` — Keychain provisioning
