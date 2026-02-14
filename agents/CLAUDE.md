# Odoo Development Workflow Guide

## Quick Start (Local Development)

### Prerequisites
- Colima installed and configured (see `docs/COLIMA_SETUP.md`)
- Docker context set to `colima` (automatic via `.zshrc`)
- Project root: `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo`

### Start Odoo Stack

**Recommended (Scripted)**:
```bash
# From project root
./scripts/colima-up.sh

# Verify services
docker compose ps
```

**Manual (Alternative)**:
```bash
# Start Colima
colima start --profile odoo

# Start Docker Compose stack
docker compose up -d

# Verify services healthy
docker compose ps
```

**Expected Output**:
```
NAME            IMAGE             STATUS         PORTS
odoo-db-1       postgres:16       Up (healthy)   0.0.0.0:5432->5432/tcp
odoo-redis-1    redis:7-alpine    Up (healthy)   0.0.0.0:6379->6379/tcp
odoo-odoo-1     odoo:19.0         Up (healthy)   0.0.0.0:8069->8069/tcp, 0.0.0.0:8072->8072/tcp
```

### Stop Odoo Stack

```bash
# Scripted (recommended)
./scripts/colima-down.sh

# Manual
docker compose down
colima stop --profile odoo
```

---

## Docker Compose Architecture

### File Hierarchy (SSOT Pattern)

**See `docker/README.md` for complete documentation.**

| File | Purpose | Use When |
|------|---------|----------|
| `docker-compose.yml` | Root SSOT (Odoo + PostgreSQL + Redis) | Primary development |
| `docker-compose.dev.yml` | Extended stack (+ Superset, n8n, MCP) | Full dev environment |
| `sandbox/dev/compose.yml` | Lightweight alternative | Quick module testing |
| `.devcontainer/docker-compose.devcontainer.yml` | VS Code overrides | DevContainer mode |

### Service Names (Stable)

| Service | Container | Port | Health Check |
|---------|-----------|------|--------------|
| `db` | `odoo-db-1` | 5432 | `pg_isready` |
| `redis` | `odoo-redis-1` | 6379 | `redis-cli ping` |
| `odoo` | `odoo-odoo-1` | 8069, 8072 | `/web/health` |

**Important**: Never use `postgres` as service name - always `db` for consistency.

### Network Configuration

**Deterministic External Network**:
- **Service-level name**: `default` (implicit)
- **Docker network name**: `ipai-network` (created by root compose)
- **Type**: Bridge network
- **External**: Extended stacks reference as `external: true`

**Why External?**
- No manual `docker network create` needed
- Consistent across all compose files
- Survives stack restarts
- CI-safe with override: `IPAI_NETWORK_NAME=ipai-ci-network`

---

## Common Workflows

### Option 1: Base Stack (Module Development)
```bash
docker compose up -d
docker compose logs -f odoo
```

**Access**:
- Odoo: http://localhost:8069
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Option 2: Full Development Stack (BI + Automation)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
```

**Additional Services**:
- Superset: http://localhost:8088
- n8n: http://localhost:5678
- MCP Gateway: http://localhost:3333

### Option 3: Sandbox Quick Start (Isolated Testing)
```bash
cd sandbox/dev
docker compose up -d
docker compose logs -f odoo

# Return to root
cd ../..
```

### Option 4: VS Code Dev Container
1. Open VS Code in project root
2. Command Palette: `Dev Containers: Rebuild and Reopen in Container`
3. DevContainer uses `.devcontainer/docker-compose.devcontainer.yml` automatically

---

## Verification Commands

### Service Health
```bash
# All services status
docker compose ps

# Individual service health
docker compose ps db
docker compose ps odoo

# Odoo web health endpoint
curl -s http://localhost:8069/web/health
```

### Network Inspection
```bash
# Verify network exists
docker network ls | grep ipai

# Inspect network details
docker network inspect ipai-network

# Show connected containers
docker network inspect ipai-network -f '{{range .Containers}}{{.Name}} {{end}}'
```

### Database Connection
```bash
# Test PostgreSQL connection
docker compose exec db psql -U odoo -d odoo_dev -c "SELECT version();"

# Check active connections
docker compose exec db psql -U odoo -d odoo_dev -c "SELECT count(*) FROM pg_stat_activity;"
```

### Configuration Validation
```bash
# Validate compose files
docker compose config --quiet

# Check Odoo config
docker compose exec odoo cat /etc/odoo/odoo.conf
```

---

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
If ports are already in use, create `.env` file in project root:
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

### Configuration Warnings
```bash
# Check for deprecated options in Odoo logs
docker compose logs odoo | grep -i "warning\|deprecated"

# View complete Odoo startup log
docker compose logs odoo --tail 100
```

---

## Environment Variables

### Required Variables
Create `.env` file in project root:

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

### Default Values
All compose files use `${VAR_NAME:-default}` syntax:
- `POSTGRES_USER=${POSTGRES_USER:-odoo}`
- `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-odoo}`
- `ODOO_HTTP_PORT=${ODOO_HTTP_PORT:-8069}`

**Override in `.env` or environment variables as needed.**

---

## Best Practices

1. **Always use `docker compose` (not `docker-compose`)**
   - Modern Docker Compose V2 syntax

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

---

## Configuration Reference

### Odoo Config (`config/odoo.conf`)

**Complete addons_path runtime contract**:
```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/var/lib/odoo/addons/19.0,/mnt/extra-addons/ipai,/usr/lib/python3/dist-packages/addons
```

**Odoo 19 compatible options**:
```ini
http_port = 8069
http_interface = 0.0.0.0
gevent_port = 8072
```

**Deprecated (never use)**:
- `xmlrpc_port` → Use `http_port`
- `longpolling_port` → Use `gevent_port`
- `xmlrpc_interface` → Use `http_interface`

---

## CI/CD Integration

### GitHub Actions
Workflows use overridable network name for safety:
```yaml
env:
  IPAI_NETWORK_NAME: ipai-ci-network-${{ github.run_id }}
```

### Multi-Repo Safety
Network name can be customized to prevent conflicts:
```bash
IPAI_NETWORK_NAME=ipai-custom docker compose up -d
```

---

## Additional Documentation

- **Architecture**: `docker/README.md` (280 lines, complete guide)
- **Colima Setup**: `docs/COLIMA_SETUP.md`
- **DevContainer**: `.devcontainer/README.md` (if exists)
- **Troubleshooting**: `docs/ai/TROUBLESHOOTING.md`

---

*Last updated: 2026-02-13*
*Docker Compose SSOT implementation: feat/infra-dns-ssot branch*
