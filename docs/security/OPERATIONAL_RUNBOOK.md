# Secret Management Operational Runbook

## Your Infrastructure Setup

**GitHub**: 1 repo (`Insightpulseai/odoo`)
**Supabase**: 1 project (`spdtwktxdalcfigzeqrz`) - unified dev/stage/prod
**Secrets**: 6 total (4 GitHub, 2 Supabase)

---

## How Many Times Do You Set Each Token?

### **Answer: Maximum 2 times total**

| Secret | GitHub | Supabase | Total |
|--------|--------|----------|-------|
| `CLOUDFLARE_API_TOKEN` | ✅ 1× | ❌ | **1** |
| `SUPABASE_ANON_KEY` | ✅ 1× | ❌ | **1** |
| `DO_ACCESS_TOKEN` | ✅ 1× | ❌ | **1** |
| `GITHUB_TOKEN` | 🤖 auto | ❌ | **0** |
| `OPENAI_API_KEY` | ❌ | ✅ 1× | **1** |
| `SUPABASE_SERVICE_ROLE_KEY` | ❌ | ✅ 1× | **1** |

**Total manual operations**: 5 (GITHUB_TOKEN is auto-injected)

---

## Initial Setup (One-Time)

### Prerequisites

1. **Environment Variables Loaded**
   ```bash
   # Add to ~/.zshrc or load before sync
   export CLOUDFLARE_API_TOKEN="ggIENOdaBh3jgD59eg9zfMkqM3Bjv6eKuO32hSLv"
   export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   export DO_ACCESS_TOKEN="dop_v1_..."
   export OPENAI_API_KEY="sk-..."
   export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   export SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"
   ```

2. **CLI Tools Authenticated**
   ```bash
   # GitHub
   gh auth status

   # Supabase
   supabase link --project-ref spdtwktxdalcfigzeqrz
   ```

### Execute Full Sync

```bash
# Validate registry
./scripts/secrets/validate_registry.py

# Sync all secrets (one command)
./scripts/secrets/sync_all.sh

# Or selective
ONLY=github ./scripts/secrets/sync_all.sh    # 4 secrets to GitHub
ONLY=supabase ./scripts/secrets/sync_all.sh  # 2 secrets to Supabase
```

---

## Rotation Workflows

### Cloudflare API Token (30-day rotation)

**Frequency**: Every 30 days (per registry policy)

**Steps**:
1. Generate new token at Cloudflare
2. Update local env var
3. Sync to GitHub
4. Verify workflows

```bash
# 1. Generate at https://dash.cloudflare.com/profile/api-tokens

# 2. Update env var
export CLOUDFLARE_API_TOKEN="new-token-value"

# 3. Sync
ONLY=github ./scripts/secrets/sync_all.sh

# 4. Verify
gh secret list | grep CLOUDFLARE_API_TOKEN

# 5. Test in CI
gh workflow run infra-cloudflare-dns.yml --ref feat/infra-dns-ssot
```

### Supabase Service Role Key (90-day rotation)

**Frequency**: Every 90 days (per registry policy)

**Steps**:
1. Generate new key at Supabase Dashboard
2. Update local env var
3. Sync to Supabase Edge
4. Verify Edge Functions

```bash
# 1. Generate at https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api

# 2. Update env var
export SUPABASE_SERVICE_ROLE_KEY="new-key-value"

# 3. Sync
ONLY=supabase ./scripts/secrets/sync_all.sh

# 4. Verify
supabase secrets list | grep SUPABASE_SERVICE_ROLE_KEY

# 5. Test Edge Function
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/test
```

### OpenAI API Key (90-day rotation)

**Frequency**: Every 90 days (per registry policy)

**Steps**:
```bash
# 1. Generate at https://platform.openai.com/api-keys

# 2. Update env var
export OPENAI_API_KEY="sk-new-key"

# 3. Sync
ONLY=supabase ./scripts/secrets/sync_all.sh

# 4. Verify
supabase secrets list | grep OPENAI_API_KEY
```

---

## Emergency Response

### Token Exposure Incident

**Immediate Actions** (< 5 minutes):

```bash
# 1. Rotate at provider IMMEDIATELY
# 2. Update env var
export EXPOSED_TOKEN="new-rotated-value"

# 3. Sync to all stores
./scripts/secrets/sync_all.sh

# 4. Verify old token no longer works
# (provider-specific test)

# 5. Check git history
git log --all --source --remotes -S "old-token-value"

# 6. If committed, purge from history
# (See docs/security/SECRET_MANAGEMENT.md)
```

### Sync Failure Recovery

