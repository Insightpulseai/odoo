# Docker Canonical Setup - Official vs Current

**Source**: https://github.com/docker-library/docs/tree/master/odoo
**Date**: 2026-01-14
**Purpose**: Single source of truth for Odoo Docker deployment

---

## Comparison Matrix

| Aspect | Official Canonical | Our Current Setup | Status | Notes |
|--------|-------------------|-------------------|--------|-------|
| **Service Names** | `web` + `db` | `odoo` + `db` | ⚠️ Minor | Official uses `web`, we use `odoo` |
| **Container Names** | Not specified | `odoo-dev` + `odoo-dev-db` | ✅ OK | Explicit names for clarity |
| **Odoo Image** | `odoo:17.0` | `odoo:18` | ✅ OK | Using latest stable |
| **PostgreSQL Image** | `postgres:15` | `postgres:16` | ✅ OK | Using latest stable |
| **Database Name** | `postgres` (default) | `odoo_dev_sandbox` | ✅ OK | Explicit sandbox naming |
| **Port Mapping** | `8069:8069` | `8069:8069` | ✅ Match | Standard Odoo port |
| **Environment Variables** | `HOST`, `PORT`, `USER`, `PASSWORD` | `HOST`, `USER`, `PASSWORD`, `DB_NAME` | ⚠️ Extra | We added `DB_NAME` |
| **Named Volumes** | ❌ Not in minimal example | ✅ `db-data`, `odoo-web-data` | ✅ Better | Production-ready |
| **Custom Addons** | ❌ Not in minimal example | ✅ `../../addons:/mnt/extra-addons` | ✅ Better | Development-ready |
| **Custom Config** | ❌ Not in minimal example | ✅ `./config/odoo.conf:/etc/odoo/odoo.conf` | ✅ Better | Configuration override |
| **Secrets Management** | `PASSWORD_FILE` (production) | Plain env vars (dev) | ✅ OK | Dev environment acceptable |

---

## Official Canonical Pattern (Minimal)

```yaml
version: "3.9"

services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
```

**Purpose**: Quick start, ephemeral data (suitable for testing only)

---

## Official Canonical Pattern (Production)

```yaml
version: "3.9"

services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    secrets:
      - source: odoo_password
        target: /run/secrets/password
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD_FILE=/run/secrets/password
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    volumes:
      - db-data:/var/lib/postgresql/data
    secrets:
      - source: postgres_password
        target: /run/secrets/postgres_password

volumes:
  odoo-web-data:
  db-data:

secrets:
  odoo_password:
    file: ./secrets/odoo_password.txt
  postgres_password:
    file: ./secrets/postgres_password.txt
```

---

## Our Current Setup (Dev-Optimized)

```yaml
version: "3.9"

services:
  db:
    container_name: odoo-dev-db
    image: postgres:16
    environment:
      POSTGRES_DB: odoo_dev_sandbox
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - db-data:/var/lib/postgresql/data

  odoo:
    container_name: odoo-dev
    image: odoo:18
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
      DB_NAME: odoo_dev_sandbox
    volumes:
      - ../../addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf
      - odoo-web-data:/var/lib/odoo

volumes:
  db-data:
  odoo-web-data:
```

---

## Key Differences Analysis

### 1. Service Naming
**Official**: `web` + `db`
**Ours**: `odoo` + `db`
**Verdict**: ⚠️ **Cosmetic difference** - Both work identically. Official uses generic `web`, we use explicit `odoo`.

### 2. Container Names
**Official**: Auto-generated (e.g., `dev_web_1`)
**Ours**: Explicit (`odoo-dev`, `odoo-dev-db`)
**Verdict**: ✅ **Better for dev** - Explicit names aid debugging and scripts.

### 3. Database Name
**Official**: `postgres` (default PostgreSQL database)
**Ours**: `odoo_dev_sandbox` (explicit sandbox)
**Verdict**: ✅ **Better for clarity** - Explicit naming prevents confusion with system databases.

### 4. DB_NAME Environment Variable
**Official**: ❌ Not documented
**Ours**: ✅ `DB_NAME: odoo_dev_sandbox`
**Verdict**: ⚠️ **Undocumented variable** - Works but not in official docs. Consider removing if unnecessary.

