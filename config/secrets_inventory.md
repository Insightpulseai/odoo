# IPAI Secrets Inventory (Names Only)
# This file lists expected secret names across all platforms.
# DO NOT put actual values here - this is committed to git.
# Values are managed via: Supabase Vault, Vercel env, GitHub Secrets

# ==============================================================================
# GLOBAL / CONTROL PLANE (Supabase Vault / env)
# ==============================================================================

# Mail (Mailgun)
MAILGUN_SMTP_LOGIN=
MAILGUN_SMTP_PASSWORD=
MAILGUN_DOMAIN=mg.insightpulseai.net

# Supabase (canonical project: spdtwktxdalcfigzeqrz)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# ==============================================================================
# DATABASE (DigitalOcean Managed Postgres)
# ==============================================================================

# Canonical DO Postgres cluster (odoo-db-sgp1)
DO_PG_HOST=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
DO_PG_PORT=25060
DO_PG_DATABASE=defaultdb
DO_PG_USER=doadmin
DO_PG_PASSWORD=
DO_PG_SSLMODE=require

# ==============================================================================
# ODOO CE STACK
# ==============================================================================

ODOO_ADMIN_PASSWORD=
ODOO_DB_PASSWORD=
ODOO_URL=

# ==============================================================================
# AI / AGENTS
# ==============================================================================

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GITHUB_TOKEN_MCP=

# ==============================================================================
# INFRASTRUCTURE (DigitalOcean, Vercel)
# ==============================================================================

DIGITALOCEAN_TOKEN=
VERCEL_TOKEN=

# ==============================================================================
# GITHUB (CI/CD)
# ==============================================================================

# These are set via `gh secret set` not env files
# GITHUB_TOKEN (auto-provided in Actions)
# SUPABASE_ACCESS_TOKEN
# DO_API_TOKEN

# ==============================================================================
# OPTIONAL / FUTURE
# ==============================================================================

# FIGMA_ACCESS_TOKEN=
# SLACK_BOT_TOKEN=
# HUBSPOT_API_KEY=
# FIRECRAWL_API_KEY=