```bash
# 1. Validate registry
./scripts/secrets/validate_registry.py

# 2. Check CLI auth
gh auth status
supabase status

# 3. Verify env vars set
echo ${CLOUDFLARE_API_TOKEN:+SET}
echo ${SUPABASE_PROJECT_REF:+SET}

# 4. Retry with verbose output
./scripts/secrets/sync_all.sh 2>&1 | tee /tmp/sync-debug.log

# 5. If still failing, manual fallback
gh secret set SECRET_NAME -b "$VALUE" -R Insightpulseai/odoo
supabase secrets set SECRET_NAME="$VALUE"
```

---

## Monitoring & Audit

### Check Secret Status

```bash
# GitHub secrets (names only)
gh secret list -R Insightpulseai/odoo

# Supabase Edge secrets (names only)
supabase secrets list

# Last rotation dates (from registry)
grep -E 'rotation_days' infra/secrets/registry.yaml
```

### Audit Trail

**Registry Changes**:
```bash
git log --oneline -- infra/secrets/registry.yaml
```

**Secret Rotation Events**:
```bash
# GitHub audit log (web UI)
# https://github.com/organizations/Insightpulseai/settings/audit-log

# Supabase audit log (web UI)
# https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/audit
```

---

## CI Integration

### Automatic Validation

**Workflow**: `.github/workflows/secrets-registry-validate.yml`

**Triggers**:
- Every PR
- Push to main/feat branches
- Manual dispatch

**What it does**:
1. Validates registry structure
2. Dry-runs sync scripts with dummy values
3. Fails PR if registry is broken

### Manual Sync from CI (Future)

**Optional Enhancement**: Add workflow dispatch to sync secrets from CI

```yaml
# .github/workflows/secrets-sync-dispatch.yml
name: secrets-sync-dispatch
on:
  workflow_dispatch:
    inputs:
      target:
        description: 'Sync target (github|supabase|all)'
        required: true
        default: 'all'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sync secrets
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          SUPABASE_PROJECT_REF: spdtwktxdalcfigzeqrz
          # ... other secrets
        run: |
          ONLY=${{ inputs.target }} ./scripts/secrets/sync_all.sh
```

---

## Best Practices

### ✅ DO

- Set tokens once per store (GitHub or Supabase)
- Use registry as SSOT for metadata
- Rotate on schedule (registry defines frequency)
- Validate before syncing
- Test after rotation
- Document incidents and resolutions

### ❌ DON'T

- Commit secret values to git
- Share tokens via chat/email
- Skip validation step
- Sync without testing
- Ignore rotation schedules
- Set secrets manually (use sync scripts)

---

## Future Enhancements

### 1. Org-Level GitHub Secrets

**Current**: Repo-level (set once per repo)
**Future**: Org-level (set once for all repos)

```bash
# Convert to org-level
gh secret set CLOUDFLARE_API_TOKEN \
  --org Insightpulseai \
  --visibility all \
  -b "${CLOUDFLARE_API_TOKEN}"
```

**Update registry**:
```yaml
- name: CLOUDFLARE_API_TOKEN
  store: github_actions
  repo: Insightpulseai/*  # All org repos
  org: Insightpulseai
```

### 2. Multi-Environment Supabase

**Current**: 1 project (unified)
**Future**: 2 projects (stage + prod)

```yaml
# Additional secrets for staging
- name: SUPABASE_SERVICE_ROLE_KEY_STAGING
  store: supabase_edge_secrets
  supabase_project_ref_env: SUPABASE_STAGING_REF
  env_var: SUPABASE_SERVICE_ROLE_KEY_STAGING
```

**Sync**:
```bash
SUPABASE_PROJECT_REF=staging-ref ONLY=supabase ./scripts/secrets/sync_all.sh
SUPABASE_PROJECT_REF=prod-ref ONLY=supabase ./scripts/secrets/sync_all.sh
```

### 3. Supabase Vault (DB-Side Secrets)

**Use Case**: Secrets accessed by PostgreSQL functions/triggers

**Registry Addition**:
```yaml
- name: CLOUDFLARE_API_TOKEN_DB
  store: supabase_vault
  vault_id: cf_api_token
  required: true
```

**Sync Script**: `scripts/secrets/sync_supabase_vault.sh` (future)

---

## Quick Reference

| Task | Command |
|------|---------|
| Validate registry | `./scripts/secrets/validate_registry.py` |
| Sync all | `./scripts/secrets/sync_all.sh` |
| Sync GitHub only | `ONLY=github ./scripts/secrets/sync_all.sh` |
| Sync Supabase only | `ONLY=supabase ./scripts/secrets/sync_all.sh` |
| Check GitHub secrets | `gh secret list` |
| Check Supabase secrets | `supabase secrets list` |
| Test Cloudflare token | `gh workflow run infra-cloudflare-dns.yml` |
| Emergency rotation | See "Token Exposure Incident" section |

---

**Last Updated**: 2026-02-13
**Registry Version**: 1.0.0
**Secrets Tracked**: 6 (4 GitHub, 2 Supabase)