### 5. Named Volumes
**Official Minimal**: ❌ No volumes (ephemeral)
**Official Production**: ✅ Named volumes
**Ours**: ✅ Named volumes
**Verdict**: ✅ **Production-ready** - Data persists across container restarts.

### 6. Configuration Override
**Official**: ❌ Not in minimal, ✅ in production
**Ours**: ✅ `./config/odoo.conf:/etc/odoo/odoo.conf`
**Verdict**: ✅ **Development-ready** - Allows `list_db = True` and other dev configs.

### 7. Custom Addons
**Official**: ❌ Not in minimal, ✅ in production
**Ours**: ✅ `../../addons:/mnt/extra-addons`
**Verdict**: ✅ **Development-ready** - Live addon development without rebuilding.

---

## Volume Paths (Canonical Reference)

| Path | Purpose | Official | Ours | Status |
|------|---------|----------|------|--------|
| `/var/lib/odoo` | Odoo filestore, sessions | ✅ | ✅ | Match |
| `/var/lib/postgresql/data` | PostgreSQL data | ✅ | ✅ | Match |
| `/etc/odoo/odoo.conf` | Configuration file | ✅ | ✅ | Match |
| `/mnt/extra-addons` | Custom addons | ✅ | ✅ | Match |

**All paths match official documentation** ✅

---

## Environment Variables (Canonical Reference)

| Variable | Purpose | Default | Official | Ours | Status |
|----------|---------|---------|----------|------|--------|
| `HOST` | PostgreSQL host | `db` | ✅ | ✅ | Match |
| `PORT` | PostgreSQL port | `5432` | ✅ (implicit) | ❌ (not set) | OK (uses default) |
| `USER` | PostgreSQL user | `odoo` | ✅ | ✅ | Match |
| `PASSWORD` | PostgreSQL password | `odoo` | ✅ | ✅ | Match |
| `PASSWORD_FILE` | Secrets file path | - | ✅ (production) | ❌ | OK (dev only) |
| `DB_NAME` | Target database | - | ❌ | ✅ | **Undocumented** |
| `POSTGRES_DB` | Database to create | `postgres` | ✅ | ✅ | Match |
| `POSTGRES_USER` | PostgreSQL superuser | `postgres` | ✅ | ✅ | Match |
| `POSTGRES_PASSWORD` | Superuser password | - | ✅ | ✅ | Match |

**Undocumented variable**: `DB_NAME` - works but not in official docs.

---

## Deployment Recommendations

### For Development (Current Use Case)
✅ **Our setup is production-ready with dev optimizations**:
- Named volumes for data persistence
- Config override for `list_db = True`
- Live addon mounting for development
- Explicit container names for debugging

### For Production
⚠️ **Required changes**:
1. Use Docker secrets instead of plain `PASSWORD`
2. Remove `list_db = True` from config
3. Set `admin_passwd` to strong password
4. Add `dbfilter` to restrict database access
5. Consider using `odoo-bin` with `--workers` for multi-threading

---

## Single Canonical Truth

**Development Setup** (sandbox/dev):
```yaml
services:
  db:
    container_name: odoo-dev-db
    image: postgres:16
    environment:
      POSTGRES_DB: odoo_dev_sandbox
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - db-data:/var/lib/postgresql/data

  odoo:
    container_name: odoo-dev
    image: odoo:18
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - ../../addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf
      - odoo-web-data:/var/lib/odoo

volumes:
  db-data:
  odoo-web-data:
```

**Key Points**:
1. Remove `DB_NAME` env var (undocumented, unnecessary)
2. Database name controlled via `POSTGRES_DB` in db service
3. Odoo connects to whatever database exists (filtered by `dbfilter` in config)
4. Use explicit container names for clarity
5. Mount config and addons for development

---

## Action Items

1. ✅ Document canonical setup (this file)
2. ⚠️ Remove `DB_NAME` from docker-compose.yml (undocumented)
3. ✅ Verify volume paths match official docs
4. ✅ Confirm environment variables align with official docs
5. ⚠️ Update CLAUDE.md with canonical reference

---

## References

- Official Docs: https://github.com/docker-library/docs/tree/master/odoo
- Docker Hub: https://hub.docker.com/_/odoo
- Odoo Source: https://github.com/odoo/docker
- PostgreSQL Image: https://hub.docker.com/_/postgres

---

**Last Updated**: 2026-01-14
**Reviewed By**: Claude Code
**Status**: ✅ Canonical reference established
