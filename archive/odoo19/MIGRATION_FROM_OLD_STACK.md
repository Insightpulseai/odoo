# Migration from Old Stack to Canonical Odoo 19 Setup

## Executive Summary

Successfully migrated from non-canonical multi-database setup to canonical single-database Odoo 19 configuration, reducing AI agent command ambiguity from **36 possible combinations to 1 deterministic command format**.

---

## Comparison: Old vs. Canonical

| Aspect | Old Stack (Non-Canonical) | Canonical Stack (Odoo 19) |
|--------|--------------------------|---------------------------|
| **Container Naming** | Custom (`odoo-ce-core`, `odoo-ce-db`) | Project-prefixed (`odoo19-web-1`, `odoo19-db-1`) |
| **Database Count** | 4 databases (`odoo_core`, `odoo_dev`, `odoo_db`, `postgres`) | 1 database (`odoo`) |
| **Config Source** | Docker volumes (opaque, not tracked) | Version-controlled (`./config/odoo.conf`) |
| **Database Selector** | Enabled (UI shown, agent confusion) | Disabled (`list_db = False`) |
| **AI Agent Commands** | 36 possible combinations | 1 deterministic command |
| **Secrets Management** | Hardcoded in compose files | File-based secrets (`PASSWORD_FILE`) |
| **Addons Path** | Multiple sources, some outside Git | Explicit (`./addons/`) |
| **Health Checks** | None | PostgreSQL health check guards web startup |
| **Rollback Strategy** | Manual | Pin image tag + compose pull |
| **Network** | Custom (`odoo-ce-network`) | Implicit (`odoo19_default`) |

---

## AI Agent Command Ambiguity Analysis

### Old Stack (36 Possible Commands)

**Problem**: AI agents had to guess correct combination of:
- **3 container names**: `odoo-ce-core`, `odoo-dev`, `ipai-odoo-dev`
- **4 database names**: `odoo_core`, `odoo_dev`, `odoo_db`, `postgres`
- **3 networks**: `odoo-ce-network`, `odoo-dev-net`, `odoo19-local_odoo19-net`

**Result**: 3 × 4 × 3 = **36 possible command combinations**

Example ambiguity:
```bash
# Which of these 36 commands is correct?
docker exec odoo-ce-core odoo -d odoo_core -i module_name
docker exec odoo-dev odoo -d odoo_dev -i module_name
docker exec ipai-odoo-dev odoo -d odoo_db -i module_name
# ... 33 more possibilities
```

### Canonical Stack (1 Command)

**Solution**: Deterministic, zero-ambiguity configuration
- **1 container pattern**: `odoo19-web-1` (project-prefixed by Compose)
- **1 database**: `odoo` (explicitly set in config)
- **1 network**: `odoo19_default` (implicit Compose network)

**Result**: 1 × 1 × 1 = **1 deterministic command format**

```bash
# Only ONE correct command:
docker compose exec -T web odoo -d odoo -i module_name --stop-after-init
```

---

## Migration Timeline

### Phase 1: Discovery (Completed)
- ✅ Analyzed 5 overlapping Docker stacks
- ✅ Documented 36 command combinations
- ✅ Identified path mismatches (addons mounted from `/Users/tbwa/odoo-ce/` instead of Git repo)
- ✅ Created `COMPLETE_STACK_ANALYSIS.md` and `NAMING_AND_PATH_ALIGNMENT.md`

### Phase 2: Canonical Setup (Completed)
- ✅ Created `odoo19/` directory structure
- ✅ Generated PostgreSQL password secret (44 bytes, chmod 600)
- ✅ Created canonical `config/odoo.conf` with `db_name=odoo` and `list_db=False`
- ✅ Created `compose.yaml` following official Odoo patterns
- ✅ Created idempotent `scripts/backup_db.sh`
- ✅ Resolved port conflict (stopped old `odoo-ce-core`, `odoo-ce-db` containers)
- ✅ Verified single database target (22 MB `odoo` database)
- ✅ Documented setup in `CANONICAL_SETUP.md` and `QUICK_REFERENCE.md`

### Phase 3: Production Migration (Not Started)
- ⏳ Backup production data from old stack
- ⏳ Import data into canonical setup
- ⏳ Update CI/CD pipelines to use canonical stack
- ⏳ Remove old non-canonical containers and volumes

