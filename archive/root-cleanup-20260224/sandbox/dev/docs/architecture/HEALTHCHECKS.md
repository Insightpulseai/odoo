# Health Check System

Comprehensive health check system for validating all deployed services across dev/staging/prod environments.

## Overview

The health check system provides automated verification of:

- **Odoo** - Web interface, longpolling, database selector
- **Supabase** - Auth, PostgREST, Storage, RPC functions
- **PostgreSQL** - Connection, version, schema validation
- **n8n** - Health endpoints and availability
- **MCP Servers** - Health endpoints for model context protocol servers
- **Apache Superset** - Web interface and API
- **Vercel Surfaces** - Ops console, marketing site
- **GitHub** - API availability (optional)
- **Cloudflare** - Zone status (optional)

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r scripts/health/requirements.txt

# Or install system-wide
pip install requests pyyaml psycopg2-binary
```

### Basic Usage

```bash
# Check dev environment
python scripts/health/all_services_healthcheck.py --env dev --verbose

# Check staging with reports
python scripts/health/all_services_healthcheck.py --env staging \
  --json out/health/staging-report.json \
  --md out/health/staging-report.md

# Check production with custom timeout
python scripts/health/all_services_healthcheck.py --env prod --timeout 15
```

## Environment Variables

### Required for Core Services

| Variable | Service | Example |
|----------|---------|---------|
| `ODOO_BASE_URL` | Odoo | `http://localhost:8069` |
| `SUPABASE_URL` | Supabase | `https://xxx.supabase.co` |
| `N8N_BASE_URL` | n8n | `http://localhost:5678` |
| `SUPERSET_BASE_URL` | Superset | `http://localhost:8088` |
| `OPS_CONSOLE_URL` | Vercel | `https://console.example.com` |
| `MARKETING_URL` | Vercel | `https://www.example.com` |

### Optional Enhancement Variables

| Variable | Service | Purpose |
|----------|---------|---------|
| `ODOO_LONGPOLLING_URL` | Odoo | Check longpolling endpoint |
| `SUPABASE_ANON_KEY` | Supabase | Enhanced API checks |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase | Admin-level checks (use cautiously) |
| `POSTGRES_URL` | PostgreSQL | Direct database validation |
| `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` | PostgreSQL | Alternative connection method |
| `MCP_BASE_URLS` | MCP | Comma-separated server URLs |
| `SUPERSET_TOKEN` | Superset | API authentication |
| `GITHUB_TOKEN` | GitHub | API checks |
| `CLOUDFLARE_TOKEN`, `CLOUDFLARE_ZONE_ID` | Cloudflare | DNS/zone checks |

## Configuration by Environment

### Development (Local)

```bash
export ODOO_BASE_URL="http://localhost:8069"
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export N8N_BASE_URL="http://localhost:5678"
export SUPERSET_BASE_URL="http://localhost:8088"
export POSTGRES_URL="postgresql://odoo:odoo@localhost:5432/odoo"

python scripts/health/all_services_healthcheck.py --env dev --verbose
```

### Staging

```bash
export ODOO_BASE_URL="https://staging.insightpulseai.com"
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="eyJ..."
export N8N_BASE_URL="https://n8n-staging.insightpulseai.com"
export SUPERSET_BASE_URL="https://superset-staging.insightpulseai.com"
export OPS_CONSOLE_URL="https://console-staging.insightpulseai.com"
export MARKETING_URL="https://staging.insightpulseai.com"

python scripts/health/all_services_healthcheck.py --env staging \
  --json out/health/staging-report.json \
  --md out/health/staging-report.md
```

### Production

```bash
export ODOO_BASE_URL="https://erp.insightpulseai.com"
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="eyJ..."
export N8N_BASE_URL="https://n8n.insightpulseai.com"
export SUPERSET_BASE_URL="https://superset.insightpulseai.com"
export OPS_CONSOLE_URL="https://console.insightpulseai.com"
export MARKETING_URL="https://www.insightpulseai.com"

python scripts/health/all_services_healthcheck.py --env prod --timeout 15
```

## Output Formats

### Console Output

