# Odoo Local Health Check Runbook

**Purpose**: Define health invariants for local Colima + Odoo development environment.

## Expected Container Names

| Container | Service | Health Check Endpoint |
|-----------|---------|----------------------|
| `odoo-core` | Odoo 19 CE | `/web/health` (port 8069) |
| `odoo-db` | PostgreSQL 16 | `pg_isready -h db -p 5432` |
| `odoo-redis` | Redis 7 | `redis-cli -h redis ping` |

## Expected Port Forwarding

| Port | Service | Protocol |
|------|---------|----------|
| `8069` | Odoo HTTP | TCP |
| `8072` | Odoo Longpolling | TCP |

## Health Invariants

### Critical (FAIL if not met)

1. **Container Network Health**:
   - Odoo HTTP responds on container network: `docker exec odoo-core curl -f http://localhost:8069/web/health` → 200 OK
   - DB reachable from Odoo: `docker exec odoo-core pg_isready -h db -p 5432 -U odoo` → "accepting connections"
   - Redis reachable from Odoo: `docker exec odoo-core python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('redis', 6379)); s.close()"` → success

2. **Container Status**:
   - All 3 containers running: `docker ps --filter name=odoo` shows 3 containers
   - All 3 containers healthy: `docker ps --format '{{.Status}}'` contains "(healthy)"

3. **Port Forwarding**:
   - TCP port 8069 listening: `nc -z localhost 8069` → success
   - TCP port 8072 listening: `nc -z localhost 8072` → success

### Warning (WARN if not met, but non-blocking)

1. **Host HTTP Response**:
   - Host curl may show "Empty reply from server" due to SSH tunnel quirks
   - If container-network health passes, this is acceptable
   - Browser access should work even if curl fails

## Verification Commands

See `scripts/health/odoo_local_health.sh` for automated checks.

Manual verification:

```bash
# Container network checks
docker exec odoo-core curl -f http://localhost:8069/web/health
docker exec odoo-core pg_isready -h db -p 5432 -U odoo
docker exec odoo-core python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('redis', 6379)); s.close()" && echo "Redis: PASS"

# Container status
docker ps --filter name=odoo

# Port forwarding
nc -z localhost 8069 && echo "8069: PASS" || echo "8069: FAIL"
nc -z localhost 8072 && echo "8072: PASS" || echo "8072: FAIL"

# Host HTTP (may show "Empty reply" - acceptable if container health passes)
curl -f -m 5 http://localhost:8069/web/health
```

## Evidence Logging

Health check evidence stored in: `docs/evidence/local/<YYYY-MM-DD-HHMM>/`

Run automated health check with evidence generation:
```bash
./scripts/health/odoo_local_health.sh --evidence
```
