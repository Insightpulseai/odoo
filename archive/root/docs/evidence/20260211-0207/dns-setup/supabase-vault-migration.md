# Supabase Vault Secret Migration

**Date**: 2026-02-11 02:07 UTC
**Requirement**: Store Cloudflare API token in Supabase Vault

## Current State

- ❌ Token stored in ~/.zshrc as `TF_VAR_cloudflare_api_token`
- ❌ Token value appears invalid/expired: `774c9c222751c919caa3cd07cc39f65b7dab7`
- ✅ Supabase project: `spdtwktxdalcfigzeqrz`

## Required Actions

### 1. Store Valid Cloudflare API Token in Supabase Vault

```sql
-- Connect to Supabase project spdtwktxdalcfigzeqrz
-- Store Cloudflare API token in vault
SELECT vault.create_secret(
  'CLOUDFLARE_API_TOKEN',
  '<valid_cloudflare_api_token>',
  'Cloudflare API token for DNS management (Zone:DNS edit permission)'
);
```

### 2. Retrieve Token for DNS Operations

```sql
-- Retrieve from vault when needed
SELECT decrypted_secret
FROM vault.decrypted_secrets
WHERE name = 'CLOUDFLARE_API_TOKEN';
```

### 3. Update DNS Upsert Script to Use Vault

```bash
#!/bin/bash
set -euo pipefail

# Retrieve token from Supabase Vault
export CF_API_TOKEN=$(psql "$SUPABASE_DB_URL" -t -c "
  SELECT decrypted_secret
  FROM vault.decrypted_secrets
  WHERE name = 'CLOUDFLARE_API_TOKEN'
" | xargs)

export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"
export CF_ZONE_NAME="insightpulseai.com"
export TARGET_IP="178.128.112.214"

# ... rest of upsert_a function and execution
```

## Token Provided by User

**Hash/Token**: `v1.0-4daf41bee9e67085f8a85edb-52a723da994eafebaa682cd1fdef1946fda4cc7160d3ad51f37a83f4fdc9a0e88036049ffcf664b675e0e0e43b6fc837c47cd3651d8939844a8896dd177f2c9b21bf767ba0c6ba9fd1`

**Verification Result**: ❌ Invalid format for Cloudflare API token
**Error**: "Invalid format for Authorization header" (code 6111)
**Conclusion**: This appears to be a different type of credential, not a Cloudflare API token

**Action Required**: Obtain valid Cloudflare API token from Cloudflare dashboard (Profile → API Tokens → Create Token with Zone:DNS Edit permission)

## Supabase Vault Setup

**Project**: spdtwktxdalcfigzeqrz.supabase.co
**Connection String**: Available in environment as `SUPABASE_DB_URL`

**Vault Documentation**: https://supabase.com/docs/guides/database/vault

## Security Benefits

1. ✅ Centralized secret management
2. ✅ Encrypted at rest
3. ✅ Audit trail for secret access
4. ✅ No secrets in shell config files
5. ✅ Easy rotation without code changes

## Migration Checklist

- [ ] Verify user-provided token is valid Cloudflare API token
- [ ] Store token in Supabase Vault
- [ ] Update DNS upsert script to retrieve from vault
- [ ] Test DNS record creation with vault-retrieved token
- [ ] Remove token from ~/.zshrc after successful migration
- [ ] Document vault retrieval pattern for other scripts