```
Environment: staging
Total checks: 15
✅ Passed: 12
❌ Failed: 1
⚠️  Warnings: 0
⏭️  Skipped: 2
```

### JSON Report

```json
{
  "environment": "staging",
  "timestamp": "2026-02-16T12:34:56.789Z",
  "total_checks": 15,
  "passed": 12,
  "failed": 1,
  "skipped": 2,
  "warnings": 0,
  "checks": [
    {
      "service": "odoo",
      "component": "web-login",
      "status": "OK",
      "message": "HTTP 200",
      "duration_ms": 123.4,
      "details": {
        "url": "https://erp.insightpulseai.com/web/login",
        "status_code": 200
      },
      "timestamp": "2026-02-16T12:34:56.789Z"
    }
  ],
  "metadata": {}
}
```

### Markdown Report

See `out/health/*.md` for formatted reports with:
- Summary table
- Service-by-service breakdown
- Status icons (✅❌⚠️⏭️)
- Response times
- Actionable recommendations

## Service-Specific Checks

### Odoo

| Check | Endpoint | Expected |
|-------|----------|----------|
| Web login | `/web/login` | 200 |
| DB selector (dev) | `/web/database/selector` | 200/303/404 |
| Longpolling | `${ODOO_LONGPOLLING_URL}` | 200/404/405 |

### Supabase

| Check | Endpoint | Expected |
|-------|----------|----------|
| Auth health | `/auth/v1/health` | 200 |
| PostgREST | `/rest/v1/` | 200/401/404 |
| Storage | `/storage/v1/bucket` | 200/401/403 |
| RPC smoke | `/rest/v1/rpc/version` | 200/404 |

### PostgreSQL

| Check | Query | Expected |
|-------|-------|----------|
| Connection | `SELECT version(), now();` | Success |
| Schemas | `SELECT schema_name FROM information_schema.schemata` | public, auth, storage |

### n8n

| Check | Endpoint | Expected |
|-------|----------|----------|
| Health | `/healthz` | 200 |
| Root (fallback) | `/` | 200/301/302 |

### MCP Servers

| Check | Endpoint | Expected |
|-------|----------|----------|
| Health | `/health` | 200/404 |

Note: MCP servers using stdio instead of HTTP will be marked as "SKIP: non-http".

### Apache Superset

| Check | Endpoint | Expected |
|-------|----------|----------|
| Health | `/health` | 200 |
| Login (fallback) | `/login` | 200 |
| API /me | `/api/v1/me` | 200 (requires token) |

### Vercel

| Check | Endpoint | Expected |
|-------|----------|----------|
| Ops console | `${OPS_CONSOLE_URL}` | 200-399 |
| Marketing | `${MARKETING_URL}` | 200-399 |

### GitHub (Optional)

| Check | Endpoint | Expected |
|-------|----------|----------|
| API root | `https://api.github.com` | 200 |

Requires: `GITHUB_TOKEN`

### Cloudflare (Optional)

| Check | Endpoint | Expected |
|-------|----------|----------|
| Zone status | `/client/v4/zones/${ZONE_ID}` | 200 |

Requires: `CLOUDFLARE_TOKEN`, `CLOUDFLARE_ZONE_ID`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All critical checks passed |
| 1 | One or more critical checks failed |

Use exit codes in CI:

```bash
if python scripts/health/all_services_healthcheck.py --env staging; then
  echo "Health check passed"
else
  echo "Health check failed"
  exit 1
fi
```

## Failure Modes & Fixes

### Odoo Not Reachable

**Symptoms:**
- `FAIL: Timeout after 10s` for Odoo checks

**Typical Fixes:**
1. Verify Odoo container is running: `docker ps | grep odoo`
2. Check Odoo logs: `docker logs odoo-web-1`
3. Verify network: `curl -I $ODOO_BASE_URL/web/login`
4. Check firewall rules if remote

### Supabase Auth Failure

**Symptoms:**
- `FAIL: HTTP 401` for Supabase checks

**Typical Fixes:**
1. Verify `SUPABASE_ANON_KEY` is correct
2. Check project status in Supabase dashboard
3. Verify project URL matches environment
4. Check RLS policies if using service role key

