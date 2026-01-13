# Production Infrastructure Documentation

**Server:** odoo-erp-prod (178.128.112.214 / SGP1)
**Stack Manager:** Docker Compose
**Active Config:** `/opt/odoo-ce/repo/deploy/docker-compose.yml`
**Network:** deploy_default (external bridge)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│              (nginx-prod-v2 - nginx:alpine)                     │
│              Ports: 80→443 (SSL/TLS termination)                │
└──────────────────┬──────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┬──────────────┐
    │              │              │              │              │
┌───▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌──────▼──────┐
│ Odoo   │   │   n8n   │   │Superset │   │   MCP   │   │   OCR       │
│ :8069  │   │  :5678  │   │  :8088  │   │  :3000  │   │   :8001     │
└───┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └──────┬──────┘
    │             │             │             │               │
    └─────────────┴─────────────┴─────────────┴───────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  DigitalOcean Managed  │
                    │   PostgreSQL 16        │
                    │   (private-odoo-db)    │
                    └────────────────────────┘
```

---

## Running Services

### Core Services

| Service | Container | Image | Port | Domain |
|---------|-----------|-------|------|--------|
| Odoo 18 | odoo-prod | odoo:18.0 | 8069 | erp.insightpulseai.net |
| n8n | c95d05274029_n8n-prod | n8nio/n8n:latest | 5678 | n8n.insightpulseai.net |
| Superset | 8ce7c585a4e2_superset-prod | apache/superset:latest | 8088 | superset.insightpulseai.net |
| OCR | ocr-prod | ocr-service:latest | 8001 | ocr.insightpulseai.net (503) |
| MCP | mcp-prod | node:20-alpine | 3000 | mcp.insightpulseai.net (503) |
| Auth | auth-prod | node:20-alpine | 8080 | auth.insightpulseai.net (503) |
| Nginx | nginx-prod-v2 | nginx:alpine | 80/443 | *.insightpulseai.net |

**Status:**
- ✅ **Running**: Odoo, n8n, Superset, Nginx, OCR, MCP, Auth (containers up)
- ⚠️ **503 Placeholders**: MCP, OCR, Auth (nginx returns 503, services exist but not proxied)
- 📦 **Planned**: Mattermost (chat.insightpulseai.net), Affine (affine.insightpulseai.net)

---

## Docker Volumes

| Volume | Purpose | Size | Backup |
|--------|---------|------|--------|
| deploy_odoo-web-data | Odoo filestore (attachments, sessions) | Growing | Critical |
| deploy_n8n-data | n8n workflows and credentials | Growing | Critical |
| deploy_superset-data | Superset dashboards and config | Growing | Important |
| deploy_postgres-data | Local PostgreSQL (legacy, unused) | Static | Deprecated |
| deploy_ocr-models | PaddleOCR-VL 900M model files | Static | Cache |
| deploy_mcp-node-modules | MCP coordinator node_modules | Static | Cache |
| deploy_auth-node-modules | Auth service node_modules | Static | Cache |
| deploy_odoo-db-data | Local database (unused - external DB) | Static | Deprecated |

**Storage Management:**
- **Critical volumes** (odoo-web-data, n8n-data): Daily backups to DigitalOcean Spaces
- **Cache volumes** (node_modules, ocr-models): Rebuild on demand, no backups
- **Deprecated volumes** (postgres-data, odoo-db-data): Kept for rollback, will be removed

---

## External Dependencies

### DigitalOcean Managed PostgreSQL

**Cluster:** private-odoo-db-sgp1-do-user-27714628-0
**Host:** private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
**Port:** 25060 (SSL required)
**Region:** SGP1 (Singapore)

**Databases:**
- `odoo` - Odoo 18 production database (main)
- `n8n` - n8n workflow engine database
- `superset` - Apache Superset BI database
- `postgres` - Default admin database

**Connection Strings:**
```bash
# Odoo (from odoo.conf)
postgresql://doadmin:${DB_PASSWORD}@private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/odoo?sslmode=require

# n8n (from docker-compose.yml)
postgresql://doadmin:${DB_PASSWORD}@private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/n8n?sslmode=require

