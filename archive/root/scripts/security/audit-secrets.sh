#!/bin/bash
# Secret Audit and Migration Script
# Identifies secrets, creates migration plan, generates templates

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT_DIR="$REPO_ROOT/docs/evidence/$(date +%Y%m%d-%H%M)/secret-audit"
mkdir -p "$AUDIT_DIR"

echo "🔍 Secret Audit Starting..."
echo "📁 Output: $AUDIT_DIR"

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Find all .env files
echo -e "\n${BLUE}=== 1. Finding .env files ===${NC}"
find "$REPO_ROOT" -type f \( -name ".env" -o -name ".env.*" \) \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/odoo19/*" \
  ! -name "*.example" \
  ! -name "*.template" \
  > "$AUDIT_DIR/env-files.txt"

echo -e "${YELLOW}Found $(wc -l < "$AUDIT_DIR/env-files.txt") .env files${NC}"
cat "$AUDIT_DIR/env-files.txt"

# 2. Scan for hardcoded secrets (common patterns)
echo -e "\n${BLUE}=== 2. Scanning for hardcoded secrets ===${NC}"
SECRET_PATTERNS=(
  "AVNS_[a-zA-Z0-9_-]+"                    # Aiven passwords
  "ghp_[a-zA-Z0-9]{36}"                    # GitHub Personal Access Tokens
  "gho_[a-zA-Z0-9]{36}"                    # GitHub OAuth tokens
  "github_pat_[a-zA-Z0-9_]{82}"            # GitHub Fine-grained PATs
  "sk_live_[a-zA-Z0-9]{24,}"               # Stripe secret keys
  "pk_live_[a-zA-Z0-9]{24,}"               # Stripe public keys (less sensitive)
  "sk_test_[a-zA-Z0-9]{24,}"               # Stripe test keys
  "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" # JWT tokens (long ones)
  "AKIA[0-9A-Z]{16}"                       # AWS Access Keys
  "dop_v1_[a-f0-9]{64}"                    # DigitalOcean tokens
  "supa_[a-zA-Z0-9]{40,}"                  # Supabase tokens
)

> "$AUDIT_DIR/hardcoded-secrets.txt"
for pattern in "${SECRET_PATTERNS[@]}"; do
  echo "Scanning for: $pattern"
  grep -rE "$pattern" "$REPO_ROOT" \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude-dir=odoo19 \
    --exclude-dir=.next \
    --exclude="*.log" \
    --exclude="pnpm-lock.yaml" \
    --exclude="package-lock.json" \
    --exclude="audit-secrets.sh" \
    2>/dev/null >> "$AUDIT_DIR/hardcoded-secrets.txt" || true
done

SECRET_COUNT=$(wc -l < "$AUDIT_DIR/hardcoded-secrets.txt")
if [ "$SECRET_COUNT" -gt 0 ]; then
  echo -e "${RED}⚠️  Found $SECRET_COUNT potential hardcoded secrets!${NC}"
else
  echo -e "${GREEN}✅ No hardcoded secrets found${NC}"
fi

# 3. Identify secret types and destinations
echo -e "\n${BLUE}=== 3. Categorizing secrets by destination ===${NC}"

cat > "$AUDIT_DIR/secret-destinations.md" << 'EOF'
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
- ❌ Client-side code (anything in web/web)

EOF

cat "$AUDIT_DIR/secret-destinations.md"

# 4. Generate .env.example from existing .env files
echo -e "\n${BLUE}=== 4. Generating .env.example templates ===${NC}"

while IFS= read -r env_file; do
  if [ -f "$env_file" ]; then
    example_file="${env_file%.local}.example"
    example_file="${example_file%.production}.example"
    example_file="${example_file/.env/.env.example}"

    echo "📝 Creating template: $example_file"

    # Redact values but keep keys
    sed -E 's/=.*/=REDACTED_SET_IN_VAULT_OR_SECRETS/g' "$env_file" > "$example_file.tmp"

    # Add header
    cat > "$example_file" << 'HEADER'
# Environment Variables Template
#
# ⚠️  DO NOT commit actual secrets to this file
#
# Secret Storage Locations:
# - Database passwords, API keys: Supabase Vault
# - Edge Function secrets: Supabase Edge Secrets
# - CI/CD credentials: GitHub Actions Secrets
# - Droplet runtime: DO Environment Variables
#
# For local development:
# 1. Copy this file to .env (gitignored)
# 2. Replace REDACTED values with actual secrets
# 3. Get secrets from team lead or Supabase Dashboard

HEADER

    cat "$example_file.tmp" >> "$example_file"
    rm "$example_file.tmp"

    echo "  → $example_file created"
  fi
done < "$AUDIT_DIR/env-files.txt"

# 5. Create migration checklist
echo -e "\n${BLUE}=== 5. Creating migration checklist ===${NC}"

cat > "$AUDIT_DIR/MIGRATION_CHECKLIST.md" << 'EOF'
# Secret Migration Checklist

## Phase 1: Audit ✅
- [x] Scan repository for secrets
- [x] Identify .env files
- [x] Categorize secrets by destination
- [ ] Review hardcoded-secrets.txt findings
- [ ] Identify secret owners (who has access)

