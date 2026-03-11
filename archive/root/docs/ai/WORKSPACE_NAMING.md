# Workspace Naming Convention

**Status**: Active | **Version**: 1.0 | **Last Updated**: 2026-02-13

---

## Overview

"ipai" is the canonical workspace identifier for InsightPulse AI across all development tools and platforms.

**Rationale**:
- Short (4 chars), memorable, unique
- Lowercase aligns with Docker/Kubernetes conventions
- No hyphens/underscores for env var and DNS compatibility
- Distinct from project names (which can be descriptive)

---

## Applications

### Docker Compose

**Project Name**: `ipai`
```yaml
# docker-compose.yml
name: ipai
```

**Network Name**: `ipai-network`
```yaml
networks:
  ipai-net:
    name: ipai-network
```

**Volume Names**: `ipai-*`
```yaml
volumes:
  pgdata:
    name: ipai-pgdata
  redisdata:
    name: ipai-redisdata
  odoo-web-data:
    name: ipai-web-data
```

### DevContainer

**Container Name**: `ipai-devcontainer`
```json
{
  "name": "ipai-devcontainer",
  "dockerComposeFile": ["../docker-compose.yml"],
  "service": "odoo"
}
```

### VS Code

**Workspace Files**: `ipai.code-workspace`
```
~/Documents/GitHub/Insightpulseai/odoo/ipai.code-workspace
```

### Local Development

**Directory Structure**: `~/ipai/`
```
~/ipai/
├── odoo/          (main app)
├── infra/         (infrastructure as code)
├── docs/          (documentation)
└── scripts/       (automation)
```

---

## Migration from "odoo"

**Old Naming**:
- Docker project: `odoo`
- Network: `odoo-network`
- Volumes: `odoo-pgdata`, `odoo-redisdata`, etc.
- DevContainer: `InsightPulseAI-Odoo-DevContainer`

**New Naming**:
- Docker project: `ipai`
- Network: `ipai-network`
- Volumes: `ipai-pgdata`, `ipai-redisdata`, etc.
- DevContainer: `ipai-devcontainer`

**Migration Script**: `scripts/migrate-workspace-ipai.sh`
```bash
#!/usr/bin/env bash
# Migrate existing Docker workspace from "odoo" to "ipai"

set -euo pipefail

echo "🔄 Migrating Docker workspace from 'odoo' to 'ipai'..."

# 1. Stop existing containers
echo "Stopping existing containers..."
docker compose down

# 2. Rename volumes
echo "Renaming volumes..."
docker volume create ipai-pgdata
docker volume create ipai-redisdata
docker volume create ipai-web-data
docker volume create ipai-pgadmin-data

# Copy data (if old volumes exist)
if docker volume inspect odoo-pgdata &> /dev/null; then
  docker run --rm -v odoo-pgdata:/from -v ipai-pgdata:/to alpine sh -c "cd /from && cp -av . /to"
fi

# 3. Recreate network
echo "Creating new network..."
docker network create ipai-network || true

# 4. Start new stack
echo "Starting new stack..."
docker compose up -d

echo "✅ Migration complete!"
echo "Old volumes preserved. Remove manually with:"
echo "  docker volume rm odoo-pgdata odoo-redisdata odoo-web-data odoo-pgadmin-data"
```

---

## Docker Compose vs DevContainer

### Runtime SSOT: Docker Compose

**docker-compose.yml** defines what runs:
- Services (Odoo, PostgreSQL, Redis)
- Networks (ipai-network)
- Volumes (ipai-pgdata, ipai-redisdata)
- Ports (8069, 5432, 6379)

### Developer Shell: DevContainer

**.devcontainer/devcontainer.json** defines how developers interact:
- Wraps Docker Compose services
- Adds VS Code extensions
- Configures shell environment
- Enables debugging tools

**Key Rules**:
1. Never duplicate service definitions
2. DevContainer extends, never overrides, base Compose
3. All runtime config goes in `docker-compose.yml`
4. Dev-only tooling goes in `docker-compose.devcontainer.yml`

---

## Extended Dev Stack

**File**: `docker-compose.dev.yml`

**Namespace**: `ipai_dev_*` (not `ipai-*`)
```yaml
# Avoids collision with main stack
services:
  ipai_dev_superset:
    image: apache/superset:3.0
    container_name: ipai_dev_superset
    networks:
      - ipai_dev_network

networks:
  ipai_dev_network:
    name: ipai_dev_network
```

**Usage**:
```bash
# Main stack
docker compose up -d

# Extended dev stack
docker compose -f docker-compose.dev.yml up -d

# Both together
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

---

## Verification

```bash
# 1. Verify Docker Compose project name
docker compose ps  # Should show project: ipai

# 2. Verify network name
docker network ls | grep ipai  # Should show ipai-network

# 3. Verify volume names
docker volume ls | grep ipai  # Should show ipai-pgdata, ipai-redisdata, etc.

# 4. Verify DevContainer name
cat .devcontainer/devcontainer.json | jq '.name'  # Should be "ipai-devcontainer"

# 5. Test dev stack (no namespace collision)
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps  # All services healthy
```

---

## References

- **Docker Compose SSOT**: `docker-compose.yml`
- **DevContainer Config**: `.devcontainer/devcontainer.json`
- **Extended Dev Stack**: `docker-compose.dev.yml`
- **Migration Script**: `scripts/migrate-workspace-ipai.sh`
