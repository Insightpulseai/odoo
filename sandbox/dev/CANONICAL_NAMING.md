# Canonical Database Naming Conventions

## DigitalOcean Managed PostgreSQL Cluster

**Cluster Name:** `odoo-db-sgp1`
**Version:** PostgreSQL 16
**Region:** SGP1 (Singapore)
**Connection:** `odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060`

---

## Database Naming Standards

### 1. Odoo Database

```
Database Name: odoo
User: odoo_app
Purpose: Canonical Odoo application database
```

**Rationale:**
- Matches official docker-library convention
- Aligns with local sandbox naming
- Clear, unambiguous naming
- No "defaultdb" ambiguity

**Configuration:**
```ini
db_name = odoo
db_user = odoo_app
```

---

### 2. Apache Superset Database

```
Database Name: superset
User: superset_app
Purpose: Superset metadata storage
```

**Rationale:**
- Separate metadata database from Odoo
- Isolated permissions and access
- Standard Superset convention

**Configuration:**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://superset_app:password@host:25060/superset'
```

---

### 3. n8n Database

```
Database Name: n8n
User: n8n_app
Purpose: n8n workflow metadata
```

**Rationale:**
- Separate workflow metadata from Odoo
- Isolated permissions
- Standard n8n convention

**Configuration:**
```bash
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n_app
```

---

## Service-to-Database Mapping

| Service | Database | User | Purpose |
|---------|----------|------|---------|
| **Odoo** | `odoo` | `odoo_app` | ERP application data |
| **Superset** | `superset` | `superset_app` | BI metadata |
| **n8n** | `n8n` | `n8n_app` | Workflow metadata |

---

## Local Sandbox Alignment

### Local Development (`docker-compose.yml`)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: odoo          # ✅ Matches production
      POSTGRES_USER: odoo        # Simplified for local
      POSTGRES_PASSWORD: odoo    # Simplified for local
```

**Configuration (`odoo.conf`):**
```ini
db_host = db                     # Local container service name
db_port = 5432                   # Standard PostgreSQL port
db_user = odoo                   # Simplified for local
db_name = odoo                   # ✅ Matches production
```

---

### Production Connection (`docker-compose.production.yml`)

```yaml
services:
  dbssl:
    # stunnel SSL tunnel to DO Managed DB

  odoo:
    environment:
      DB_HOST: dbssl             # Via SSL tunnel
      DB_PORT: 5432              # Tunnel local port
      DB_USER: odoo_app          # ✅ Production user
      DB_NAME: odoo              # ✅ Production database
```

**Configuration (`odoo.conf.production`):**
```ini
db_host = dbssl                  # Via stunnel
db_port = 5432                   # Tunnel port
db_user = odoo_app               # ✅ Production user
db_name = odoo                   # ✅ Production database
```

---

## User Permissions Matrix

### odoo_app (Odoo Application User)

**Database:** `odoo`
**Permissions:**
- CONNECT
- CREATE (schemas)
- All privileges on `odoo` database
- No access to `superset` or `n8n` databases

**Grant SQL:**
```sql
CREATE USER odoo_app WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE odoo TO odoo_app;
ALTER DATABASE odoo OWNER TO odoo_app;
```

---

### superset_app (Superset Metadata User)

**Database:** `superset`
**Permissions:**
- CONNECT
- CREATE (schemas)
- All privileges on `superset` database
- **Read-only access** to `odoo` database (for analytics)

**Grant SQL:**
```sql
CREATE USER superset_app WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE superset TO superset_app;
GRANT CONNECT ON DATABASE odoo TO superset_app;
GRANT USAGE ON SCHEMA public TO superset_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_app;
```

---

### n8n_app (n8n Workflow User)

**Database:** `n8n`
**Permissions:**
- CONNECT
- CREATE (schemas)
- All privileges on `n8n` database
- No direct access to other databases (uses Odoo API)

