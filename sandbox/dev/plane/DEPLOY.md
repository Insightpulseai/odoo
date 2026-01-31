# Plane Deployment Guide

## Prerequisites

1. **DigitalOcean CLI** (`doctl`) authenticated
2. **SSH access** to ocr-service-droplet (188.166.237.231)
3. **Environment variables** set:

```bash
export PLANE_DB_PASSWORD="$PLANE_DB_PASSWORD"  # From secure source (Keychain/Vault)
export DO_SPACES_KEY="your-spaces-access-key"
export DO_SPACES_SECRET="your-spaces-secret-key"
```

## Deployment Steps

### Step 1: Create Database (run from droplet in same VPC)

SSH to ocr-service-droplet and create the database:

```bash
ssh root@188.166.237.231

# On droplet:
PGPASSWORD="$PLANE_DB_PASSWORD" psql \
  "host=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com port=25060 user=doadmin dbname=defaultdb sslmode=require" \
  -c "CREATE DATABASE plane;"
```

### Step 2: Deploy Plane

**Option A: CI/CD (Recommended)**

Trigger the GitHub Actions workflow:
1. Go to Actions → "Deploy Plane CE"
2. Click "Run workflow"
3. Select action: `deploy`

**Option B: Manual Script**

From local machine with doctl access:

```bash
cd /path/to/odoo-ce/sandbox/dev/plane/infra

# Set required environment variables from secure source
export PLANE_DB_PASSWORD="..."  # From Keychain/Vault
export DO_SPACES_KEY="..."
export DO_SPACES_SECRET="..."

# Run deployment
./deploy-plane-ocr-droplet.sh
```

### Step 3: Verify

```bash
# Check from local
curl -I https://plane.insightpulseai.net

# Check logs from droplet
ssh root@188.166.237.231 'cd /opt/plane && docker compose ps'
ssh root@188.166.237.231 'cd /opt/plane && docker compose logs api --tail 50'
```

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │       ocr-service-droplet               │
                    │         188.166.237.231                 │
                    │                                         │
Internet ──────────►│  nginx (443) ──► Plane (8080)          │
                    │                    │                    │
                    │  ┌─────────────────┼─────────────────┐  │
                    │  │ Docker          │                 │  │
                    │  │  ├─ plane-web   │                 │  │
                    │  │  ├─ plane-api ──┼──────────────┐  │  │
                    │  │  ├─ plane-worker│              │  │  │
                    │  │  ├─ plane-redis │              │  │  │
                    │  │  └─ plane-mq    │              │  │  │
                    │  └─────────────────┼──────────────│──┘  │
                    └────────────────────┼──────────────│─────┘
                                         │              │
                    ┌────────────────────┼──────────────│─────┐
                    │  DO Managed PostgreSQL            │     │
                    │  odoo-db-sgp1                     ▼     │
                    │  25060/tcp ◄───────────────────────     │
                    └─────────────────────────────────────────┘
```

## Required GitHub Secrets

Configure these in repo Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `DROPLET_SSH_KEY` | SSH private key for root@188.166.237.231 |
| `PLANE_DB_PASSWORD` | PostgreSQL password for odoo-db-sgp1 |
| `PLANE_SECRET_KEY` | Django secret key (generate with `openssl rand -hex 32`) |
| `DIGITALOCEAN_ACCESS_TOKEN` | DO API token |

## Credentials Summary

| Service | Host | Port | User | Database |
|---------|------|------|------|----------|
| PostgreSQL | odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com | 25060 | doadmin | plane |
| Plane Web | plane.insightpulseai.net | 443 | - | - |
| Plane Direct | 188.166.237.231 | 8080 | - | - |

## Troubleshooting

### Database connection fails
- Ensure droplet IP is in database trusted sources
- Check VPC connectivity

### Plane won't start
```bash
ssh root@188.166.237.231
cd /opt/plane
docker compose logs api
docker compose logs migrator
```

### SSL certificate issues
```bash
ssh root@188.166.237.231
certbot certonly --nginx -d plane.insightpulseai.net
nginx -t && systemctl reload nginx
```
