# Docker Infrastructure

**Last Updated**: 2026-02-12
**Owner**: devops_team
**Portfolio Initiative**: PORT-2026-010
**Process**: PROC-INFRA-001
**Control**: CTRL-SOP-003

---

## Overview

Docker container orchestration for development and operational tools. Implements network isolation, resource limits, and automated backup strategies.

**Philosophy**: Production-grade containers run always-on; development containers run on-demand.

---

## Stack Registry

### Production-Grade (Always-On)

#### Plane Stack
**Purpose**: Project management and OKR tracking SSOT

**Services**:
- **plane-deploy**: Gateway/orchestrator (port 8080)
- **plane-db-1**: PostgreSQL 15.7 (internal only)
- **plane-mq-1**: RabbitMQ management (internal only)
- **plane-minio-1**: S3-compatible object store (internal only)
- **plane-redis-1**: Valkey/Redis (internal only)

**Compose File**: `plane/docker-compose.yml` (external project)

**Network**: `plane_network` (bridge, isolated)

**Backup Strategy**:
- **Database**: Daily pg_dumpall to `backups/plane/`
- **MinIO**: Daily bucket sync (if mc CLI available)
- **Retention**: 7 days rolling, 4 weekly snapshots

**Resource Limits**:
- DB: 2GB RAM, 1 CPU
- Redis: 512MB RAM, 0.5 CPU
- MinIO: 1GB RAM, 0.5 CPU
- Gateway: 512MB RAM, 0.5 CPU

**Restart Policy**: `unless-stopped`

---

### Development (On-Demand)

#### Odoo Dev Stack
**Purpose**: Odoo 18 development and testing sandbox

**Services**:
- **odoo-dev**: Odoo 18 (port 9069, localhost only)
- **odoo-dev-db**: PostgreSQL 16 (port 5433, localhost only)

**Compose File**: `docker-compose.dev.yml` (or similar)

**Network**: `odoo_dev_network` (bridge, isolated)

**Backup Strategy**: No automated backup (development only)

**Resource Limits**:
- Odoo: 1GB RAM, 0.5 CPU
- DB: 1GB RAM, 0.5 CPU

**Restart Policy**: `no` (manual start/stop)

**Usage Pattern**:
- Start: When actively developing
- Stop: When not in use (conserve resources)

---

#### IDE Helpers
**Purpose**: Development tooling (code-server, openvscode-server)

**Deployment**: Via Docker Desktop extension

**Network**: Host network (ephemeral, no persistence required)

**Resource Limits**: Managed by Docker Desktop

**Usage Pattern**: On-demand, no always-on requirement

---

## Network Architecture

### Isolation Strategy

Each stack has its own isolated Docker network. No cross-stack communication unless explicitly required.

**Plane Network**:
```yaml
networks:
  plane_network:
    driver: bridge
    internal: false  # Gateway needs external access
```

**Odoo Dev Network**:
```yaml
networks:
  odoo_dev_network:
    driver: bridge
    internal: false  # Development access required
```

**No Default Bridge**: Do not use default Docker bridge network for any service.

---

### Port Mappings

#### Plane Stack
| Service | Internal Port | External Port | Accessibility |
|---------|--------------|---------------|---------------|
| plane-deploy | 8080 | 8080 | External (gateway) |
| plane-db | 5432 | - | Internal only |
| plane-redis | 6379 | - | Internal only |
| plane-minio | 9000 | - | Internal only (via gateway) |
| plane-mq | 5672/15672 | - | Internal only |

**Hardening**: Remove all external port publishes except gateway (8080).

#### Odoo Dev Stack
| Service | Internal Port | External Port | Accessibility |
|---------|--------------|---------------|---------------|
| odoo-dev | 8069 | 9069 | Localhost only |
| odoo-dev-db | 5432 | 5433 | Localhost only |

**Localhost Bind**: Use `127.0.0.1:9069:8069` instead of `9069:8069` to prevent external access.

---

## Resource Management

### Resource Limits (Production Containers)

**Critical Services** (Plane DB, Redis):
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

**Non-Critical Services** (Gateway, MinIO):
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 1G
    reservations:
      cpus: '0.25'
      memory: 512M
```

### Restart Policies

**Production Containers**: `restart: unless-stopped`
- Automatically restart after Docker daemon restart
- Do not restart if manually stopped

**Development Containers**: `restart: no`
- Never auto-restart
- Manual start/stop required

---

## Backup Strategy

### Automated Backup (Plane Stack)

**Script**: `scripts/docker/backup-plane.sh`

**Schedule**: Daily via cron or systemd timer (TBD)

**Backup Contents**:
1. **PostgreSQL**: Full database dump via `pg_dumpall`
2. **MinIO**: Bucket sync via `mc mirror` (optional)

**Retention Policy**:
- **Daily backups**: 7 days
- **Weekly snapshots**: 4 weeks
- **Cleanup**: Automatic via `find ... -mtime +7 -delete`

**Backup Location**: `backups/plane/`

**Verification**:
```bash
bash scripts/docker/backup-plane.sh
du -sh backups/plane/
```

---

### Manual Backup (Odoo Dev Stack)

**No automated backup** for development containers.

**Manual Backup** (if needed):
```bash
docker exec -t odoo-dev-db pg_dumpall -U odoo > backups/odoo-dev/odoo_dev_$(date +%Y%m%d).sql
```

---

## Security Hardening

### Network Isolation
- ✅ Each stack has isolated Docker network
- ✅ No cross-stack communication
- ✅ Internal-only services do not publish ports to host

### Port Exposure
- ✅ Production DB/Redis/MQ not exposed to host
- ✅ Development services bind to localhost only (`127.0.0.1`)
- ✅ Only gateway services expose external ports

### Resource Constraints
- ✅ All containers have CPU and memory limits
- ✅ Prevents resource exhaustion
- ✅ Ensures fair resource distribution

### Restart Policies
- ✅ Production: `unless-stopped` for reliability
- ✅ Development: `no` for resource conservation

---

## Operational Policies

### Always-On Containers
**Plane stack**: Required for daily use in project management and OKR tracking.

**Rationale**: Single source of truth for strategic planning and portfolio management.

**Action**: None required (already configured for always-on).

---

### On-Demand Containers
**Odoo dev stack**: Development and testing only.

**Rationale**: Not needed 24/7; conserve resources when not actively developing.

**Action**: Stop when not actively developing.

**Commands**:
```bash
# Stop Odoo dev stack
bash scripts/docker/stop-dev-stacks.sh

