# Supabase Integration – IPAI Sample Metrics

> **Pattern Reference**: This document describes the canonical pattern for mirroring
> Odoo 18 CE data to Supabase for Fluent-based dashboards and external analytics.

## Purpose

Mirror Odoo 18 CE custom metrics (`ipai.sample.metric`) into Supabase
for use by Fluent-based Scout dashboards and external analytics engines.

This pattern is designed to:
- Keep Odoo as the **source of truth** for business data
- Provide **low-latency reads** for React dashboards via Supabase
- Enable **real-time subscriptions** for live KPI updates
- Support **multi-tenant** analytics without Odoo load

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Flow Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Odoo 18 CE                     Supabase                        │
│   ┌──────────────────┐          ┌──────────────────┐            │
│   │ ipai.sample.metric│  sync   │ ipai.ipai_sample │            │
│   │ (PostgreSQL)     │ ──────► │ _metrics         │            │
│   │                  │ XML-RPC  │ (PostgreSQL+RLS) │            │
│   └──────────────────┘          └────────┬─────────┘            │
│          ▲                               │                       │
│          │ create/update                 │ select (REST/WS)      │
│          │                               ▼                       │
│   ┌──────────────────┐          ┌──────────────────┐            │
│   │ Odoo Backend UI  │          │ React + Fluent   │            │
│   │ (business users) │          │ (dashboards)     │            │
│   └──────────────────┘          └──────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layers

### 1. Odoo 18 CE / OCA (Source of Truth)

**Module**: `addons/ipai/ipai_sample_metrics/`

**Model**: `ipai.sample.metric`

- Business logic, validation rules
- PH-specific rules (if applicable)
- Cron seeders and generators
- Full CRUD via Odoo backend UI

**Key Files**:
- `models/sample_metric.py` - ORM model with API helpers
- `views/sample_metric_views.xml` - List/Form/Search views
- `security/ir.model.access.csv` - Access control

**API Methods** (callable via XML-RPC/JSON-RPC):
- `create_from_payload(payload)` - Create metric from dict
- `get_metrics(filters, limit)` - Read metrics with domain
- `export_to_supabase_payload(limit, since_date)` - Export for sync
- `get_sync_stats()` - Get count statistics

### 2. Supabase (PostgreSQL + RLS)

**Schema**: `ipai`

**Table**: `ipai.ipai_sample_metrics`

- Upserted from Odoo via sync script
- Row-level security for tenant isolation
- Exposed read-only to `authenticated` role
- Full access for `service_role` (sync scripts)

**Key Files**:
- `supabase/migrations/202601130001_IPAI_SAMPLE_METRICS.sql`

**Features**:
- Auto-updated `updated_at` timestamp
- Indexes for code, date, brand, store queries
- Seed data matching Odoo demo records

### 3. Sync Script (Bridge)

**Script**: `scripts/sync_ipai_sample_metrics_to_supabase.py`

- Fetches from Odoo via XML-RPC
- Upserts to Supabase using `odoo_id` as conflict key
- Supports incremental sync via `--since` flag
- Dry-run mode for testing

### 4. React + Fluent 2 (Dashboard)

**Location**: `apps/scout-dashboard/` (or similar)

- Uses `@supabase/supabase-js` client
- Reads from `ipai_sample_metrics` for KPIs, charts
- Real-time subscriptions for live updates
- AI prompt context (RAG source)

---

## Data Contracts

### Odoo → Supabase

The `export_to_supabase_payload` method returns records matching this schema:

```python
{
    "odoo_id": int,          # Primary sync key
    "name": str,             # Human-readable label
    "code": str,             # Technical code (e.g., "CONV_RATE")
    "date": str | None,      # ISO date (YYYY-MM-DD)
    "brand_id": int | None,  # res.partner.id
    "store_id": int | None,  # res.partner.id
    "value": float,          # Metric value
    "unit": str,             # "percent" | "count" | "amount"
    "is_alert": bool,        # Computed flag
    "notes": str,            # Optional notes
    "active": bool,          # Archive flag
}
```

### Supabase → React

TypeScript interface for frontend consumption:

```typescript
interface SampleMetric {
  id: number;
  odoo_id: number | null;
  name: string;
  code: string;
  date: string;
  brand_id: number | null;
  store_id: number | null;
  value: number;
  unit: "percent" | "count" | "amount";
  is_alert: boolean;
  notes: string | null;
  active: boolean;
  inserted_at: string;
  updated_at: string;
}
```

---

## Setup

### 1. Apply Supabase Migration

```bash
# Via Supabase CLI
supabase db push

# Or via SQL Editor
# Copy contents of supabase/migrations/202601130001_IPAI_SAMPLE_METRICS.sql
```

### 2. Configure Environment

```bash
# .env or export
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo_core"
export ODOO_USER="api-user@example.com"
export ODOO_PASSWORD="your-password"
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
```

### 3. Install Python Dependencies

```bash
pip install supabase
```

### 4. Run Initial Sync

