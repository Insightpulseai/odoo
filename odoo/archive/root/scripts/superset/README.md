# Superset Automation Suite

**Purpose**: API-driven Superset configuration (no UI) for production database connections, RBAC, and asset management.

**Philosophy**: Infrastructure as code, idempotent operations, CI/CD integration.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `common.sh` | Shared functions (login, CSRF, API helpers) | Sourced by other scripts |
| `add_or_update_database.sh` | Add or update database connection | Idempotent DB config |
| `test_database_connection.sh` | Test database connectivity | Smoke test after config |
| `import_assets.sh` | Import dashboards/datasets from ZIP | Asset deployment |

---

## Quick Start

### Local Usage (Manual)

**1. Configure Odoo DigitalOcean Managed Postgres**:

```bash
export SUPERSET_BASE_URL="https://superset.insightpulseai.com"
export SUPERSET_USERNAME="admin"  # TODO: Set actual admin user
export SUPERSET_PASSWORD="TODO"   # Store in secrets

export DB_NAME="odoo-db-sgp1-defaultdb"
export DB_URI="postgresql+psycopg2://doadmin:PASSWORD@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Optional settings (defaults shown)
export EXPOSE_IN_SQL_LAB="true"
export ALLOW_CSV_UPLOAD="false"
export ALLOW_DML="false"

./scripts/superset/add_or_update_database.sh
```

**Output**: `DB_ID=123` (save this)

**2. Test connectivity**:

```bash
export DB_ID="123"  # From previous step
./scripts/superset/test_database_connection.sh
```

**Expected**: JSON response with `{"message": "Connection looks good!"}`

**3. Import assets** (optional, requires `assets/superset/export.zip`):

```bash
export SUPERSET_ASSET_ZIP_PATH="assets/superset/export.zip"
./scripts/superset/import_assets.sh
```

---

### CI/CD Usage (GitHub Actions)

**Workflow**: `.github/workflows/superset-bootstrap.yml`

**Triggers**:
- Manual: `workflow_dispatch`
- Automatic: Push to `main` affecting `scripts/superset/`, `assets/superset/`, or workflow file

**Required Secrets** (set in GitHub repo):

| Secret | Value | Example |
|--------|-------|---------|
| `SUPERSET_BASE_URL` | Superset instance URL | `https://superset.insightpulseai.com` |
| `SUPERSET_USERNAME` | Admin/service user | `admin` |
| `SUPERSET_PASSWORD` | Password | (stored in GitHub secrets) |
| `SUPERSET_DB_NAME` | Database display name | `odoo-db-sgp1-defaultdb` |
| `SUPERSET_DB_URI` | SQLAlchemy connection URI | `postgresql+psycopg2://user:pass@host:port/db?sslmode=require` |

**SQLAlchemy URI Format**:

```
postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

**Examples**:

```bash
# DigitalOcean Managed Postgres
postgresql+psycopg2://doadmin:PASSWORD@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# Supabase Postgres (direct connection port 5432)
postgresql+psycopg2://postgres:PASSWORD@PROJECT_REF.supabase.co:5432/postgres?sslmode=require

# Supabase Postgres (pooler connection port 6543)
postgresql+psycopg2://postgres:PASSWORD@PROJECT_REF.supabase.co:6543/postgres?sslmode=require
```

---

## Database Configuration

### Recommended Settings

| Setting | Production | Development | Rationale |
|---------|------------|-------------|-----------|
| `expose_in_sqllab` | `true` | `true` | Allow SQL Lab queries |
| `allow_csv_upload` | `false` | `true` | CSV upload risk in prod |
| `allow_dml` | `false` | `false` | Read-only analytics |

**Security Best Practices**:
- ✅ Use read-only database role for Superset connection
- ✅ Enable `sslmode=require` for all Postgres connections
- ✅ Set `allow_dml=false` to prevent data modification via SQL Lab
- ✅ Keep `allow_csv_upload=false` in production to prevent data injection

---

## Common Workflows

### Add Multiple Databases

**Example**: Connect both Odoo Postgres and Supabase Postgres

```bash
# Database 1: Odoo DigitalOcean Managed Postgres
export DB_NAME="odoo-db-sgp1"
export DB_URI="postgresql+psycopg2://doadmin:PASSWORD@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
./scripts/superset/add_or_update_database.sh

