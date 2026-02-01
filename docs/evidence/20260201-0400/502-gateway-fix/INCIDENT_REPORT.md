# Incident Report: 502 Bad Gateway - erp.insightpulseai.net

## Summary
- **Date**: 2026-02-01 04:09 UTC
- **Symptom**: 502 Bad Gateway returned by nginx/1.29.4
- **Affected Service**: erp.insightpulseai.net (Odoo ERP production)
- **Status**: FIX COMMITTED - Requires deployment

## Root Cause Analysis

The nginx configuration used Docker service hostname resolution (`odoo:8069`) for the upstream, but nginx runs **on the host** (not in Docker). The Docker service name `odoo` is only resolvable within the Docker network `odoo_backend`.

### Configuration Mismatch

| Component | Expected | Actual |
|-----------|----------|--------|
| Nginx upstream | `127.0.0.1:8069` (localhost) | `odoo:8069` (Docker hostname) |
| Nginx location | Host-based access | Docker network access |
| Result | Connection | DNS resolution failure |

### Evidence

**docker-compose.prod.yml port binding** (correct):
```yaml
ports:
  - "127.0.0.1:${ODOO_PORT:-8069}:8069"
```

**nginx upstream** (was incorrect):
```nginx
upstream odoo {
    server odoo:8069;  # WRONG: odoo hostname not resolvable from host
}
```

## Fix Applied

### 1. Updated nginx upstream configuration

**File**: `deploy/nginx/erp.insightpulseai.net.conf`

```diff
-upstream odoo {
-    server odoo:8069;
-}
-upstream odoo_im {
-    server odoo:8072;
-}
+# Upstreams use localhost since nginx runs on host, not in Docker
+# Odoo container binds to 127.0.0.1:8069 (see docker-compose.prod.yml)
+upstream odoo {
+    server 127.0.0.1:8069;
+}
+upstream odoo_im {
+    server 127.0.0.1:8072;
+}
```

### 2. Added longpolling port binding

**File**: `deploy/docker-compose.prod.yml`

```diff
 ports:
   - "127.0.0.1:${ODOO_PORT:-8069}:8069"
+  - "127.0.0.1:8072:8072"  # Longpolling (required when workers > 0)
```

### 3. Created diagnostic script

**File**: `scripts/deploy/diagnose_502.sh`

Usage:
```bash
# Diagnose
./scripts/deploy/diagnose_502.sh

# Diagnose + Auto-fix
./scripts/deploy/diagnose_502.sh --fix
```

## Deployment Instructions

On the DigitalOcean droplet (178.128.112.214):

```bash
# 1. Pull latest changes
cd /opt/odoo-ce/repo
git pull origin claude/erp-odoo-implementation-M3RDD

# 2. Copy updated nginx config
sudo cp deploy/nginx/erp.insightpulseai.net.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/

# 3. Test nginx config
sudo nginx -t

# 4. Reload nginx
sudo systemctl reload nginx

# 5. Restart Odoo stack (if not already running)
cd /opt/odoo-ce/deploy
docker compose -f docker-compose.prod.yml up -d

# 6. Verify
curl -I https://erp.insightpulseai.net/web/health
```

## Verification Checklist

- [ ] nginx config test passes (`nginx -t`)
- [ ] nginx reload successful
- [ ] Odoo container running (`docker ps | grep odoo`)
- [ ] Health check returns 200 (`curl http://127.0.0.1:8069/web/health`)
- [ ] External access works (`curl -I https://erp.insightpulseai.net`)

## Prevention

1. **Consistency rule**: When nginx runs on host, always use `127.0.0.1:PORT` for upstreams
2. **Alternative**: Move nginx into Docker on `odoo_backend` network (then `odoo:8069` works)
3. **Added diagnostic script** for future 502 issues: `scripts/deploy/diagnose_502.sh`

## Files Changed

| File | Change |
|------|--------|
| `deploy/nginx/erp.insightpulseai.net.conf` | Fixed upstream to use localhost |
| `deploy/docker-compose.prod.yml` | Added port 8072 for longpolling |
| `scripts/deploy/diagnose_502.sh` | New diagnostic/recovery script |
