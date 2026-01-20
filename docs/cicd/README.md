# InsightPulse CI/CD Pipeline

Automated deployment pipeline for InsightPulse infrastructure using GitHub Actions, Supabase, n8n, and DigitalOcean.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                             │
│  ├── supabase/migrations/     (Database changes)                │
│  ├── supabase/functions/      (Edge Functions)                  │
│  ├── addons/                  (Odoo modules)                    │
│  ├── n8n/workflows/           (Automation workflows)            │
│  └── .github/workflows/       (CI/CD pipelines)                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Supabase      │    │ n8n           │    │ Odoo          │
│ (Auth/Data)   │    │ (Automation)  │    │ (ERP)         │
│               │    │               │    │               │
│ • Migrations  │    │ • Webhooks    │    │ • Docker      │
│ • Edge Funcs  │    │ • Slack cmds  │    │ • SSH deploy  │
│ • RLS         │    │ • Notifs      │    │ • Health chk  │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Quick Start

### 1. Set Up GitHub Secrets

Go to your repository → Settings → Secrets → Actions and add:

| Secret | Description |
|--------|-------------|
| `SUPABASE_ACCESS_TOKEN` | Personal access token from Supabase |
| `SUPABASE_DB_PASSWORD` | Database password |
| `SUPABASE_PROJECT_ID` | Production project ref (`spdtwktxdalcfigzeqrz`) |
| `SUPABASE_PROJECT_ID_STAGING` | Staging project ref (optional) |
| `SUPABASE_URL` | Project URL |
| `SUPABASE_ANON_KEY` | Anon/public key |
| `SUPABASE_SERVICE_KEY` | Service role key |
| `SSH_HOST` | Production server IP |
| `SSH_USER` | SSH username (usually `root` or `deploy`) |
| `SSH_PRIVATE_KEY` | SSH private key for deployment |
| `ODOO_DB_PASSWORD` | Odoo database password |
| `N8N_API_URL` | n8n API endpoint |
| `N8N_API_KEY` | n8n API key |
| `N8N_WEBHOOK_URL` | n8n webhook base URL |

### 2. Configure Environments

Create GitHub Environments for `staging` and `production`:
1. Go to Settings → Environments
2. Create `staging` environment
3. Create `production` environment with required reviewers

### 3. Initial Supabase Setup

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize in your project
supabase init

# Link to your project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Pull existing schema (if any)
supabase db pull