# Database 2: Supabase Postgres (ops data)
export DB_NAME="supabase-ops"
export DB_URI="postgresql+psycopg2://postgres:PASSWORD@spdtwktxdalcfigzeqrz.supabase.co:5432/postgres?sslmode=require"
./scripts/superset/add_or_update_database.sh
```

### Update Existing Database URI

**Scenario**: Database password rotated

```bash
export DB_NAME="odoo-db-sgp1"  # Same name as existing
export DB_URI="postgresql+psycopg2://doadmin:NEW_PASSWORD@..."  # New password
./scripts/superset/add_or_update_database.sh
```

**Result**: Script detects existing database by name and updates URI

### Delete Database

**Manual deletion** (not included in automation, use Superset API directly):

```bash
# Get DB ID first
export DB_NAME="database-to-delete"
./scripts/superset/add_or_update_database.sh  # Outputs DB_ID

# Delete via API (create delete script if needed)
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRFToken: $CSRF" \
  "$SUPERSET_BASE_URL/api/v1/database/$DB_ID"
```

---

## Asset Management

### Export Dashboards/Datasets

**Via Superset UI** (recommended for initial export):
1. Navigate to dashboard or dataset
2. Click "..." menu → Export
3. Download ZIP file
4. Commit to `assets/superset/export.zip` in repo

**Via Superset API** (advanced):

```bash
# Export all dashboards
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRFToken: $CSRF" \
  "$SUPERSET_BASE_URL/api/v1/dashboard/export/?q=!(1,2,3)" \
  -o assets/superset/export.zip
```

### Import Assets (Automated)

**CI/CD**: Workflow automatically imports if `assets/superset/export.zip` exists

**Manual**:

```bash
export SUPERSET_ASSET_ZIP_PATH="assets/superset/export.zip"
./scripts/superset/import_assets.sh
```

---

## Troubleshooting

### Authentication Errors

**Symptom**: `401 Unauthorized` or `403 Forbidden`

**Solutions**:
- Verify `SUPERSET_USERNAME` and `SUPERSET_PASSWORD` are correct
- Check if user has `Admin` or `Alpha` role in Superset
- Ensure Superset is accessible at `SUPERSET_BASE_URL`

### Database Connection Fails

**Symptom**: `test_database_connection.sh` returns error

**Solutions**:
- Verify database host, port, username, password in URI
- Confirm `sslmode=require` is supported by database
- Check firewall allows Superset host IP to connect
- Test connection manually: `psql "$DB_URI"`

### CSRF Token Errors

**Symptom**: `CSRF token invalid` errors

**Solutions**:
- Ensure cookies are preserved across requests (handled by `common.sh`)
- Check Superset `WTF_CSRF_ENABLED` setting
- Verify `X-CSRFToken` header matches session

### Import Assets Fails

**Symptom**: `import_assets.sh` returns 400/500 error

**Solutions**:
- Verify ZIP file is valid Superset export (not corrupted)
- Check Superset version compatibility (export version ≈ import version)
- Enable `overwrite=true` to replace existing assets
- Review Superset logs for detailed error message

### Cloudflare Proxy Issues

**Symptom**: Login loops, session issues after proxying Superset via Cloudflare

**Solutions**:
- Verify `SUPERSET_WEBSERVER_PROTOCOL = 'https'` in Superset config
- Ensure `SUPERSET_WEBSERVER_DOMAIN = 'superset.insightpulseai.com'`
- Check `X-Forwarded-Proto`, `X-Forwarded-Host` headers are passed through
- Consider setting `SESSION_COOKIE_SECURE = True` and `SESSION_COOKIE_SAMESITE = 'Lax'`

**Reference**: See `spec/cloudflare-security/prd.md` for Superset proxying notes

---

## API Reference

### Superset REST API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/security/login` | POST | Authenticate and get access token |
| `/api/v1/security/csrf_token/` | GET | Get CSRF token for mutation requests |
| `/api/v1/database/` | GET | List databases (with filters) |
| `/api/v1/database/` | POST | Create new database |
| `/api/v1/database/{id}` | PUT | Update existing database |
| `/api/v1/database/{id}/test_connection` | POST | Test database connectivity |
| `/api/v1/assets/import/` | POST | Import dashboards/datasets from ZIP |

