# Multi-Environment Database Configuration

**Status**: Active | **Version**: 1.0 | **Last Updated**: 2026-02-13

---

## Overview

Three database environments for the Odoo deployment lifecycle:

1. **`odoo_dev`** — Local development
2. **`odoo_stage`** — Staging/testing
3. **`odoo_prod`** — Production

---

## Environment Files

| File | Purpose | Committed | Database |
|------|---------|-----------|----------|
| `.env` | Active config (gitignored) | ❌ No | Variable |
| `.env.example` | Template | ✅ Yes | `odoo_dev` |
| `.env.dev` | Development | ✅ Yes | `odoo_dev` |
| `.env.stage` | Staging | ✅ Yes | `odoo_stage` |
| `.env.prod` | Production | ✅ Yes | `odoo_prod` |

---

## Usage

### Local Development

```bash
# Use development environment
cp .env.dev .env
docker compose up -d

# Verify database
docker compose exec db psql -U odoo -d odoo_dev -c "SELECT version();"
```

### Staging

```bash
# Use staging environment
cp .env.stage .env
# Edit .env with staging credentials
docker compose -f docker-compose.yml -f infra/deploy/docker-compose.prod.yml up -d

# Verify database
docker compose exec db psql -U odoo -d odoo_stage -c "SELECT version();"
```

### Production

```bash
# Use production environment
cp .env.prod .env
# Edit .env with production credentials from vault
docker compose -f docker-compose.yml -f infra/deploy/docker-compose.prod.yml up -d

# Verify database
docker compose exec db psql -U odoo -d odoo_prod -c "SELECT version();"
```

---

## Database Lifecycle

### Create Database

```bash
# Development
docker compose exec db createdb -U odoo odoo_dev

# Staging
docker compose exec db createdb -U odoo odoo_stage

# Production
docker compose exec db createdb -U odoo odoo_prod
```

### Initialize Odoo

```bash
# Development
docker compose --profile init up

# Staging
ODOO_DB=odoo_stage docker compose --profile init up

# Production
ODOO_DB=odoo_prod docker compose --profile init up
```

### Backup Database

```bash
# Development
docker compose exec db pg_dump -U odoo odoo_dev > backups/odoo_dev_$(date +%Y%m%d).sql

# Staging
docker compose exec db pg_dump -U odoo odoo_stage > backups/odoo_stage_$(date +%Y%m%d).sql

# Production
docker compose exec db pg_dump -U odoo odoo_prod > backups/odoo_prod_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Development
cat backups/odoo_dev_20260213.sql | docker compose exec -T db psql -U odoo odoo_dev

# Staging
cat backups/odoo_stage_20260213.sql | docker compose exec -T db psql -U odoo odoo_stage

# Production
cat backups/odoo_prod_20260213.sql | docker compose exec -T db psql -U odoo odoo_prod
```

---

## Environment Variables

### Required

| Variable | Dev | Stage | Prod |
|----------|-----|-------|------|
| `COMPOSE_PROJECT_NAME` | `ipai` | `ipai` | `ipai` |
| `POSTGRES_DB` | `odoo_dev` | `odoo_stage` | `odoo_prod` |
| `ODOO_DB` | `odoo_dev` | `odoo_stage` | `odoo_prod` |
| `POSTGRES_PASSWORD` | `odoo` | Vault | Vault |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `ODOO_LOG_LEVEL` | `info` | `debug` (dev), `warn` (prod) |
| `POSTGRES_PORT` | `5433` | External port mapping |
| `ODOO_PORT` | `8069` | HTTP port |
| `ODOO_LONGPOLL_PORT` | `8072` | WebSocket port |

---

## Security

### Secrets Management

**Development**: Hardcoded safe defaults (`odoo` / `odoo`)

**Staging/Production**: Store in vault
```bash
# Example: Store in 1Password/Vault
op read "op://Vault/odoo-stage/password" > /tmp/stage_pw
export POSTGRES_PASSWORD=$(cat /tmp/stage_pw)
rm /tmp/stage_pw

# Or use environment variables from CI
export POSTGRES_PASSWORD="${VAULT_ODOO_STAGE_PASSWORD}"
```

### Never Commit

❌ **NEVER** commit `.env` with real credentials
❌ **NEVER** commit production passwords
✅ **ALWAYS** use vault/secrets management for stage/prod

---

## CI/CD Integration

### GitHub Actions

```yaml
jobs:
  deploy-stage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup environment
        run: |
          cp .env.stage .env
          echo "POSTGRES_PASSWORD=${{ secrets.ODOO_STAGE_PASSWORD }}" >> .env
      - name: Deploy
        run: docker compose up -d
```

### Verification

```bash
# Verify active database
docker compose exec odoo odoo --version
docker compose exec odoo odoo shell -d ${ODOO_DB} -c "print(cr.dbname)"
```

---

## Troubleshooting

### Wrong Database Active

**Symptom**: Changes not appearing, wrong data

**Fix**:
```bash
# Check active database
docker compose exec odoo env | grep ODOO_DB

# Verify .env file
grep ODOO_DB .env

# Restart with correct environment
cp .env.dev .env  # or .env.stage, .env.prod
docker compose restart odoo
```

### Database Does Not Exist

**Symptom**: `FATAL: database "odoo_stage" does not exist`

**Fix**:
```bash
# Create database
docker compose exec db createdb -U odoo odoo_stage

# Initialize
ODOO_DB=odoo_stage docker compose --profile init up
```

---

## References

- **Docker Compose SSOT**: `docker-compose.yml`
- **Environment Templates**: `.env.example`, `.env.dev`, `.env.stage`, `.env.prod`
- **Workspace Naming**: `docs/ai/WORKSPACE_NAMING.md`
