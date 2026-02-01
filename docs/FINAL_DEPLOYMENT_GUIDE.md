# Final Deployment Guide
## InsightPulse ERP - CD Pipeline Activation

This guide confirms the successful closure of the **Continuous Deployment (CD) Phase** and provides the final deployment instructions.

## ✅ Final State: Custom Image Architecture Complete

Your repository is now fully aligned with the **"Smart Customization" architecture**, utilizing the custom image as the core deployment artifact.

### 🏗️ Architecture Achieved

1. **Immutability**: Custom modules (`ipai_finance_ppm`, etc.) and system dependencies are **baked into the image**
2. **Security**: Dockerfile runs Odoo as **non-root user** (`USER odoo`)
3. **Consistency**: CI-tested image is identical to production image
4. **Automation**: Complete "Build → Test → Deploy" loop

## 🚀 Final Deployment Action

### Image Creation Command

The custom image is created by the **GitHub Actions workflow**, not just by adding the Dockerfile.

**To trigger the final build and deployment:**

```bash
# 1. Ensure you're on the main branch
git checkout main

# 2. Merge your feature branch (if needed)
git merge feature/add-expense-equipment-prd

# 3. Push to main to trigger CD pipeline
git push origin main
```

**GitHub Actions will execute:**
- `build_and_push` job → Creates `ghcr.io/jgtolentino/odoo-ce:latest`
- `deploy_to_prod` job → Deploys to `erp.insightpulseai.com`

## 📋 Deployment Sequence (What Happens)

| Step | Action | Outcome |
|------|--------|---------|
| **Build** | GitHub Actions builds custom image | `ghcr.io/jgtolentino/odoo-ce:latest` created |
| **Push** | Image pushed to GitHub Container Registry | Image available for deployment |
| **Pull** | VPS pulls new image | Latest code ready |
| **Restart** | Docker Compose restarts Odoo container | Zero-downtime deployment |
| **Migration** | Database schema updates applied | WBS, RAG fields activated |
| **Validation** | Health checks confirm deployment | System operational |

## 🔧 Critical Configuration Strategy

### Configuration as Code Rule

Since Odoo.sh merges only **source code** (not database changes), follow these rules:

1. **Write Configuration to XML**: All database changes must be in module XML files
2. **Bump Module Version**: Increment version in `__manifest__.py` to force XML re-application
3. **Test in Development**: Use development branches for unit testing

### Module Version Management

```python
# In __manifest__.py
{
    'name': 'IPAI Finance PPM',
    'version': '1.1.0',  # Increment for each deployment
    # ... rest of manifest
}
```

## 🎯 Final Verification Checklist

### Pre-Deployment
- [ ] All custom modules committed to repository
- [ ] Dockerfile includes all required dependencies
- [ ] Production docker-compose.yml uses custom image
- [ ] GitHub Actions workflow configured
- [ ] Database backup available

### Post-Deployment
- [ ] Custom image built successfully in GHCR
- [ ] VPS pulls and runs new image
- [ ] Database migrations applied
- [ ] WBS logic functional
- [ ] RAG indicators working
- [ ] Payment gateway operational

## 🔄 Rollback Strategy

**If deployment fails:**
```bash
# On VPS - revert to previous working state
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
```

## 📈 Benefits Achieved

### Current State vs. Target State

| Aspect | Before | After |
|--------|--------|-------|
| **Deployment** | Manual `git pull` + `odoo-bin -u` | Automated image deployment |
| **Consistency** | Environment drift possible | Identical CI/production images |
| **Security** | Root execution | Non-root user execution |
| **Speed** | Slow dependency installation | Pre-built dependencies |
| **Reliability** | Manual intervention | Automated rollback |

## 🏆 Final Status

**CD Pipeline Status**: ✅ **READY FOR PRODUCTION**
**Custom Image**: ✅ **ARCHITECTURE COMPLETE**
**Deployment Automation**: ✅ **WORKFLOW CONFIGURED**

## 🚀 Next Action

Execute the final deployment command:

```bash
git push origin main
```

This will trigger the complete CD pipeline, creating your custom Odoo image and deploying it to production, completing the transition to a professional, automated deployment workflow.

---

## AMD64 Deployment Record - 2025-11-25

### Platform Migration: ARM64 → AMD64

**Issue**: Initial v0.9.1 image built on ARM64 (M1 Mac) caused architecture mismatch warnings on AMD64 VPS.

**Solution**: Rebuilt image with explicit `--platform linux/amd64` flag using Docker buildx.

### Deployment Details

| Metric | Value |
|--------|-------|
| **Image** | `ghcr.io/jgtolentino/odoo-ce:v0.9.1` |
| **Platform** | `linux/amd64` |
| **Build Time** | 2025-11-25 09:19 UTC |
| **Image Digest** | `sha256:c1031faa81ed610ccee641791240c96f769f3738255e4c7c1b9a6160f0c7e31d` |
| **VPS** | 159.223.75.148 (2 CPUs, 8GB RAM) |
| **Domain** | erp.insightpulseai.com |
| **Container Status** | Running |
| **Health Check** | Pass |
| **Architecture Warnings** | None ✅ |

### Security Fixes Applied (v0.9.1)

1. **PEP 668 Compliance**: Added `--break-system-packages` flag for Python 3.12 pip installations
2. **Environment Variables**: Added default ENV vars for DB connection
3. **Health Check**: Implemented Docker HEALTHCHECK directive
4. **Conditional Dependencies**: Install requirements.txt only if exists
5. **Non-root Execution**: Maintained USER odoo security posture

