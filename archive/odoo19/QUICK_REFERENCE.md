# Odoo 19 Canonical Setup - Quick Reference

## One-Line Status Check
```bash
docker compose ps && docker compose exec -T db psql -U odoo -d postgres -c "\l+" | grep odoo
```

## AI Agent Commands (Zero Ambiguity)

### Module Operations
```bash
# Install
docker compose exec -T web odoo -d odoo -i MODULE_NAME --stop-after-init

# Update
docker compose exec -T web odoo -d odoo -u MODULE_NAME --stop-after-init

# Shell
docker compose exec -it web odoo shell -d odoo
```

### Database
```bash
# SQL Shell
docker compose exec -it db psql -U odoo -d odoo

# Backup
./scripts/backup_db.sh

# Size
docker compose exec -T db psql -U odoo -d odoo -c "SELECT pg_size_pretty(pg_database_size('odoo'));"
```

### Logs
```bash
# Tail
docker compose logs -f web

# Last 100 lines
docker compose logs --tail 100 web
```

### Stack Control
```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart web
docker compose restart web

# Pull updates
docker compose pull && docker compose up -d
```

## Key Facts

- **Database**: Single `odoo` database (deterministic)
- **Config**: `./config/odoo.conf` with `list_db = False`
- **Secrets**: File-based at `./secrets/postgresql_password`
- **Containers**: `odoo19-db-1`, `odoo19-web-1` (no custom names)
- **Ports**: 8069 (web)
- **Access**: http://localhost:8069

## Directory Structure
```
odoo19/
├── compose.yaml       # Canonical compose
├── config/odoo.conf   # Agent-proof config
├── addons/            # Custom modules
├── secrets/           # Password file
├── backups/           # Timestamped backups
└── scripts/           # Automation scripts
```

## Troubleshooting

**Port conflict**:
```bash
docker stop odoo-ce-core odoo-ce-db  # Stop old stack
docker compose up -d
```

**Reset everything**:
```bash
docker compose down -v  # WARNING: Destroys data
rm -rf backups/*
docker compose up -d
```

**Check config**:
```bash
docker compose exec -T web cat /etc/odoo/odoo.conf
```

**Health check**:
```bash
curl -sf http://localhost:8069/web/health && echo OK || echo FAIL
```