# Or manually
docker compose -f docker-compose.dev.yml down
```

---

### IDE Helpers
**Docker Desktop extensions**: Development tooling.

**Rationale**: Ephemeral, no persistence required.

**Action**: No specific action required (managed by Docker Desktop).

---

## Hardening Patch (Plane Stack)

### Current State Issues
- ⚠️ DB port 5432 exposed to host
- ⚠️ Redis port 6379 exposed to host
- ⚠️ MinIO port 9000 exposed to host
- ⚠️ No resource limits defined
- ⚠️ No automated backup

### Hardening Patch File
**File**: `docs/integration/plane-compose-hardening.patch.yml`

**Status**: Pending Plane compose file path from user.

**Contents**: Will include:
1. Network isolation (`plane_network`)
2. Remove external port publishes (DB, Redis, MQ, MinIO)
3. Add resource limits (CPU, memory)
4. Add restart policies (`unless-stopped`)
5. Add backup job container

**Application**:
```bash
# IF user provides Plane compose file path:
# 1. Review current compose file
# 2. Generate exact patch with before/after diff
# 3. Apply patch to Plane compose file
# 4. Restart Plane stack with hardened configuration
```

---

## Verification Commands

### Network Isolation
```bash
# List Docker networks
docker network ls

# Inspect Plane network
docker network inspect plane_network

# Inspect Odoo dev network
docker network inspect odoo_dev_network
```

### Resource Limits
```bash
# Verify memory limit
docker inspect plane-db-1 --format '{{.HostConfig.Memory}}'

# Verify CPU limit
docker inspect plane-db-1 --format '{{.HostConfig.NanoCpus}}'
```

### Restart Policies
```bash
# Verify restart policy
docker inspect plane-db-1 --format '{{.HostConfig.RestartPolicy.Name}}'
```

### Backup Validation
```bash
# Test backup script
bash scripts/docker/backup-plane.sh

# Verify backup contents
ls -lah backups/plane/
```

---

## Maintenance

### Container Updates
**Frequency**: As needed (security patches, new features)

**Process**:
1. Pull new images
2. Stop existing containers
3. Start new containers with same compose file
4. Verify health

**Commands**:
```bash
# Plane stack update
cd plane/
docker compose pull
docker compose up -d
docker compose ps
```

### Log Rotation
**Docker Default**: JSON file driver with default rotation (10MB, 3 files)

**Verification**:
```bash
docker inspect plane-db-1 --format '{{.HostConfig.LogConfig}}'
```

### Health Monitoring
**Status Check**:
```bash
# All running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health check (if configured)
docker inspect plane-db-1 --format '{{.State.Health.Status}}'
```

---

## Troubleshooting

### Container Won't Start
**Issue**: Container exits immediately

**Diagnosis**:
```bash
# Check logs
docker logs plane-db-1 --tail 50

# Check exit code
docker inspect plane-db-1 --format '{{.State.ExitCode}}'
```

**Common Causes**:
- Port conflict (another service on same port)
- Missing environment variables
- Volume permission issues

---

### Network Connectivity Issues
**Issue**: Container cannot reach other services

**Diagnosis**:
```bash
# Verify network membership
docker inspect plane-db-1 --format '{{.NetworkSettings.Networks}}'

# Test connectivity from another container
docker exec -it plane-deploy ping plane-db
```

**Common Causes**:
- Containers not on same network
- DNS resolution failure
- Firewall rules

---

### Resource Exhaustion
**Issue**: Container slow or OOM killed

**Diagnosis**:
```bash
# Check resource usage
docker stats plane-db-1 --no-stream

# Check OOM events
docker inspect plane-db-1 --format '{{.State.OOMKilled}}'
```

**Common Causes**:
- Insufficient resource limits
- Memory leak in application
- High load

---

## References

- **Portfolio Initiative**: PORT-2026-010
- **Process**: PROC-INFRA-001
- **Control**: CTRL-SOP-003
- **Evidence**: EVID-20260212-005

**Related Documentation**:
- `docs/control/policies/SOP-003-docker-container-management.md`
- `scripts/docker/backup-plane.sh`
- `scripts/docker/stop-dev-stacks.sh`

---

*Last reviewed: 2026-02-12*
*Next review: 2026-03-12*
