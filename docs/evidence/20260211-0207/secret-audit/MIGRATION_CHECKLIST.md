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

