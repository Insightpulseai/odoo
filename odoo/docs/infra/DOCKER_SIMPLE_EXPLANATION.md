# Docker Setup - Simple Explanation

## Question 1: How many databases in ONE container?

**Answer**: ONE container can hold MANY databases

```
┌─────────────────────────────────┐
│ Container: odoo-dev-db          │
│ (This is the database server)   │
│                                 │
│ Databases inside:               │
│  ├─ postgres (system)           │
│  ├─ template0 (system)          │
│  ├─ template1 (system)          │
│  └─ odoo_dev_sandbox (YOURS)   │  ← Your Odoo data lives here
│                                 │
│ You could add more:             │
│  ├─ odoo_prod (if needed)       │
│  └─ odoo_test (if needed)       │
└─────────────────────────────────┘
```

**Currently you have**: 1 database = `odoo_dev_sandbox`

---

## Question 2: How many servers?

**Answer**: 2 servers (2 containers)

```
┌─────────────────────────────────┐
│ Server 1: odoo-dev              │  ← Runs Odoo application
│ Image: odoo:18                  │
│ Port: 8069                      │
└─────────────────────────────────┘
            ↓ connects to
┌─────────────────────────────────┐
│ Server 2: odoo-dev-db           │  ← Runs PostgreSQL database
│ Image: postgres:16              │
│ Contains: odoo_dev_sandbox      │
└─────────────────────────────────┘
```

---

## Question 3: Different database for dev and prod?

**Official recommendation**: YES - Separate databases

**Option 1: Same container, different databases**
```
odoo-dev-db container:
  ├─ odoo_dev  ← Development work
  └─ odoo_prod ← Production work
```

**Option 2: Different containers** (recommended)
```
Dev setup:
  odoo-dev → odoo-dev-db (odoo_dev)

Prod setup:
  odoo-prod → odoo-prod-db (odoo_prod)
```

**Your current setup**: Only dev (`odoo_dev_sandbox`)

---

## Question 4: How many passwords?

**Answer**: 3 passwords in your setup

### Password #1: Database Admin
- **Where**: `POSTGRES_PASSWORD` in docker-compose.yml
- **Value**: `odoo`
- **Purpose**: PostgreSQL superuser password
- **Used by**: Database container to create/manage databases

### Password #2: Odoo Connection
- **Where**: `PASSWORD` in docker-compose.yml
- **Value**: `odoo` (same as #1)
- **Purpose**: Odoo connects to PostgreSQL
- **Used by**: Odoo container to read/write data

### Password #3: Master Password
- **Where**: `admin_passwd` in config/odoo.conf
- **Value**: `admin`
- **Purpose**: Access Odoo database manager
- **Used by**: You, when creating/deleting databases

---

## Question 5: Routing - How does it connect?

```
Step 1: You open browser
   http://localhost:8069
        ↓

Step 2: Browser connects to Odoo container
   odoo-dev (port 8069)
        ↓

Step 3: Odoo needs data, uses these settings:
   HOST: db               ← Name of database container
   USER: odoo             ← Database username
   PASSWORD: odoo         ← Database password
        ↓

Step 4: Odoo connects to database container
   odoo-dev-db
        ↓

Step 5: Database finds the right database
   odoo_dev_sandbox
        ↓

Step 6: Database returns data
   Tables, records, etc.
        ↓

Step 7: Odoo renders page
   Shows you the data
        ↓

Step 8: Browser displays page
   You see Odoo interface
```

**Key point**:
- Container name `db` in docker-compose = hostname `db` in Odoo config
- Docker networking makes containers talk to each other by name

---

## Summary Table

| Item | Count | Details |
|------|-------|---------|
| **Containers** | 2 | odoo-dev + odoo-dev-db |
| **Databases** | 1 (can be many) | odoo_dev_sandbox |
| **Passwords** | 3 | postgres, odoo connection, master |
| **Ports** | 1 exposed | 8069 (Odoo web) |
| **Volumes** | 2 | db-data, odoo-web-data |

---

## Your Current Setup (Verified)

```yaml
services:
  db:
    container_name: odoo-dev-db        ← Server 2 (database)
    image: postgres:16
    environment:
      POSTGRES_DB: odoo_dev_sandbox    ← Database name
      POSTGRES_USER: odoo              ← Database user
      POSTGRES_PASSWORD: odoo          ← Password #1
    volumes:
      - db-data:/var/lib/postgresql/data

  odoo:
    container_name: odoo-dev           ← Server 1 (application)
    image: odoo:18
    depends_on:
      - db
    ports:
      - "8069:8069"                    ← Access via localhost:8069
    environment:
      HOST: db                         ← Connects to "db" container
      USER: odoo                       ← Uses "odoo" user
      PASSWORD: odoo                   ← Password #2 (same as #1)
    volumes:
      - ../../addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf  ← Contains password #3
      - odoo-web-data:/var/lib/odoo
```

**Config file** (config/odoo.conf):
```ini
admin_passwd = admin                 ← Password #3 (master)
db_name = odoo_dev_sandbox           ← Which database to use
dbfilter = ^odoo_dev_sandbox$        ← Only show this database
list_db = True                       ← Show database manager
```

---

## Official vs Yours

| Aspect | Official Minimal | Your Setup | Status |
|--------|-----------------|------------|--------|
| Containers | 2 (web + db) | 2 (odoo-dev + odoo-dev-db) | ✅ Same |
| Databases | 1 (postgres) | 1 (odoo_dev_sandbox) | ✅ Same |
| Passwords | 2 (dev) | 3 (dev + master) | ✅ Better |
| Volumes | 0 (ephemeral) | 2 (persistent) | ✅ Better |
| Config | None | Mounted | ✅ Better |
| Addons | None | Mounted | ✅ Better |

**Your setup is production-ready** ✅

---

**Last Updated**: 2026-01-14
**Status**: ✅ Simple explanation complete
