# Production Redeploy Runbook

## Overview

This runbook provides step-by-step procedures for deploying Odoo 18 CE to production on DigitalOcean, with specific focus on preventing 502 errors and ensuring reliable deployments.

---

## Quick Reference

| Component | Value |
|-----------|-------|
| Ship Version | v1.1.0 |
| Droplet | insightpulse-odoo |
| Domain | erp.insightpulseai.com |
| Compose File | `deploy/docker-compose.prod.yml` |
| Nginx Config | `deploy/nginx/erp.insightpulseai.com.conf` |

---

## 1. Pre-Deploy Checklist

Before deploying, verify:

- [ ] All CI gates passing on target branch
- [ ] Ship modules exist and manifests are valid
- [ ] `.env` file configured on droplet (not in repo)
- [ ] GHCR login configured
- [ ] Database backup taken (if upgrading)

---

## 2. Fresh Deploy (New Environment)

### 2.1 Initial Setup

```bash
# SSH to droplet
ssh root@insightpulse-odoo

# Clone repo
git clone https://github.com/jgtolentino/odoo-ce.git /opt/odoo-ce
cd /opt/odoo-ce

# Create .env from template
cp deploy/.env.production.template .env

# Edit .env with actual values
nano .env
# Set: DB_PASSWORD, ADMIN_PASSWD, APP_IMAGE_VERSION
```

### 2.2 Configure Nginx

```bash
# Copy nginx config
sudo cp deploy/nginx/erp.insightpulseai.com.conf /etc/nginx/sites-available/odoo.conf
sudo ln -sf /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload nginx
sudo nginx -s reload
```

### 2.3 Pull and Start

```bash
# Login to GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull latest image
docker compose -f deploy/docker-compose.prod.yml pull

# Start stack
docker compose -f deploy/docker-compose.prod.yml up -d

# Wait for DB to be ready
echo "Waiting for database..."
sleep 30
```

### 2.4 Install Ship Modules

```bash
# Install modules
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  odoo -d odoo -i ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr \
  --stop-after-init

# Restart to apply
docker compose -f deploy/docker-compose.prod.yml restart odoo

# Wait for startup
sleep 15
```

### 2.5 Verify

```bash
# Run verification
./scripts/deploy/verify_prod.sh

# Or manual checks
curl -sS -o /dev/null -w '%{http_code}' https://erp.insightpulseai.com/web/login
curl -sS -o /dev/null -w '%{http_code}' https://erp.insightpulseai.com/web/health
```

---

## 3. Upgrade Deploy (Existing Environment)

### 3.1 Pre-Upgrade

```bash
cd /opt/odoo-ce

# Create backup
docker compose -f deploy/docker-compose.prod.yml exec db \
  pg_dump -U odoo odoo > backup_$(date +%Y%m%d_%H%M%S).sql

# Note current image tag for rollback
docker compose -f deploy/docker-compose.prod.yml images odoo
```

### 3.2 Pull New Code

```bash
# Pull latest code
git fetch origin
git checkout main
git pull origin main

# Or specific tag
git checkout ship-aiux-v1.1.0
```

### 3.3 Pull New Image

```bash
# Pull new image
docker compose -f deploy/docker-compose.prod.yml pull odoo
```

### 3.4 Upgrade Modules

```bash
# Stop odoo
docker compose -f deploy/docker-compose.prod.yml stop odoo

# Start with upgrade
docker compose -f deploy/docker-compose.prod.yml up -d odoo

# Run module upgrade
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  odoo -d odoo -u ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr \
  --stop-after-init

# Restart
docker compose -f deploy/docker-compose.prod.yml restart odoo
```

### 3.5 Verify Upgrade

```bash
./scripts/deploy/verify_prod.sh
```

---

## 4. Rollback Procedure

### 4.1 Immediate Rollback (Same Image)

```bash
# If module upgrade broke things
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  odoo -d odoo -u base,web --stop-after-init

docker compose -f deploy/docker-compose.prod.yml restart odoo
```

### 4.2 Full Rollback (Previous Image)

```bash
# Edit .env to use previous image tag
nano .env
# Set APP_IMAGE_VERSION to previous version

# Pull and restart
docker compose -f deploy/docker-compose.prod.yml pull odoo
docker compose -f deploy/docker-compose.prod.yml up -d odoo

# Verify
./scripts/deploy/verify_prod.sh
```

### 4.3 Database Rollback (Last Resort)

```bash
# Stop services
docker compose -f deploy/docker-compose.prod.yml down

# Restore database
docker compose -f deploy/docker-compose.prod.yml up -d db
sleep 10

docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo;"

docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d postgres -c "CREATE DATABASE odoo OWNER odoo;"

docker compose -f deploy/docker-compose.prod.yml exec -T db \
  psql -U odoo -d odoo < backup_YYYYMMDD_HHMMSS.sql

# Start odoo
docker compose -f deploy/docker-compose.prod.yml up -d
```

---

## 5. Debugging 502 Errors

### 5.1 Check Container Status

```bash
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs --tail=200 odoo
```

### 5.2 Check Internal Health

```bash
# Internal connectivity
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' http://localhost:8069/web/login

# Check if port 8072 is responding (longpolling)
docker compose -f deploy/docker-compose.prod.yml exec -T odoo \
  curl -sS -o /dev/null -w '%{http_code}' http://localhost:8072/longpolling/poll
```

### 5.3 Check Nginx

```bash
# Test config
sudo nginx -t

# Check error log
sudo tail -100 /var/log/nginx/error.log
sudo tail -100 /var/log/nginx/odoo.error.log

# Verify upstream connectivity
curl -sS http://127.0.0.1:8069/web/login
```

### 5.4 Common Fixes

| Issue | Fix |
|-------|-----|
| Odoo not starting | `docker compose logs odoo` - check for errors |
| Module crash | `odoo -u base,web --stop-after-init` |
| Asset 500 | `odoo -u web --stop-after-init` then restart |
| DB connection | Check `HOST` env var in container |
| Longpoll 502 | Verify nginx has `/longpolling` route |

---

## 6. Monitoring Commands

### 6.1 Live Logs

```bash
# All logs
docker compose -f deploy/docker-compose.prod.yml logs -f

# Just Odoo
docker compose -f deploy/docker-compose.prod.yml logs -f odoo

# Filter for errors
docker compose -f deploy/docker-compose.prod.yml logs -f odoo 2>&1 | grep -i error
```

### 6.2 Resource Usage

```bash
docker stats --no-stream
```

### 6.3 Database Status

```bash
docker compose -f deploy/docker-compose.prod.yml exec db \
  psql -U odoo -d odoo -c "SELECT count(*) FROM ir_module_module WHERE state='installed';"
```

---

## 7. Scheduled Maintenance

### 7.1 Weekly Tasks

- [ ] Review error logs
- [ ] Check disk space: `df -h`
- [ ] Verify backups exist
- [ ] Review container restarts: `docker compose ps`

### 7.2 Monthly Tasks

- [ ] Update base image if security patches
- [ ] Review module upgrade availability
- [ ] Test restore from backup
- [ ] Review access logs for anomalies

---

## 8. Emergency Contacts

| Role | Contact |
|------|---------|
| Platform Lead | [internal contact] |
| DO Support | support.digitalocean.com |
| Odoo Community | odoo.com/forum |

---

*Last updated: 2026-01-08*
