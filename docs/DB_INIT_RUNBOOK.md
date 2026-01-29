# Database Initialization Runbook

**Version:** 1.0.0
**Phase:** 2 - Database Initialization (Controlled)
**Status:** EXECUTE ONCE, THEN ARCHIVE

---

## Prerequisites (Phase 0 + 1 Complete)

Before executing this runbook, verify:

```bash
# Phase 0: Platform readiness
./scripts/check_odoosh_parity.py --threshold 95  # Must pass
ls llms.txt llms-full.txt                         # Must exist
ls .github/workflows/docs-drift-gate.yml          # Must exist

# Phase 1: Infrastructure locked
ls docker-compose.yml docker-compose.dev.yml      # Must exist
ls deploy/docker-compose.prod.yml                 # Must exist
```

**GO / NO-GO Checklist:**
- [ ] Parity score ≥95%
- [ ] LLM context files present
- [ ] CI gates active
- [ ] Docker topology locked
- [ ] Backup scripts present

---

## 1. Database Model Decision

**Default Strategy:** 1 database per environment

| Environment | Database Name | Purpose |
|-------------|---------------|---------|
| Development | `odoo_dev` | Local development |
| Staging | `odoo_staging` | Pre-production testing |
| Production | `odoo_prod` | Live system |

### Environment Variables

```bash
# Set in .env or export
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=odoo
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export POSTGRES_DB_DEV=odoo_dev
export POSTGRES_DB_STAGING=odoo_staging
export POSTGRES_DB_PROD=odoo_prod
```

---

## 2. Create Databases (CLI Only)

### 2.1 Start PostgreSQL Container

```bash
# If using Docker Compose
docker compose up -d postgres

# Verify PostgreSQL is running
docker compose exec postgres pg_isready -U odoo
```

### 2.2 Create Databases

```bash
# Create development database
docker compose exec postgres createdb -U odoo "$POSTGRES_DB_DEV"

# Create staging database
docker compose exec postgres createdb -U odoo "$POSTGRES_DB_STAGING"

# Create production database (only on production server)
docker compose exec postgres createdb -U odoo "$POSTGRES_DB_PROD"

# Verify databases exist
docker compose exec postgres psql -U odoo -c "\l" | grep odoo_
```

Expected output:
```
 odoo_dev      | odoo | UTF8     | ...
 odoo_staging  | odoo | UTF8     | ...
 odoo_prod     | odoo | UTF8     | ...
```

---

## 3. Initialize Odoo Schema

### 3.1 Initialize with Base Modules

```bash
# Development environment
docker compose exec odoo-core odoo \
  -d "$POSTGRES_DB_DEV" \
  -i base \
  --stop-after-init \
  --without-demo=all

# Staging environment
docker compose exec odoo-core odoo \
  -d "$POSTGRES_DB_STAGING" \
  -i base \
  --stop-after-init \
  --without-demo=all
```

### 3.2 Verify Schema Created

```bash
# Check table count (should be >100)
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Check Odoo version
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" -c \
  "SELECT latest_version FROM ir_module_module WHERE name = 'base';"
```

Expected:
- Table count: ~150-200 tables
- Version: 19.0.x.x.x (Odoo 19)

---

## 4. Create Database Roles

### 4.1 Application User (Read/Write)

```bash
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" << 'EOF'
-- Create app user with RW access
CREATE ROLE odoo_app WITH LOGIN PASSWORD 'app_secure_password';
GRANT CONNECT ON DATABASE odoo_dev TO odoo_app;
GRANT USAGE ON SCHEMA public TO odoo_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO odoo_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO odoo_app;

-- Apply to future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO odoo_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO odoo_app;

\echo 'App user created successfully'
EOF
```

### 4.2 Reporting User (Read-Only)

```bash
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" << 'EOF'
-- Create reporting user with RO access
CREATE ROLE odoo_reporting WITH LOGIN PASSWORD 'reporting_secure_password';
GRANT CONNECT ON DATABASE odoo_dev TO odoo_reporting;
GRANT USAGE ON SCHEMA public TO odoo_reporting;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO odoo_reporting;

-- Apply to future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO odoo_reporting;

\echo 'Reporting user created successfully'
EOF
```

### 4.3 Verify Roles

```bash
docker compose exec postgres psql -U odoo -c "\du" | grep odoo_
```

Expected:
```
 odoo_app       |                                       | {}
 odoo_reporting |                                       | {}
```

---

## 5. Snapshot Baseline

### 5.1 Create Evidence Directory

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}"
mkdir -p "$EVIDENCE_DIR"
```

### 5.2 Capture Database Baseline

```bash
# Schema snapshot
docker compose exec postgres pg_dump -U odoo -d "$POSTGRES_DB_DEV" \
  --schema-only --no-owner --no-acl \
  > "${EVIDENCE_DIR}/schema_baseline.sql"

# Table list
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" \
  -t > "${EVIDENCE_DIR}/table_list.txt"

# Module list
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" \
  -c "SELECT name, state, latest_version FROM ir_module_module WHERE state = 'installed' ORDER BY name;" \
  > "${EVIDENCE_DIR}/installed_modules.txt"

