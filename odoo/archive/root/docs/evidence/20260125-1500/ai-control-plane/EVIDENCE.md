# AI Control Plane Implementation Evidence

**Date:** 2026-01-25 15:00 UTC
**Scope:** AI Control Plane with Vercel AI Gateway + Supabase Vault

## Summary

Implemented the AI Control Plane infrastructure with:
- Supabase control_plane schema with Vault integration for secure secret management
- Next.js app (ai-control-plane) with BugBot and Vercel Bot API routes
- Supabase Edge Function for runtime secret access from any runtime (DO, Vercel, n8n)

## Components Shipped

### 1. Supabase Migration: control_plane Schema

**File:** `supabase/migrations/20260125_100001_control_plane_vault.sql`

**Tables:**
- `control_plane.secret_index` - Maps logical secret names to Vault IDs
- `control_plane.secret_access_log` - Audit trail for secret access
- `control_plane.bot_registry` - Registry of control plane bots and permissions
- `control_plane.bot_execution_log` - Execution history for bot operations

**Functions:**
- `control_plane.get_secret(p_name)` - Get secret by name (SECURITY DEFINER)
- `control_plane.get_secret_logged(...)` - Get secret with audit logging
- `control_plane.bot_can_access_secret(...)` - Check bot permissions
- `control_plane.register_secret(...)` - Register new secret in Vault
- `public.control_plane_get_secret(...)` - Public RPC wrapper
- `public.control_plane_get_secret_logged(...)` - Public RPC wrapper with logging

**Seeded Bots:**
| Bot ID | Type | Allowed Secrets |
|--------|------|-----------------|
| bugbot | sre | DIGITALOCEAN_API_TOKEN, OPENAI_API_KEY, SUPABASE_SERVICE_ROLE_KEY, SENTRY_DSN |
| vercel-bot | deployment | VERCEL_API_TOKEN, OPENAI_API_KEY, GITHUB_TOKEN |
| do-infra-bot | infra | DIGITALOCEAN_API_TOKEN, DO_SPACES_ACCESS_KEY, DO_SPACES_SECRET_KEY |
| n8n-orchestrator | general | SUPABASE_SERVICE_ROLE_KEY, N8N_API_KEY |

### 2. Next.js App: ai-control-plane

**Location:** `apps/ai-control-plane/`

**API Routes:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/bugbot` | POST | AI SRE & debugging assistant |
| `/api/bugbot` | GET | Health check |
| `/api/vercel-bot` | POST | Deployment SRE (status, suggest) |
| `/api/vercel-bot` | GET | Health check |
| `/api/control-plane` | POST | Secret access and proxying |
| `/api/control-plane` | GET | List available secrets (metadata only) |

**Dependencies:**
- Next.js 14.2
- Vercel AI SDK (ai@3.4.0)
- Supabase JS (2.48.0)
- Zod for validation

### 3. Supabase Edge Function: bugbot-control-plane

**Location:** `supabase/functions/bugbot-control-plane/index.ts`

**Modes:**
- `raw` - Return decrypted secret value directly
- `proxy` - Proxy API call using secret as Bearer token
- `exchange` - Return secret (future: short-lived token exchange)

**Allowed Proxy Hosts:**
- api.digitalocean.com
- api.vercel.com
- api.openai.com
- api.anthropic.com
- api.github.com

## File Manifest

```
supabase/migrations/20260125_100001_control_plane_vault.sql
apps/ai-control-plane/
├── package.json
├── tsconfig.json
├── next.config.js
├── .env.example
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/
│       ├── bugbot/route.ts
│       ├── vercel-bot/route.ts
│       └── control-plane/route.ts
└── lib/
    ├── supabase.ts
    └── types.ts
supabase/functions/bugbot-control-plane/index.ts
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI Control Plane                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Vercel Sandbox (ai-control-plane)                                       │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │
│  │    BugBot     │  │  Vercel Bot   │  │ Control Plane │                │
│  │  /api/bugbot  │  │/api/vercel-bot│  │/api/control-  │                │
│  │               │  │               │  │    plane      │                │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                │
│          │                  │                  │                         │
│          └──────────────────┴──────────────────┘                         │
│                            │                                             │
│                            ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   Vercel AI Gateway                              │    │
│  │  (OpenAI, Anthropic routing, caching, rate limiting)            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                            │                                             │
├────────────────────────────┼────────────────────────────────────────────┤
│                            │                                             │
│  Supabase (Control Plane DB)                                            │
│  ┌─────────────────────────┴───────────────────────────────────────┐    │
│  │                   control_plane schema                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │ secret_index │  │ bot_registry │  │ bot_execution_log    │  │    │
│  │  │ (Vault refs) │  │ (permissions)│  │ (audit trail)        │  │    │
│  │  └──────┬───────┘  └──────────────┘  └──────────────────────┘  │    │
│  │         │                                                       │    │
│  │         ▼                                                       │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │              Supabase Vault (encrypted secrets)          │  │    │
│  │  │  DIGITALOCEAN_API_TOKEN, VERCEL_API_TOKEN, OPENAI_KEY   │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                            │                                             │
│  ┌─────────────────────────┴───────────────────────────────────────┐    │
│  │            Edge Function: bugbot-control-plane                   │    │
│  │  (Runtime secret access for DO, n8n, external consumers)        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     External Infrastructure                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ DigitalOcean │  │    Vercel    │  │   GitHub     │  │    n8n      │  │
│  │   Droplets   │  │ Deployments  │  │   Issues     │  │  Workflows  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Verification Commands

```bash
# Apply Supabase migration
supabase db push

# Deploy Edge Function
supabase functions deploy bugbot-control-plane

# Install app dependencies
cd apps/ai-control-plane && npm install

# Run local dev server
npm run dev  # Runs on port 3100

# Test BugBot endpoint
curl -X POST http://localhost:3100/api/bugbot \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "message": "Test error message",
    "service": "odoo-core",
    "severity": "medium"
  }'

# Test Vercel Bot endpoint
curl -X POST http://localhost:3100/api/vercel-bot \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "my-project",
    "action": "status"
  }'

# Test Edge Function (after deploy)
curl -X POST "https://<PROJECT>.supabase.co/functions/v1/bugbot-control-plane" \
  -H "Content-Type: application/json" \
  -d '{"secretName": "DIGITALOCEAN_API_TOKEN", "mode": "raw"}'
```

## Deployment

### Vercel Deployment

```bash
cd apps/ai-control-plane

# Link to Vercel project
npx vercel link

# Set environment variables
npx vercel env add SUPABASE_URL
npx vercel env add SUPABASE_SERVICE_ROLE_KEY
npx vercel env add OPENAI_API_KEY
npx vercel env add CONTROL_PLANE_AUTH_TOKEN

# Deploy
npx vercel deploy --prod
```

### Supabase Deployment

```bash
# Push migration
supabase db push

# Deploy Edge Function
supabase functions deploy bugbot-control-plane
```

## Security Considerations

1. **Secret Isolation**: All secrets stored in Supabase Vault, encrypted at rest
2. **Access Control**: Bot permissions defined in bot_registry table
3. **Audit Logging**: All secret access logged with accessor, timestamp, IP
4. **Proxy Allowlist**: Only known API hosts can be proxied
5. **Auth Token**: Control plane protected by CONTROL_PLANE_AUTH_TOKEN

## Next Steps

1. Register actual secrets in Vault (one-time setup via SQL editor)
2. Configure Vercel AI Gateway for centralized AI routing
3. Wire n8n workflows to call bugbot-control-plane Edge Function
4. Add GitHub issue creation to BugBot for critical errors
5. Implement token exchange for short-lived credentials