# Superset (from docker-compose.yml)
postgresql+psycopg2://doadmin:${DB_PASSWORD}@private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/superset?sslmode=require
```

**Note:** Replace `${DB_PASSWORD}` with actual password from DigitalOcean database credentials.

### Supabase (External Integrations Only)

**Project:** spdtwktxdalcfigzeqrz
**URL:** https://spdtwktxdalcfigzeqrz.supabase.co
**Region:** Southeast Asia (Singapore)

**Usage:**
- Task queue for OCR jobs
- Analytics data warehouse (Bronze/Silver/Gold medallion)
- n8n workflow storage and triggers
- NOT used for Odoo core database

---

## SSL/TLS Configuration

**Certificate Provider:** Let's Encrypt
**Certificate Path:** `/etc/letsencrypt/live/www.insightpulseai.net/`
**Protocols:** TLSv1.2, TLSv1.3
**Ciphers:** HIGH:!aNULL:!MD5

**Domains Covered:**
- www.insightpulseai.net
- erp.insightpulseai.net
- n8n.insightpulseai.net
- superset.insightpulseai.net
- mcp.insightpulseai.net
- ocr.insightpulseai.net
- auth.insightpulseai.net
- chat.insightpulseai.net (planned)
- affine.insightpulseai.net (planned)

**Certificate Renewal:**
```bash
# Auto-renewal via certbot cron
# Check renewal status
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

---

## Nginx Routing Configuration

### Active Routes

| Domain | Upstream | Container | Status |
|--------|----------|-----------|--------|
| erp.insightpulseai.net | odoo-prod:8069 | odoo-prod | ✅ Active |
| erp.insightpulseai.net/websocket | odoo-prod:8072 | odoo-prod | ✅ Active |
| n8n.insightpulseai.net | c95d05274029_n8n-prod:5678 | n8n-prod | ✅ Active |
| superset.insightpulseai.net | 8ce7c585a4e2_superset-prod:8088 | superset-prod | ✅ Active |
| www.insightpulseai.net | /var/www/html | Static files | ✅ Active |

### Placeholder Routes (503 Response)

| Domain | Planned Upstream | Status |
|--------|------------------|--------|
| mcp.insightpulseai.net | mcp-prod:3000 | ⏳ Needs nginx update |
| ocr.insightpulseai.net | ocr-prod:8001 | ⏳ Needs nginx update |
| auth.insightpulseai.net | auth-prod:8080 | ⏳ Needs nginx update |
| chat.insightpulseai.net | 127.0.0.1:3001 | ⏳ Service not deployed |
| affine.insightpulseai.net | 127.0.0.1:3002 | ⏳ Service not deployed |

### Rate Limiting

**API Rate Limit:** 10 requests/second per IP
**Burst:** 20 requests
**Zone:** api_limit (10MB memory)

Applied to:
- n8n.insightpulseai.net (webhook endpoints)

---

## Service-Specific Configuration

### Odoo 18.0 Production

**Configuration File:** `/opt/odoo-ce/repo/deploy/odoo.conf`

**Key Settings:**
- **Database:** External DigitalOcean PostgreSQL (port 25060)
- **Addons Path:** `/mnt/extra-addons` (mounted from repo)
- **Workers:** Auto (based on CPU cores)
- **Proxy Mode:** Enabled (behind nginx)
- **Session Store:** Redis (future - currently file-based)

**Mailgun Integration:**
- SMTP Host: smtp.mailgun.org:587
- SMTP User: postmaster@mg.insightpulseai.net
- SMTP Password: ${MAILGUN_SMTP_PASSWORD} (env var)
- Encryption: STARTTLS

**Volumes:**
```
../addons:/mnt/extra-addons (IPAI custom modules)
odoo-web-data:/var/lib/odoo (filestore)
./odoo.conf:/etc/odoo/odoo.conf (config)
```

### n8n Workflow Automation

**Environment:**
- N8N_HOST=n8n.insightpulseai.net
- N8N_PROTOCOL=https
- WEBHOOK_URL=https://n8n.insightpulseai.net/
- GENERIC_TIMEZONE=Asia/Manila
- DB_POSTGRESDB_URL=postgresql://... (DigitalOcean)

**Workflows:**
- BIR deadline alerts (7 days before)
- Task escalation (3 days overdue)
- Monthly compliance reports
- OCR job processing
- Mattermost notifications

### Apache Superset BI

**Environment:**
- SUPERSET_ENV=production
- SUPERSET_DATABASE_URI=postgresql+psycopg2://... (DigitalOcean)
- SUPERSET_SECRET_KEY=insightpulse_superset_secret_key_change_me