### PostgreSQL Connection Refused

**Symptoms:**
- `FAIL: connection refused` for Postgres checks

**Typical Fixes:**
1. Verify Postgres is running: `docker ps | grep postgres`
2. Check connection params: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`
3. Test connection: `psql $POSTGRES_URL -c "SELECT 1;"`
4. Verify pg_hba.conf allows connection

### n8n Unavailable

**Symptoms:**
- `FAIL: Timeout` for n8n checks

**Typical Fixes:**
1. Check n8n is running: `docker ps | grep n8n`
2. Verify base URL is correct
3. Check n8n logs: `docker logs n8n-1`
4. Ensure n8n has started (may take 30s+)

### Superset Startup Issues

**Symptoms:**
- `FAIL: HTTP 503` for Superset checks

**Typical Fixes:**
1. Wait for Superset initialization (can take 1-2 min)
2. Check Superset logs: `docker logs superset-1`
3. Verify database migration completed
4. Check Redis is running if configured

### Vercel Deploy Not Propagated

**Symptoms:**
- `FAIL: HTTP 404` for Vercel checks

**Typical Fixes:**
1. Check deployment status in Vercel dashboard
2. Verify domain configuration
3. Wait for CDN propagation (up to 60s)
4. Check DNS resolution: `dig $OPS_CONSOLE_URL`

## CI Integration

The health check is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions usage
- name: Install health check deps
  run: pip install -r scripts/health/requirements.txt

- name: Run health checks
  env:
    ODOO_BASE_URL: ${{ secrets.ODOO_BASE_URL }}
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
  run: |
    python scripts/health/all_services_healthcheck.py \
      --env staging \
      --json out/health/staging-report.json \
      --md out/health/staging-report.md

- name: Upload reports
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: health-check-reports
    path: out/health/
```

## Advanced Usage

### Custom Timeout

For slow networks or remote deployments:

```bash
python scripts/health/all_services_healthcheck.py --env prod --timeout 30
```

### Verbose Logging

For debugging:

```bash
python scripts/health/all_services_healthcheck.py --env dev --verbose
```

### Selective Checks

Filter by providing only relevant env vars:

```bash
# Only check Odoo and Supabase
export ODOO_BASE_URL="..."
export SUPABASE_URL="..."
# Other services will be skipped

python scripts/health/all_services_healthcheck.py --env dev
```

### Machine-Readable Output

Process JSON reports programmatically:

```bash
python scripts/health/all_services_healthcheck.py --env staging --json /tmp/report.json
jq '.checks[] | select(.status == "FAIL")' /tmp/report.json
```

## Security Considerations

- **Never commit secrets** to the repository
- Use environment variables for all credentials
- In CI, use GitHub Actions secrets or equivalent
- Prefer anon keys over service role keys when possible
- Rotate tokens regularly
- Review failed checks for potential security issues

## Maintenance

### Adding New Services

1. Add new check method to `HealthChecker` class
2. Call method in `run_all_checks()`
3. Document env vars in this file
4. Update CI workflow if needed

### Updating Check Logic

1. Modify relevant check method
2. Test locally across all environments
3. Update documentation if behavior changes
4. Consider backward compatibility

## Troubleshooting

### Script Errors

**Missing dependencies:**
```bash
pip install -r scripts/health/requirements.txt
```

**Permission denied:**
```bash
chmod +x scripts/health/all_services_healthcheck.py
```

**Python version:**
Requires Python 3.11+. Check with:
```bash
python --version
```

### False Positives

If a service is healthy but marked as failed:

1. Check expected status codes in script
2. Verify endpoint paths are correct
3. Increase timeout if network is slow
4. Check for redirects (301/302)

## Related Documentation

- [Infrastructure Overview](./INFRASTRUCTURE.md)
- [Service Architecture](./SERVICES.md)
- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [Troubleshooting Guide](../troubleshooting/COMMON_ISSUES.md)

---

**Last Updated:** 2026-02-16
**Maintainer:** DevOps Team
**Status:** Production Ready
