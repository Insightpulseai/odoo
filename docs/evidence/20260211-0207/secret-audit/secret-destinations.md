# Secret Migration Plan

## 🔐 Supabase Vault
**Purpose:** Database passwords, third-party API keys, service tokens
**Access:** `supabase secrets list`, `supabase secrets set`

**Migrate these:**
- Database passwords (PostgreSQL, DO Managed DB)
- Third-party API keys (OpenAI, Anthropic, DeepSeek, etc.)
- Service account tokens
- Webhook secrets
- Encryption keys

**Commands:**
```bash
# Set vault secret
supabase secrets set DB_PASSWORD=actual_password --project-ref spdtwktxdalcfigzeqrz

# List vault secrets
supabase secrets list --project-ref spdtwktxdalcfigzeqrz

# Use in Edge Functions
const { DB_PASSWORD } = Deno.env.toObject()
```

---

## ⚡ Supabase Edge Secrets
**Purpose:** Edge Function runtime environment variables
**Access:** Supabase Dashboard → Edge Functions → Secrets

**Migrate these:**
- SUPABASE_SERVICE_ROLE_KEY
- External API endpoints for Edge Functions
- Edge Function-specific tokens
- CORS allowed origins

**Commands:**
```bash
# Via CLI (sets both vault AND edge secrets)
supabase secrets set SERVICE_ROLE_KEY=eyJ... --project-ref spdtwktxdalcfigzeqrz

# Via Dashboard
# Settings → Edge Functions → Secrets → Add Secret
```

---

## 🔧 GitHub Actions Secrets
**Purpose:** CI/CD deployment credentials ONLY
**Access:** GitHub → Settings → Secrets and variables → Actions

**Migrate these:**
- DO_ACCESS_TOKEN (DigitalOcean API)
- DOCKER_HUB_TOKEN (if using Docker Hub)
- SSH_PRIVATE_KEY (deployment keys)
- VERCEL_TOKEN (if using Vercel)
- NPM_TOKEN (if publishing packages)

**Commands:**
```bash
# Via GitHub CLI
gh secret set DO_ACCESS_TOKEN --body "dop_v1_..." --repo Insightpulseai/odoo

# Via GitHub UI
# Settings → Secrets and variables → Actions → New repository secret
```

**Usage in workflows:**
```yaml
- name: Deploy to DO
  env:
    DO_TOKEN: ${{ secrets.DO_ACCESS_TOKEN }}
  run: doctl apps update ...
```

---

## 🖥️ DigitalOcean Environment Variables
**Purpose:** Droplet runtime configuration
**Access:** SSH to droplet, edit docker-compose or systemd env files

**Migrate these:**
- POSTGRES_PASSWORD (local PostgreSQL)
- ODOO_ADMIN_PASSWORD (master password)
- Runtime config (not secrets, but config)

**Commands:**
```bash
# Edit compose environment
ssh root@178.128.112.214
vi /opt/odoo/repo/deploy/odoo-prod.compose.yml
# OR
vi /opt/odoo/repo/deploy/.env

# Restart to apply
docker-compose -f odoo-prod.compose.yml restart
```

---

## 📝 .env.example Templates
**Purpose:** Developer onboarding, documentation
**Location:** Git repository (committed)

**Create templates for:**
```bash
# .env.example
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=eyJhbGci... # Get from Supabase Dashboard
SUPABASE_SERVICE_ROLE_KEY=    # NEVER commit actual value

# Database (use Supabase Vault or DO env vars)
DATABASE_URL=                 # postgresql://user:password@host:port/db

# Third-party APIs (use Supabase Vault)
OPENAI_API_KEY=              # sk-...
ANTHROPIC_API_KEY=           # sk-ant-...

# Local development only
NODE_ENV=development
PORT=3000
```

---

## 🚫 Never Store Secrets In:
- ❌ Source code files (.ts, .js, .py, .sh)
- ❌ Configuration files committed to git (.yml, .json, .toml)
- ❌ Documentation files (.md)
- ❌ Docker images (build-time secrets)
- ❌ Client-side code (anything in apps/web)