**Dashboards:**
- Finance PPM metrics
- BIR compliance tracking
- Expense analytics
- Scout transaction analysis

### OCR Service (PaddleOCR-VL 900M)

**Environment:**
- MIN_CONFIDENCE=0.60
- MODEL_PATH=/models/paddleocr-vl-900m
- SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
- Multiple OCR backends: OCR.space, Azure, Google Vision, Gemini

**Features:**
- Receipt OCR with 60%+ confidence threshold
- Multi-provider fallback chain
- Async job processing via Supabase task queue
- OpenAI GPT-4o-mini post-processing

### MCP Coordinator

**Environment:**
- PORT=3000
- SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

**Purpose:**
- Model Context Protocol coordination
- Multi-agent orchestration
- Task routing and delegation

### Auth Service

**Environment:**
- PORT=8080
- JWT_SECRET=${SUPABASE_JWT_SECRET}
- SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

**Purpose:**
- Centralized authentication gateway
- JWT token validation
- Session management

---

## Deployment Workflow

### Current Deployment Process

```bash
# 1. SSH to production
ssh root@178.128.112.214

# 2. Navigate to repo
cd /opt/odoo-ce/repo

# 3. Pull latest changes
git pull origin main

# 4. Rebuild and restart services
cd deploy
docker-compose down
docker-compose up -d

# 5. Check logs
docker-compose logs -f odoo
docker-compose logs -f n8n
docker-compose logs -f nginx

# 6. Verify services
curl -I https://erp.insightpulseai.net
curl -I https://n8n.insightpulseai.net
curl -I https://superset.insightpulseai.net
```

### Service-Specific Restarts

```bash
# Restart Odoo only
docker restart odoo-prod

# Restart nginx only (after config changes)
docker exec nginx-prod-v2 nginx -t  # Test config
docker restart nginx-prod-v2

# Restart n8n only
docker restart c95d05274029_n8n-prod

# Restart Superset only
docker restart 8ce7c585a4e2_superset-prod
```

### Odoo Module Updates

```bash
# SSH to production
ssh root@178.128.112.214

# Update modules
docker exec odoo-prod odoo -d odoo -u ipai_finance_ppm,ipai_bir_compliance --stop-after-init

# Or use management script
cd /opt/odoo-ce/repo
./scripts/deploy-odoo-modules.sh
```

---

## Monitoring & Health Checks

### Service Health Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Odoo | https://erp.insightpulseai.net/web/login | HTTP 200 + login page |
| n8n | https://n8n.insightpulseai.net/healthz | HTTP 200 + {"status":"ok"} |
| Superset | https://superset.insightpulseai.net/health | HTTP 200 + {"status":"ok"} |
| MCP | http://mcp-prod:3000/health | HTTP 200 (internal only) |
| OCR | http://ocr-prod:8001/health | HTTP 200 (internal only) |
| Auth | http://auth-prod:8080/health | HTTP 200 (internal only) |

### Docker Health Checks

```bash
# Check all container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# View health check logs
docker inspect odoo-prod --format='{{json .State.Health}}' | jq

# Force health check
docker exec odoo-prod ps aux | grep odoo
```

### Log Monitoring

```bash
# Real-time logs
docker logs -f odoo-prod --tail 100
docker logs -f nginx-prod-v2 --tail 100

# Search for errors
docker logs odoo-prod --since 1h | grep -i error
docker logs nginx-prod-v2 --since 1h | grep -i "502\|503\|504"

# Odoo specific logs
ssh root@178.128.112.214
docker exec odoo-prod tail -f /var/log/odoo/odoo-server.log
```

---

## Backup & Recovery

### Database Backups

**Managed by DigitalOcean:**
- Automated daily backups (7-day retention)
- Point-in-time recovery (7 days)
- Manual snapshots available

**Manual Backup:**
```bash
# Backup Odoo database
ssh root@178.128.112.214
docker exec odoo-prod pg_dump -h private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo > odoo_backup_$(date +%Y%m%d).sql

# Backup n8n database
docker exec c95d05274029_n8n-prod pg_dump -h private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d n8n > n8n_backup_$(date +%Y%m%d).sql
```

### Volume Backups

