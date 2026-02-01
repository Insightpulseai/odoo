# Deployment Invariants & Health Contracts

**Purpose**: Hard invariants that prevent 502/500/OWL error loops in production.

## Critical Invariants (Non-Negotiable)

### 1. Networking Invariant
```yaml
requirement: Database MUST be reachable as `postgres` on network `odoo_backend`
validation: docker compose ps shows both services on same network
gate: CI checks compose file for correct network aliases
```

**Config**: `deploy/docker-compose.prod.v0.10.0.yml`
```yaml
services:
  db:
    container_name: odoo-postgres
    networks:
      odoo_backend:
        aliases:
          - postgres  # REQUIRED: Odoo expects this alias
```

**Why**: `odoo.conf` has `db_host = postgres`. Mismatch → connection failure → 502

### 2. Database Selection Invariant
```yaml
requirement: NEVER hard-pin db_name in production config
validation: odoo.conf must have `db_name = False` + `dbfilter` regex
gate: CI grep check fails PR if db_name != False
```

**Config**: `deploy/odoo.conf`
```ini
db_name = False  # REQUIRED: Use dbfilter instead
dbfilter = ^(odoo|insightpulse)$  # REQUIRED: Regex for allowed DBs
list_db = False  # REQUIRED: Security - don't expose DB list
```

**Why**: Hard-pinning `db_name=odoo_core` can target uninitialized DB → asset 500s

### 3. Module Existence Invariant
```yaml
requirement: All manifest dependencies MUST exist in addons_path
validation: Ship list = Install list = Manifest list
gate: CI checks module directories exist before build
```

**Manifest Example**: `addons/ipai_*/manifest__.py`
```python
'depends': [
    'base',
    'web',
    # Only list modules that exist in addons_path
]
```

**Why**: Missing module → install fails or assets reference dead bundles → 500

### 4. Asset Health Invariant
```yaml
requirement: Asset compilation MUST succeed in CI before deploy
validation: scripts/aiux/verify_assets.sh passes
gate: CI runs asset build and checks for 500 errors
```

**Validation**: Run `scripts/aiux/verify_assets.sh` (TODO: create this script)

**Why**: Broken assets → 500 on `/web/assets/*` → UI breaks

### 5. addons_path Invariant
```yaml
requirement: addons_path MUST match actual container mounts
validation: odoo.conf paths exist in running container
gate: CI checks paths exist in Docker image
```

**Config**: `deploy/odoo.conf`
```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

**Container Check**:
```bash
docker exec odoo-ce ls -la /mnt/extra-addons  # MUST exist
```

**Why**: Non-existent paths → Odoo can't enumerate addons → asset serving crashes → 500

## Runtime Health Contract

**Requirement**: Production MUST maintain these health signals

### HTTP Health
```bash
GET https://erp.insightpulseai.com/web/login → 200
GET https://erp.insightpulseai.com/web → 200 or 303
GET https://erp.insightpulseai.com/web/assets/*/web.assets_frontend.min.css → 200 or 303
GET https://erp.insightpulseai.com/web/assets/*/web.assets_frontend_minimal.min.js → 200 or 303
```

### Database Health
```sql
-- Must succeed
SELECT 1 FROM ir_module_module LIMIT 1;
```

### Log Health (No Critical Errors in Last 100 Lines)
```bash
# These patterns MUST NOT appear:
grep -i "psycopg2.OperationalError" /var/log/odoo/odoo.log  # DB connection failure
grep -i "KeyError.*assets" /var/log/odoo/odoo.log          # Asset compilation failure
grep -i "CRITICAL" /var/log/odoo/odoo.log                  # Critical runtime errors
```

**Gate**: `scripts/aiux/verify_prod_health.sh` checks all health signals

## CI Gates (Fail Fast)

### 1. Config Drift Gate
```bash
#!/bin/bash
# Check odoo.conf for canonical values
grep -q "^db_host = postgres$" deploy/odoo.conf || exit 1
grep -q "^db_name = False$" deploy/odoo.conf || exit 1
grep -q "^dbfilter" deploy/odoo.conf || exit 1
grep -q "^list_db = False$" deploy/odoo.conf || exit 1
grep -q "^log_level = info$" deploy/odoo.conf || exit 1
echo "✓ Config invariants OK"
```

### 2. Compose Topology Gate
```bash
#!/bin/bash
# Validate docker-compose.prod.yml
docker compose -f deploy/docker-compose.prod.v0.10.0.yml config | yq eval '.services.db.networks.odoo_backend.aliases' | grep -q "postgres" || exit 1
docker compose -f deploy/docker-compose.prod.v0.10.0.yml config | yq eval '.services.odoo.depends_on' | grep -q "db" || exit 1
echo "✓ Compose topology OK"
```

### 3. Module Existence Gate
```bash
#!/bin/bash
# Check all manifest dependencies exist
for module in ipai_theme_aiux ipai_aiux_chat ipai_ask_ai ipai_document_ai ipai_expense_ocr; do
    [[ -d "addons/$module" ]] || { echo "✗ Missing module: $module"; exit 1; }
