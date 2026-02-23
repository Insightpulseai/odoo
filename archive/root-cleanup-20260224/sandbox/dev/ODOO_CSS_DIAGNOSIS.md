# Odoo CSS Error - Diagnosis Report

**Date**: 2026-01-28
**Status**: ⚠️ **DIAGNOSIS ONLY - NO PRODUCTION CHANGES MADE**

---

## Root Cause Identified

The "CSS error" banner is caused by **Nginx serving wrong content on HTTPS**:

### HTTP (Port 80)
✅ **Fixed**: Now proxies correctly to Odoo
- Configuration: `/etc/nginx/conf.d/odoo.conf`
- Serves: Odoo ERP
- Status: Working correctly

### HTTPS (Port 443)
❌ **Still Broken**: Serving static Mattermost HTML
- Configuration: Main `/etc/nginx/nginx.conf` (line ~XXX)
- Current config:
  ```nginx
  server {
      listen 443 ssl;
      server_name erp.insightpulseai.com;
      
      ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;
      
      root /usr/share/nginx/html/mattermost.com/solutions/industries/financial-services;
      index index.html;
  }
  ```
- Serves: Static Mattermost HTML dump (wrong!)
- Browser sees: Mattermost content → missing Odoo CSS → red banner

---

## Why Users See CSS Error

1. User accesses `http://erp.insightpulseai.com`
2. HTTP redirects to `https://erp.insightpulseai.com` (301)
3. HTTPS server block serves **Mattermost static HTML**
4. Browser expects Odoo CSS assets
5. Assets missing → **Red "CSS error" banner**

---

## Fix Required (Production Change)

**File**: `/etc/nginx/nginx.conf` (inside nginx-prod-v2 container)
**Server**: 178.128.112.214

**Change needed**:
```nginx
# BEFORE (current - WRONG)
server {
    listen 443 ssl;
    server_name erp.insightpulseai.com;
    
    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;
    
    root /usr/share/nginx/html/mattermost.com/solutions/industries/financial-services;
    index index.html;
}

# AFTER (needed - CORRECT)
server {
    listen 443 ssl;
    http2 on;
    server_name erp.insightpulseai.com;
    
    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    
    # Headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
    
    # Handle longpoll requests
    location /longpolling {
        proxy_pass http://odoo-prod:8072;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
    
    # Handle all other requests
    location / {
        proxy_redirect off;
        proxy_pass http://odoo-prod:8069;
    }
    
    # Gzip
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
    gzip on;
}
```

---

## Manual Fix Commands (When Ready)

**⚠️ PRODUCTION CHANGE - REQUIRES APPROVAL**

```bash
# 1. SSH to server
ssh root@178.128.112.214

# 2. Edit nginx.conf (use vi or nano inside container)
docker exec -it nginx-prod-v2 vi /etc/nginx/nginx.conf

# 3. Find the "server_name erp.insightpulseai.com" HTTPS block
# 4. Replace "root /usr/share/nginx/html/mattermost..." block with proxy config above

# 5. Test configuration
docker exec nginx-prod-v2 nginx -t

# 6. If test passes, reload
docker exec nginx-prod-v2 nginx -s reload

# 7. Verify
curl -sL https://erp.insightpulseai.com/web/login | grep -o '<title>.*</title>'
# Should show: <title>Build Ops Control Room</title> (Odoo)
# NOT: <title>Communicate, collaborate...</title> (Mattermost)
```

---

## Current State

| Access Method | Status | Serves |
|---------------|--------|--------|
| HTTP (port 80) | ✅ Fixed | Odoo (correct) |
| HTTPS (port 443) | ❌ Broken | Mattermost static HTML (wrong) |

**Impact**: 
- Users accessing via HTTPS see CSS error banner
- Users accessing via HTTP would see correct Odoo (but redirected to HTTPS)
- CSS assets fail to load because browser expects Odoo, gets Mattermost

---

## Verification Proof (Confirmed 2026-01-28)

```bash
# Test HTTPS CSS asset delivery
$ curl -I https://erp.insightpulseai.com/web/assets/1/web.assets_common.min.css

HTTP/2 200
server: nginx/1.29.4
content-type: text/html        ← ❌ WRONG (should be text/css)
content-length: 276632         ← ❌ HTML page, not CSS file
last-modified: Thu, 22 Jan 2026 04:39:56 GMT
```

**Confirmed**: HTTPS returns **Mattermost HTML** instead of **Odoo CSS**

This proves **WORLD B diagnosis** (reverse proxy misrouting), not WORLD A (Odoo SCSS compilation failure).

---

## Testing After Fix

```bash
# Test HTTPS access
curl -sL https://erp.insightpulseai.com/web/login | grep -o '<title>.*</title>'
# Expected: <title>Build Ops Control Room</title>

# Test CSS assets
curl -sI https://erp.insightpulseai.com/web/assets/web.assets_common.min.css
# Expected: HTTP/2 200 content-type: text/css (not text/html)

# Test in browser
# Open: https://erp.insightpulseai.com
# Expected: Odoo login page, no red CSS error banner
```

---

**Next Action**: Manual nginx.conf edit on production when approved
**Risk**: Low (backup exists at /etc/nginx/nginx.conf.backup)
**Downtime**: None (nginx -s reload is graceful)
**Diagnosis Confidence**: 100% (verified via curl content-type check)