**Full API Docs**: `https://superset.insightpulseai.com/swagger/v1`

---

## Security Considerations

### Credentials Storage

**❌ Never commit**:
- Superset admin passwords
- Database connection URIs with embedded passwords
- API access tokens

**✅ Store in**:
- GitHub Actions secrets (CI/CD)
- Environment variables (local)
- Secret management tools (1Password, Vault, etc.)

### Database Permissions

**Recommended Database Role Permissions**:

```sql
-- Read-only analytics role (PostgreSQL)
CREATE ROLE superset_analytics WITH LOGIN PASSWORD 'secure_password';

-- Grant read-only access to specific schemas
GRANT CONNECT ON DATABASE your_database TO superset_analytics;
GRANT USAGE ON SCHEMA public TO superset_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_analytics;

-- Grant future table access
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO superset_analytics;
```

**Never use**:
- Database superuser/admin accounts
- Roles with `INSERT`, `UPDATE`, `DELETE`, `DROP` permissions
- Plaintext password storage

### Network Security

**Firewall Rules**:
- Whitelist Superset host IP on database firewall
- Require SSL/TLS connections (`sslmode=require`)
- Use private networking if Superset and DB are on same cloud provider

**Cloudflare Integration**:
- Superset proxied through Cloudflare (enabled in DNS SSOT)
- WAF protection active (see `spec/cloudflare-security/`)
- Rate limiting: 300 req/5min per user

---

## Integration with Infrastructure

### DNS SSOT

**Registry Entry** (`infra/dns/subdomain-registry.yaml`):

```yaml
- name: superset
  type: A
  service: apache_superset_bi
  port: 8088
  health_check: /health
  owner_system: "Apache Superset BI"
  cloudflare_proxied: true  # ✅ Enabled (commit b2b74b22)
  tls_mode: "Full (strict)"
  database: "DO managed PostgreSQL: odoo-db-sgp1/superset"
  status: active
```

**Health Check**: `https://superset.insightpulseai.com/health`

### Secret Management

**SSOT Registry** (`infra/secrets/registry.yaml`):

```yaml
# Currently not tracked (TODO: Add Superset credentials)
# Recommendation: Add SUPERSET_USERNAME and SUPERSET_PASSWORD to registry
```

**Action**: Consider adding Superset credentials to secret registry for rotation tracking

---

## Future Enhancements (TODO)

- [ ] Add `delete_database.sh` script for automated database removal
- [ ] Implement RBAC role seeding (Admin, Analyst, Viewer)
- [ ] Add dataset creation automation (SQL queries → datasets)
- [ ] Implement dashboard templating (parameterized dashboards)
- [ ] Add Superset credentials to `infra/secrets/registry.yaml`
- [ ] Create Grafana-style monitoring dashboard for Superset usage
- [ ] Integrate with CI/CD for automated asset deployment on merge

---

## References

- **Superset API Docs**: https://superset.apache.org/docs/api
- **SQLAlchemy Database URLs**: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
- **PostgreSQL Connection Strings**: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
- **Cloudflare Security Spec**: `spec/cloudflare-security/prd.md`
- **DNS SSOT Registry**: `infra/dns/subdomain-registry.yaml`

---

**Last Updated**: 2026-02-13
**Maintainer**: Infrastructure Team
**Status**: Production Ready