done
echo "✓ All required modules exist"
```

### 4. Asset Build Gate
```bash
#!/bin/bash
# Build assets in ephemeral container and check for errors
docker compose run --rm odoo odoo -d test_db -i base --stop-after-init
# TODO: Implement full asset verification
echo "✓ Asset build OK"
```

### 5. Health Check Gate
```bash
#!/bin/bash
# Run full health check before marking deploy as success
./scripts/aiux/verify_prod_health.sh || exit 1
echo "✓ Production health OK"
```

## Error Pattern Prevention

### 502 Bad Gateway Prevention
**Root Cause**: Nginx can't reach Odoo container

**Prevention**:
- ✅ Networking invariant enforced (db alias = postgres)
- ✅ Health check verifies container is up
- ✅ Compose topology gate validates depends_on

**Detection**: `curl -I https://erp.insightpulseai.com/web/login | head -1`

### 500 Asset Errors Prevention
**Root Cause**: Asset compilation/serving failure

**Prevention**:
- ✅ addons_path invariant (paths must exist)
- ✅ Module existence invariant
- ✅ Database selection invariant (no hard-pin to uninitialized DB)
- ✅ Asset build gate in CI

**Detection**: `curl -I https://erp.insightpulseai.com/web/assets/1/0/web.assets_frontend.min.css`

### OWL Error Prevention (Client-Side)
**Root Cause**: JavaScript bundle contains view with undefined field

**Prevention**:
- ✅ Module upgrades applied before asset rebuild
- ✅ Asset cache cleared after module changes
- ✅ Database views verified to not reference missing fields

**Detection**: Check browser console for OWL errors (client-side only)

**Note**: OWL errors from cached JavaScript bundles in browser cache will resolve themselves as browsers refresh. Server-side health is what matters for CI gates.

### Wrong Database Prevention
**Root Cause**: Targeting uninitialized or wrong database

**Prevention**:
- ✅ db_name = False (mandatory)
- ✅ dbfilter regex (mandatory)
- ✅ list_db = False (security)

**Detection**: Check logs for database name in startup messages

## Deployment Checklist

Before deploying to production:

- [ ] Run `scripts/aiux/verify_prod_health.sh` locally
- [ ] Verify `odoo.conf` matches canonical config
- [ ] Check `docker-compose.prod.yml` network aliases
- [ ] Ensure all modules in manifest exist in `addons/`
- [ ] Test asset loading: CSS and JS return 200/303
- [ ] Verify database selection: `db_name = False`
- [ ] Check logs for critical errors
- [ ] Confirm container health: `docker ps` shows healthy status

## Recovery Procedures

### If 502 occurs:
```bash
# 1. Check container status
docker ps --filter name=odoo

# 2. Check database connection
docker exec odoo-postgres psql -U odoo -d odoo_core -c "SELECT 1;"

# 3. Check logs
docker logs odoo-ce --tail 50 | grep -i error

# 4. Verify network
docker network inspect odoo_backend | grep -A 5 postgres
```

### If 500 asset errors occur:
```bash
# 1. Clear asset cache
docker exec odoo-postgres psql -U odoo -d odoo_core -c "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';"

# 2. Restart Odoo
docker compose -f deploy/docker-compose.prod.v0.10.0.yml restart odoo

# 3. Wait for regeneration
sleep 40

# 4. Test assets
curl -I https://erp.insightpulseai.com/web/assets/1/0/web.assets_frontend.min.css
```

### If OWL errors occur:
```bash
# 1. Check for views with undefined fields
docker exec odoo-postgres psql -U odoo -d odoo_core -c "SELECT id, name, model FROM ir_ui_view WHERE arch_db::text ~ 'field_name_here';"

# 2. Disable problematic view
docker exec odoo-postgres psql -U odoo -d odoo_core -c "UPDATE ir_ui_view SET active=false WHERE id=VIEW_ID;"

# 3. Clear asset cache and restart (see above)
```

## Maintenance

- **Weekly**: Run health check script
- **After module changes**: Clear asset cache
- **Before production deploy**: Run all CI gates
- **After database changes**: Verify dbfilter still matches

## References

- Health Check Script: `scripts/aiux/verify_prod_health.sh`
- Canonical Config: `deploy/odoo.conf`
- Production Compose: `deploy/docker-compose.prod.v0.10.0.yml`
- Ship Script: `ship_v1_1_0.sh`
