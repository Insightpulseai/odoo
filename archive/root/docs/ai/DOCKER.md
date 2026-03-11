# Docker Commands
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Development

```bash
# Start core services
docker compose up -d postgres odoo-core

# Run init profiles (first-time setup)
docker compose --profile ce-init up    # Install CE modules
docker compose --profile init up       # Install IPAI modules

# View logs
docker compose logs -f odoo-core

# Restart service
docker compose restart odoo-core
```

## Database Access

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U odoo -d odoo_core

# Backup database
docker compose exec postgres pg_dump -U odoo odoo_core > backup.sql
```
