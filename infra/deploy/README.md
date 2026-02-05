# Deployment Guide

Quick reference for deploying and managing the Odoo CE production stack.

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Server with Docker & Docker Compose v2 installed
- [ ] Valid `.env` file (copy from `.env.example`)
- [ ] Logged into GitHub Container Registry
- [ ] DNS pointing to server IP
- [ ] SSL certificates configured (Nginx/Certbot)

### Registry Login

```bash
# Set your GitHub Personal Access Token (with packages:read scope)
export GHCR_TOKEN=ghp_xxxxxxxxxxxx

# Login to GitHub Container Registry
echo $GHCR_TOKEN | docker login ghcr.io -u jgtolentino --password-stdin
```

---

## Quick Commands

### 1. Fresh Deployment

```bash
# Clone the repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce/deploy

# Create environment file
cp ../.env.example .env
# Edit .env with production values (DB_PASSWORD, ADMIN_PASSWD)

# Pull and start
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 2. Update to Latest Version (One-Liner)

```bash
docker compose -f docker-compose.prod.yml pull && \
docker compose -f docker-compose.prod.yml up -d --remove-orphans
```

### 3. View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Odoo only
docker compose -f docker-compose.prod.yml logs -f odoo

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 odoo
```

### 4. Restart Services

```bash
# Restart Odoo only
docker compose -f docker-compose.prod.yml restart odoo

# Restart all
docker compose -f docker-compose.prod.yml restart
```

### 5. Stop Everything

```bash
docker compose -f docker-compose.prod.yml down
```

---

## Module Management

### Update/Install Modules

After deploying a new image with updated modules:

```bash
# Update specific module
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -u ipai_finance_ppm --stop-after-init

# Update all custom modules
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -u ipai_finance_ppm,ipai_ppm_monthly_close,ipai_docs --stop-after-init

# Install new module
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -i new_module_name --stop-after-init
```

### List Installed Modules

```bash
docker compose -f docker-compose.prod.yml exec odoo \
  odoo shell -d odoo --no-http << 'EOF'
for mod in env['ir.module.module'].search([('state', '=', 'installed')]):
    print(f"{mod.name}: {mod.installed_version}")
EOF
```

---

## Rollback Procedure

If the new image causes issues:

### Step 1: Identify Last Working Version

Check GitHub Packages for available tags:
https://github.com/jgtolentino/odoo-ce/pkgs/container/odoo-ce

### Step 2: Edit docker-compose.prod.yml

```yaml
services:
  odoo:
    # Change from :latest to specific SHA
    image: ghcr.io/jgtolentino/odoo-ce:sha-057bb3a
```

### Step 3: Redeploy

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## Database Operations

### Backup Database

```bash
# Create backup directory
mkdir -p /opt/backups

# Backup database
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U odoo odoo | gzip > /opt/backups/odoo_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup filestore
docker cp odoo-ce:/var/lib/odoo/filestore /opt/backups/filestore_$(date +%Y%m%d)
```

### Restore Database

```bash
# Stop Odoo first
docker compose -f docker-compose.prod.yml stop odoo

# Restore database
gunzip -c /opt/backups/odoo_20251125_120000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U odoo odoo

# Start Odoo
docker compose -f docker-compose.prod.yml start odoo
```

---

## Health Checks

### Manual Health Check

```bash
# Check Odoo is responding
curl -f http://localhost:8069/web/health

# Expected: {"status": "pass"}
```

### Check Container Status

```bash
docker compose -f docker-compose.prod.yml ps
```

### Check Resource Usage

```bash
docker stats odoo-ce odoo-db
```

---

## Troubleshooting

### Odoo Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.prod.yml logs odoo | tail -50

# Common issues:
# - Database connection refused: Check DB_HOST, DB_PASSWORD
# - Module not found: Check addons_path in odoo.conf
# - Permission denied: Check file ownership
```

### Database Connection Issues

```bash
# Test database connectivity
docker compose -f docker-compose.prod.yml exec odoo \
  python -c "import psycopg2; psycopg2.connect('host=db user=odoo password=YOUR_PASSWORD dbname=odoo')"
```

### Reset Admin Password

```bash
docker compose -f docker-compose.prod.yml exec db \
  psql -U odoo odoo -c "UPDATE res_users SET password='admin' WHERE login='admin';"
```

---

## File Structure

```
deploy/
├── docker-compose.yml       # Development stack (volume mounts)
├── docker-compose.prod.yml  # Production stack (immutable image)
├── odoo.conf                # Odoo server configuration
├── nginx/
│   └── erp.insightpulseai.com.conf  # Nginx reverse proxy config
└── README.md                # This file
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `ADMIN_PASSWD` | Yes | Odoo master password |
| `DB_HOST` | No | Default: `db` |
| `DB_USER` | No | Default: `odoo` |
| `WORKERS` | No | Default: `4` |
| `PROXY_MODE` | No | Default: `True` |

See `.env.example` for complete list.

---

## Support

- **Documentation:** `docs/` directory
- **Issues:** https://github.com/jgtolentino/odoo-ce/issues
- **Mattermost:** #odoo-support channel

---

**Last Updated:** 2025-11-25
