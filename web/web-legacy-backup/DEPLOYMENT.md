# insightpulseai.com Deployment Guide

**Goal**: Deploy Next.js website to https://insightpulseai.com (NOT Odoo)

**Current Issue**: Main domain currently serves Odoo (wrong!)

---

## Architecture

```
insightpulseai.com → Vercel (Next.js public website) ✅
erp.insightpulseai.com → DigitalOcean (Odoo ERP) ✅
```

---

## Quick Deployment (Vercel Dashboard)

### Step 1: Deploy to Vercel

1. **Visit**: https://vercel.com/new

2. **Import Git Repository**:
   - Repository: `Insightpulseai/odoo`
   - Framework Preset: **Next.js**
   - Root Directory: **`apps/web`**

3. **Build & Development Settings**:
   ```
   Framework: Next.js
   Root Directory: apps/web
   Build Command: cd ../.. && pnpm install && pnpm build --filter=@ipai/web
   Output Directory: .next
   Install Command: pnpm install --frozen-lockfile
   Development Command: pnpm dev
   ```

4. **Environment Variables** (none required for now)

5. **Click**: Deploy

6. **Wait**: ~3 minutes for build

7. **Result**: You'll get a URL like `https://web-xxxxx.vercel.app`

### Step 2: Add Custom Domain

1. **In Vercel Project**:
   - Settings → Domains
   - Add Domain: `insightpulseai.com`

2. **Vercel will show**:
   ```
   Add the following DNS record:

   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

### Step 3: Update Cloudflare DNS

1. **Login to Cloudflare**: https://dash.cloudflare.com

2. **Select Domain**: insightpulseai.com

3. **Update DNS Records**:

   **Current (WRONG)**:
   ```
   A @ 172.67.137.254 (Cloudflare proxy to Odoo)
   ```

   **New (CORRECT)**:
   ```
   Type: CNAME
   Name: @
   Target: cname.vercel-dns.com
   Proxy Status: DNS only (grey cloud, NOT orange)
   TTL: Auto
   ```

4. **Add Odoo Subdomain** (if not exists):
   ```
   Type: A
   Name: erp
   Target: 178.128.112.214 (DigitalOcean droplet)
   Proxy Status: Proxied (orange cloud)
   ```

5. **Save Changes**

### Step 4: Verify

```bash
# Wait 5 minutes for DNS propagation
dig insightpulseai.com +short
# Should show Vercel IPs (76.76.21.21 or similar)

# Test website
curl -I https://insightpulseai.com
# Should show HTTP 200 and Vercel server headers

# Test Odoo
curl -I https://erp.insightpulseai.com
# Should show Odoo redirect
```

---

## Current DNS Configuration (TO CHANGE)

**Before (Wrong - Main domain serves Odoo)**:
```
insightpulseai.com → Cloudflare → Odoo
```

**After (Correct - Separation of concerns)**:
```
insightpulseai.com → Vercel → Next.js website
erp.insightpulseai.com → DigitalOcean → Odoo ERP
```

---

## Troubleshooting

### Issue: Vercel build fails with "workspace not found"

**Solution**: Use monorepo build command:
```bash
cd ../.. && pnpm install && pnpm build --filter=@ipai/web
```

### Issue: DNS not updating

**Solutions**:
1. Disable Cloudflare proxy (grey cloud, not orange)
2. Wait 5-10 minutes for propagation
3. Clear DNS cache: `sudo dscacheutil -flushcache` (macOS)
4. Check with: `dig insightpulseai.com +short`

### Issue: SSL certificate not provisioning

**Solutions**:
1. Ensure CNAME points to `cname.vercel-dns.com`
2. Remove Cloudflare proxy (DNS only mode)
3. Wait 10 minutes for Vercel to provision Let's Encrypt certificate
4. Check Vercel dashboard for certificate status

### Issue: 404 on main domain

**Solutions**:
1. Verify deployment completed successfully in Vercel
2. Check build logs for errors
3. Ensure root directory is set to `apps/web`
4. Verify production deployment is active (not just preview)

---

## Post-Deployment Checklist

- [ ] https://insightpulseai.com loads Next.js website (not Odoo)
- [ ] SSL certificate valid (green lock icon)
- [ ] https://erp.insightpulseai.com redirects to Odoo login
- [ ] No mixed content warnings
- [ ] Mobile responsive
- [ ] Performance score > 90 (test at PageSpeed Insights)

---

## Odoo Configuration Update

After DNS change, update Odoo to use subdomain:

**File**: `/etc/odoo/odoo.conf` (on DigitalOcean droplet)

```ini
[options]
# Update base URL
web.base.url = https://erp.insightpulseai.com

# Other settings remain the same...
```

Or via Odoo UI:
1. Settings → General Settings
2. System Parameters
3. Key: `web.base.url`
4. Value: `https://erp.insightpulseai.com`

---

## Deployment Checklist

### Before Deployment
- [x] Next.js app exists at `apps/web`
- [x] Build command configured for monorepo
- [x] Vercel project created
- [ ] Custom domain added in Vercel
- [ ] DNS records updated in Cloudflare

### During Deployment
- [ ] Build succeeds on Vercel
- [ ] Preview deployment works
- [ ] Production deployment promoted

### After Deployment
- [ ] Main domain serves Next.js
- [ ] Odoo accessible on subdomain
- [ ] SSL certificates valid
- [ ] All links working
- [ ] Mobile responsive
- [ ] Analytics configured (optional)

---

**Last Updated**: 2026-02-09
**Status**: Ready to deploy
**Estimated Time**: 15 minutes total