**Grant SQL:**
```sql
CREATE USER n8n_app WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n_app;
ALTER DATABASE n8n OWNER TO n8n_app;
```

---

## Network Access Configuration

### Allowlisted IPs (DO Dashboard → Network Access)

```
178.128.112.214    # Odoo production droplet ✅
10.104.0.0/20      # VPC network (if using private connectivity)
```

**How to Add:**
1. DigitalOcean Dashboard
2. Databases → odoo-db-sgp1
3. Network Access tab
4. Add Trusted Source → Enter IP

---

## Connection String Formats

### Odoo (via stunnel)

```bash
# Local (sandbox)
postgresql://odoo:odoo@db:5432/odoo

# Production (via stunnel)
postgresql://odoo_app:password@dbssl:5432/odoo
```

---

### Superset

```python
# Metadata database
SQLALCHEMY_DATABASE_URI = 'postgresql://superset_app:password@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/superset?sslmode=require'

# Odoo database (read-only analytics)
SQLALCHEMY_EXAMPLES_URI = 'postgresql://superset_app:password@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/odoo?sslmode=require'
```

---

### n8n

```bash
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
DB_POSTGRESDB_PORT=25060
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n_app
DB_POSTGRESDB_PASSWORD=password
DB_POSTGRESDB_SSL_ENABLED=true
```

---

## Migration Path (defaultdb → odoo)

If you currently have data in `defaultdb`:

### 1. Create new `odoo` database

```sql
-- Connect as doadmin
CREATE DATABASE odoo WITH OWNER odoo_app;
```

### 2. Dump existing data

```bash
pg_dump -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 -U doadmin -d defaultdb --no-owner --no-acl \
  | gzip > defaultdb_backup_$(date +%Y%m%d).sql.gz
```

### 3. Restore to `odoo` database

```bash
gunzip -c defaultdb_backup_*.sql.gz | \
  psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 -U odoo_app -d odoo
```

### 4. Update all configurations

```bash
# Update all service configs to use:
DB_NAME=odoo
```

### 5. Test thoroughly

```bash
# Verify Odoo can connect
# Verify data integrity
# Verify all modules load
```

### 6. Archive defaultdb

```sql
-- After successful migration
-- Keep for 30 days, then drop
```

---

## Verification Commands

### Check current databases

```sql
\l  -- List all databases
```

Expected output:
```
     Name     |    Owner     | Encoding
--------------+--------------+----------
 odoo         | odoo_app     | UTF8
 superset     | superset_app | UTF8
 n8n          | n8n_app      | UTF8
 defaultdb    | doadmin      | UTF8  (legacy, to be removed)
```

---

### Check user permissions

```sql
-- As doadmin
\du  -- List all users
```

Expected output:
```
        Role name        | Attributes
-------------------------+------------
 doadmin                 | Superuser
 odoo_app                |
 superset_app            |
 n8n_app                 |
```

---

### Test connection from droplet

```bash
# Odoo app user
PGPASSWORD='password' psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo \
  --set=sslmode=require \
  -c "SELECT version();"
```

---

## Canonical Configuration Summary

| Environment | db_host | db_port | db_name | db_user | SSL |
|-------------|---------|---------|---------|---------|-----|
| **Local Sandbox** | `db` | 5432 | `odoo` | `odoo` | No |
| **Production** | `dbssl` | 5432 | `odoo` | `odoo_app` | Yes (via stunnel) |

**Key Principles:**
- ✅ Database name `odoo` is canonical across all environments
- ✅ Separate users per service (`odoo_app`, `superset_app`, `n8n_app`)
- ✅ Separate databases per service (`odoo`, `superset`, `n8n`)
- ✅ Local sandbox mirrors production naming
- ✅ SSL/TLS enforced in production via stunnel

---

**Last Updated:** 2026-01-14
**Cluster:** odoo-db-sgp1 (PostgreSQL 16)
**Region:** SGP1 (Singapore)
