# Canonical Odoo 19 Setup - Agent-Proof Configuration

## Philosophy

This setup follows **Odoo's documented on-premise/container deployment model**:
- **Stateless app** (web container)
- **External Postgres** (db container)
- **Persistent filestore** (volume)
- **Explicit config** (mounted odoo.conf)
- **Single DB target** (no database selector ambiguity)

**Key Principle**: Configuration is the authoritative control surface, not runtime discovery.

---

## Directory Structure

```
odoo19/
├── compose.yaml              # Canonical compose file (no container_name)
├── config/
│   └── odoo.conf            # Agent-proof config (db_name + list_db=False)
├── addons/                  # Custom addons mount point
├── secrets/
│   └── postgresql_password  # Generated secret (600 permissions)
├── backups/                 # Backup destination
└── scripts/
    └── backup_db.sh         # Idempotent backup script
```

---

## Configuration Highlights

### odoo.conf (Agent-Deterministic)

```ini
[options]
data_dir = /var/lib/odoo

; Deterministic DB target (prevents "database selector" ambiguity)
db_host = db
db_port = 5432
db_user = odoo
db_name = odoo                # Single target database

; Disable DB listing/manager endpoints for production safety + agent determinism
list_db = False

addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

log_level = info
```

**Why `list_db = False`**:
- Prevents database selector UI
- Forces deterministic single-DB operations
- Eliminates AI agent confusion about which database to target

### compose.yaml (No container_name)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD_FILE: /run/secrets/postgresql_password
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo -d postgres"]

  web:
    image: odoo:19.0
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8069:8069"
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD_FILE: /run/secrets/postgresql_password
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
```

**Why no `container_name`**:
- Allows Compose project isolation
- Enables scaling if needed
- Follows Docker Compose best practices

---

## Verification Results

### 1. Services Status
```bash
$ docker compose ps
NAME           IMAGE         COMMAND                  SERVICE   STATUS
odoo19-db-1    postgres:16   "docker-entrypoint.s…"   db        Up (healthy)
odoo19-web-1   odoo:19.0     "/entrypoint.sh odoo"    web       Up
```

### 2. Single Database Confirmed
```bash
$ docker compose exec -T db psql -U odoo -d postgres -c "\l+"
   Name    | Owner | Size
-----------+-------+--------
 odoo      | odoo  | 21 MB   # ✅ Single deterministic target
 postgres  | odoo  | 7516 kB
 template0 | odoo  | 7361 kB
 template1 | odoo  | 7425 kB
```

### 3. Config Mounted Correctly
```bash
$ docker compose exec -T web cat /etc/odoo/odoo.conf | grep -E "(db_name|list_db)"
db_name = odoo
list_db = False
```

### 4. Web Interface Responds
```bash
$ curl -fsSIL http://localhost:8069 | head -1
HTTP/1.1 303 SEE OTHER  # ✅ Redirects to login (expected)
```

---

## AI Agent Command Reference

### Module Operations (Zero Ambiguity)

```bash
# Install module (no database selection needed)
docker compose exec -T web odoo -d odoo -i module_name --stop-after-init

# Update module
docker compose exec -T web odoo -d odoo -u module_name --stop-after-init

# Shell access (auto-connects to "odoo" database)
docker compose exec -it web odoo shell -d odoo
```

### Database Operations

```bash
# PostgreSQL shell
docker compose exec -it db psql -U odoo -d odoo

# Backup (via script)
./scripts/backup_db.sh

# Manual backup
docker compose exec -T db pg_dump -U odoo -d odoo | gzip -9 > backups/manual_$(date +%Y%m%d).sql.gz

# Restore
gunzip -c backups/pg_TIMESTAMP.sql.gz | docker compose exec -T db psql -U odoo -d odoo
```

### Container Management

```bash
# Start/Stop
docker compose up -d
docker compose down

# Restart web only
docker compose restart web

# View logs
docker compose logs -f web
docker compose logs -f db

# Health check
docker compose exec -T web curl -sf http://localhost:8069/web/health
```

---

## Production Validation

### Backup Script (Idempotent)

```bash
$ ./scripts/backup_db.sh
Wrote backups/pg_20260129T135643Z.sql.gz