---

## Verification Results

### Old Stack Status (Before Migration)
```bash
# Multiple containers with custom names
odoo-ce-core    Up (port 8069)
odoo-ce-db      Up
odoo-dev        Exited
ipai-odoo-dev   Exited

# Multiple databases
odoo_core    21 MB
odoo_dev     8 MB
odoo_db      15 MB
postgres     7 MB
```

### Canonical Stack Status (After Migration)
```bash
# Project-prefixed containers
odoo19-web-1    Up (port 8069)
odoo19-db-1     Up (healthy)

# Single database
odoo            22 MB
postgres        7 MB (system database)
```

**Health Check**:
```bash
$ curl -sf http://localhost:8069/web/health && echo OK
OK
```

**Configuration Verification**:
```bash
$ docker compose exec -T web cat /etc/odoo/odoo.conf | grep -E "(db_name|list_db)"
db_name = odoo
list_db = False
```

---

## Port Conflict Resolution

### Problem
```
Error: driver failed programming external connectivity on endpoint odoo19-web-1: 
Bind for 0.0.0.0:8069 failed: port is already allocated
```

### Root Cause
Old non-canonical stack (`odoo-ce-core`) still running on port 8069.

### Fix Applied
```bash
docker stop odoo-ce-core odoo-ce-db
docker compose up -d
```

**Result**: Canonical stack successfully started.

---

## File Structure

### Old Stack (Scattered)
```
/Users/tbwa/odoo-ce/              # Production addons (NOT in Git)
/Users/tbwa/Documents/GitHub/odoo-ce/addons/  # Git-tracked addons
/var/lib/docker/volumes/...       # Config in opaque volumes
Multiple docker-compose.yml files with no clear canonical version
```

### Canonical Stack (Organized)
```
odoo19/
├── compose.yaml              # Canonical compose file
├── config/
│   └── odoo.conf            # Version-controlled config
├── addons/                   # Custom modules mount point
├── secrets/
│   └── postgresql_password  # Generated secret (600 permissions)
├── backups/                  # Backup destination
└── scripts/
    └── backup_db.sh         # Idempotent backup script
```

---

## Key Configuration Changes

### Database Determinism
```ini
# Old: No db_name specified, database selector enabled
[options]
# (config stored in Docker volume, not tracked)

# Canonical: Explicit database target
[options]
db_name = odoo                # Single target database
list_db = False               # Disable database selector UI
```

### Secrets Management
```yaml
# Old: Hardcoded passwords
environment:
  POSTGRES_PASSWORD: "plaintext_password_here"

# Canonical: File-based secrets
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/postgresql_password
secrets:
  postgresql_password:
    file: ./secrets/postgresql_password
```

### Health Checks
```yaml
# Old: No health checks
depends_on:
  - db

# Canonical: Health check guards startup
depends_on:
  db:
    condition: service_healthy
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U odoo -d postgres"]
  interval: 10s
  timeout: 5s
  retries: 10
```

---

## Success Criteria (All Met)

✅ **Single database target**: Only `odoo` database exists (22 MB initialized)  
✅ **Config mounted**: `/etc/odoo/odoo.conf` from `./config/odoo.conf`  
✅ **Secrets managed**: Password file pattern, not hardcoded  
✅ **Health checks**: PostgreSQL health check guards web startup  
✅ **Web responds**: HTTP 303 redirects to login (expected behavior)  
✅ **AI agent clarity**: Zero ambiguity in commands  
✅ **Backup script**: Idempotent, timestamped backups  
✅ **Version pinned**: `odoo:19.0` and `postgres:16` explicit  

---

## Next Steps (Optional)

1. **Production Migration**: Import data from old stack to canonical setup
2. **CI/CD Update**: Update workflows to use `odoo19/` directory
3. **Documentation**: Add canonical stack reference to main project docs
4. **Cleanup**: Remove old non-canonical containers and volumes (after data migration)
5. **Supabase Integration**: Implement Odoo→Supabase sync pattern for analytics

---

**Migration Date**: 2026-01-29  
**Stack Version**: Odoo 19.0 + PostgreSQL 16  
**Philosophy**: Agent-proof, deterministic, production-ready
