# EE Parity Test Runner - Required Secrets

This document lists the GitHub Secrets and environment variables needed for the EE Parity Test Runner CI workflow.

## GitHub Secrets

Add these secrets in your repository settings: **Settings → Secrets and variables → Actions → New repository secret**

### Odoo Connection (Required for live testing)

| Secret | Description | Example |
|--------|-------------|---------|
| `ODOO_URL` | Odoo instance URL | `https://odoo.example.com` |
| `ODOO_DB` | Database name | `odoo_production` |
| `ODOO_USER` | Odoo username | `admin` |
| `ODOO_PASS` | Odoo password | `your_password` |

### Supabase (Required for schema deployment)

| Secret | Description | Where to find |
|--------|-------------|---------------|
| `SUPABASE_ACCESS_TOKEN` | Personal access token | [Supabase Dashboard → Account → Access Tokens](https://supabase.com/dashboard/account/tokens) |
| `SUPABASE_DB_PASSWORD` | Database password | Supabase Dashboard → Project → Settings → Database |

## Environment Variables

These are automatically set by the CI workflow but can be overridden:

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_PROJECT_REF` | `spdtwktxdalcfigzeqrz` | Supabase project reference |

## Local Development

For local development, create a `.env` file (not committed):

```bash
# .env (add to .gitignore)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USER=admin
ODOO_PASS=admin

SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_DB_PASSWORD=your_password
SUPABASE_ACCESS_TOKEN=sbp_xxxxxxxxxxxx
```

Then source it before running:

```bash
source .env
./tools/parity/run_ee_parity.sh
```

## Schema Deployment

### Option 1: Via CI (Automatic)

Schema deploys automatically on push to `main` when `SUPABASE_ACCESS_TOKEN` is set.

### Option 2: Manual Deployment

```bash
export SUPABASE_DB_PASSWORD='your_password'
export SUPABASE_PROJECT_REF='spdtwktxdalcfigzeqrz'
./scripts/deploy_parity_schema.sh
```

### Option 3: Direct SQL

```bash
psql "postgres://postgres:PASSWORD@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres" \
  -f supabase/migrations/20260126_000001_ee_parity_tracking.sql
```

## Verification

After setting secrets, verify with a manual workflow dispatch:

1. Go to **Actions → EE Parity Test Runner**
2. Click **Run workflow**
3. Select category (optional) and format
4. Check the run results

## Security Notes

- Never commit secrets to the repository
- Use GitHub Secrets for CI/CD
- Rotate passwords periodically
- Use service accounts for production
- The `ODOO_PASS` should be for a dedicated CI user with read-only access
