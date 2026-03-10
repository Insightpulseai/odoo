# Secret Management

## Architecture

**Two-Tier Secret System:**

1. **GitHub Secrets** (CI/CD): Infrastructure automation, Terraform, deployment workflows
2. **Supabase Edge/Vault** (Runtime): Edge Functions, application code, database operations

## SSOT Secret Registry

**Location**: `infra/secrets/registry.yaml`

**Purpose**: Metadata-only registry (names, stores, rotation policies) - **NEVER contains secret values**.

### Registry Structure

```yaml
secrets:
  - name: SECRET_NAME
    description: Human-readable purpose
    store: github_actions | supabase_edge_secrets | supabase_vault
    env_var: ENV_VAR_NAME
    required: true | false
    rotation_days: N
    used_by:
      - path/to/consumer
```

## Commands

### Validate Registry

```bash
# Validates registry structure and constraints
./scripts/secrets/validate_registry.py
```

### Sync Secrets

**Prerequisites**:
- Secret values must be in environment variables
- Appropriate CLI tools authenticated (`gh`, `supabase`)

```bash
# Sync all secrets (auto-detects available tools)
export CLOUDFLARE_API_TOKEN="your-token"
export SUPABASE_PROJECT_REF="your-project-ref"
./scripts/secrets/sync_all.sh

# Or sync individually
./scripts/secrets/sync_github_secrets.sh    # GitHub Actions secrets
./scripts/secrets/sync_supabase_secrets.sh  # Supabase Edge secrets
```

### Dry-Run (Print Commands Without Executing)

```bash
# See what would be synced
./scripts/secrets/sync_github_secrets.sh
./scripts/secrets/sync_supabase_secrets.sh
```

## Secret Stores

### GitHub Actions Secrets

**When to Use**: CI/CD workflows, Terraform, infrastructure automation

**Set via**:
- `gh secret set SECRET_NAME -b "$VALUE" -R owner/repo`
- Or use sync script: `./scripts/secrets/sync_github_secrets.sh`

**Scope**: Repo-level or org-level

### Supabase Edge Secrets

**When to Use**: Edge Functions, runtime application code

**Set via**:
- `supabase secrets set SECRET_NAME="$VALUE"`
- Or use sync script: `./scripts/secrets/sync_supabase_secrets.sh`

**Scope**: Project-level

### Supabase Vault

**When to Use**: Database-side operations, PostgreSQL functions/triggers

**Set via**: SQL or Edge Function calls to Vault API

**Scope**: Project-level, database-accessible

## Rotation

1. Rotate secret at provider (Cloudflare, OpenAI, etc.)
2. Update environment variable with new value
3. Run appropriate sync script
4. Verify in consuming workflows/functions

**Recommended Schedule** (from registry):
- Critical infrastructure (DNS, auth): 30 days
- API keys: 90 days
- Auto-rotated (GITHUB_TOKEN): N/A

## Security Rules

❌ **NEVER**:
- Commit secret values to git
- Hardcode secrets in source files
- Log/echo secrets in CI output
- Share secrets via chat/email

✅ **ALWAYS**:
- Store values in appropriate secret store
- Use environment variables for access
- Validate registry on every PR
- Rotate on schedule or on exposure

## CI Validation

**Workflow**: `.github/workflows/secrets-registry-validate.yml`

**Runs on**:
- Every PR touching secret registry or sync scripts
- Every push to main/feat branches

**Validates**:
- Registry structure and required fields
- Store-specific constraints (repo, project_ref)
- No duplicate secret names
- Dry-run sync scripts with dummy values

## Troubleshooting

### Secret Not Found in CI

1. Check registry: `cat infra/secrets/registry.yaml`
2. Verify secret exists: `gh secret list -R owner/repo`
3. Check workflow references correct secret name
4. Re-sync if needed: `./scripts/secrets/sync_github_secrets.sh`

### Sync Failed

1. Verify env var is set: `echo ${SECRET_NAME:+SET}`
2. Check CLI authentication: `gh auth status`, `supabase status`
3. Validate registry: `./scripts/secrets/validate_registry.py`
4. Check registry constraints (required fields, store-specific)

### Secret Exposed

1. **Immediate**: Rotate at provider
2. Update env var with new value
3. Re-sync to all stores: `./scripts/secrets/sync_all.sh`
4. If committed: Purge from git history (see incident response docs)

## Reference

- Registry: `infra/secrets/registry.yaml`
- Validator: `scripts/secrets/validate_registry.py`
- Sync Scripts: `scripts/secrets/sync_*.sh`
- CI Gate: `.github/workflows/secrets-registry-validate.yml`
