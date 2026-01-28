# GitHub Codespaces Setup Guide

## Prerequisites

- GitHub Team/Pro account with Codespaces enabled
- Personal Access Token (PAT) with `codespace` scope

## Environment Variables Strategy

We use **three layers** for secrets management:

1. **GitHub Codespaces Secrets** (preferred) - auto-loaded in all Codespaces
2. **Devcontainer Environment** (fallback) - loaded from `.env.local` if secrets unavailable
3. **Local `.env.local`** (local dev) - never committed

## Setup Instructions

### Option 1: GitHub Codespaces Secrets (Recommended)

**Step 1: Update GitHub PAT**
1. Go to https://github.com/settings/tokens
2. Find your token or create new one
3. Add `codespace` scope
4. Regenerate token and update `GITHUB_TOKEN` in `~/.zshrc`

**Step 2: Run Setup Script**
```bash
./scripts/setup-codespaces-secrets.sh
```

**Step 3: Verify**
```bash
# Check secrets were created
gh secret list --repo jgtolentino/odoo-ce --app codespaces
```

Visit: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces

### Option 2: Manual UI Setup

1. Go to https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces
2. Click **New repository secret**
3. Add each secret from `.env.local`:

```
NEXT_PUBLIC_SUPABASE_ANON_KEY
POSTGRES_PASSWORD
POSTGRES_PRISMA_URL
POSTGRES_URL
POSTGRES_URL_NON_POOLING
SUPABASE_JWT_SECRET
SUPABASE_PUBLISHABLE_KEY
SUPABASE_SECRET_KEY
SUPABASE_SERVICE_ROLE_KEY
VITE_SUPABASE_ANON_KEY
VITE_SUPABASE_PUBLISHABLE_KEY
```

### Option 3: Devcontainer Environment (Fallback)

If GitHub Codespaces secrets are unavailable, the devcontainer will:
1. Check for `.env.local` in repo root
2. Load all variables into the container environment
3. Make them available to all shells and processes

**Setup:**
```bash
# Copy example and fill in values
cp .env.example .env.local

# Start Codespace (secrets auto-loaded)
```

## Supabase Configuration

**Project**: `spdtwktxdalcfigzeqrz` (InsightPulse AI)
**Region**: US East 1
**Database**: PostgreSQL 16

**Connection Strings:**
- **Pooled** (default): Port 6543 with pgbouncer
- **Direct**: Port 5432 for migrations/admin
- **Prisma**: Prisma-optimized pooling

**API Keys:**
- **Anon Key**: Public, frontend-safe
- **Service Role Key**: Backend-only, full access
- **JWT Secret**: Token signing/verification

## DigitalOcean Database (DEPRECATED)

**⚠️ Do NOT use for Supabase operations**

This is the managed PostgreSQL cluster in Singapore:
- **Host**: `odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com`
- **Port**: 25060
- **User**: doadmin
- **Purpose**: Odoo CE application database (self-hosted)

**When to use:**
- Odoo CE local development
- Legacy data migrations
- NOT for Supabase schema operations

## Mailgun Configuration

**Domain**: `mg.insightpulseai.net`

**DNS Records** (already configured in DigitalOcean):
- MX: `mxa.mailgun.org`, `mxb.mailgun.org` (priority 10)
- SPF: `v=spf1 include:mailgun.org ~all`
- DMARC: Policy `none`, reporting enabled
- DKIM: `pic._domainkey.mg.insightpulseai.net`

**API Integration:**
- Use Mailgun API for transactional emails
- SMTP relay for Odoo email campaigns
- Webhook receivers for email events

## Verification

**Test Database Connection:**
```bash
psql "$POSTGRES_URL" -c "SELECT version();"
```

**Test Supabase API:**
```bash
curl -H "apikey: $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/"
```

**Check Environment:**
```bash
env | grep -E "SUPABASE|POSTGRES|VITE"
```

## Troubleshooting

**403 Error When Setting Secrets:**
- PAT missing `codespace` scope
- Solution: Regenerate token with proper scopes

**Secrets Not Available in Codespace:**
- Restart Codespace after setting secrets
- Verify secrets exist in repo settings
- Check devcontainer rebuilds from clean state

**Database Connection Failed:**
- Verify `POSTGRES_URL` includes `sslmode=require`
- Check Supabase project not paused
- Test with non-pooled connection string

**API Key Invalid:**
- Keys expire in 2076 (check JWT `exp` claim)
- Verify project ref matches: `spdtwktxdalcfigzeqrz`
- Regenerate in Supabase dashboard if needed

## Security Notes

- ✅ **DO**: Set secrets via GitHub Codespaces secrets
- ✅ **DO**: Use `.env.local` for local development (gitignored)
- ❌ **DON'T**: Commit secrets to git
- ❌ **DON'T**: Use production keys in public repositories
- ❌ **DON'T**: Share service role keys in chat logs

## Resources

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [Supabase Dashboard](https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz)
- [DigitalOcean Database Console](https://cloud.digitalocean.com/databases/odoo-db-sgp1)
- [Mailgun Dashboard](https://app.mailgun.com/mg/insightpulseai.net)
