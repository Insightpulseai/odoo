# Cloudflare API Token - Permissions Issue

**Date**: 2026-02-11 02:11 UTC
**Status**: ❌ Authentication Failed (Rate Limited)

## Token Status

**Token Created**: `zBLMUS5lmx81MDvDNUEGwVqlnyGL64akYup-JTZX`
**Verify Endpoint**: ✅ Success (token is valid)
**DNS Operations**: ❌ Failed (authentication error)

## Error Sequence

1. **DNS Record Creation (n8n)**: `Authentication error` (code 10000)
2. **DNS Record Creation (superset)**: `Authentication error` (code 10000)
3. **DNS Record Creation (mcp)**: `Rate limited` (code 10429)
4. **Zone List**: Failed (no zones accessible)
5. **Zone Direct Access**: `Too many authentication failures` (code 10502)

## Root Cause

**Token permissions insufficient** - Token verifies successfully but lacks necessary permissions for:
- Zone read access
- DNS record create/edit access for insightpulseai.com

## Resolution

### Recreate Token with Correct Permissions

**Cloudflare Dashboard Steps**:

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click: **Create Token**
3. Use template: **Edit zone DNS**
4. **CRITICAL**: Configure Zone Resources:
   - Click **Zone Resources** section
   - Change from "All zones" to: **Include** → **Specific zone**
   - Select: **insightpulseai.com**
5. **Permissions should show**:
   - Zone → DNS → Edit ✅
   - Zone → Zone → Read ✅
6. **Optional**: Set expiration (default: no expiration)
7. Click: **Continue to summary**
8. Click: **Create Token**
9. **Copy token immediately** (shown only once)

### Expected Token Permissions

```yaml
Permissions:
  - Zone.DNS.Edit (allows creating/editing DNS records)
  - Zone.Zone.Read (allows reading zone information)

Zone Resources:
  - Include: Specific zone
  - Zone: insightpulseai.com (73f587aee652fc24fd643aec00dcca81)

Account Resources:
  - Not required
```

### After Token Creation

```bash
# Test token
export CF_API_TOKEN="<new_token>"
curl -sS "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# Verify zone access
export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"
curl -sS "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# Store in Supabase Vault
psql "$SUPABASE_DB_URL" -c "
  DELETE FROM vault.secrets WHERE name = 'CLOUDFLARE_API_TOKEN';
  SELECT vault.create_secret(
    'CLOUDFLARE_API_TOKEN',
    '<new_token>',
    'Cloudflare API token for insightpulseai.com DNS - created 2026-02-11'
  );
"

# Execute DNS upsert
bash docs/evidence/20260211-0207/dns-setup/dns-upsert-config.md
```

## Rate Limiting

**Current Status**: Temporarily rate limited due to multiple authentication failures

**Wait Time**: 5-10 minutes before retrying

**Mitigation**: Recreate token with correct permissions before retrying to avoid further rate limiting

## What Went Wrong

The "Edit zone DNS" template requires **explicit zone selection**. If the token was created without:
- Selecting "Specific zone" in Zone Resources, OR
- Selecting the correct zone (insightpulseai.com)

Then the token will verify successfully but fail on all actual API operations with authentication errors.

## Current Vault Status

✅ Token stored in Supabase Vault as `CLOUDFLARE_API_TOKEN`
⚠️ Token has insufficient permissions and needs replacement

**To replace**:
```sql
-- Delete old token
DELETE FROM vault.secrets WHERE name = 'CLOUDFLARE_API_TOKEN';

-- Store new token with correct permissions
SELECT vault.create_secret(
  'CLOUDFLARE_API_TOKEN',
  '<new_token_with_zone_access>',
  'Cloudflare API token for insightpulseai.com DNS'
);
```

## Verification Checklist

After recreating token, verify:
- [ ] Token verifies successfully: `/user/tokens/verify`
- [ ] Zone accessible: `/zones/73f587aee652fc24fd643aec00dcca81`
- [ ] DNS records listable: `/zones/.../dns_records`
- [ ] DNS record creation works: Create test A record
- [ ] All three subdomains created: n8n, superset, mcp
- [ ] DNS resolution works: `dig @1.1.1.1 +short <subdomain>`
