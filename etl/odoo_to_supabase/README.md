# Odoo → Supabase ETL (Logical Replication)

**Purpose**: One-way Change Data Capture (CDC) from Odoo PostgreSQL to Supabase PostgreSQL for analytics, AI memory, and cross-app integration.

**Architecture**:
```
Odoo PG (prod)  --logical replication-->  ETL (Rust)  --writes-->  Supabase PG
     │                                                                    │
     └── Source of Truth (ERP)                                           └── Analytics + AI Mirror
```

**Key Principles**:
1. **Odoo DB** = source of truth for ERP transactions (invoices, partners, projects)
2. **Supabase** = analytics mirror + AI memory (Superset, n8n, MCP, Vercel)
3. **GitHub** = source of truth for schema + ETL code (NOT data)
4. **One-way flow**: Odoo → Supabase, never uncontrolled Supabase → Odoo

---

## Architecture

### Data Flow

```
┌─────────────┐     Logical Replication    ┌───────────────┐
│  Odoo PG    │ ─────────────────────────▶ │ supabase/etl  │
│  (Source)   │     Publication: odoo_pub  │   (Rust CDC)  │
└─────────────┘                            └───────┬───────┘
                                                   │
                                                   │ Custom Postgres Writer
                                                   ▼
                                           ┌───────────────┐
                                           │  Supabase PG  │
                                           │  (Destination)│
                                           └───────┬───────┘
                                                   │
        ┌──────────────────────────────────────────┼──────────────────────────┐
        │                                          │                          │
        ▼                                          ▼                          ▼
┌──────────────┐                         ┌────────────────┐         ┌──────────────┐
│  Superset    │                         │  n8n Workflows │         │  MCP Memory  │
│ (Dashboards) │                         │  (Automation)  │         │   (AI Agent) │
└──────────────┘                         └────────────────┘         └──────────────┘
```

### Components

1. **Odoo Publication**: Defines which tables to replicate
2. **supabase/etl**: Rust-based CDC engine
3. **Custom Postgres Writer**: Transforms and writes to Supabase
4. **Supabase Schema**: Mirrors Odoo tables + adds analytics views

---

## Prerequisites

### 1. Odoo Database Configuration

Enable logical replication on Odoo PostgreSQL:

**On DigitalOcean Droplet** (odoo-erp-prod: 159.223.75.148):

```bash
ssh root@159.223.75.148

# Edit PostgreSQL config
vi /var/lib/postgresql/data/postgresql.conf

# Add/update:
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10
```

**Restart PostgreSQL**:
```bash
docker restart odoo-postgres-1  # or systemctl restart postgresql
```

### 2. Create Publication

Connect to Odoo database and create publication:

```sql
-- Connect to Odoo DB
psql -U odoo -d odoo_core

-- Create publication for selected tables
CREATE PUBLICATION odoo_pub_scout FOR TABLE
    account_move,
    account_move_line,
    res_partner,
    project_task,
    hr_expense,
    hr_expense_sheet;

-- Verify publication
SELECT * FROM pg_publication;
SELECT * FROM pg_publication_tables WHERE pubname = 'odoo_pub_scout';
```

### 3. Supabase Database Setup

**Apply memory schema** (if not already done):

```bash
cd ~/Documents/GitHub/odoo-ce
psql "$SUPABASE_URL" -f db/migrations/ipai_memory_schema.sql
```

**Create replication schema**:

```sql
-- Create schema for Odoo mirror
CREATE SCHEMA IF NOT EXISTS odoo_mirror;

-- Grant permissions
GRANT USAGE ON SCHEMA odoo_mirror TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA odoo_mirror TO postgres;
```

---

## Installation

### 1. Install Rust (if not already installed)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. Clone supabase/etl

```bash
cd ~/Documents/GitHub/odoo-ce/etl/odoo_to_supabase
git clone https://github.com/supabase/etl.git supabase-etl
cd supabase-etl
```

### 3. Build ETL

```bash
cargo build --release
```

---

## Configuration

### ETL Config (`etl-config.toml`)

