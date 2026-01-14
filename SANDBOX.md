# Canonical Sandbox

**Three canonical environments. Everything else is special-purpose.**

---

## Local Dev (default)

**Purpose**: Isolated local development with PostgreSQL 16 container

```bash
cd sandbox/dev
cp .env.example .env  # optional, defaults work
docker compose up -d
docker compose ps
open http://localhost:8069
```

**Credentials**:
- Database: `odoo`
- Master password: (leave empty for first-time setup)
- Login: `admin` / `admin` (after database initialization)

**Documentation**:
- **Quick Start**: `sandbox/dev/README_CANONICAL.md` (hot reload, module updates)
- **Full Setup**: `sandbox/dev/README.md`

---

## Prod-Connection Sandbox (DO Managed Postgres)

**Purpose**: Connect local Odoo to production DO Managed PostgreSQL via stunnel

**⚠️ WARNING**: This connects to **production database**. Use for:
- Production troubleshooting
- Database migrations testing
- Read-only production data analysis

```bash
cd sandbox/dev
cp .env.production.example .env.production
# Edit .env.production with real DO Managed DB credentials
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

**Documentation**: See `sandbox/dev/README_PRODUCTION.md`

---

## Production Deploy

**Location**: `deploy/docker-compose.prod.yml` (single canonical file)

**Purpose**: Production deployment on DigitalOcean droplet 178.128.112.214

```bash
# On production droplet
cd /opt/odoo-ce/deploy
docker compose -f docker-compose.prod.yml up -d
```

**Access**: https://erp.insightpulseai.net

**Documentation**: See `deploy/PRODUCTION_SETUP.md`

---

## Special-Purpose Environments

**Do not run these unless explicitly instructed by subsystem documentation:**

- `archive/compose/*` - Legacy/experimental configurations
- `infra/superset/` - Apache Superset BI (standalone)
- `infra/lakehouse/` - Data lakehouse (standalone)
- Other `docker-compose*.yml` files - Archived or special-purpose

---

## Quick Reference

| Environment | Command | URL |
|-------------|---------|-----|
| **Local dev** | `cd sandbox/dev && docker compose up -d` | http://localhost:8069 |
| **Prod-connection** | `cd sandbox/dev && docker compose -f docker-compose.production.yml --env-file .env.production up -d` | http://localhost:8069 |
| **Production** | `cd deploy && docker compose -f docker-compose.prod.yml up -d` | https://erp.insightpulseai.net |

---

**Last Updated**: 2026-01-14
**Odoo Version**: 18.0 (official docker-library image)
**Database**: PostgreSQL 16