# Push initial migrations
supabase db push
```

## Workflows

### Main Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Supabase Deploy | `supabase-deploy.yml` | Push to `supabase/**` | Deploy migrations and Edge Functions |
| n8n Orchestrator | `n8n-orchestrator.yml` | Push to `n8n/**` | Validate and sync n8n workflows |
| InsightPulse CI/CD | `insightpulse-cicd.yml` | Push to main/develop | Unified multi-component deployment |
| Deploy Pipeline | `deploy.yml` | Push + manual | Full deployment with Docker builds |

### Path-Based Detection

The pipeline only deploys components that have changed:

| Path | Component | Action |
|------|-----------|--------|
| `supabase/migrations/**` | Supabase | Push migrations |
| `supabase/functions/**` | Supabase | Deploy Edge Functions |
| `addons/**` | Odoo | Build and deploy Docker image |
| `n8n/**` | n8n | Sync workflows via API |

### Environment Mapping

| Branch | Environment | Approval |
|--------|-------------|----------|
| `develop` | Staging | Automatic |
| `main` | Production | Manual (via GitHub Environment) |

## n8n Workflows

### Deployment Notifications

**File:** `n8n/workflows/deployment-notify.json`

Receives GitHub Actions webhook notifications and:
- Logs deployment to Supabase `deployment_logs` table
- Sends Slack notifications (success/failure)
- Alerts Mattermost on failures
- Tracks deployment statistics

### GitHub Deploy Trigger

**File:** `n8n/workflows/github-deploy-trigger.json`

Enables deployment triggers from n8n:
- Production deployments require approval
- Staging deployments are automatic
- All triggers are logged to Supabase

## Manual Deployment

### Via GitHub UI

1. Go to Actions → Select workflow
2. Click "Run workflow"
3. Select environment and component
4. Click "Run workflow"

### Via GitHub CLI

```bash
# Deploy all to staging
gh workflow run insightpulse-cicd.yml -f environment=staging -f component=all

# Deploy Supabase to production
gh workflow run supabase-deploy.yml -f environment=production

# Deploy Odoo only
gh workflow run insightpulse-cicd.yml -f environment=staging -f component=odoo
```

## Database Migrations

### Creating a New Migration

```bash
# Create migration file
supabase migration new my_migration_name

# Edit the file
vim supabase/migrations/TIMESTAMP_my_migration_name.sql

# Test locally
supabase db reset

# Commit and push
git add supabase/migrations/
git commit -m "feat(db): add my_migration_name migration"
git push
```

### Migration Best Practices

1. **Always use transactions** - Wrap DDL in `BEGIN;` and `COMMIT;`
2. **Make migrations idempotent** - Use `IF NOT EXISTS`, `OR REPLACE`
3. **Never modify existing migrations** - Create new ones instead
4. **Test locally first** - Run `supabase db reset` before pushing
5. **Include rollback comments** - Document how to reverse changes

### Migration Naming Convention

```
YYYYMMDD[HHMM]_description.sql
```

Examples:
- `20260120_add_deployment_logs.sql`
- `20260120153000_create_audit_schema.sql`

## Deployment Logs

### Supabase Schema

```sql
-- Deployment logs table (created automatically)
CREATE TABLE IF NOT EXISTS deployment_logs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  event_type text NOT NULL,
  environment text NOT NULL,
  commit_sha text,
  branch text,
  triggered_by text,
  status text NOT NULL,
  components jsonb,
  run_url text,
  deployed_at timestamptz NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Query deployment history
SELECT * FROM deployment_logs
ORDER BY created_at DESC
LIMIT 10;
```

## Monitoring

### Health Endpoints

| Service | Endpoint | Expected |
|---------|----------|----------|
| Odoo | `https://erp.insightpulseai.net/web/health` | `200 OK` |
| n8n | `https://n8n.insightpulseai.net/healthz` | `{"status": "ok"}` |
| Superset | `https://bi.insightpulseai.net/health` | `{"status": "OK"}` |

### n8n Health Monitoring

Configure n8n workflows to:
- Monitor health endpoints every 5 minutes
- Alert on 3 consecutive failures
- Track deployment frequency and success rates

## Troubleshooting

### Supabase Migration Failed

```bash
# Check migration status
supabase migration list --linked

# View schema diff
supabase db diff --linked

# Repair migration (CAUTION)
supabase migration repair --status reverted TIMESTAMP
```

### Odoo Deployment Failed

```bash
# SSH to server
ssh root@178.128.112.214

# Check container logs
docker logs odoo-prod --tail 100

# Check health endpoint
curl http://localhost:8069/web/health

# Rollback to previous image
docker run -d --name odoo ghcr.io/jgtolentino/odoo-ce:previous-sha
```

### n8n Workflow Import Failed

```bash
# Check n8n logs
docker logs n8n

# Verify API connectivity
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  https://n8n.insightpulseai.net/api/v1/workflows

# Validate workflow JSON
python3 -c "import json; json.load(open('n8n/workflows/workflow.json'))"
```

## Security

### Best Practices

- Never commit secrets to git
- Use GitHub Environments for production protection
- Require PR reviews for `main` branch
- Rotate SSH keys regularly
- Use strong, unique database passwords
- Enable RLS on all Supabase tables

### Secret Rotation

1. Generate new credentials
2. Update GitHub Secrets
3. Re-run deployment to verify
4. Revoke old credentials

## Related Documentation

- [Spec Bundle](../../spec/cicd-supabase-n8n/) - Constitution, PRD, Plan, Tasks
- [Supabase Config](../../supabase/config.toml) - Project configuration
- [n8n Workflows](../../n8n/workflows/) - Automation workflows
- [GitHub Workflows](../../.github/workflows/) - CI/CD pipelines

## License

AGPL-3.0 - See LICENSE file