```bash
# Backup Odoo filestore
docker run --rm -v deploy_odoo-web-data:/data -v $(pwd):/backup ubuntu tar czf /backup/odoo-web-data_$(date +%Y%m%d).tar.gz -C /data .

# Backup n8n data
docker run --rm -v deploy_n8n-data:/data -v $(pwd):/backup ubuntu tar czf /backup/n8n-data_$(date +%Y%m%d).tar.gz -C /data .
```

### Recovery Procedure

```bash
# 1. Stop affected service
docker stop odoo-prod

# 2. Restore database
psql "postgresql://doadmin:PASSWORD@HOST:25060/odoo?sslmode=require" < odoo_backup_20260113.sql

# 3. Restore volume
docker run --rm -v deploy_odoo-web-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/odoo-web-data_20260113.tar.gz -C /data

# 4. Start service
docker start odoo-prod

# 5. Verify
curl -I https://erp.insightpulseai.net
```

---

## Security Configuration

### Firewall Rules

**DigitalOcean Cloud Firewall:**
- Inbound: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Outbound: All
- SSH access: Key-based authentication only

### Container Security

**Network Isolation:**
- All services in deploy_default bridge network
- No direct external access to service ports
- Only nginx exposes ports 80/443 externally

**Environment Variables:**
- Stored in docker-compose.yml (gitignored on production)
- Sensitive values injected via .env file
- No hardcoded credentials in images

### SSL/TLS Best Practices

- TLSv1.2+ only (TLSv1.0/1.1 disabled)
- Strong cipher suites (HIGH:!aNULL:!MD5)
- HTTP → HTTPS redirect enforced
- HSTS header enabled (future enhancement)

---

## Troubleshooting Guide

### Service Won't Start

```bash
# Check container logs
docker logs odoo-prod --tail 50

# Check docker-compose config
cd /opt/odoo-ce/repo/deploy
docker-compose config

# Check volume permissions
docker exec odoo-prod ls -la /mnt/extra-addons
docker exec odoo-prod ls -la /var/lib/odoo

# Check database connectivity
docker exec odoo-prod psql "postgresql://doadmin:PASSWORD@HOST:25060/odoo?sslmode=require" -c "SELECT 1"
```

### Nginx 502 Bad Gateway

```bash
# Check upstream service is running
docker ps | grep odoo-prod

# Check nginx config
docker exec nginx-prod-v2 nginx -t

# Check upstream connectivity
docker exec nginx-prod-v2 wget -O- http://odoo-prod:8069/web/login

# Reload nginx
docker exec nginx-prod-v2 nginx -s reload
```

### Odoo Module Issues

```bash
# Check module installation
docker exec odoo-prod odoo -d odoo --stop-after-init

# Update module list
docker exec odoo-prod odoo -d odoo -u base --stop-after-init

# Check module paths
docker exec odoo-prod ls -la /mnt/extra-addons/ipai/

# View Odoo logs
docker logs odoo-prod --tail 100 | grep -i "module\|error"
```

### Database Connection Issues

```bash
# Test connection from Odoo container
docker exec odoo-prod psql "postgresql://doadmin:PASSWORD@HOST:25060/odoo?sslmode=require" -c "SELECT version()"

# Check DNS resolution
docker exec odoo-prod nslookup private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com

# Check SSL/TLS
docker exec odoo-prod openssl s_client -connect private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060
```

---

## Future Enhancements

### Planned Services

1. **Mattermost** (chat.insightpulseai.net)
   - Team collaboration and ChatOps
   - n8n webhook integration
   - BIR compliance notifications

2. **Affine** (affine.insightpulseai.net)
   - Knowledge base and documentation
   - Notion-like workspace
   - Team wiki

3. **Redis** (Internal)
   - Odoo session storage
   - n8n job queue
   - Cache layer

### Infrastructure Improvements

1. **Container Orchestration:**
   - Migrate to Docker Swarm or Kubernetes
   - Auto-scaling based on load
   - Zero-downtime deployments

2. **Monitoring:**
   - Prometheus + Grafana
   - Application performance monitoring (APM)
   - Alert manager integration

3. **Backup Automation:**
   - Daily automated backups to DigitalOcean Spaces
   - Offsite backup replication
   - Automated recovery testing

4. **Security Hardening:**
   - WAF (Web Application Firewall)
   - DDoS protection
   - Security scanning automation

---

*Last updated: 2026-01-13*
*Maintainer: Claude Code*
*Infrastructure version: v1.0.0*
