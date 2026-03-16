# Cloudflare API Token - IP Restriction Issue

**Date**: 2026-02-11 02:13 UTC
**Status**: ❌ IP Restricted

## Token Status

**Token**: `mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_`
**Type**: Account API Token
**Permission**: Read all resources
**Verify**: ✅ Success (account-specific endpoint)
**Zone Access**: ❌ Failed (IP restriction)

## Error Details

**Error Code**: 9109
**Error Message**: `Cannot use the access token from location: 130.105.68.4`

**Current IP**: 130.105.68.4
**Restriction**: Token has IP allowlist that excludes current location

## Root Cause

Token was created with **IP address filtering** enabled, and the current IP (130.105.68.4) is not in the allowed list.

## Additional Issue

**Token Type**: Account API token with "Read all resources" permission
**Problem**: READ-ONLY access (cannot create/edit DNS records)

**What's needed**: Zone-specific token with DNS EDIT permission

## Resolution Options

### Option 1: Create New Token (Recommended)

**Correct Configuration**:

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click: **Create Token**
3. Template: **Edit zone DNS**
4. **Zone Resources**:
   - Include → Specific zone → **insightpulseai.com**
5. **Client IP Address Filtering**:
   - **Leave blank** (no restrictions), OR
   - Add: `130.105.68.4/32` to allowed IPs
6. **Permissions** (auto-configured by template):
   - Zone → DNS → Edit ✅
   - Zone → Zone → Read ✅
7. Create token and copy immediately

### Option 2: Modify Existing Token

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Find token: `mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_`
3. Click: **Edit**
4. **Client IP Address Filtering**:
   - Add: `130.105.68.4/32`, OR
   - Remove all IP restrictions
5. **Change permissions**:
   - Add: Zone → DNS → Edit
   - Add: Zone → Zone → Read
   - Scope to: insightpulseai.com
6. Save changes

**Note**: Option 2 still has the READ-ONLY limitation. Option 1 is strongly recommended.

## Required Token Specifications

```yaml
Token Type: User API Token (not Account token)
Template: Edit zone DNS

Permissions:
  - Zone.DNS.Edit ✅
  - Zone.Zone.Read ✅

Zone Resources:
  - Include: Specific zone
  - Zone: insightpulseai.com

IP Restrictions:
  - None (recommended), OR
  - Allowlist: 130.105.68.4/32

TTL: No expiration (or as needed)
```

## Test Procedure

After creating correct token:

```bash
export CF_API_TOKEN="<new_token>"
export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"

# 1. Verify token
curl -sS "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# 2. Test zone read
curl -sS "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# 3. Test DNS record list
curl -sS "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN"

# 4. Test DNS record creation (with test record)
curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"test.insightpulseai.com","content":"1.2.3.4","ttl":1,"proxied":false}'
```

Expected results: All 4 tests should return `"success": true`

## Comparison: Account vs User Tokens

| Feature | Account Token (Current) | User Token (Needed) |
|---------|------------------------|---------------------|
| Scope | Account-wide | Zone-specific |
| Permissions | Read all resources | DNS Edit + Zone Read |
| IP Restrictions | Yes (blocking) | Configurable |
| DNS Edit | ❌ No | ✅ Yes |
| Our Use Case | ❌ Insufficient | ✅ Correct |

## Current Vault Status

No valid token stored yet. After creating correct token:

```sql
-- Store in Supabase Vault
SELECT vault.create_secret(
  'CLOUDFLARE_API_TOKEN',
  '<new_user_token_with_dns_edit>',
  'Cloudflare API token for insightpulseai.com DNS - User token with zone-specific DNS edit'
);
```

## Summary

**Problem 1**: IP restriction (130.105.68.4 blocked)
**Problem 2**: Read-only permissions (no DNS edit)
**Problem 3**: Account-level token instead of zone-specific user token

**Solution**: Create zone-specific USER token with DNS edit permission and no IP restrictions (or include 130.105.68.4)
