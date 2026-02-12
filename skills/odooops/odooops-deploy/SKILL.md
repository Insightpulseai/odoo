---
name: odooops-deploy
description: Deploy Odoo applications to OdooOps platform (Odoo.sh Next). Use this skill when the user requests deployment actions such as "Deploy my Odoo app", "Create a preview environment", "Deploy to staging", "Promote to production", or "Push this live". Requires ODOOOPS_TOKEN for authentication.
metadata:
  author: insightpulseai
  version: "1.0.0"
  platform: odooops
---

# OdooOps Deploy

Deploy Odoo projects to OdooOps platform (Odoo.sh Next) with ephemeral preview environments, staging, and production deployments.

## How It Works

1. Authenticates with OdooOps API using `ODOOOPS_TOKEN`
2. Triggers build for current branch + commit SHA
3. Creates environment (dev/preview/staging/prod) based on branch policy
4. Waits for environment to be ready (up to 20 minutes)
5. Returns **Environment URL** and **Deployment ID**

## Usage

```bash
bash /mnt/skills/user/odooops-deploy/scripts/deploy.sh [stage] [branch]
```

**Arguments:**
- `stage` - Environment stage: `dev`, `preview`, `staging`, `prod` (defaults to `preview`)
- `branch` - Git branch name (defaults to current branch)

**Environment Variables:**
- `ODOOOPS_API_BASE` - API base URL (e.g., `https://api.odooops.io`)
- `ODOOOPS_TOKEN` - Authentication token (required)
- `ODOOOPS_PROJECT_ID` - Project ID (required)

**Examples:**

```bash
# Deploy current branch to preview environment
bash /mnt/skills/user/odooops-deploy/scripts/deploy.sh

# Deploy specific branch to staging
bash /mnt/skills/user/odooops-deploy/scripts/deploy.sh staging feat/new-module

# Deploy to production (requires approval)
bash /mnt/skills/user/odooops-deploy/scripts/deploy.sh prod main
```

## Output

```
Creating deployment for branch: feat/new-module
Stage: preview
Commit SHA: abc123...

Triggering build...
✓ Build started: build_xyz789

Creating environment...
✓ Environment created: env_preview_abc123

Waiting for environment to be ready... (max 20 minutes)
[====================] 100%

✓ Deployment successful!

Environment URL: https://preview-abc123.odooops.app
Environment ID:  env_preview_abc123
Build ID:        build_xyz789
Commit SHA:      abc123def456
```

The script also outputs JSON to stdout for programmatic use:

```json
{
  "environmentUrl": "https://preview-abc123.odooops.app",
  "environmentId": "env_preview_abc123",
  "buildId": "build_xyz789",
  "commitSha": "abc123def456",
  "stage": "preview",
  "branch": "feat/new-module"
}
```

## Environment Stages

### Preview (default)
- **Purpose**: Per-PR ephemeral environments
- **Lifetime**: TTL-based (auto-cleanup after merge/close)
- **Features**: Neutralized (email capture, test mode payments)
- **Cost**: Budget-capped, scale-to-zero when idle

### Staging
- **Purpose**: Pre-production validation
- **Lifetime**: Persistent until explicitly destroyed
- **Features**: Production-like, masked data from prod snapshot
- **Cost**: Always-on, moderate resources

### Production
- **Purpose**: Live customer-facing environment
- **Lifetime**: Permanent
- **Features**: Full functionality, backups, SLO guarantees
- **Cost**: High-availability, auto-scaling

## Branch Policies

OdooOps automatically maps branches to stages based on patterns:

- `main` or `master` → `prod`
- `release/*` or `staging` → `staging`
- `feature/*`, `feat/*`, `fix/*` → `preview` (ephemeral)
- `dev` or `develop` → `dev` (shared development)

## Present Results to User

Always show environment URL and stage information:

```
✓ Deployment successful!

Environment URL: https://preview-abc123.odooops.app
Stage:          preview
Branch:         feat/new-module
Commit:         abc123d

Your Odoo environment is live. Database is seeded with demo data.
Email capture is enabled - check logs for outgoing emails.

Run E2E tests: bash /mnt/skills/user/odooops-test/scripts/test.sh env_preview_abc123
Check logs:    bash /mnt/skills/user/odooops-logs/scripts/logs.sh env_preview_abc123
```

## Promotion Workflow

To promote from staging to production:

```bash
# 1) Deploy to staging and run E2E tests
bash /mnt/skills/user/odooops-deploy/scripts/deploy.sh staging release/v1.2.0
bash /mnt/skills/user/odooops-test/scripts/test.sh <staging-env-id>

# 2) If E2E passes, promote to production
bash /mnt/skills/user/odooops-deploy/scripts/promote.sh <staging-env-id> prod
```

## Troubleshooting

### Authentication Error

If deployment fails with "401 Unauthorized":

```
Authentication failed. Check your ODOOOPS_TOKEN:

1. Ensure ODOOOPS_TOKEN environment variable is set
2. Verify token is valid: https://odooops.io/settings/tokens
3. Check token has project access

Generate a new token at: https://odooops.io/settings/tokens/new
```

### Build Timeout

If build exceeds 20 minutes:

```
Build timeout (20 minutes exceeded). Common causes:

- Large Odoo database restore
- Network issues fetching addons
- Python dependency resolution failures

Check build logs: bash /mnt/skills/user/odooops-logs/scripts/logs.sh <env-id> --type build
```

### Environment Not Ready

If environment fails health checks:

```
Environment created but failed health checks. Troubleshoot:

1. Check logs: bash /mnt/skills/user/odooops-logs/scripts/logs.sh <env-id>
2. Verify database migration succeeded
3. Check Odoo worker status
4. Review module installation errors

Destroy and retry: bash /mnt/skills/user/odooops-deploy/scripts/destroy.sh <env-id>
```

## Integration with E2E Testing

OdooOps deployments automatically trigger E2E tests via GitHub Actions. To run tests manually:

```bash
# Run E2E suite against deployed environment
bash /mnt/skills/user/odooops-test/scripts/test.sh <env-id>

# Check test results and artifacts
bash /mnt/skills/user/odooops-status/scripts/status.sh <env-id> --include-tests
```

## Related Skills

- **odooops-test**: Run E2E tests against environments
- **odooops-logs**: Fetch logs from environments
- **odooops-status**: Check deployment and test status
- **odooops-snapshot**: Create/restore database snapshots

## API Reference

See [`scripts/odooops/`](../../scripts/odooops/) for implementation details of the OdooOps API client.