```toml
[source]
type = "postgres"
host = "159.223.75.148"
port = 5432
database = "odoo_core"
user = "odoo"
password = "$ODOO_DB_PASSWORD"
publication = "odoo_pub_scout"

# Connection pool settings
max_connections = 10
idle_timeout = 300

[destination]
type = "postgres"
host = "db.spdtwktxdalcfigzeqrz.supabase.co"
port = 6543  # Supabase pooler port
database = "postgres"
user = "postgres"
password = "$SUPABASE_SERVICE_ROLE_KEY"
schema = "odoo_mirror"

# Write settings
batch_size = 1000
flush_interval = 5  # seconds

[mappings]
# Table mappings (1:1 at start)
account_move = "odoo_mirror.account_move"
account_move_line = "odoo_mirror.account_move_line"
res_partner = "odoo_mirror.res_partner"
project_task = "odoo_mirror.project_task"
hr_expense = "odoo_mirror.hr_expense"
hr_expense_sheet = "odoo_mirror.hr_expense_sheet"

[logging]
level = "info"
format = "json"
output = "stdout"

[metrics]
enabled = true
port = 9090
path = "/metrics"
```

### Environment Variables

Create `.env` file:

```bash
# Odoo Database
ODOO_DB_HOST=159.223.75.148
ODOO_DB_PORT=5432
ODOO_DB_NAME=odoo_core
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=<odoo-password>

# Supabase Database
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_POOLER_HOST=db.spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_POOLER_PORT=6543

# ETL Settings
ETL_LOG_LEVEL=info
ETL_BATCH_SIZE=1000
ETL_FLUSH_INTERVAL=5
```

### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  etl:
    build:
      context: ./supabase-etl
      dockerfile: Dockerfile
    container_name: odoo-supabase-etl
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./etl-config.toml:/app/config.toml:ro
      - etl-data:/app/data
    ports:
      - "9090:9090"  # Metrics endpoint
    networks:
      - etl-network
    depends_on:
      - prometheus
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9090/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: etl-prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9091:9090"
    networks:
      - etl-network

volumes:
  etl-data:
  prometheus-data:

networks:
  etl-network:
    driver: bridge
```

### Prometheus Config (`prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'odoo-supabase-etl'
    static_configs:
      - targets: ['etl:9090']
        labels:
          service: 'odoo-etl'
          env: 'production'
```

---

## Usage

### Start ETL

```bash
cd ~/Documents/GitHub/odoo-ce/etl/odoo_to_supabase

# Using Docker Compose
docker compose up -d

# Or direct binary
./supabase-etl/target/release/etl --config etl-config.toml
```

### Monitor ETL

```bash
# View logs
docker compose logs -f etl

# Check metrics
curl http://localhost:9090/metrics

# Prometheus UI
open http://localhost:9091
```

### Verify Replication

```sql
-- Connect to Supabase
psql "$SUPABASE_URL"

-- Check replicated tables
\dt odoo_mirror.*

-- Verify row counts
SELECT
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'odoo_mirror'
ORDER BY n_live_tup DESC;

-- Sample data
SELECT * FROM odoo_mirror.account_move LIMIT 5;
```

---

## Monitoring & Maintenance

### Key Metrics

**ETL Metrics** (Prometheus):
- `etl_records_processed_total` - Total records processed
- `etl_records_failed_total` - Failed records
- `etl_lag_seconds` - Replication lag
- `etl_batch_duration_seconds` - Batch processing time

**Postgres Metrics**:
```sql
-- Replication slot status
SELECT * FROM pg_replication_slots WHERE slot_name = 'odoo_pub_scout';