# Summary JSON
cat > "${EVIDENCE_DIR}/summary.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "phase": "2-database-init",
  "database": "$POSTGRES_DB_DEV",
  "odoo_version": "19.0",
  "action": "initial_schema_creation",
  "table_count": $(wc -l < "${EVIDENCE_DIR}/table_list.txt"),
  "roles_created": ["odoo_app", "odoo_reporting"],
  "status": "baseline_captured"
}
EOF
```

### 5.3 Create Full Backup (Rollback Point)

```bash
# Create full database backup
docker compose exec postgres pg_dump -U odoo -d "$POSTGRES_DB_DEV" \
  --format=custom --compress=9 \
  > "${EVIDENCE_DIR}/${POSTGRES_DB_DEV}_baseline.dump"

# Verify backup integrity
pg_restore --list "${EVIDENCE_DIR}/${POSTGRES_DB_DEV}_baseline.dump" > /dev/null \
  && echo "✅ Backup verified" \
  || echo "❌ Backup verification failed"
```

---

## 6. Validation Checklist

Run these checks to confirm successful initialization:

```bash
#!/bin/bash
# db_init_verify.sh

echo "=== Database Initialization Verification ==="
echo ""

# 1. Database exists
echo "1. Checking database existence..."
docker compose exec postgres psql -U odoo -c "\l" | grep -q "$POSTGRES_DB_DEV" \
  && echo "   ✅ Database exists" \
  || echo "   ❌ Database not found"

# 2. Tables created
echo "2. Checking table count..."
TABLE_COUNT=$(docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" -t -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
TABLE_COUNT=$(echo "$TABLE_COUNT" | tr -d ' ')
if [ "$TABLE_COUNT" -gt 100 ]; then
  echo "   ✅ $TABLE_COUNT tables created"
else
  echo "   ❌ Only $TABLE_COUNT tables (expected >100)"
fi

# 3. Base module installed
echo "3. Checking base module..."
docker compose exec postgres psql -U odoo -d "$POSTGRES_DB_DEV" -t -c \
  "SELECT state FROM ir_module_module WHERE name = 'base';" | grep -q "installed" \
  && echo "   ✅ Base module installed" \
  || echo "   ❌ Base module not installed"

# 4. Roles created
echo "4. Checking database roles..."
docker compose exec postgres psql -U odoo -c "\du" | grep -q "odoo_app" \
  && echo "   ✅ odoo_app role exists" \
  || echo "   ❌ odoo_app role missing"
docker compose exec postgres psql -U odoo -c "\du" | grep -q "odoo_reporting" \
  && echo "   ✅ odoo_reporting role exists" \
  || echo "   ❌ odoo_reporting role missing"

# 5. Evidence captured
echo "5. Checking evidence pack..."
if [ -f "${EVIDENCE_DIR}/summary.json" ]; then
  echo "   ✅ Evidence pack created at ${EVIDENCE_DIR}"
else
  echo "   ❌ Evidence pack missing"
fi

echo ""
echo "=== Verification Complete ==="
```

---

## 7. Post-Initialization Actions

### 7.1 Commit Evidence

```bash
git add docs/evidence/
git commit -m "docs(evidence): database initialization baseline - Phase 2

- Created databases: odoo_dev, odoo_staging
- Initialized Odoo 19.0 schema
- Created roles: odoo_app (rw), odoo_reporting (ro)
- Captured baseline evidence pack

Phase 2 complete. Safe rollback point established.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push origin main
```

### 7.2 Lock Database Admin Password

```bash
# Set admin password (required for security)
docker compose exec odoo-core odoo \
  -d "$POSTGRES_DB_DEV" \
  --no-http \
  --stop-after-init \
  -c "from odoo import SUPERUSER_ID; env = api.Environment(cr, SUPERUSER_ID, {}); env['res.users'].browse(2).write({'password': 'secure_admin_password'})"
```

Or via odoo.conf:
```ini
admin_passwd = $(openssl rand -base64 32)
```

### 7.3 Set Security Defaults

Add to `odoo.conf`:
```ini
# Database security
list_db = False                    # Hide database selector
dbfilter = ^%d$                    # Restrict to single DB

# Admin security
admin_passwd = <generated_hash>    # Master password

# Session security
session_store = redis              # If using Redis
server_wide_modules = base,web
```

---

## 8. Rollback Procedure

If initialization fails, restore from baseline:

```bash
# Drop failed database
docker compose exec postgres dropdb -U odoo "$POSTGRES_DB_DEV"

# Recreate from backup
docker compose exec postgres createdb -U odoo "$POSTGRES_DB_DEV"
cat "${EVIDENCE_DIR}/${POSTGRES_DB_DEV}_baseline.dump" | \
  docker compose exec -T postgres pg_restore -U odoo -d "$POSTGRES_DB_DEV"

echo "✅ Database restored to baseline"
```

---

## 9. Next Phase (Phase 3)

After successful database initialization:

1. Install curated OCA modules (see `docs/OCA_MODULE_PLAN.md`)
2. Configure accounting chart of accounts
3. Set up company and users
4. Import master data

**Proceed to Phase 3 only after:**
- [ ] All verification checks pass
- [ ] Evidence pack committed
- [ ] Baseline backup verified
- [ ] Admin password set

---

**Document Control:**
- Created: 2026-01-29
- Author: Claude Code (Phase 2)
- Status: Ready for execution
- Archive after: First successful run
