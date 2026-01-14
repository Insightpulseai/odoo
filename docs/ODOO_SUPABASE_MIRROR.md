# Odoo → Supabase Mirror Architecture

**Purpose**: Canonical reference for Odoo→Supabase logical replication pipeline

**Architecture**: One-way CDC (Change Data Capture) from Odoo PostgreSQL to Supabase PostgreSQL for analytics, AI memory, and cross-app integration.

---

## Quick Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| **Mirror Schema** | `db/migrations/odoo_mirror_schema.sql` | Indexes, views, RPC functions, AI triggers |
| **ETL Config** | `etl/odoo_to_supabase/README.md` | Complete deployment guide |
| **ETL Environment** | `etl/odoo_to_supabase/.env.example` | Credential template |
| **Verification Script (SQL)** | `scripts/verify-etl-replication.sql` | Verify replication + views + memory |
| **Verification Script (Bash)** | `scripts/verify-etl-health.sh` | Check ETL container health |

---

## Architecture Overview

```
┌─────────────────┐                            ┌─────────────────┐
│  Odoo PG (prod) │  Logical Replication       │  Supabase PG    │
│  159.223.75.148 │ ────────────────────────▶  │  spdtwktxdal... │
│                 │  Publication: odoo_pub     │                 │
│  Source of      │                            │  Analytics +    │
│  Record (ERP)   │                            │  AI Mirror      │
└─────────────────┘                            └────────┬────────┘
                                                        │
        ┌───────────────────────────────────────────────┼──────────────────┐
        │                                               │                  │
        ▼                                               ▼                  ▼
┌──────────────┐                              ┌─────────────┐    ┌──────────────┐
│  Superset    │                              │  n8n        │    │  MCP Memory  │
│ (Dashboards) │                              │ (Workflows) │    │  (AI Agent)  │
└──────────────┘                              └─────────────┘    └──────────────┘
```

---

## Core Principles

1. **Odoo PG = source of truth for ERP data** (invoices, partners, projects, expenses)
2. **Supabase PG = analytics + AI mirror** (Superset, n8n, MCP, Vercel)
3. **GitHub = source of truth for schema + ETL code** (NOT data)
4. **One-way flow**: Odoo → Supabase (never uncontrolled Supabase → Odoo)

---

## Components

### 1. Odoo Publication

**Location**: Odoo PostgreSQL (159.223.75.148:5432/odoo_core)

**Publication Name**: `odoo_pub_scout`

**Tables Replicated**:
- `account_move` (invoices)
- `account_move_line` (invoice lines)
- `res_partner` (customers/vendors)
- `project_task` (tasks)
- `hr_expense` (expenses)
- `hr_expense_sheet` (expense reports)

**Setup**:
```sql
-- On Odoo DB
CREATE PUBLICATION odoo_pub_scout FOR TABLE
    account_move,
    account_move_line,
    res_partner,
    project_task,
    hr_expense,
    hr_expense_sheet;
```

### 2. ETL Engine

