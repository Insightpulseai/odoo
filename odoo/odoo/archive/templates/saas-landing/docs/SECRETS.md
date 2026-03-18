# Secrets & Credentials Reference

Complete reference for all secrets used in the saas-landing template.

---

## 🔐 Secret Locations

### 1. **Supabase Vault** (Remote)

**Project**: `spdtwktxdalcfigzeqrz`

**Stored secrets** (42 total):
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ZOHO_SMTP_PASS`
- `GITHUB_TOKEN`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- ... and 35 more

**Access via**:
```bash
# List all secrets
supabase secrets list

# Secrets are available to Edge Functions automatically
# No manual retrieval needed for serverless functions
```

**Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/vault

---

### 2. **~/.zshrc** (Local Machine)

**Location**: `/Users/tbwa/.zshrc`

**Stored secrets**:

```bash
# Supabase
export SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
export SUPABASE_ANON_KEY=eyJhbGci...IHBJ0c
export SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...YboyvhU
export SUPABASE_JWT_SECRET=UCrAMrC...B5EWng==
export SUPABASE_ACCESS_TOKEN=sbp_666b03766354c64f6f3949082bfc46704c45edac

# Zoho Mail
export ZOHO_SMTP_PASSWORD=ka8EnXL4ttS9

# OPEX Project (separate Supabase instance)
export OPEX_SUPABASE_URL=https://ublqmilcjtpnflofprkr.supabase.co
export OPEX_SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...CrHYo
```

**Usage**:
```bash
# Source in new shells
source ~/.zshrc

# Or access directly
echo $ZOHO_SMTP_PASSWORD
```

---

### 3. **.env.local** (Local Development)

**Location**: `templates/saas-landing/.env.local`

**Status**: ✅ **Populated with all required secrets**

**Contents**:
```bash
# Supabase (from ~/.zshrc)
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...IHBJ0c
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...YboyvhU

# Zoho Mail (from ~/.zshrc)
ZOHO_USER=business@insightpulseai.com
ZOHO_PASS=ka8EnXL4ttS9  # ✅ Now populated
ZOHO_FROM_NAME=InsightPulse.ai

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Note**: This file is **gitignored** and contains actual secrets.

---

### 4. **Vercel Environment** (Production)

**Status**: ⚠️ **Not yet configured**

**Required variables** (7):

```bash
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...IHBJ0c
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...YboyvhU
ZOHO_USER=business@insightpulseai.com
ZOHO_PASS=ka8EnXL4ttS9
ZOHO_FROM_NAME=InsightPulse.ai
NEXT_PUBLIC_APP_URL=https://ops.insightpulseai.com
```

**Set via deployment script**:
```bash
cd templates/saas-landing
source ~/.zshrc  # Load secrets from .zshrc
./scripts/deploy-production.sh
```

---

## 📋 Secret Inventory

### Supabase Credentials

| Secret | Source | Used For |
|--------|--------|----------|
| `SUPABASE_URL` | .zshrc, Vault | API endpoint |
| `SUPABASE_ANON_KEY` | .zshrc, Vault | Client-side auth |
| `SUPABASE_SERVICE_ROLE_KEY` | .zshrc, Vault | Server-side RPC |
| `SUPABASE_JWT_SECRET` | .zshrc, Vault | Token verification |
| `SUPABASE_ACCESS_TOKEN` | .zshrc | CLI operations |

**Get fresh keys**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api

---

### Zoho Mail Credentials

| Secret | Source | Used For |
|--------|--------|----------|
| `ZOHO_USER` | Hardcoded | SMTP username |
| `ZOHO_SMTP_PASSWORD` | .zshrc, Vault | SMTP auth |
| `ZOHO_FROM_NAME` | Hardcoded | Email sender name |

**Value**: `ka8EnXL4ttS9` (app password, not main password)

**Generate new**: https://mail.zoho.com/ → Settings → Security → App Passwords

---

### Other Available Secrets (in Vault)