## Phase 2: Migrate to Vaults
### Supabase Vault
- [ ] Database passwords (DO Managed PostgreSQL)
- [ ] OpenAI API key
- [ ] Anthropic API key
- [ ] DeepSeek API key
- [ ] Webhook signing secrets
- [ ] Encryption keys

### Supabase Edge Secrets
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] External API endpoints for Edge Functions
- [ ] Edge Function-specific tokens

### GitHub Actions Secrets
- [ ] DO_ACCESS_TOKEN
- [ ] DOCKER_HUB_TOKEN (if applicable)
- [ ] SSH deployment keys
- [ ] VERCEL_TOKEN (if applicable)

### DigitalOcean Environment Variables
- [ ] POSTGRES_PASSWORD (local DB on droplet)
- [ ] ODOO_ADMIN_PASSWORD (master password)
- [ ] Runtime configuration

## Phase 3: Clean Repository
- [ ] Add all .env files to .gitignore
- [ ] Remove hardcoded secrets from source
- [ ] Replace with environment variable references
- [ ] Create .env.example templates
- [ ] Update documentation

## Phase 4: Update Code
- [ ] Replace hardcoded secrets with env var lookups
- [ ] Update docker-compose files to use env vars
- [ ] Update CI/CD workflows to use GitHub Secrets
- [ ] Update deployment scripts

## Phase 5: Verify
- [ ] Test local development with .env file
- [ ] Test CI/CD with GitHub Secrets
- [ ] Test production with Vault/Edge secrets
- [ ] Verify no secrets in git history
- [ ] Run secret scanner on final state

## Phase 6: Rotate Exposed Secrets
- [ ] Rotate any secrets found in git history
- [ ] Update Vault with new secrets
- [ ] Update Edge Secrets with new values
- [ ] Test all services with rotated secrets

## Phase 7: Documentation
- [ ] Document secret locations in README
- [ ] Create onboarding guide for new developers
- [ ] Document secret rotation procedures
- [ ] Update CLAUDE.md with secret management rules

EOF

cat "$AUDIT_DIR/MIGRATION_CHECKLIST.md"

# 6. Generate .gitignore additions
echo -e "\n${BLUE}=== 6. Generating .gitignore additions ===${NC}"

cat > "$AUDIT_DIR/gitignore-additions.txt" << 'EOF'
# Environment files (local development only)
.env
.env.local
.env.development
.env.test
.env.production
.env.staging

# Keep templates (committed to git)
!.env.example
!.env.template
!.env.sample

# Secret files
secrets/
*.key
*.pem
*.p12
*.pfx

# Vault files
vault/
.vault/
EOF

echo "📄 Add these lines to .gitignore:"
cat "$AUDIT_DIR/gitignore-additions.txt"

# 7. Create migration scripts
echo -e "\n${BLUE}=== 7. Creating migration helper scripts ===${NC}"

cat > "$AUDIT_DIR/migrate-to-supabase-vault.sh" << 'MIGRATE_SCRIPT'
#!/bin/bash
# Helper script to migrate secrets to Supabase Vault

PROJECT_REF="spdtwktxdalcfigzeqrz"

echo "🔐 Migrating secrets to Supabase Vault..."

# Example: Set a secret
# supabase secrets set SECRET_NAME="secret_value" --project-ref $PROJECT_REF

echo "
Usage:
  supabase secrets set DB_PASSWORD=\"your_password\" --project-ref $PROJECT_REF
  supabase secrets set OPENAI_API_KEY=\"sk-...\" --project-ref $PROJECT_REF

View secrets:
  supabase secrets list --project-ref $PROJECT_REF

Delete secret:
  supabase secrets unset SECRET_NAME --project-ref $PROJECT_REF
"
MIGRATE_SCRIPT

chmod +x "$AUDIT_DIR/migrate-to-supabase-vault.sh"

# 8. Final report
echo -e "\n${GREEN}=== ✅ Audit Complete ===${NC}"
echo ""
echo "📊 Summary:"
echo "  - .env files found: $(wc -l < "$AUDIT_DIR/env-files.txt")"
echo "  - Potential secrets: $(wc -l < "$AUDIT_DIR/hardcoded-secrets.txt")"
echo ""
echo "📁 Outputs:"
echo "  - Full report: $AUDIT_DIR/"
echo "  - Secret destinations: $AUDIT_DIR/secret-destinations.md"
echo "  - Migration checklist: $AUDIT_DIR/MIGRATION_CHECKLIST.md"
echo "  - .gitignore additions: $AUDIT_DIR/gitignore-additions.txt"
echo ""
echo "🔧 Next steps:"
echo "  1. Review $AUDIT_DIR/hardcoded-secrets.txt"
echo "  2. Follow $AUDIT_DIR/MIGRATION_CHECKLIST.md"
echo "  3. Run $AUDIT_DIR/migrate-to-supabase-vault.sh"
echo "  4. Update .gitignore with $AUDIT_DIR/gitignore-additions.txt"
echo ""
echo -e "${YELLOW}⚠️  Review findings before proceeding with migration!${NC}"
