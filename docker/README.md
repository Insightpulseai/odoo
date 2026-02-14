# Docker Compose Architecture

## File Hierarchy (SSOT Pattern)

### 1. **`docker-compose.yml`** (ROOT SSOT)
- **Location**: Project root
- **Base stack**: Odoo 19 + PostgreSQL 16 + Redis 7
- **Use**: `docker compose up -d`
- **Profiles**: `tools` (pgAdmin, Mailpit), `init`, `update`
- **Status**: Primary SSOT - all other compose files extend or reference this

### 2. **`docker-compose.dev.yml`** (EXTENDED STACK)
- **Location**: Project root
- **Extends**: `docker-compose.yml` (use together)
- **Adds**: Superset, n8n, MCP Gateway
- **Use**: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`
- **Purpose**: Full development environment with BI and automation tools

### 3. **`sandbox/dev/compose.yml`** (ALTERNATIVE QUICK START)
- **Location**: `sandbox/dev/`
- **Independent**: Standalone lightweight stack
- **Use**: `cd sandbox/dev && docker compose up -d`
- **Purpose**: Quick Odoo module testing without full extended stack
- **When to use**:
  - Quick OCA module experiments
  - Isolated module testing
  - Lightweight development without Superset/n8n/MCP

### 4. **`.devcontainer/docker-compose.devcontainer.yml`** (DEVCONTAINER OVERRIDES)
- **Location**: `.devcontainer/`
- **Extends**: `../docker-compose.yml`
- **Overrides**: Environment variables, command flags, workspace mounts
- **Use**: Automatically used by VS Code Dev Containers
- **Purpose**: VS Code Dev Container integration

## Service Names (Stable)

All services use consistent naming across all compose files:

| Service | Description | Port | Health Check |
|---------|-------------|------|--------------|
| `db` | PostgreSQL 16 | 5432 | `pg_isready` |
| `redis` | Redis 7 | 6379 | `redis-cli ping` |
| `odoo` | Odoo CE 19 | 8069, 8072 | `/web/health` |
| `pgadmin` | pgAdmin 4 (profile: tools) | 5050 | - |
| `mailpit` | Mailpit email testing (profile: tools) | 1025, 8025 | - |
| `superset` | Apache Superset (dev only) | 8088 | `/health` |
| `n8n` | n8n automation (dev only) | 5678 | `/healthz` |
| `mcp_gateway` | MCP Gateway (dev only) | 3333 | HTTP 200 |

**Note**: Never use `postgres` as service name - always `db` for consistency.

## Network

### Network Name
- **Service-level name**: `ipai-net` (used in `docker-compose.yml` network definition)
- **Docker network name**: `ipai-network` (actual Docker network created)
- **Type**: Bridge network
- **External**: All extended stacks reference this network as external

### Network Configuration
All services communicate on the `ipai-network` bridge network:

```yaml
# Root docker-compose.yml creates the network
networks:
  ipai-net:
    name: ipai-network
    driver: bridge

# Extended stacks reference it as external
networks:
  default:
    name: ipai-network
    external: true
```

## Environment Variables

### Required Variables
Create a `.env` file in the project root with:

```bash
# PostgreSQL Configuration
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo
POSTGRES_DB=odoo_dev

# Odoo Configuration
ODOO_ADMIN_PASSWD=admin
ODOO_DB_FILTER=.*

# Superset (dev only)
SUPERSET_SECRET_KEY=dev-secret-key-change-in-prod
SUPERSET_PASSWORD=admin

# n8n (dev only)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin
```

### Variable Usage
- All compose files use `${VAR_NAME:-default}` syntax for environment variables
- Default values are provided for development convenience
- Production deployments should override defaults via environment-specific `.env` files

### Never Hardcode
- ❌ Hardcoded credentials (e.g., `user: dev`, `password: dev`)
- ✅ Environment variables (e.g., `${POSTGRES_USER:-odoo}`)

## Volume Mounts

### Odoo Addons
All compose files mount addons consistently:

```yaml
volumes:
  # IPAI custom modules
  - ./addons/ipai:/mnt/extra-addons/ipai:ro

  # OCA modules (third-party)
  - ./third_party/oca:/mnt/extra-addons/third_party/oca:ro

  # Workspace root (sandbox only)
  - ../..:/workspaces/odoo:cached
```

### Configuration
- **Root SSOT**: `./config/odoo.conf:/etc/odoo/odoo.conf:ro`
- **Environment-specific**: Use `config/dev/`, `config/staging/`, `config/prod/` when needed
- **Current approach**: Single `odoo.conf` for all environments (minimal differences)

## Quick Start Guide

### Option 1: Base Stack (Recommended for Module Development)
```bash
# Start Odoo + PostgreSQL + Redis
docker compose up -d

# View logs
docker compose logs -f odoo

# Stop stack
docker compose down
```

### Option 2: Full Development Stack (BI + Automation)
```bash
# Start all services including Superset, n8n, MCP
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View all service logs
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Stop all services
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Option 3: Sandbox Quick Start (Isolated Testing)
```bash
# Change to sandbox directory
cd sandbox/dev

# Start lightweight stack
docker compose up -d

# View logs
docker compose logs -f odoo

# Stop stack
docker compose down

# Return to project root
cd ../..
```

### Option 4: VS Code Dev Container
1. Open VS Code in project root
2. Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Select: "Dev Containers: Rebuild and Reopen in Container"
4. VS Code automatically uses `.devcontainer/docker-compose.devcontainer.yml`

## Troubleshooting

### Services Not Starting
```bash
# Check service status
docker compose ps

# Check logs for specific service
docker compose logs db
docker compose logs odoo

# Restart specific service
docker compose restart odoo
```

### Network Issues
```bash
# Verify network exists
docker network ls | grep ipai

# Inspect network
docker network inspect ipai-network

# Recreate network (if needed)
docker compose down
docker compose up -d
```

### Port Conflicts
If ports are already in use, update `.env` file:
```bash
# Override default ports
ODOO_HTTP_PORT=8070
DB_PORT_HOST=5433
REDIS_PORT_HOST=6380
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
docker compose exec db psql -U odoo -d odoo_dev -c "SELECT version();"

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

## Best Practices

1. **Always use `docker compose` (not `docker-compose`)**
   - Modern Docker Compose V2 uses `docker compose` command

2. **Use environment variables**
   - Never hardcode credentials in compose files
   - Use `.env` for local development
   - Use GitHub Actions secrets for CI/CD

3. **Keep root docker-compose.yml as SSOT**
   - Extend with `docker-compose.dev.yml` for additional services
   - Document purpose in headers when creating alternative stacks

4. **Service name consistency**
   - Always use `db` (not `postgres`)
   - Use `ipai-network` for network references

5. **Health checks are required**
   - All services must have health checks
   - Use `depends_on` with `condition: service_healthy`

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Odoo Docker Documentation](https://hub.docker.com/_/odoo)
- [PostgreSQL Docker Documentation](https://hub.docker.com/_/postgres)
- [Colima Setup](../docs/COLIMA_SETUP.md) - macOS Docker Desktop alternative
