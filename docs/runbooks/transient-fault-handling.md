# Transient Fault Handling

## Why this matters

Azure Database for PostgreSQL Flexible Server drops connections during:

- **Planned maintenance** (patching, minor version upgrades)
- **Failover** (HA zone-redundant failover, typically 60-120s)
- **Throttling** (connection limit reached, CPU pressure)
- **Network blips** (transient Azure fabric issues)

All three Odoo containers (`ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`) share the same PostgreSQL server (`pg-ipai-odoo`). Without retry logic, a single transient fault cascades to all services simultaneously.

## Retry doctrine

### Strategy: exponential backoff with jitter

```
retry_delay = min(base_delay * 2^attempt + random_jitter, max_delay)
```

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `base_delay` | 0.5s | Fast first retry for transient blips |
| `max_delay` | 30s | Cap to avoid blocking request threads |
| `max_retries` | 5 | Fail fast after ~60s total (0.5 + 1 + 2 + 4 + 8 + jitter) |
| `jitter` | 0-1s random | Prevent thundering herd across web/worker/cron |

### Retry budget (aggregate limit)

Each container must enforce an aggregate retry budget to prevent collectively overwhelming PostgreSQL:

| Container | Max retries/minute | Rationale |
|-----------|-------------------|-----------|
| `ipai-odoo-dev-web` (4 workers) | 60 | Highest connection volume |
| `ipai-odoo-dev-worker` | 30 | Background jobs, lower urgency |
| `ipai-odoo-dev-cron` | 15 | Scheduled, can wait longer |

If the retry budget is exhausted, the container should enter a **cooldown period** (30s) before resuming retries. This prevents a recovery storm when PostgreSQL comes back online.

### What to retry

| Fault | Retry? | Notes |
|-------|--------|-------|
| Connection refused / reset | Yes | Typical during failover |
| SSL handshake failure | Yes | Transient during cert rotation |
| Query timeout | Conditional | Only for idempotent reads; never for writes mid-transaction |
| Authentication failure | No | Configuration error, not transient |
| Disk full / out of memory | No | Requires operator intervention |

### What never to retry

- **Write operations mid-transaction** — risk of duplicate side effects
- **Authentication errors** — wrong credentials won't self-heal
- **Schema errors** — missing table/column is a deployment issue

## Implementation paths

### Path A: Odoo `db_maxconn` + connection validation (minimal)

Odoo's connection pool (`psycopg2` pool, configured via `db_maxconn`) does not have built-in retry logic. The minimal intervention is:

1. Set `db_maxconn = 64` in `odoo.conf` (default is 64, verify it's not lower)
2. Enable connection validation: Odoo checks connection liveness before use (default behavior in recent versions)
3. Set PostgreSQL server-side `idle_in_transaction_session_timeout = 300000` (5 min) to reclaim leaked connections

### Path B: PgBouncer sidecar (recommended for production)

Deploy PgBouncer as a sidecar container in the ACA environment:

```
Odoo container → localhost:6432 (PgBouncer) ��� pg-ipai-odoo.postgres.database.azure.com:5432
```

Benefits:
- **Connection pooling** — reduces connection count to PostgreSQL (important for Flexible Server limits)
- **Health checking** — PgBouncer validates backend connections before handing them to Odoo
- **Transparent retry** — PgBouncer can reconnect to a new primary after failover without Odoo knowing
- **Query queueing** — during brief outages, queries queue in PgBouncer instead of failing immediately

Configuration:

```ini
[databases]
odoo = host=pg-ipai-odoo.postgres.database.azure.com port=5432 dbname=odoo

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3
server_check_delay = 10
server_check_query = SELECT 1
server_connect_timeout = 5
server_login_retry = 3
query_wait_timeout = 30
```

### Path C: Application-level retry middleware (for API/agent calls)

For FastAPI endpoints (`OCA/rest-framework`) and agent-to-Odoo API calls:

```python
import tenacity

@tenacity.retry(
    retry=tenacity.retry_if_exception_type((psycopg2.OperationalError, ConnectionError)),
    wait=tenacity.wait_exponential(multiplier=0.5, max=30) + tenacity.wait_random(0, 1),
    stop=tenacity.stop_after_attempt(5),
    before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
)
def execute_with_retry(cr, query, params):
    cr.execute(query, params)
```

## Verification

### Config check script

`scripts/ci/check_pg_resilience.sh` validates:

1. `db_maxconn` is set and >= 32
2. PostgreSQL `idle_in_transaction_session_timeout` is configured
3. If PgBouncer sidecar is deployed, its health endpoint responds

### Pipeline assertion

The prod-verify pipeline can include a transient fault resilience check:

```bash
# Verify PostgreSQL connection with timeout and retry behavior
PGCONNECT_TIMEOUT=5 psql "host=${PGHOST} port=${PGPORT} dbname=${PGDATABASE} user=${PGUSER} sslmode=require connect_timeout=5" -c "SELECT 1" 2>&1
```

## Reference

- [Azure Architecture Center: Transient fault handling](https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults)
- [Azure PostgreSQL Flexible Server: Connection handling best practices](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-connection-handling-best-practices)
- `config/azure/odoo.conf` — Odoo runtime config
- `infra/azure/front-door-routes.yaml` — health probe definitions