**Framework**: [supabase/etl](https://github.com/supabase/etl) (Rust-based CDC)

**Location**: `etl/odoo_to_supabase/`

**Configuration**: `etl-config.toml` (see `.env.example` for credentials)

**Deployment**: Docker Compose with Prometheus monitoring

**Key Features**:
- Batch processing (1000 records per batch)
- Automatic retry logic
- Metrics endpoint (http://localhost:9090/metrics)
- Connection pooling (max 10 connections)

### 3. Mirror Schema

**Location**: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)

**Schema**: `odoo_mirror.*`

**Enhancements** (defined in `db/migrations/odoo_mirror_schema.sql`):

#### Indexes (15 total)
- `idx_account_move_partner` - Invoice partner lookup
- `idx_account_move_date` - Invoice date filtering
- `idx_account_move_type` - Invoice type filtering
- `idx_account_move_state` - Invoice state filtering
- `idx_res_partner_name` - Partner name search
- `idx_res_partner_vat` - Partner VAT lookup
- `idx_project_task_deadline` - Task deadline queries
- `idx_hr_expense_date` - Expense date filtering
- And 7 more...

#### Analytics Views (5 total)
- `v_invoice_summary` - Invoice summary with partner details
- `v_expense_summary` - Expense summary with employee and sheet details
- `v_task_summary` - Project task summary with stage and priority
- `v_revenue_by_partner` - Revenue analysis by partner
- `v_expense_by_employee` - Expense analysis by employee

#### RPC Functions (3 total)
- `get_pending_expenses(limit)` - For n8n approval workflows
- `get_overdue_tasks(limit)` - For Mattermost alerts
- `get_revenue_trends(months)` - For BI dashboards

#### AI Memory Integration
- `on_invoice_insert()` - Trigger to auto-add invoice events to `ipai_memory.chunks`
- Links Odoo data to AI agent memory for context-aware operations

#### Security
- Role grants: `superset_readonly` (SELECT on all tables/views)
- Role grants: `n8n_service` (EXECUTE on all functions)
- RLS ready (optional per-security-policy enforcement)

---

## Integration Patterns

### Superset Dashboards

**Connection**:
- Type: PostgreSQL
- Host: `db.spdtwktxdalcfigzeqrz.supabase.co`
- Port: 6543 (pooler)
- Database: `postgres`
- User: `superset_readonly`
- Schema: `odoo_mirror`

**Usage**:
```sql
-- Use analytics views, not raw tables
SELECT * FROM odoo_mirror.v_invoice_summary
WHERE invoice_date >= '2025-01-01';

SELECT * FROM odoo_mirror.v_revenue_by_partner
ORDER BY net_revenue DESC
LIMIT 10;
```

### n8n Workflows

**Connection**: Use Supabase RPC functions (not Odoo directly)

**Example Workflow** (Pending Expense Approvals):
```javascript
// n8n HTTP Request node
{
  "method": "POST",
  "url": "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/odoo_mirror.get_pending_expenses",
  "headers": {
    "apikey": "{{$env.SUPABASE_ANON_KEY}}",
    "Authorization": "Bearer {{$env.SUPABASE_SERVICE_ROLE_KEY}}"
  },
  "body": {
    "p_limit": 20
  }
}
```

### MCP Memory Server

**Configuration**: `~/.mcp/config.json`

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_BACKEND": "postgres",
        "POSTGRES_URL": "postgresql://postgres:[PASSWORD]@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres"
      }
    }
  }
}
```

**Usage**: AI agents query `ipai_memory.*` which includes auto-generated invoice signals from `odoo_mirror.*`

### Vercel Apps

**Server-Side API** (Next.js):
```typescript
// app/api/invoices/route.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET() {
  const { data } = await supabase
    .from('odoo_mirror.v_invoice_summary')
    .select('*')
    .order('invoice_date', { ascending: false })
    .limit(10);

  return Response.json(data);
}
```

---

## Verification

### SQL Verification (Supabase)

Run `scripts/verify-etl-replication.sql`:

```bash
cd ~/Documents/GitHub/odoo-ce
psql "$SUPABASE_URL" -f scripts/verify-etl-replication.sql
```

**Expected Output**:
- All 6 base tables with row_count > 0
- All 5 analytics views populated
- RPC functions return data without errors
- AI memory chunks exist (if trigger enabled)
- 15 indexes present
- Role permissions granted

### ETL Health Check

Run `scripts/verify-etl-health.sh`:

```bash
cd ~/Documents/GitHub/odoo-ce
./scripts/verify-etl-health.sh
```

**Expected Output**:
- ETL container running
- Metrics endpoint responding
- Replication lag <60 seconds
- Prometheus monitoring active
- .env configuration complete

---

## Execution Rules for Agents

**DO**:
- Use analytics views (`odoo_mirror.v_*`) for dashboards and queries
- Use RPC functions for n8n workflows and API integrations
- Query `ipai_memory.*` for AI agent context
- Update schema via `db/migrations/odoo_mirror_schema.sql`
- Update ETL config via `etl/odoo_to_supabase/README.md`

**DO NOT**:
- Write directly to `odoo_mirror.*` tables from app code (ETL owns the mirror)
- Query raw `odoo_mirror.*` base tables (use views instead)
- Create implicit Supabase → Odoo sync (violates one-way principle)
- Store secrets in GitHub (use `.env` files only)

---

## Monitoring & Maintenance

### Key Metrics (Prometheus)

Access: http://localhost:9091

**Metrics to Watch**:
- `etl_records_processed_total` - Total records replicated
- `etl_records_failed_total` - Failed records (should be near zero)
- `etl_lag_seconds` - Replication lag (target: <60s)
- `etl_batch_duration_seconds` - Processing time per batch

### Alerts

**High Lag** (>60s for 5 minutes):
```bash
# Check ETL logs
docker compose -f etl/odoo_to_supabase/docker-compose.yml logs etl