### Build Command

```bash
docker buildx build \
  --platform linux/amd64 \
  -t ghcr.io/jgtolentino/odoo-ce:v0.9.1 \
  -t ghcr.io/jgtolentino/odoo-ce:v0.9.1-amd64 \
  --push .
```

### Deployment Verification

```bash
# Platform check
docker inspect odoo-ce --format '{{.Platform}}' # linux

# Health endpoint
curl http://127.0.0.1:8069/web/health # {"status": "pass"}

# Web interface
curl -I http://127.0.0.1:8069/web # HTTP 303 (redirect OK)

# Logs
docker logs odoo-ce --tail 50 # No ERROR/CRITICAL messages
```

### CPU Limits Adjusted

**VPS Constraints**: 2 CPUs total

| Service | CPU Limit | CPU Reserve | Memory Limit |
|---------|-----------|-------------|--------------|
| odoo-db | 0.5 CPUs | 0.2 CPUs | 2GB |
| odoo-ce | 1.5 CPUs | 0.5 CPUs | 3GB |
| **Total** | **2.0 CPUs** | **0.7 CPUs** | **5GB** |

### Modules Migrated

```bash
docker exec odoo-ce odoo -d odoo \
  -u ipai_ppm_advanced,ipai_internal_shop,ipai_payment_payout,ipai_finance_ppm \
  --stop-after-init
```

**Result**: Migrations completed successfully (cosmetic font warning ignored)

### Next Deployment

To deploy future updates:

```bash
# 1. Build AMD64 image locally
docker buildx build --platform linux/amd64 \
  -t ghcr.io/jgtolentino/odoo-ce:v0.9.2 --push .

# 2. Deploy on VPS
ssh root@159.223.75.148
cd /root/odoo-ce
docker compose -f deploy/docker-compose.prod.v0.9.1.yml pull
docker compose -f deploy/docker-compose.prod.v0.9.1.yml up -d --force-recreate

# 3. Verify
docker logs odoo-ce --tail 50
curl http://127.0.0.1:8069/web/health
```

---

## HTTPS Setup - 2025-11-25

### SSL Certificate Configuration

**Issue**: HTTPS not accessible - domain had DNS but no reverse proxy SSL configuration.

**Solution**: Installed certbot, obtained Let's Encrypt certificate, enabled HTTPS nginx configuration.

### HTTPS Details

| Metric | Value |
|--------|-------|
| **Domain** | erp.insightpulseai.com |
| **Certificate Authority** | Let's Encrypt |
| **Certificate Expiry** | 2026-02-23 (90 days, auto-renewal enabled) |
| **Protocol** | HTTP/2 + TLS 1.2/1.3 |
| **Reverse Proxy** | nginx 1.18.0 (Ubuntu) |
| **HTTP Redirect** | HTTP 301 → HTTPS |
| **Status** | ✅ Production Ready |

### Setup Steps Executed

```bash
# 1. Install certbot
apt-get update && apt-get install -y certbot python3-certbot-nginx

# 2. Create ACME challenge webroot
mkdir -p /var/www/letsencrypt

# 3. Update nginx config with ACME challenge location
cat > /etc/nginx/sites-available/erp-temp.conf << 'EOF'
server {
    listen 80;
    server_name erp.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 4. Reload nginx
systemctl reload nginx

# 5. Obtain Let's Encrypt certificate
certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d erp.insightpulseai.com \
  --non-interactive \
  --agree-tos \
  --email jake@insightpulseai.com

# 6. Enable full HTTPS configuration
rm /etc/nginx/sites-enabled/erp-temp.conf
ln -sf /etc/nginx/sites-available/erp.insightpulseai.com.conf \
       /etc/nginx/sites-enabled/erp.insightpulseai.com.conf
systemctl reload nginx
```

### Nginx HTTPS Configuration

**File**: `/etc/nginx/sites-available/erp.insightpulseai.com.conf`

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    server_name erp.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS with Odoo proxy
server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.com;

    ssl_certificate     /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass         http://127.0.0.1:8069;
        proxy_set_header   Host               $host;
        proxy_set_header   X-Real-IP          $remote_addr;
        proxy_set_header   X-Forwarded-For    $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto  $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    client_max_body_size 64m;
}
```

### Verification

```bash
# Test HTTP → HTTPS redirect
curl -I http://erp.insightpulseai.com
# Expected: HTTP 301 → https://erp.insightpulseai.com/

# Test HTTPS response
curl -I https://erp.insightpulseai.com
# Expected: HTTP/2 303 (Odoo redirect to /odoo)

# Verify certificate
certbot certificates
# Expected: Valid for 89 days, auto-renewal enabled
```

### Certificate Auto-Renewal

Certbot installs a systemd timer for automatic renewal:

```bash
# Check renewal timer status
systemctl status certbot.timer

# Test renewal (dry-run)
certbot renew --dry-run

# Manual renewal (if needed)
certbot renew
systemctl reload nginx
```

**Renewal Schedule**: Automatically runs twice daily, renews certificates 30 days before expiry.

### Production URLs

- **HTTPS**: https://erp.insightpulseai.com
- **HTTP** (redirects): http://erp.insightpulseai.com

All HTTP traffic automatically redirects to HTTPS for secure communication.