| Secret | Purpose |
|--------|---------|
| `GITHUB_TOKEN` | GitHub API access |
| `ANTHROPIC_API_KEY` | Claude API |
| `OPENAI_API_KEY` | OpenAI API |
| `GEMINI_API_KEY` | Google Gemini |
| `N8N_BASE_URL` | n8n automation |
| `OCR_API_KEY` | OCR service |
| `ODOO_PASSWORD` | Odoo integration |
| `MAILGUN_API_KEY` | Mailgun (deprecated) |

**Full list**: Run `supabase secrets list`

---

## 🔄 Secret Propagation Flow

```
1. Master Storage: ~/.zshrc
   ↓
2. Local Dev: .env.local (copy values)
   ↓
3. Remote Vault: Supabase Vault (for Edge Functions)
   ↓
4. Production: Vercel Environment Variables
```

---

## 🚀 Quick Commands

### Update Local Environment

```bash
# Source latest from .zshrc
source ~/.zshrc

# Verify secrets loaded
echo $ZOHO_SMTP_PASSWORD  # Should show: ka8EnXL4ttS9
echo $SUPABASE_SERVICE_ROLE_KEY | head -c 20  # Should show: eyJhbGci...
```

### Deploy with Secrets

```bash
cd templates/saas-landing

# Load secrets from .zshrc
source ~/.zshrc

# Deploy (script reads from environment)
./scripts/deploy-production.sh
```

### Manual Vercel Setup

```bash
# Set each variable using values from .zshrc
vercel env add ZOHO_PASS production <<<"$ZOHO_SMTP_PASSWORD"
vercel env add SUPABASE_SERVICE_ROLE_KEY production <<<"$SUPABASE_SERVICE_ROLE_KEY"
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<<"$SUPABASE_ANON_KEY"
# ... etc
```

---

## 🔒 Security Best Practices

### ✅ DO

- Store master secrets in `~/.zshrc`
- Use Supabase Vault for Edge Functions
- Keep `.env.local` gitignored
- Use environment variables in code (`process.env.SECRET`)
- Rotate secrets periodically
- Use app passwords (Zoho) instead of main passwords

### ❌ DON'T

- Commit secrets to git (`.env.local` is gitignored)
- Hardcode secrets in source code
- Share secrets via Slack/email
- Use production secrets in development
- Expose `SUPABASE_SERVICE_ROLE_KEY` to client code

---

## 🔍 Verification

### Check Local Setup

```bash
cd templates/saas-landing

# Verify .env.local has all secrets
cat .env.local | grep -E "SUPABASE|ZOHO"

# Should show:
# NEXT_PUBLIC_SUPABASE_URL=https://...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
# SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
# ZOHO_USER=business@...
# ZOHO_PASS=ka8EnXL4ttS9  # ✅ Populated
# ZOHO_FROM_NAME=InsightPulse.ai
```

### Check Vault Secrets

```bash
# List all secrets in Supabase Vault
supabase secrets list

# Should show 42 secrets including:
# SUPABASE_ANON_KEY
# SUPABASE_SERVICE_ROLE_KEY
# ZOHO_SMTP_PASS
```

### Check Vercel (after deployment)

```bash
# List production environment variables
vercel env ls production

# Should show 7+ variables
```

---

## 🆘 Troubleshooting

### "ZOHO_PASS not set"

**Fix**:
```bash
# Add to .env.local
echo 'ZOHO_PASS=ka8EnXL4ttS9' >> .env.local
```

### "Supabase service role key invalid"

**Fix**:
```bash
# Get fresh key from dashboard
open https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api

# Copy "service_role" key and update .env.local
```

### "Can't access Supabase Vault"

**Fix**:
```bash
# Login to Supabase CLI
supabase login

# Link to project
supabase link --project-ref spdtwktxdalcfigzeqrz

# List secrets
supabase secrets list
```

---

## 📚 Related Documentation

- **Configuration Guide**: `docs/CONFIGURATION.md`
- **Deployment Evidence**: `docs/evidence/20260212-0711/DEPLOYMENT.md`
- **Deployment Script**: `scripts/deploy-production.sh`
- **Supabase Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- **Vercel Dashboard**: https://vercel.com/dashboard

---

**Last Updated**: 2026-02-12
**Secret Count**: 42 in Vault, 8 in .zshrc, 7 in .env.local
