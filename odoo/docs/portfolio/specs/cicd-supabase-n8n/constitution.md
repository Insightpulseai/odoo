# CI/CD with Supabase + n8n — Constitution

## Non-Negotiables

1. **No manual deployments to production** — All production changes must go through CI/CD pipelines
2. **Path-based change detection** — Only deploy components that have actually changed
3. **Secrets never in code** — All credentials stored in GitHub Secrets or environment variables
4. **Rollback capability** — Every deployment must be reversible
5. **Evidence required** — All deployments must produce audit logs

## Architecture Constraints

### Deployment Flow

```
GitHub Push → Change Detection → [Supabase | Odoo | n8n] → Notify
                  ↓
              Path Filters:
              - supabase/** → Deploy Supabase
              - addons/**   → Deploy Odoo
              - n8n/**      → Sync n8n
```

### Environment Separation

| Branch | Environment | Approval |
|--------|-------------|----------|
| `develop` | Staging | Automatic |
| `main` | Production | Manual (workflow_dispatch) or automatic with gates |

### Component Isolation

- Supabase, Odoo, and n8n deployments are **independent**
- Failure in one component does not block others
- Cross-component dependencies handled via webhooks/events

## Security Boundaries

### Required Secrets

| Secret | Purpose | Scope |
|--------|---------|-------|
| `SUPABASE_ACCESS_TOKEN` | Supabase CLI auth | All Supabase operations |
| `SUPABASE_DB_PASSWORD` | Database access | Migrations only |
| `SSH_PRIVATE_KEY` | Server access | Odoo deployment only |
| `N8N_API_KEY` | n8n API auth | Workflow sync only |
| `GITHUB_TOKEN` | GitHub API | Automatic (provided by Actions) |

### Forbidden Actions

- Direct database access from CI (use Supabase CLI)
- Hardcoded credentials in workflow files
- Deployment without health checks
- Skipping notification steps

## Integration Rules

### n8n Webhook Contract

All deployment events sent to n8n must include:

```json
{
  "event": "string",
  "environment": "staging|production",
  "commit": "string",
  "branch": "string",
  "actor": "string",
  "timestamp": "ISO8601"
}
```

### Supabase Migration Rules

- Migrations must be idempotent
- Naming: `YYYYMMDD[HHMM]_description.sql`
- No destructive operations without explicit confirmation
- Edge functions must pass Deno type checking

### n8n Workflow Requirements

- All workflows must have `name`, `nodes`, and `connections`
- Valid JSON syntax required
- Credentials referenced by ID (not embedded)
