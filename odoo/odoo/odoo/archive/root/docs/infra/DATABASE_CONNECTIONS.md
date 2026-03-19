# Superset Database Connections Guide

Complete guide for connecting Apache Superset to Odoo PostgreSQL and Supabase.

## Prerequisites

- Apache Superset installed and running
- Database credentials (PostgreSQL)
- Network access to database servers

## Connection 1: Odoo PostgreSQL (Local)

### Connection String Format

```
postgresql://username:password@host:port/database
```

### Odoo Dev Database

```bash
# Connection URI
postgresql://odoo:odoo@localhost:5432/odoo_dev

# Or with environment variables
postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}
```

### Add via Superset UI

1. Navigate to: **Data → Databases**
2. Click **+ Database**
3. Select **PostgreSQL**
4. Enter details:

```yaml
Display Name: Odoo Development
SQLAlchemy URI: postgresql://odoo:odoo@localhost:5432/odoo_dev
```

5. Click **Test Connection**
6. Click **Connect**

### Add via Superset CLI

```bash
superset db upgrade

# Add database connection
superset set-database-uri \
  --database_name "Odoo Development" \
  --sqlalchemy_uri "postgresql://odoo:odoo@localhost:5432/odoo_dev"
```

### Add via Python (Programmatic)

```python
from superset import db
from superset.models.core import Database

# Create database connection
database = Database(
    database_name="Odoo Development",
    sqlalchemy_uri="postgresql://odoo:odoo@localhost:5432/odoo_dev",
    expose_in_sqllab=True,
    allow_ctas=True,
    allow_cvas=True,
)

db.session.add(database)
db.session.commit()
```

---

## Connection 2: Supabase PostgreSQL

### Get Supabase Connection Details

From your Supabase project (`spdtwktxdalcfigzeqrz`):

**Direct Connection (Port 5432):**
```
Host: aws-0-us-east-1.pooler.supabase.com
Port: 5432
Database: postgres
User: postgres.spdtwktxdalcfigzeqrz
Password: [your-db-password]
```

**Pooler Connection (Port 6543):**
```
Host: aws-0-us-east-1.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.spdtwktxdalcfigzeqrz
Password: [your-db-password]
```

### Connection String

```bash
# Direct connection (for analytics/reporting - use this for Superset)
postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Pooler connection (for transactional workloads)
postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Add via Superset UI

1. Navigate to: **Data → Databases**
2. Click **+ Database**
3. Select **PostgreSQL**
4. Enter details:

```yaml
Display Name: Supabase (OPS)
SQLAlchemy URI: postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Advanced → SQL Lab
☑ Expose database in SQL Lab
☑ Allow CREATE TABLE AS
☑ Allow CREATE VIEW AS
☑ Allow DML

# Advanced → Security
☑ Allow file uploads to database
```

5. **Extra** (JSON config):

```json
{
  "metadata_params": {},
  "engine_params": {
    "connect_args": {
      "sslmode": "require"
    }
  },
  "metadata_cache_timeout": {},
  "schemas_allowed_for_file_upload": ["public", "ops", "cms"]
}
```

6. Click **Test Connection**
7. Click **Connect**

---

## Connection 3: Secure Connection with Environment Variables

### Store Credentials Securely

**In `.env` file:**

```bash
# Odoo PostgreSQL
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=odoo
ODOO_DB_HOST=localhost
ODOO_DB_PORT=5432
ODOO_DB_NAME=odoo_dev

# Supabase PostgreSQL
SUPABASE_DB_USER=postgres.spdtwktxdalcfigzeqrz
SUPABASE_DB_PASSWORD=your_password_here
SUPABASE_DB_HOST=aws-0-us-east-1.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
```

### Use in Superset Config

Edit `superset_config.py`:

```python
import os

# Odoo connection
SQLALCHEMY_DATABASE_URI_ODOO = (
    f"postgresql://{os.getenv('ODOO_DB_USER')}:"
    f"{os.getenv('ODOO_DB_PASSWORD')}@"
    f"{os.getenv('ODOO_DB_HOST')}:"
    f"{os.getenv('ODOO_DB_PORT')}/"
    f"{os.getenv('ODOO_DB_NAME')}"
)

# Supabase connection
SQLALCHEMY_DATABASE_URI_SUPABASE = (
    f"postgresql://{os.getenv('SUPABASE_DB_USER')}:"
    f"{os.getenv('SUPABASE_DB_PASSWORD')}@"
    f"{os.getenv('SUPABASE_DB_HOST')}:"
    f"{os.getenv('SUPABASE_DB_PORT')}/"
    f"{os.getenv('SUPABASE_DB_NAME')}?sslmode=require"
)
```

---

## Verification Scripts

### Test Odoo Connection

```bash
# Using psql
PGPASSWORD=odoo psql -h localhost -p 5432 -U odoo -d odoo_dev -c "SELECT version();"