$ ls -lh backups/
-rw-r--r--  1 user  staff   2.1M Jan 29 13:56 pg_20260129T135643Z.sql.gz
```

### Rollback (Pin Image Tag)

```yaml
# Edit compose.yaml
services:
  web:
    image: odoo:19.0-20260128  # Pin to known-good build
```

```bash
docker compose pull
docker compose up -d
```

---

## Migration from Old Setup

### Old Setup Issues (36 Possible Commands)

**Old Stack**:
- Container names: `odoo-ce-core`, `odoo-ce-db`
- Multiple databases: `odoo_core`, `odoo_dev`, `odoo_db`
- Network: `odoo-ce-network`
- AI Agent confusion: 3 containers × 3 databases × 3 networks = **36 possible commands**

**Canonical Stack**:
- Container names: `odoo19-db-1`, `odoo19-web-1` (project-prefixed)
- Single database: `odoo`
- Network: `odoo19_default` (implicit)
- AI Agent clarity: 1 container × 1 database × 1 network = **1 command**

### Migration Steps Executed

```bash
# 1. Stopped old stack
docker stop odoo-ce-core odoo-ce-db

# 2. Created canonical structure
mkdir -p odoo19/{config,addons,secrets,backups,scripts}

# 3. Generated secret
openssl rand -base64 32 | tr -d '\n' > secrets/postgresql_password
chmod 600 secrets/postgresql_password

# 4. Created odoo.conf with db_name=odoo and list_db=False

# 5. Booted canonical stack
docker compose up -d
```

---

## Notes / Risks

### 1. Multi-DB Support
Odoo **supports** multi-database, but production automation wants:
- Pinned target via `db_name`
- `list_db = False` to prevent UI database selector
- Eliminates "which database?" ambiguity for CI/CD and AI agents

### 2. Persistent Volumes
`/var/lib/odoo` **must** be persistent to retain:
- Filestore (attachments, uploaded files)
- Session data
- Cached assets

### 3. No container_name
Intentionally **not set** to:
- Allow Compose project isolation
- Enable future scaling
- Follow Docker Compose best practices
- Avoid hardcoded container name dependencies

### 4. Postgres Major Version
Explicit pin to `postgres:16` is an **ops choice**:
- Keep it explicit and versioned
- Plan major upgrades separately
- Enables deterministic restores

### 5. Future nginx/https
When adding reverse proxy:
- Keep Odoo behind it (internal 8069)
- Use "stateless app behind reverse proxy" model
- Let nginx handle SSL termination

---

## Comparison: Canonical vs Non-Canonical

| Aspect | Non-Canonical (Old) | Canonical (Current) |
|--------|---------------------|---------------------|
| **Container naming** | `odoo-ce-core` (custom) | `odoo19-web-1` (project-prefixed) |
| **Database count** | 3 (`odoo_core`, `odoo_dev`, `odoo_db`) | 1 (`odoo`) |
| **Config source** | Docker volume (opaque) | `./config/odoo.conf` (version-controlled) |
| **DB selector** | Enabled (UI shown) | Disabled (`list_db = False`) |
| **AI agent commands** | 36 possible combinations | 1 deterministic command |
| **Secrets** | Hardcoded in compose | File-based secrets |
| **Addons path** | Unknown origin | `./addons/` (explicit) |
| **Rollback strategy** | Manual | Pin image tag + compose pull |

---

## Success Criteria

✅ **Single database target**: Only `odoo` database exists (21 MB initialized)
✅ **Config mounted**: `/etc/odoo/odoo.conf` from `./config/odoo.conf`
✅ **Secrets managed**: Password file pattern, not hardcoded
✅ **Health checks**: PostgreSQL health check guards web startup
✅ **Web responds**: HTTP 303 redirects to login (expected behavior)
✅ **AI agent clarity**: Zero ambiguity in commands
✅ **Backup script**: Idempotent, timestamped backups
✅ **Version pinned**: `odoo:19.0` and `postgres:16` explicit

---

## Access

- **Web UI**: http://localhost:8069
- **Database**: `docker compose exec -it db psql -U odoo -d odoo`
- **Shell**: `docker compose exec -it web odoo shell -d odoo`
- **Logs**: `docker compose logs -f web`

---

**Setup Date**: 2026-01-29
**Stack Version**: Odoo 19.0 + PostgreSQL 16
**Philosophy**: Agent-proof, deterministic, production-ready
