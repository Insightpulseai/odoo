# Supabase CI Secrets (GitHub Actions)

This document lists all secrets required for the Supabase CI/CD workflows.

## Required Repository Secrets

### Core Supabase Secrets

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `SUPABASE_ACCESS_TOKEN` | Supabase personal access token for CLI authentication | Yes |
| `SUPABASE_PROJECT_REF_STAGING` | Project reference ID for staging environment | Yes |
| `SUPABASE_PROJECT_REF_PROD` | Project reference ID for production environment | Yes |

### Optional Database Access

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `SUPABASE_DB_URL_STAGING` | PostgreSQL connection string for staging | For db settings |
| `SUPABASE_DB_URL_PROD` | PostgreSQL connection string for production | For db settings |
| `SUPABASE_URL_STAGING` | Supabase API URL for staging (e.g., `https://xxx.supabase.co`) | For db settings |
| `SUPABASE_URL_PROD` | Supabase API URL for production | For db settings |

### Repo Auditor Secrets

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `GITHUB_APP_ID` | GitHub App ID for repo auditor | For auditor |
| `GITHUB_APP_PRIVATE_KEY_B64` | Base64-encoded GitHub App private key | For auditor |
| `ADMIN_API_KEY` | Admin API key for Edge Function protection | For auditor |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | Optional |

## Environment Configuration

The workflows use GitHub Environments for deployment gating:

- **staging**: First deployment target, requires `SUPABASE_PROJECT_REF_STAGING`
- **production**: Gated deployment after staging, requires `SUPABASE_PROJECT_REF_PROD`

## Getting the Secrets

### Supabase Access Token

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click your avatar → Account Settings → Access Tokens
3. Generate a new token with appropriate permissions

### Project Reference

1. Go to your Supabase project
2. Settings → General → Reference ID
3. Copy the reference (e.g., `abcdefghijklmnop`)

### Database URL

1. Go to your Supabase project
2. Settings → Database → Connection String
3. Copy the URI format with password

### GitHub App Credentials

1. Create a GitHub App at https://github.com/settings/apps
2. Required permissions:
   - Repository: Contents (read), Issues (write)
3. Generate and download private key
4. Base64 encode: `base64 -w0 < private-key.pem`
5. Store as `GITHUB_APP_PRIVATE_KEY_B64`

## Security Notes

- **Never** commit secrets to the repository
- **Never** add `supabase/functions/.env` to git (add to `.gitignore`)
- Use GitHub Environments for production gating with required reviewers
- Rotate secrets periodically, especially after team changes
- The `ADMIN_API_KEY` should be a strong random string (32+ characters)

## Local Development

For local development, create `supabase/functions/.env`:

```bash
# Do NOT commit this file
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_B64=base64encodedkey...
ADMIN_API_KEY=your-local-admin-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

Then run:

```bash
npm run sb:fn:serve
```

## Workflow Triggers

| Workflow | Trigger | Environments |
|----------|---------|--------------|
| `supabase-pr-checks` | Pull requests | None (local stack) |
| `supabase-deploy` | Push to main, workflow_dispatch | staging → production |
