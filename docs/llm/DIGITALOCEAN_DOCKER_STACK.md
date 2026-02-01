# DigitalOcean & Docker Stack

> **Purpose**: Infrastructure configuration for LLM agents.
> **Provider**: DigitalOcean (Singapore region)

---

## DigitalOcean Resources

### Droplet: `odoo-erp-prod`

| Setting | Value |
|---------|-------|
| Region | SGP1 (Singapore) |
| Size | s-4vcpu-8gb |
| OS | Ubuntu 22.04 LTS |
| IPv4 | 178.128.112.214 |
| Monitoring | Enabled |

**Services Running**:
- Odoo 18 CE (port 8069)
- Nginx reverse proxy (80/443)
- Docker daemon

### Managed Database: `odoo-db-sgp1`

| Setting | Value |
|---------|-------|
| Engine | PostgreSQL 15 |
| Region | SGP1 |
| Size | db-s-1vcpu-1gb |
| Port | 25060 |
| SSL Mode | Required |
| Connection Pool | 25 |

**Databases**:
- `odoo_core` - Production Odoo
- `odoo_dev` - Development/staging

---

## Docker Architecture

### Container Topology

```
┌─────────────────────────────────────────────────────┐
│                  Docker Host (Droplet)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│   nginx-proxy (:80/:443)                           │
│       │                                             │
│       ├── odoo-core (:8069)                        │
│       │       └── PostgreSQL (DO Managed)          │
│       │                                             │
│       ├── n8n (:5678)                              │
│       │       └── PostgreSQL (internal)            │
│       │                                             │
│       └── mattermost (:8065)                       │
│               └── PostgreSQL (internal)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Key Containers

| Container | Image | Ports | Purpose |
|-----------|-------|-------|---------|
| `odoo-core` | `odoo:18.0` | 8069 | Main ERP |
| `nginx-proxy` | `nginx:alpine` | 80, 443 | Reverse proxy |
| `n8n` | `n8nio/n8n` | 5678 | Workflow automation |
| `mattermost` | `mattermost/mattermost-team` | 8065 | Team chat |

### Docker Compose Profiles

| Profile | Containers | Use Case |
|---------|------------|----------|
| (default) | odoo-core, nginx | Production |
| `ce-init` | odoo-init | First-time CE setup |
| `init` | ipai-init | IPAI module install |
| `dev` | All + devtools | Development |

---

## Volume Mounts

### Odoo Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `odoo-web-data` | `/var/lib/odoo` | Filestore |
| `./addons/ipai` | `/mnt/extra-addons/ipai` | IPAI modules |
| `./addons/oca` | `/mnt/extra-addons/oca` | OCA modules |
| `./config/odoo.conf` | `/etc/odoo/odoo.conf` | Configuration |

### n8n Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `n8n-data` | `/home/node/.n8n` | Workflows & credentials |

---

## Network Configuration

### Internal Network

```yaml
networks:
  odoo-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Service Discovery

| Service | Internal DNS | Port |
|---------|-------------|------|
| odoo-core | `odoo-core` | 8069 |
| n8n | `n8n` | 5678 |
| mattermost | `mattermost` | 8065 |

---

## Deployment Commands

### Container Management

```bash
# Start stack
docker compose up -d

# View logs
docker compose logs -f odoo-core

# Restart service
docker compose restart odoo-core

# Update and restart
docker compose pull && docker compose up -d
```

### Module Deployment

```bash
# Install module
docker compose exec -T odoo-core odoo \
  -d odoo_core \
  -i ipai_enterprise_bridge \
  --stop-after-init

# Update module
docker compose exec -T odoo-core odoo \
  -d odoo_core \
  -u ipai_finance_ppm \
  --stop-after-init
```

### Database Operations

```bash
# Backup
docker compose exec -T odoo-core pg_dump \
  -h $DB_HOST -U odoo -d odoo_core \
  > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T odoo-core psql \
  -h $DB_HOST -U odoo -d odoo_core \
  < backup.sql
```

---

## Health Checks

### Odoo Health

```bash
# HTTP health check
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8069/web/health

# Database connectivity
docker compose exec -T odoo-core odoo \
  -d odoo_core \
  --stop-after-init \
  2>&1 | grep -q "Database odoo_core"
```

### Container Health

```bash
# All containers running
docker compose ps --format json | jq '.[] | {name: .Name, status: .Status}'

# Resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## Environment Variables

### Required for Odoo

```env
# Database
DB_HOST=odoo-db-sgp1-do-user-xxxxx.b.db.ondigitalocean.com
DB_PORT=25060
DB_USER=odoo
DB_PASSWORD=<from-vault>
DB_NAME=odoo_core

# Odoo
ODOO_ADMIN_PASSWORD=<from-vault>
ODOO_DATA_DIR=/var/lib/odoo

# SMTP (Mailgun)
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@mg.insightpulseai.com
```

### Required for Integrations

```env
# Supabase
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<from-vault>

# n8n
N8N_ENCRYPTION_KEY=<from-vault>
WEBHOOK_URL=https://n8n.insightpulseai.com
```

---

## Monitoring & Alerts

### DigitalOcean Monitoring

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU | > 80% 5min | Alert |
| Memory | > 90% | Alert |
| Disk | > 85% | Alert |
| Network | > 100Mbps | Alert |

### Log Aggregation

Logs flow to:
1. Docker logs (local)
2. Supabase `ops.logs` (via n8n)
3. Mattermost alerts (critical only)

---

## Backup Strategy

| Resource | Frequency | Retention | Location |
|----------|-----------|-----------|----------|
| Odoo DB | Daily | 30 days | DO Spaces |
| Filestore | Daily | 30 days | DO Spaces |
| n8n workflows | Weekly | 12 weeks | Git |
| Config files | On change | Unlimited | Git |

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs odoo-core --tail 100

# Check resources
df -h
free -m

# Restart Docker
systemctl restart docker
```

### Database Connection Failed

```bash
# Test connectivity
nc -zv $DB_HOST $DB_PORT

# Check SSL
openssl s_client -connect $DB_HOST:$DB_PORT -starttls postgres

# Verify credentials
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U odoo -d odoo_core -c "SELECT 1"
```

### Module Installation Failed

```bash
# Check dependencies
docker compose exec -T odoo-core odoo \
  -d odoo_core \
  --stop-after-init \
  2>&1 | grep -i "missing"

# Reset module state
docker compose exec -T db psql -U odoo -d odoo_core -c "
  UPDATE ir_module_module SET state='uninstalled'
  WHERE name='failed_module';"
```