```bash
# Full sync
python scripts/sync_ipai_sample_metrics_to_supabase.py

# Dry run first
python scripts/sync_ipai_sample_metrics_to_supabase.py --dry-run --verbose

# Incremental sync (last 7 days)
python scripts/sync_ipai_sample_metrics_to_supabase.py --since 2026-01-06
```

---

## React Integration

### Supabase Client Setup

```typescript
// src/lib/supabase.ts
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL!;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { persistSession: true },
  db: { schema: "ipai" },
});
```

### Data Hook

```typescript
// src/hooks/useSampleMetrics.ts
import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import type { SampleMetric } from "@/types";

export function useSampleMetrics(code?: string) {
  const [data, setData] = useState<SampleMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      let query = supabase
        .from("ipai_sample_metrics")
        .select("*")
        .eq("active", true);

      if (code) {
        query = query.eq("code", code);
      }

      const { data, error } = await query
        .order("date", { ascending: false })
        .limit(100);

      if (!cancelled) {
        if (error) {
          setError(error);
          setData([]);
        } else {
          setData(data ?? []);
        }
        setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [code]);

  return { data, loading, error };
}
```

### Dashboard Component

```tsx
// src/pages/MetricsDashboard.tsx
import { Card, Text, Spinner } from "@fluentui/react-components";
import { useSampleMetrics } from "@/hooks/useSampleMetrics";

export function MetricsDashboard() {
  const { data, loading, error } = useSampleMetrics("CONV_RATE");

  if (loading) return <Spinner label="Loading metrics..." />;
  if (error) return <Text>Error: {error.message}</Text>;

  const latest = data[0];

  return (
    <Card>
      <Text weight="semibold">Conversion Rate</Text>
      <Text size={600}>
        {latest ? `${latest.value.toFixed(1)}%` : "--"}
      </Text>
      {latest?.is_alert && (
        <Text style={{ color: "red" }}>⚠ Alert threshold exceeded</Text>
      )}
    </Card>
  );
}
```

---

## Extension Points

### Adding New Fields

1. **Odoo model** (`models/sample_metric.py`):
   ```python
   new_field = fields.Char(help="New field description")
   ```

2. **Supabase migration** (new file in `supabase/migrations/`):
   ```sql
   alter table ipai.ipai_sample_metrics
     add column new_field text;
   ```

3. **Export payload** (update `export_to_supabase_payload`):
   ```python
   payload.append({
       ...
       "new_field": r.new_field or "",
   })
   ```

4. **TypeScript interface** (update `SampleMetric`):
   ```typescript
   new_field: string | null;
   ```

### Adding New Modules

Repeat this pattern for other models:

1. Create Odoo module in `addons/ipai/ipai_<name>/`
2. Add `export_to_supabase_payload` method to model
3. Create Supabase migration in `supabase/migrations/`
4. Create sync script in `scripts/sync_ipai_<name>_to_supabase.py`
5. Add React hook and components

### Scheduled Sync

Configure via GitHub Actions, n8n, or cron:

```yaml
# .github/workflows/sync-supabase.yml
name: Sync Odoo → Supabase
on:
  schedule:
    - cron: "*/15 * * * *"  # Every 15 minutes
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install supabase
      - run: python scripts/sync_ipai_sample_metrics_to_supabase.py
        env:
          ODOO_URL: ${{ secrets.ODOO_URL }}
          ODOO_DB: ${{ secrets.ODOO_DB }}
          ODOO_USER: ${{ secrets.ODOO_USER }}
          ODOO_PASSWORD: ${{ secrets.ODOO_PASSWORD }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
```

---

## Monitoring

### Sync Health Check

```bash
# Check Odoo stats
curl -X POST https://erp.insightpulseai.com/xmlrpc/2/object \
  -d '...' | jq '.result'

# Check Supabase counts
supabase db execute --sql "
  select count(*) as total,
         count(*) filter (where is_alert) as alerts
  from ipai.ipai_sample_metrics
  where active = true;
"
```

### Alerting

Set up alerts for:
- Sync script failures (GitHub Actions notification)
- Large delta between Odoo and Supabase counts
- High alert metric counts

---

## Related Files

| File | Purpose |
|------|---------|
| `addons/ipai/ipai_sample_metrics/` | Odoo module (source of truth) |
| `supabase/migrations/202601130001_IPAI_SAMPLE_METRICS.sql` | Supabase table schema |
| `scripts/sync_ipai_sample_metrics_to_supabase.py` | Sync script |
| `apps/scout-dashboard/src/hooks/useSampleMetrics.ts` | React data hook |
| `agents/custom_module_auditor.md` | Module audit spec |

---

## Troubleshooting

### Sync Fails with Authentication Error

```
Odoo authentication failed
```

Check `ODOO_USER` has API access and correct password.

### RLS Policy Blocks Reads

```
permission denied for table ipai_sample_metrics
```

Ensure user is authenticated and table has correct RLS policies.

### Missing Data After Sync

1. Check Odoo has `active=True` records
2. Verify `odoo_id` uniqueness
3. Check for upsert conflicts

---

*Last updated: 2026-01-13*
