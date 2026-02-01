# Supabase Project Setup Evidence

**Date**: 2026-01-24 11:09:00 UTC
**Scope**: Supabase project integrations verification
**Project**: superset (`spdtwktxdalcfigzeqrz`)

## Project Configuration

| Property | Value |
|----------|-------|
| Project Name | superset |
| Project Reference | `spdtwktxdalcfigzeqrz` |
| Plan | Pro |
| Region | us-east-1 (AWS) |
| API URL | `https://spdtwktxdalcfigzeqrz.supabase.co` |

## GitHub Integration

**Status**: Connected

| Setting | Value |
|---------|-------|
| Repository | `jgtolentino/odoo-ce` |
| Supabase Directory | `supabase` |
| Production Branch | `main` |
| Deploy on Push | Enabled |
| Automatic Branching | Enabled |
| Branch Limit | 50 |
| Supabase Changes Only | Enabled |

### Integration Behavior

- Migrations in `supabase/migrations/` auto-deploy to production on push to `main`
- Preview branches created for PRs affecting `supabase/` directory
- Maximum 50 preview branches allowed

## Vercel Integration

**Status**: Connected

| Setting | Value |
|---------|-------|
| Team | `insightpulseai` |
| Created | 12 days ago |
| Added By | jgtolentino.rn@gmail.com |

### Connected Projects

| Project | Status | Added |
|---------|--------|-------|
| shelf.nu | Connected | 4 days ago |

### Environment Variable Configuration

- **Public Prefix**: `NEXT_PUBLIC_`
- Vercel Marketplace managed project
- Environment variables automatically synchronized

## AWS PrivateLink

**Status**: Not Configured (requires Team or Enterprise plan)

## Local Configuration Files

### supabase/config.toml

```toml
project_id = "spdtwktxdalcfigzeqrz"

[api]
port = 54321
schemas = ["public", "graphql_public"]
extra_search_path = ["public", "extensions"]
max_rows = 1000

[db]
port = 54322
major_version = 15

[auth]
enabled = true
site_url = "https://app.insightpulseai.com"
additional_redirect_urls = [
  "https://erp.insightpulseai.com",
  "https://n8n.insightpulseai.com",
  "https://bi.insightpulseai.com",
  "http://localhost:3000"
]
```

### supabase/.temp/project-ref

```
spdtwktxdalcfigzeqrz
```

## Environment Variables Reference

Documented in `.env.example`:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_PROJECT_REF` | Project reference ID |
| `SUPABASE_URL` | API endpoint |
| `NEXT_PUBLIC_SUPABASE_URL` | Next.js public URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Next.js public anon key |
| `SUPABASE_ANON_KEY` | Server-side anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side service role key |
| `POSTGRES_URL` | Pooled connection string |
| `POSTGRES_URL_NON_POOLING` | Direct connection string |

## Edge Functions Deployed

Total: 30+ edge functions

| Function | JWT Verification |
|----------|------------------|
| copilot-chat | false |
| github-mattermost-bridge | false |
| github-app-auth | true |
| infra-memory-ingest | true |
| schema-changed | true |
| tenant-invite | true |
| cron-processor | true |
| ipai-copilot | false |
| sync-odoo-modules | false |

## Migrations

Total: 50+ migrations covering:

- Core schemas and tenancy (`1000_CORE_SCHEMAS_AND_TENANCY`)
- Engine schemas (TE_CHEQ, DOC_OCR, PPM_FIRM)
- Odoo CE/OCA sync metadata
- Multi-engine governance
- Knowledge base (kb_core, kb_blocks)
- Infrastructure graph
- MCP jobs observability
- Skill certification
- Control room workbench

## Verification Checklist

- [x] Project reference matches config (`spdtwktxdalcfigzeqrz`)
- [x] GitHub integration connected to correct repo
- [x] Vercel integration active with correct team
- [x] Edge functions configured in config.toml
- [x] Environment variables documented
- [x] Migrations directory populated

## Deprecated Projects (DO NOT USE)

Per CLAUDE.md:
- `xkxyvboeubffxxbebsll` (old project)
- `ublqmilcjtpnflofprkr` (OPEX project only)
