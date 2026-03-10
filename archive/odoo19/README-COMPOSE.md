# Docker Compose Usage for Odoo 19

**Canonical SSOT**: Use `../docker-compose.yml` in the repository root.

## Quick Start

```bash
# From repository root
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Start Odoo 19 with PostgreSQL and Redis
docker compose up -d

# With dev tools (Superset, n8n, MCP)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# With platform services (Nginx, optional Supabase)
cd ipai-platform
docker compose up -d
```

## Why No Local compose.yaml?

To prevent Docker Compose configuration drift, all services now delegate to the canonical SSOT at `/docker-compose.yml`. This ensures:

- ✅ Single database name: `odoo_dev` (no more odoo/dev/postgres drift)
- ✅ Unified Odoo version: 19 across all overlays
- ✅ No service redefinition (delegator pattern using `include:`)
- ✅ CI-enforced governance preventing unauthorized compose files

## Previous odoo19/compose.yaml

Deleted as of 2026-02-15 (commit: Phase 4 cleanup).

**Git History Restoration**:
```bash
# View deletion commit
git log --all --full-history -- odoo19/compose.yaml

# Restore if needed
git show <commit>:odoo19/compose.yaml > restored-compose.yaml
```

## See Also

- `/docker-compose.yml` - Canonical SSOT
- `/docs/ai/DOCKER_COMPOSE_SSOT.md` - SSOT architecture documentation
- `.github/compose-allowlist.txt` - Authorized compose files