# Verify Odoo DB replication slot
ssh root@159.223.75.148
psql -U odoo -d odoo_core -c "SELECT * FROM pg_replication_slots WHERE slot_name = 'odoo_pub_scout';"
```

**Failed Records** (>10 per 5 minutes):
```bash
# Check ETL error logs
docker compose -f etl/odoo_to_supabase/docker-compose.yml logs etl | grep ERROR

# Verify Supabase schema compatibility
psql "$SUPABASE_URL" -c "\d odoo_mirror.account_move"
```

### Maintenance Tasks

**Weekly**:
- Review ETL metrics for anomalies
- Check Supabase storage usage
- Verify analytics views are up-to-date

**Monthly**:
- Rotate credentials (Odoo DB password, Supabase keys)
- Review and optimize slow queries
- Archive old Prometheus metrics

**Quarterly**:
- Audit RLS policies (if enabled)
- Review and update analytics views
- Performance tuning (batch size, connection pool)

---

## Troubleshooting

### Replication Lag

**Symptom**: `etl_lag_seconds` >60

**Diagnosis**:
```sql
-- On Odoo DB
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots
WHERE slot_name = 'odoo_pub_scout';
```

**Fix**:
- Reduce batch size in `etl-config.toml`
- Increase ETL resources (CPU/memory)
- Check network connectivity between Odoo and ETL

### Missing Data

**Symptom**: Row counts in Supabase don't match Odoo

**Diagnosis**:
```bash
# Compare row counts
psql -U odoo -d odoo_core -c "SELECT COUNT(*) FROM account_move;"
psql "$SUPABASE_URL" -c "SELECT COUNT(*) FROM odoo_mirror.account_move;"
```

**Fix**:
- Check ETL logs for errors
- Verify publication includes all tables
- Restart ETL to trigger full sync

### AI Memory Not Populating

**Symptom**: `ipai_memory.chunks` has no invoice signals

**Diagnosis**:
```sql
-- Check if trigger exists
SELECT * FROM pg_trigger WHERE tgname = 'invoice_to_memory';

-- Check trigger function
\df odoo_mirror.on_invoice_insert
```

**Fix**:
- Enable trigger in `odoo_mirror_schema.sql` (currently commented out)
- Verify `ipai_memory` schema exists
- Check session creation for 'odoo-sync' agent

---

## References

- **ETL Framework**: https://github.com/supabase/etl
- **Supabase Replication**: https://supabase.com/docs/guides/database/postgres/setup-replication-external
- **PostgreSQL Logical Replication**: https://www.postgresql.org/docs/current/logical-replication.html
- **AI Memory Schema**: `db/migrations/ipai_memory_schema.sql`
- **Mirror Schema**: `db/migrations/odoo_mirror_schema.sql`
- **ETL Config**: `etl/odoo_to_supabase/README.md`

---

**Last Updated**: 2026-01-14
**Maintained By**: InsightPulse AI DevOps Team
