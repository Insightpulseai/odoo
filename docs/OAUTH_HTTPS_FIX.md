# AADSTS50011 Fix: OAuth HTTPS Redirect URI Mismatch

**Status:** 🔴 BLOCKING PRODUCTION ISSUE
**Symptom:** Users cannot log in to erp.insightpulseai.com with Microsoft/Google accounts
**Error Code:** AADSTS50011 - "The redirect URI specified in the request does not match the redirect URIs configured for the application"
**Root Cause:** Odoo is sending HTTP redirect URIs to OAuth providers, but app registrations only accept HTTPS
**Solution:** Install `ipai_auth_oauth_https` module (already in codebase)

---

## Issue Details

### What's Happening

1. User clicks "Sign in with Microsoft" on erp.insightpulseai.com
2. Odoo generates OAuth callback URL: `http://erp.insightpulseai.com/auth_oauth/signin` ❌ HTTP
3. Azure Entra ID app registration only has: `https://erp.insightpulseai.com/auth_oauth/signin` ✅ HTTPS
4. Azure rejects the request: **AADSTS50011 error**

### App Registration Details

| Field | Value |
|-------|-------|
| **App ID** | `3446e178-3eba-48c9-b5bd-4283ff729eb1` |
| **Configured Redirect URI** | `https://erp.insightpulseai.com/auth_oauth/signin` (HTTPS) |
| **Actual Redirect Sent** | `http://erp.insightpulseai.com/auth_oauth/signin` (HTTP) ❌ |
| **Environment** | Azure Container Apps behind Azure Front Door |

### Why This Happens

When Odoo runs behind a reverse proxy (Azure Front Door), it doesn't automatically know that the original request was HTTPS. The HTTP scheme gets propagated through the proxy unless:

1. The reverse proxy forwards the `X-Forwarded-Proto: https` header, OR
2. Odoo's auth_oauth module is overridden to force HTTPS, OR
3. The issue is patched at the container image level

---

## Solution: Install `ipai_auth_oauth_https` Module

### What This Module Does

File: `addons/ipai/ipai_auth_oauth_https/controllers/main.py`

```python
class OAuthLoginHttpsFix(OAuthLogin):
    """Force HTTPS callback generation for OAuth providers
       when Odoo deployed behind Azure reverse proxies."""

    def list_providers(self):
        providers = super().list_providers()
        for provider in providers:
            auth_link = provider.get("auth_link")
            if isinstance(auth_link, str):
                # Replace http:// with https:// in redirect_uri parameter
                provider["auth_link"] = auth_link.replace(
                    "redirect_uri=http%3A%2F%2F",
                    "redirect_uri=https%3A%2F%2F",
                    1,
                )
        return providers
```

**Result:** All OAuth callbacks automatically use HTTPS, matching app registration config.

---

## How to Fix (Choose One)

### Option A: Install via Odoo UI (Fastest)

**Prerequisites:** Admin access to erp.insightpulseai.com

1. Go to: **https://erp.insightpulseai.com/web/login**
2. Log in as **admin**
3. Go to **Apps** (left sidebar)
4. Search for: **`ipai_auth_oauth_https`**
5. Click **Install**
6. Wait for installation to complete (~10 seconds)
7. **Test:** Log out, then try "Sign in with Microsoft" - should work now ✅

### Option B: Install via CLI (Production)

**Run this command on the ACA container:**

```bash
docker exec odoo odoo-bin -d erp -c /etc/odoo/odoo.conf -i ipai_auth_oauth_https
```

**Or use the deployment script:**

```bash
chmod +x scripts/fix-oauth-https-redirect.sh
./scripts/fix-oauth-https-redirect.sh

# Dry-run first to see what will happen:
./scripts/fix-oauth-https-redirect.sh --dryrun
```

### Option C: Ensure It's in Deployment (Permanent)

**File:** `ssot/odoo/module_contracts/odoo_copilot_foundry.yaml`

✅ **Already updated** - the module is now in the `canonical_custom_modules` list and will be installed by default.

Next time you deploy Odoo, `ipai_auth_oauth_https` will be automatically installed.

---

## Verification Steps

### 1. Verify Module is Installed

**In Odoo UI:**
- Go to **Apps**
- Search: `ipai_auth_oauth_https`
- Status should show: **Installed** ✅

**Via CLI:**
```bash
docker exec odoo odoo-bin -d erp -c /etc/odoo/odoo.conf --shell
# In the Odoo shell:
# >>> from odoo.modules import get_modules
# >>> 'ipai_auth_oauth_https' in [m for m in dir(get_modules())]
```

### 2. Test OAuth Login

1. **Log out** of erp.insightpulseai.com (or use incognito browser)
2. Go to login page: **https://erp.insightpulseai.com/web/login**
3. Click **"Sign in with Microsoft"** (or Google)
4. You should be redirected to OAuth provider
5. After authentication, you should be logged in ✅

**If still seeing error:**
- Check browser console (F12) for redirect URL
- It should contain `https://` (not `http://`)
- If still HTTP, see "Troubleshooting" section below

### 3. Check Azure Front Door Headers (Optional)

Verify that Azure Front Door is forwarding the `X-Forwarded-Proto` header:

```bash
curl -v https://erp.insightpulseai.com/auth_oauth/signin \
  -H "X-Forwarded-Proto: https" \
  -H "X-Forwarded-Host: erp.insightpulseai.com" 2>&1 | grep "Forwarded-Proto"
```

---

## Troubleshooting

### Still Getting AADSTS50011?

| Symptom | Check | Solution |
|---------|-------|----------|
| Error persists after module install | Module not actually installed | Run Option A or B again, refresh browser cache |
| Redirect URL still shows `http://` | Azure Front Door not forwarding headers | Contact Infrastructure team - check AFD backend settings |
| Module won't install | Missing auth_oauth module | Install auth_oauth first, then ipai_auth_oauth_https |

### Alternative: Temporary Fallback

If the module doesn't resolve it, you can **temporarily** add HTTP redirect URI to the app registration as a fallback (not recommended for production security):

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations** → Search for `3446e178-3eba-48c9-b5bd-4283ff729eb1`
2. Click **Authentication** → **Redirect URIs**
3. Add: `http://erp.insightpulseai.com/auth_oauth/signin`
4. Click **Save**

**⚠️ Security Warning:** Remove this HTTP redirect URI once Azure Front Door properly forwards `X-Forwarded-Proto: https` header.

---

## Reference Files

- **Module code:** `addons/ipai/ipai_auth_oauth_https/`
- **Deployment config:** `ssot/odoo/module_contracts/odoo_copilot_foundry.yaml`
- **App registration SSOT:** `ssot/entra/app_registrations.azure_native.yaml`
- **Deployment script:** `scripts/fix-oauth-https-redirect.sh`
- **Identity architecture:** `docs/architecture/identity-architecture.md`

---

## Related Issues

- **Azure Front Door Header Forwarding:** If X-Forwarded-Proto header not forwarded, Azure Front Door backend settings need update
- **Odoo Reverse Proxy Detection:** Odoo relies on request headers to determine HTTPS - if missing, force HTTPS via this module
- **Multi-tenant OAuth:** Each tenant's app registration must have matching redirect URIs

---

**Status:** Ready to fix
**Effort:** ~5 minutes (Option A) or ~30 seconds (Option B)
**Impact:** Unblocks all user authentication to erp.insightpulseai.com
