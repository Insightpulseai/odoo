# Foundry–Odoo Auth and Endpoint Policy

> Contract ID: C-30-AUTH
> Version: 1.1.0
> Last updated: 2026-03-14
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)

## Endpoint Policy

| Surface | When to Use | When NOT to Use |
|---------|-------------|-----------------|
| Foundry project endpoint | Hosted agent runtime, tools, grounding, tracing, evals | Raw completion-only workloads |
| Azure OpenAI endpoint | OpenAI-compatible surface explicitly required (e.g. SDK constraints) | Default agent operations |

**Canonical target:**

```
Odoo bridge
  → server-side adapter (foundry_service.py / server.ts)
    → Foundry project endpoint / agent service
      → tools / grounding / evaluations / tracing
```

**Not:**

```
Odoo bridge
  → ad hoc direct API-key call
    → generic completion endpoint
```

## Auth Preference Order

| Priority | Method | When Allowed |
|----------|--------|-------------|
| 1 | Managed identity (DefaultAzureCredential / IMDS) | Production, staging |
| 2 | Entra service principal (client credentials) | CI/CD, automated pipelines |
| 3 | API key (env var, never hardcoded) | Non-prod bootstrap, local dev only |

### Promotion Rules

- Stage 1 (Explore): API key acceptable
- Stage 2 (Expand): Must migrate to managed identity or Entra SP
- Stage 3 (Hardened): API key forbidden in all environments

## Forbidden Patterns

1. **Browser-side Foundry credentials** — all Foundry calls must be server-side
2. **API key in source code** — always env var, never committed
3. **API key in CI logs** — mask in workflows, never echo
4. **Client-side agent ID** — agent resolution happens server-side only
5. **Shared API key across environments** — each environment gets its own key
6. **API key as permanent production auth** — must be replaced by managed identity before Stage 3

## Service-to-Service Auth (Docs Widget → Odoo)

The documentation widget's Express proxy authenticates to Odoo via:

- Header: `X-Copilot-Service-Key`
- Validation: `hmac.compare_digest` (constant-time comparison)
- Key source: `IPAI_COPILOT_SERVICE_KEY` env var on both sides
- This key is separate from the Foundry API key

## Entra Tenant Context

**Tenant**: `ceoinsightpulseai.onmicrosoft.com` (Entra ID Free, cloud-only)

Current state supports the auth preference order above:
- 3 app registrations exist — service principal path is viable
- Managed identity available via Azure Container Apps
- No hybrid identity (Entra Connect not enabled) — keeps auth model simple

**Identity gaps to close before Stage 2:**
- Enforce MFA for all admin/privileged users
- Migrate to converged Authentication methods policy
- Register dedicated service principal for CI/CD

See `ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` for full assessment.

## Key Rotation

- API keys: rotate every 90 days in non-prod, not applicable in prod (use managed identity)
- Service keys (`IPAI_COPILOT_SERVICE_KEY`): rotate every 180 days
- Managed identity: no rotation needed (handled by Azure)
