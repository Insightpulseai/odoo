# Official Odoo Docker Typology - Canonical Reference

**Source**: https://hub.docker.com/_/odoo/
**Purpose**: Official naming conventions and configuration patterns

---

## Official Service Names (Docker Compose)

| Service | Official Name | Purpose |
|---------|---------------|---------|
| Odoo | `web` | Odoo application service |
| PostgreSQL | `db` | Database service (MUST be named `db`) |

**Your setup**: ✅ Matches exactly

---

## Official Environment Variables (Odoo Connection)

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST` | `db` | PostgreSQL server address |
| `PORT` | `5432` | PostgreSQL port |
| `USER` | `odoo` | Database username |
| `PASSWORD` | `odoo` | Database password |

**Your setup**: ✅ All explicit, matches defaults

---

## Official PostgreSQL Init Values

| Variable | Official Value | Purpose |
|----------|----------------|---------|
| `POSTGRES_DB` | `postgres` | Initial database created by Postgres |
| `POSTGRES_USER` | `odoo` | PostgreSQL superuser |
| `POSTGRES_PASSWORD` | `odoo` | Superuser password |

**Your setup**: ✅ Matches exactly

---

## Official Filesystem Paths

| Path | Purpose | Official |
|------|---------|----------|
| `/var/lib/odoo` | Odoo filestore, sessions | ✅ Named volume |
| `/etc/odoo/odoo.conf` | Configuration file | ✅ Mount point |
| `/mnt/extra-addons` | Custom addons directory | ✅ Mount point |
| `8069:8069` | HTTP port mapping | ✅ Standard port |

**Your setup**: ✅ All paths match official

---

## Official Docker Compose Pattern

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

  web:
    image: odoo:18
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config/odoo.conf:/etc/odoo/odoo.conf:ro
      - ../../addons:/mnt/extra-addons

volumes:
  odoo-db-data:
  odoo-web-data:
```

---

## Official Container Names (docker run)

**Postgres container**:
```bash
docker run -d \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  --name db \
  postgres:15
```

**Odoo container**:
```bash
docker run -d \
  -p 8069:8069 \
  --name odoo \
  --link db:db \
  odoo:18
```

**Official naming**:
- Postgres container: `db`
- Odoo container: `odoo`

---

## Key Official Requirements

### 1. Database Container Must Be Named `db`
**Official docs explicitly state**: The Postgres container alias **MUST be `db`** for default connection behavior.

**Why**: The `HOST` environment variable defaults to `db`, so Docker networking resolves `db` to the database container.

### 2. Two Containers Required
**Official pattern**:
- One container for Odoo (`web` service)
- One container for PostgreSQL (`db` service)

**NOT supported**: Single container with embedded database.

### 3. Initial Database vs Odoo Database
**Two different concepts**:
1. `POSTGRES_DB=postgres` - Initial Postgres database (just a container)
2. `odoo` - The actual Odoo database (created via UI/CLI)

**Confusion point**: The initial Postgres database name doesn't matter much - Odoo creates its own database inside.

---

## Production Mapping (DO Managed Postgres)

For **TBWA\SMP production** using DigitalOcean Managed Postgres:

### Conceptual Label
Keep calling the database dependency **"db"** in diagrams/docs for consistency with official typology.

### Runtime Configuration
Since you don't have a `db` container, set explicit connection:

```yaml
web:
  environment:
    HOST: odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com  # Managed DB hostname
    PORT: 25060  # Managed DB port (not 5432)
    USER: doadmin  # Managed DB user
    PASSWORD: ${ODOO_DB_PASSWORD}  # From environment variable
```

### Official Docs Reference
The official docs say: `HOST` is the Postgres address and defaults to `db`.

**Translation**: In production, override `HOST` to point to managed database instead of `db` container.

---

## Canonical Commands (Official Reference)

### Start Stack
```bash
docker compose up -d
```

### View Logs
```bash
docker compose logs web    # Odoo logs
docker compose logs db     # Postgres logs
```

### Execute Commands in Odoo
```bash
docker compose exec web odoo --version
docker compose exec web bash
```

### Initialize Database
```bash
docker compose exec web odoo -d odoo -i base --stop-after-init
```

### Restart Services
```bash
docker compose restart web
docker compose restart db
```

### Access Odoo
```
http://localhost:8069
```

---

## Official Typology Summary

| Component | Official Name | Your Setup | Status |
|-----------|---------------|------------|--------|
| **Postgres service** | `db` | `db` | ✅ Match |
| **Odoo service** | `web` | `web` | ✅ Match |
| **Postgres image** | `postgres:15` | `postgres:15` | ✅ Match |
| **Odoo image** | `odoo:17.0` | `odoo:18` | ⚠️ Newer |
| **HOST** | `db` | `db` | ✅ Match |
| **PORT** | `5432` | `5432` | ✅ Match |
| **USER** | `odoo` | `odoo` | ✅ Match |
| **PASSWORD** | `odoo` | `odoo` | ✅ Match |
| **POSTGRES_DB** | `postgres` | `postgres` | ✅ Match |
| **POSTGRES_USER** | `odoo` | `odoo` | ✅ Match |
| **POSTGRES_PASSWORD** | `odoo` | `odoo` | ✅ Match |
| **Data volume** | `/var/lib/odoo` | `/var/lib/odoo` | ✅ Match |
| **Config path** | `/etc/odoo/odoo.conf` | `/etc/odoo/odoo.conf` | ✅ Match |
| **Addons path** | `/mnt/extra-addons` | `/mnt/extra-addons` | ✅ Match |
| **HTTP port** | `8069:8069` | `8069:8069` | ✅ Match |

---

## Troubleshooting with Official Docs

### When official docs say:
**"The Postgres container must be named `db`"**
→ Your `db` service satisfies this requirement ✅

**"Mount custom addons at `/mnt/extra-addons`"**
→ Your volume mount matches: `../../addons:/mnt/extra-addons` ✅

**"Override config at `/etc/odoo/odoo.conf`"**
→ Your mount matches: `./config/odoo.conf:/etc/odoo/odoo.conf:ro` ✅

**"Set `HOST` environment variable to database address"**
→ Your config: `HOST: db` (resolves to `db` service) ✅

**"Default port is 8069"**
→ Your mapping: `8069:8069` ✅

---

## Differences from Official (Intentional)

### 1. Newer Images
**Official**: `odoo:17.0`, `postgres:15`
**Yours**: `odoo:18`, `postgres:15`

**Why**: Odoo 18 is latest stable, backward compatible.

### 2. Read-Only Config Mount
**Official**: No `:ro` flag
**Yours**: `./config/odoo.conf:/etc/odoo/odoo.conf:ro`

**Why**: Prevents accidental modification from inside container.

### 3. Explicit PORT Variable
**Official**: Not shown (uses default)
**Yours**: `PORT: 5432` (explicit)

**Why**: Clarity, easier to override for managed databases.

---

## Key Takeaways

1. **Official service names**: `web` (Odoo) + `db` (Postgres)
2. **Database container MUST be named `db`** for default behavior
3. **Two containers required** - no single-container option
4. **All environment variables have defaults** - but explicit is better
5. **Official paths are canonical** - `/var/lib/odoo`, `/etc/odoo/odoo.conf`, `/mnt/extra-addons`
6. **For managed Postgres**: Override `HOST` to external address

---

**Last Updated**: 2026-01-14
**Official Reference**: https://hub.docker.com/_/odoo/
**Status**: ✅ 100% aligned with official typology
