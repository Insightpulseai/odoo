# Docker Compose Architecture

This document describes the Docker Compose SSOT (Single Source of Truth) pattern used in this repository.

## Compose SSOT Policy

**Enforced Pattern:** "1 SSOT + 0-2 overlays"

- **SSOT Entrypoint:** `docker-compose.yml` (repo root)
- **Allowed Overlays:** `docker-compose.dev.yml` (optional), `docker-compose.ci.yml` (optional)
- **Disallowed:** Standalone compose entrypoints under `sandbox/` or other subdirectories

**Rationale:** Prevent configuration drift by maintaining a single canonical base configuration with optional, well-documented overlays. Standalone compose files in subdirectories create parallel stacks that inevitably diverge from the main configuration.

**If you need sandbox-only services:** Add them to `docker-compose.dev.yml` as an overlay, not as a separate compose file.

## File Hierarchy (SSOT Pattern)

### 1. `docker-compose.yml` (ROOT SSOT)
**Location:** Project root
**Purpose:** Base development stack
**Services:** Odoo 19 + PostgreSQL 16 + Redis 7
**Usage:** `docker compose up -d`
**Profiles:**
- `tools` - Development tools (pgAdmin, Mailpit)
- `init` - One-shot Odoo installation
- `update` - One-shot Odoo update

### 2. `docker-compose.dev.yml` (EXTENDED STACK)
**Location:** Project root
**Purpose:** Development overlay adding analytics and automation services
**Additional Services:** Superset, n8n, MCP Gateway
**Usage:** `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

### 3. `.devcontainer/docker-compose.devcontainer.yml` (DEVCONTAINER OVERRIDES)
**Location:** `.devcontainer/`
**Purpose:** VS Code Dev Container-specific overrides
**Usage:** Automatically used by VS Code Dev Containers extension
**Extends:** `../docker-compose.yml`

## Service Names (Stable)

These service names are canonical and should not be changed:

- `db` - PostgreSQL 16
- `redis` - Redis 7
- `odoo` - Odoo CE 19
- `pgadmin` - pgAdmin 4 (profile: tools)
- `mailpit` - Mailpit email testing (profile: tools)

## Network

All services run on a single Docker network for seamless communication:

- **Network Name:** `ipai-network` (overridable via `IPAI_NETWORK_NAME` env var)
- **Driver:** bridge
- **Alias:** `default` (Docker Compose default network pattern)

## Environment Variables

Required environment variables are documented in `.env.example`. Copy to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

### Start Base Stack
```bash
docker compose up -d
```

### Start Extended Stack (with Superset, n8n, MCP Gateway)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Start with Development Tools (pgAdmin, Mailpit)
```bash
docker compose --profile tools up -d
```

### Verify Services
```bash
docker compose ps
docker network ls | grep ipai
curl -s http://localhost:8069/web/health
```

## Troubleshooting

### Service won't start
Check logs:
```bash
docker compose logs <service-name>
```

### Network issues
Verify network exists:
```bash
docker network ls | grep ipai
```

### Reset environment
Stop all services and remove volumes:
```bash
docker compose down -v
docker compose up -d
```

## Related Documentation

- [Colima Setup](../docs/COLIMA_SETUP.md) - Docker runtime configuration
- [Agent Startup Guide](../agents/CLAUDE.md) - AI agent Odoo startup instructions
- [Compose Topology Guard](../.github/workflows/compose-topology-guard.yml) - CI enforcement of SSOT policy
