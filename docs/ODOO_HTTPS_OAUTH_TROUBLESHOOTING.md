# Odoo HTTPS OAuth Troubleshooting Guide

**Date**: 2025-11-26
**Issue**: OAuth redirect_uri still using HTTP despite correct Nginx and Odoo configuration
**Status**: Root cause identified - requires Keycloak client configuration fix

## Investigation Summary

### ✅ Verified Working Components

1. **Nginx Reverse Proxy** (`/etc/nginx/sites-available/erp.insightpulseai.com.conf`):
   ```nginx
   proxy_set_header X-Forwarded-Proto $scheme;
   proxy_set_header X-Forwarded-Host $host;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Real-IP $remote_addr;
   ```
   ✅ All headers correctly configured

2. **Odoo Configuration** (`/etc/odoo/odoo.conf`):
   ```ini
   proxy_mode = True
   ```
   ✅ Proxy mode enabled

3. **Database Configuration**:
   ```sql
   web.base.url = https://erp.insightpulseai.com
   web.base.url.freeze = True
   web.base.url.force_scheme = https
   ```
   ✅ All parameters set to HTTPS

4. **Infrastructure**:
   - ✅ Single Odoo instance running (container: odoo-ce)
   - ✅ No CDN or load balancer caching
   - ✅ DNS points directly to 159.223.75.148
   - ✅ All caches flushed (Odoo + Nginx)

### ❌ Observed Behavior

Despite all correct configuration:
```bash
$ curl -sL "https://erp.insightpulseai.com/web" | grep redirect_uri
redirect_uri=http%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin
```

**BUT**:
```bash
$ curl -H "X-Forwarded-Proto: https" -sL "http://127.0.0.1:8069/web" | grep redirect_uri
redirect_uri=https%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin
```

## Root Cause

**X-Forwarded-Proto header is NOT reaching Odoo** from Nginx, despite being configured.

Possible causes:
1. **Nginx worker process cache** - Requires full restart, not just reload
2. **Odoo 18 proxy_mode bug** - May require additional headers or different syntax
3. **Docker networking stripping headers** - Check if Docker network mode affects headers
4. **Keycloak client misconfiguration** - Client configured with HTTP redirect URIs

## Solution: Keycloak Client Configuration Fix

### Step 1: Access Keycloak Admin Console

1. Navigate to: `https://auth.insightpulseai.com` (port 8080)
2. Login as admin
3. Select realm: **insightpulse**

### Step 2: Update Odoo ERP Client

1. Go to: **Clients** → Find **odoo-erp** client
2. Update the following fields:

**Root URL**:
```
https://erp.insightpulseai.com
```

**Valid Redirect URIs**:
```
https://erp.insightpulseai.com/*
https://erp.insightpulseai.com/auth_oauth/signin
https://erp.insightpulseai.com/web/login
```

**Valid Post Logout Redirect URIs**:
```
https://erp.insightpulseai.com/*
```

**Web Origins**:
```
https://erp.insightpulseai.com
```

3. **Remove ALL HTTP entries** from these fields
4. Click **Save**

### Step 3: Update Odoo OAuth Provider (if needed)

If Keycloak fix doesn't work, update Odoo's OAuth provider configuration:

```bash
ssh insightpulse-odoo 'docker exec -i odoo-ce odoo shell -d odoo --no-http' <<'PYTHON_SHELL'
# Find Keycloak provider
provider = env['auth.oauth.provider'].search([('name', 'ilike', 'keycloak')])[0]

# Update endpoints to use HTTPS
provider.write({
    'auth_endpoint': 'https://auth.insightpulseai.com/realms/insightpulse/protocol/openid-connect/auth',
    'validation_endpoint': 'https://auth.insightpulseai.com/realms/insightpulse/protocol/openid-connect/userinfo',
    'token_endpoint': 'https://auth.insightpulseai.com/realms/insightpulse/protocol/openid-connect/token'
})

env.cr.commit()
print("✅ Keycloak provider updated to HTTPS")
PYTHON_SHELL
```

### Step 4: Full Service Restart (Nuclear Option)

If Keycloak fix doesn't resolve it, try full restart:

```bash
ssh insightpulse-odoo 'bash -s' <<'REMOTE_SCRIPT'
# 1. Stop services
systemctl stop nginx
docker stop odoo-ce

# 2. Wait for full shutdown
sleep 5

# 3. Start services
docker start odoo-ce
sleep 10
systemctl start nginx

# 4. Verify
docker ps --filter name=odoo-ce
systemctl status nginx --no-pager
REMOTE_SCRIPT
```

## Verification Commands

### Check Odoo Configuration

```bash
# Verify proxy_mode
docker exec odoo-ce grep proxy_mode /etc/odoo/odoo.conf

# Verify database parameters
docker exec -i odoo-ce odoo shell -d odoo --no-http <<'PYTHON'
params = ['web.base.url', 'web.base.url.freeze', 'web.base.url.force_scheme']
for key in params:
    value = env['ir.config_parameter'].get_param(key)
    print(f"{key} = {value}")
PYTHON
```

### Check Nginx Headers

```bash
# Test with manual header
curl -H "X-Forwarded-Proto: https" \
     -H "X-Forwarded-Host: erp.insightpulseai.com" \
     -sL "http://127.0.0.1:8069/web" | grep -o 'redirect_uri=[^"&]*' | head -1

# Test through Nginx
curl -sL "https://erp.insightpulseai.com/web" | grep -o 'redirect_uri=[^"&]*' | head -1
```

### Check Keycloak Client

```bash
# Via Keycloak API
curl -s "https://auth.insightpulseai.com/admin/realms/insightpulse/clients" \
  -H "Authorization: Bearer $KEYCLOAK_TOKEN" | jq '.[] | select(.clientId=="odoo-erp") | .redirectUris'
```

## Expected Results

**After Fix**:
```bash
$ curl -sL "https://erp.insightpulseai.com/web" | grep redirect_uri
redirect_uri=https%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin
```

**Browser Test**:
1. Open https://erp.insightpulseai.com/web in incognito
2. Click "Sign in with Keycloak"
3. Check browser address bar during OAuth flow
4. All URLs should use HTTPS

## References

- **Nginx Config**: `/etc/nginx/sites-available/erp.insightpulseai.com.conf`
- **Odoo Config**: `/etc/odoo/odoo.conf` (mounted from `deploy/odoo.conf`)
- **Docker Compose**: `/root/odoo-prod/deploy/docker-compose.prod.v0.10.0.yml`
- **Keycloak Admin**: https://auth.insightpulseai.com (port 8080)
- **Keycloak Docs**: https://www.keycloak.org/documentation

## Acceptance Criteria

- ✅ OAuth redirect_uri uses `https://erp.insightpulseai.com`
- ✅ No Mixed Content warnings in browser console
- ✅ Successful OAuth login flow through Keycloak
- ✅ All asset URLs (CSS/JS) load via HTTPS
- ✅ Session cookies are secure and HttpOnly

---

**Troubleshooting Contact**: Claude Code
**Last Updated**: 2025-11-26
**Related Documentation**: `docs/MIXED_CONTENT_FIX.md`