# Using Python
python3 << 'PYTHON'
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="odoo_dev",
    user="odoo",
    password="odoo"
)
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
PYTHON
```

### Test Supabase Connection

```bash
# Using psql (replace [password])
PGPASSWORD=[password] psql \
  -h aws-0-us-east-1.pooler.supabase.com \
  -p 5432 \
  -U postgres.spdtwktxdalcfigzeqrz \
  -d postgres \
  -c "SELECT version();"

# Check ops schema exists
PGPASSWORD=[password] psql \
  -h aws-0-us-east-1.pooler.supabase.com \
  -p 5432 \
  -U postgres.spdtwktxdalcfigzeqrz \
  -d postgres \
  -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ops';"
```

---

## Common Superset Queries for Odoo

### Get Active Projects

```sql
-- In Superset SQL Lab
SELECT
    id,
    name,
    create_date,
    write_date
FROM project_project
WHERE active = true
ORDER BY create_date DESC
LIMIT 100;
```

### Get Deployments Count by Status

```sql
SELECT
    state,
    COUNT(*) as count
FROM project_task
WHERE project_id IN (SELECT id FROM project_project WHERE active = true)
GROUP BY state
ORDER BY count DESC;
```

---

## Common Superset Queries for Supabase

### Get OPS Projects

```sql
-- In Superset SQL Lab
SELECT
    id,
    name,
    status,
    created_at
FROM ops.projects
ORDER BY created_at DESC
LIMIT 100;
```

### Get WAF Events

```sql
SELECT
    event_type,
    severity,
    COUNT(*) as count
FROM ops.waf_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY event_type, severity
ORDER BY count DESC;
```

---

## Troubleshooting

### Error: "Could not connect to database"

**Check 1: Network connectivity**
```bash
# Test Odoo
nc -zv localhost 5432

# Test Supabase
nc -zv aws-0-us-east-1.pooler.supabase.com 5432
```

**Check 2: Credentials**
```bash
# Verify Odoo user
PGPASSWORD=odoo psql -h localhost -U odoo -d odoo_dev -c "SELECT current_user;"

# Verify Supabase user
PGPASSWORD=[password] psql -h aws-0-us-east-1.pooler.supabase.com -U postgres.spdtwktxdalcfigzeqrz -d postgres -c "SELECT current_user;"
```

### Error: "SSL connection required"

For Supabase, always add `?sslmode=require` to connection URI:

```
postgresql://user:pass@host:port/db?sslmode=require
```

### Error: "Too many connections"

**For Supabase:** Use pooler port 6543 instead of direct port 5432:

```
postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

---

## Integration with OdooOps Dashboard

### Connect Superset to Next.js Dashboard

1. **Install Superset Python client** (if needed)
2. **Create API endpoint** in Next.js
3. **Fetch Superset charts** via REST API

**Example Next.js API Route:**

```typescript
// app/api/superset/charts/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const supersetUrl = process.env.SUPERSET_URL || "http://localhost:8088";
  const token = process.env.SUPERSET_API_TOKEN;

  const response = await fetch(
    `${supersetUrl}/api/v1/chart/${params.id}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();
  return Response.json(data);
}
```

---

## Production Deployment Checklist

### Odoo PostgreSQL

- [ ] Use strong password (not "odoo")
- [ ] Create read-only user for Superset
- [ ] Enable SSL connections
- [ ] Configure pg_hba.conf for Superset IP
- [ ] Set connection pooling limits

### Supabase PostgreSQL

- [ ] Use database password (not service_role key)
- [ ] Always use `sslmode=require`
- [ ] Use pooler port 6543 for high-frequency queries
- [ ] Set row-level security policies for sensitive tables
- [ ] Monitor connection pool usage

---

## Quick Reference

| Database | Host | Port | User | Database |
|----------|------|------|------|----------|
| Odoo Dev | localhost | 5432 | odoo | odoo_dev |
| Odoo Prod | 178.128.112.214 | 5432 | odoo | odoo |
| Supabase Direct | aws-0-us-east-1.pooler.supabase.com | 5432 | postgres.spdtwktxdalcfigzeqrz | postgres |
| Supabase Pooler | aws-0-us-east-1.pooler.supabase.com | 6543 | postgres.spdtwktxdalcfigzeqrz | postgres |

---

**Created:** 2026-02-14
**Updated:** 2026-02-14
**Status:** ✅ Ready to use