-- WAL lag
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots;
```

### Alerts

Configure alerts in Prometheus:

```yaml
# prometheus-alerts.yml
groups:
  - name: etl_alerts
    interval: 30s
    rules:
      - alert: ETLHighLag
        expr: etl_lag_seconds > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ETL replication lag exceeds 60 seconds"

      - alert: ETLFailedRecords
        expr: rate(etl_records_failed_total[5m]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High rate of ETL failures detected"
```

### Troubleshooting

**Replication slot not advancing**:
```sql
-- Check for inactive slots
SELECT * FROM pg_replication_slots WHERE active = false;

-- Drop and recreate slot if needed
SELECT pg_drop_replication_slot('odoo_pub_scout');
```

**High memory usage**:
```bash
# Reduce batch size in etl-config.toml
batch_size = 500  # down from 1000
```

**Connection timeouts**:
```bash
# Increase max_connections in source/destination configs
# Use Supabase pooler port (6543) instead of direct (5432)
```

---

## Integration Patterns

### 1. Superset Dashboards

**Create views on top of mirrored data**:

```sql
-- Create analytics view
CREATE VIEW odoo_mirror.v_invoice_summary AS
SELECT
    m.id,
    m.name as invoice_number,
    m.invoice_date,
    m.amount_total,
    p.name as partner_name
FROM odoo_mirror.account_move m
JOIN odoo_mirror.res_partner p ON m.partner_id = p.id
WHERE m.move_type IN ('out_invoice', 'out_refund');

-- Grant to Superset readonly role
GRANT SELECT ON odoo_mirror.v_invoice_summary TO superset_readonly;
```

### 2. n8n Workflows

**Use Supabase as data source** (not Odoo directly):

```javascript
// n8n HTTP Request node
{
  "method": "POST",
  "url": "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/odoo_mirror.get_pending_expenses",
  "headers": {
    "apikey": "{{$env.SUPABASE_ANON_KEY}}",
    "Authorization": "Bearer {{$env.SUPABASE_SERVICE_ROLE_KEY}}"
  }
}
```

### 3. MCP Memory Integration

**Link Odoo data to AI memory**:

```sql
-- Create trigger to add memory on invoice creation
CREATE FUNCTION odoo_mirror.on_invoice_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO ipai_memory.chunks (session_id, topic, content, importance)
    SELECT
        (SELECT id FROM ipai_memory.sessions WHERE agent_id = 'odoo-sync' ORDER BY started_at DESC LIMIT 1),
        'invoice-created',
        format('New invoice %s for %s: %s', NEW.name, NEW.partner_id, NEW.amount_total),
        4;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoice_to_memory
AFTER INSERT ON odoo_mirror.account_move
FOR EACH ROW EXECUTE FUNCTION odoo_mirror.on_invoice_insert();
```

---

## Deployment Checklist

- [ ] Odoo DB: Enable logical replication (`wal_level = logical`)
- [ ] Odoo DB: Create publication (`odoo_pub_scout`)
- [ ] Supabase: Apply memory schema (`ipai_memory_schema.sql`)
- [ ] Supabase: Create mirror schema (`odoo_mirror`)
- [ ] Install Rust toolchain
- [ ] Clone and build `supabase/etl`
- [ ] Configure `etl-config.toml` with credentials
- [ ] Create `.env` file with secrets
- [ ] Start ETL container (`docker compose up -d`)
- [ ] Verify replication (check row counts in Supabase)
- [ ] Configure Prometheus alerts
- [ ] Create Superset views on mirrored data
- [ ] Update n8n workflows to use Supabase
- [ ] Test end-to-end flow (Odoo → Supabase → Superset)

---

## Security

**Network Security**:
- Use VPN or SSH tunnel for Odoo → ETL connection
- Use Supabase pooler (port 6543) with TLS
- Never expose Odoo DB directly to internet

**Credentials**:
- Store in `.env` file (NOT tracked in Git)
- Use separate DB user with read-only access for ETL
- Rotate credentials quarterly

**RLS Policies** (Supabase):
```sql
-- Enable RLS on mirrored tables
ALTER TABLE odoo_mirror.account_move ENABLE ROW LEVEL SECURITY;

-- Policy: Only allow service role + analytics role
CREATE POLICY "Analytics access only" ON odoo_mirror.account_move
FOR SELECT
USING (auth.role() IN ('service_role', 'superset_readonly'));
```

---

## Performance Tuning

**Odoo DB**:
- Monitor WAL growth: `SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) FROM pg_replication_slots;`
- Keep publication limited to essential tables
- Use `ALTER PUBLICATION` to add/remove tables without downtime

**Supabase**:
- Create indexes on frequently queried columns
- Use partitioning for large tables
- Enable `pg_stat_statements` for query analysis

**ETL**:
- Tune `batch_size` and `flush_interval` based on throughput
- Monitor memory usage (aim for <500MB per stream)
- Use connection pooling (max 10 connections)

---

## References

- [Supabase ETL GitHub](https://github.com/supabase/etl)
- [Supabase Logical Replication Docs](https://supabase.com/docs/guides/database/postgres/setup-replication-external)
- [PostgreSQL Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [Prometheus Monitoring Best Practices](https://prometheus.io/docs/practices/naming/)

---

**Last Updated**: 2026-01-14
**Maintained By**: InsightPulse AI DevOps Team
