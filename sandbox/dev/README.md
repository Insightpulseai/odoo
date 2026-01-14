# Odoo 18 CE Local Sandbox

Canonical local development environment for Odoo 18 CE + OCA + IPAI modules.

## Quick Start

```bash
# Navigate to sandbox directory
cd sandbox/dev

# Copy environment template (optional, defaults work)
cp .env.example .env

# Start services
docker compose up -d

# Open Odoo in browser
open http://localhost:8069
```

**Default credentials:**
- Database: `odoo`
- Master password: (leave empty for first-time setup)
- Login: `admin` / `admin` (after database initialization)

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** | This file - Local sandbox quickstart |
| **HOT_RELOAD_GUIDE.md** | Hot-reload development best practices ⭐ |
| **ARCHITECTURE.md** | Infrastructure alignment (local vs production) |
| **CANONICAL_NAMING.md** | Database naming standards (DO Managed DB) |
| **README_PRODUCTION.md** | Production connection guide (advanced) |
| **Makefile** | Development shortcuts (`make help`) |

---

## Verification Commands

### Check service status
```bash
docker compose ps
```

Expected output:
```
NAME                          IMAGE        STATUS         PORTS
sandbox-dev-db-1              postgres:16  Up (healthy)   5432/tcp
sandbox-dev-odoo-1            odoo:18.0    Up (healthy)   0.0.0.0:8069->8069/tcp
```

### View logs
```bash
# All services
docker compose logs -f

# Odoo only
docker compose logs -f odoo

# Database only
docker compose logs -f db
```

### Check database connection
```bash
docker compose exec db psql -U odoo -d odoo -c "SELECT version();"
```

### Check Odoo addons path
```bash
docker compose exec odoo odoo --version
docker compose exec odoo ls -la /mnt/addons/oca
docker compose exec odoo ls -la /mnt/addons/ipai
```

---

## Module Management

### Update apps list
```bash
docker compose exec odoo odoo -d odoo -u base --stop-after-init
```

### Install a module
```bash
# Example: Install Finance PPM module
docker compose exec odoo odoo -d odoo -i ipai_finance_ppm --stop-after-init

# Install multiple modules
docker compose exec odoo odoo -d odoo -i base,account,ipai_finance_ppm --stop-after-init
```

### Upgrade a module
```bash
docker compose exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
```

### Restart Odoo after changes
```bash
docker compose restart odoo
```

---

## Makefile Shortcuts

```bash
# Start services
make start

# Stop services
make stop

# Restart Odoo
make restart

# View logs
make logs
make logs-odoo

# Install module
make install MODULE=ipai_finance_ppm

# Upgrade module
make upgrade MODULE=ipai_finance_ppm

# Open browser
make open

# Help
make help
```

---

## Reset Sandbox

### Soft reset (keep database)
```bash
docker compose restart odoo
```

### Hard reset (destroy all data)
```bash
# Stop services
docker compose down

# Remove volumes
docker volume rm sandbox-dev_odoo-web-data sandbox-dev_odoo-db-data

# Restart clean
docker compose up -d
```

---

## Troubleshooting

### Port 8069 already in use
```bash
# Find process using port
lsof -i :8069

# Kill process or change port in docker-compose.yml:
# ports:
#   - "8070:8069"  # Use 8070 instead
```

### Database connection errors
```bash
# Check database health
docker compose exec db pg_isready -U odoo -d odoo

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Odoo not starting
```bash
# Check logs for errors
docker compose logs odoo

# Verify configuration
docker compose exec odoo cat /etc/odoo/odoo.conf

# Check filesystem permissions
docker compose exec odoo ls -la /var/lib/odoo
```

### Module not found
```bash
# Verify addons directories exist
ls -la ../../addons/oca
ls -la ../../addons/ipai

# Check mounted paths inside container
docker compose exec odoo ls -la /mnt/addons/oca
docker compose exec odoo ls -la /mnt/addons/ipai

# Update apps list
docker compose exec odoo odoo -d odoo -u base --stop-after-init
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│  http://localhost:8069                   │
│  (Odoo 18 CE)                            │
└─────────────────┬───────────────────────┘
                  │
         ┌────────▼────────┐
         │   odoo:18.0     │
         │   Service       │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  postgres:16    │
         │  Service (db)   │
         │  Database: odoo │
         └─────────────────┘

Volumes:
- odoo-web-data    → /var/lib/odoo
- odoo-db-data     → /var/lib/postgresql/data/pgdata

Addons Path:
1. /usr/lib/python3/dist-packages/odoo/addons  (core)
2. /mnt/addons/oca                              (OCA modules)
3. /mnt/addons/ipai                             (custom modules)
```

---

## Environment Variables

All configuration is in `docker-compose.yml` and `odoo.conf`. The `.env` file is optional.

Default values:
- `POSTGRES_DB=odoo`
- `POSTGRES_USER=odoo`
- `POSTGRES_PASSWORD=odoo`
- `HOST=db` (service name)
- `PORT=5432`

---

## Canonical Database Access

```bash
# psql via docker compose
docker compose exec db psql -U odoo -d odoo

# Connection string (for external tools)
postgresql://odoo:odoo@localhost:5432/odoo
```

**Note:** Port 5432 is NOT exposed to host by default (security). Use `docker compose exec` for database access.

---

## OCA-Style Development Workflow

1. **Add/modify modules in repo:**
   ```bash
   # Work in host filesystem
   cd ../../addons/ipai/your_module
   # Edit files...
   ```

2. **Install/upgrade in sandbox:**
   ```bash
   cd sandbox/dev
   docker compose restart odoo
   docker compose exec odoo odoo -d odoo -u your_module --stop-after-init
   ```

3. **Verify changes:**
   ```bash
   # Check logs
   docker compose logs -f odoo

   # Test in browser
   open http://localhost:8069
   ```

4. **Commit changes:**
   ```bash
   git add addons/ipai/your_module
   git commit -m "feat(your_module): description"
   ```

---

## Production Deployment

For production deployment to DigitalOcean droplet with DO Managed PostgreSQL:

📖 **See:** `../../deploy/DROPLET_DEPLOYMENT.md`

---

## Stopping the Sandbox

```bash
# Stop services (keep volumes)
docker compose stop

# Stop and remove containers (keep volumes)
docker compose down

# Full cleanup (WARNING: destroys all data)
docker compose down -v
```

---

## Next Steps

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Infrastructure alignment details
- [CANONICAL_NAMING.md](./CANONICAL_NAMING.md) - Database naming standards
- [README_PRODUCTION.md](./README_PRODUCTION.md) - Production connection (advanced)
- [../../CLAUDE.md](../../CLAUDE.md) - Project orchestration rules
- [../../deploy/DROPLET_DEPLOYMENT.md](../../deploy/DROPLET_DEPLOYMENT.md) - Production deployment guide

---

**Last updated:** 2026-01-14
**Odoo version:** 18.0 (official docker-library image)
**Database:** PostgreSQL 16
**Canonical database name:** `odoo` (local and production)
