# Control Plane (Supabase Management API)

Server-side proxy for Supabase Management API operations.

## Architecture

```
Agents / CI / n8n Workflows
         ↓
    Control Plane API
    (Edge Function or Server)
         ↓
    Supabase Management API
    (with PAT - server-side only)
```

## Security Model

**CRITICAL**: Never expose Management API PAT to clients.

- PAT (Personal Access Token) stored as server-side secret only
- All platform operations go through authenticated proxy endpoints
- Client apps use standard Supabase client (anon/service_role keys)
- Audit trail via `ops.runs` schema

## Supported Operations

| Operation | Endpoint | Use Case |
|-----------|----------|----------|
| List projects | `GET /api/platform/projects` | Dashboard, monitoring |
| Get project | `GET /api/platform/projects/:ref` | Project details |
| Rotate keys | `POST /api/platform/projects/:ref/rotate-keys` | Key rotation workflow |
| Get secrets | `GET /api/platform/projects/:ref/secrets` | Audit, validation |
| Set secrets | `POST /api/platform/projects/:ref/secrets` | Deploy workflows |

## Environment Variables

```bash
# Server-side only (never expose to client)
SUPABASE_ACCESS_TOKEN=sbp_xxxxxxxxxxxx

# Standard Supabase client keys (can be public)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Usage from CI/Agents

```typescript
// Example: Start a run and track with ops schema
const runId = await supabase.rpc('start_run', {
  p_actor: 'ci-agent',
  p_repo: 'jgtolentino/odoo-ce',
  p_ref: 'main',
  p_pack_id: 'supabase-enterprise-parity-baseline',
  p_input: { trigger: 'push' }
});

// Log progress
await supabase.rpc('log_event', {
  p_run_id: runId,
  p_level: 'info',
  p_message: 'Applying migrations'
});

// Complete with output
await supabase.rpc('complete_run', {
  p_run_id: runId,
  p_output: { migrations_applied: 5 }
});
```

## Usage from n8n Workflows

```json
{
  "nodes": [
    {
      "name": "Start Run",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{ $env.SUPABASE_URL }}/rest/v1/rpc/start_run",
        "method": "POST",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            { "name": "p_actor", "value": "n8n" },
            { "name": "p_pack_id", "value": "n8n-workflow-as-code" }
          ]
        }
      }
    }
  ]
}
```

## Related Files

- `packages/config/template-packs.json` - Template pack registry
- `supabase/migrations/20260125_000002_ops_run_system.sql` - Ops schema
- `supabase/migrations/20260125_000001_secret_registry.sql` - Secret tracking
- `AGENTS.md` - Agent operating contract
