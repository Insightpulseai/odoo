# Apache Superset Integration

Complete integration guide for Apache Superset with Odoo and Supabase PostgreSQL databases.

## Quick Start

### 1. Test Database Connections

**Using Bash script:**
```bash
./scripts/superset_db_connect.sh
```

**Using Python script:**
```bash
python3 scripts/superset_db_setup.py
```

Both scripts will:
- ✅ Test connectivity to Odoo PostgreSQL
- ✅ Test connectivity to Supabase PostgreSQL (direct + pooler)
- ✅ Generate SQLAlchemy URIs for Superset
- ✅ Check for required schemas

### 2. Add Databases to Superset

1. Open Superset: `http://localhost:8088`
2. Navigate to: **Data → Databases → + Database**
3. Select **PostgreSQL**
4. Paste connection URI from test scripts above
5. Click **Test Connection** → **Connect**

## Database Connections

### Odoo PostgreSQL (Development)

```
postgresql://odoo:odoo@localhost:5432/odoo_dev
```

**Use for:**
- Odoo operational data
- Project/task metrics
- User activity analytics
- Business intelligence dashboards

### Supabase PostgreSQL (Direct - Analytics)

```
postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

**Use for:**
- OPS schema analytics
- WAF event analysis
- Observability metrics
- Long-running analytics queries

### Supabase PostgreSQL (Pooler - Transactional)

```
postgresql://postgres.spdtwktxdalcfigzeqrz:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

**Use for:**
- High-frequency queries
- Real-time dashboards
- Transactional workloads

## Example Dashboards

### 1. OdooOps Overview Dashboard

**Metrics:**
- Total projects
- Active deployments
- Health score
- WAF posture score

**Charts:**
- Deployments over time (line chart)
- Projects by status (pie chart)
- Recent events (table)

**SQL Queries:**

```sql
-- Projects count
SELECT COUNT(*) as total_projects
FROM project_project
WHERE active = true;

-- Deployments by status
SELECT
    state,
    COUNT(*) as count
FROM project_task
WHERE project_id IN (SELECT id FROM project_project WHERE active = true)
GROUP BY state;
```

### 2. WAF Security Dashboard

**Metrics:**
- Threat events (24h)
- Blocked requests
- Top attack vectors
- Security score

**Charts:**
- Threats timeline (time series)
- Attack types (bar chart)
- Top IPs (table)
- Geographic distribution (map)

**SQL Queries (Supabase):**

```sql
-- Threat events last 24h
SELECT
    event_type,
    severity,
    COUNT(*) as count,
    MAX(created_at) as last_seen
FROM ops.waf_events
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type, severity
ORDER BY count DESC;
```

### 3. Observability Dashboard

**Metrics:**
- P50/P95/P99 latency
- Error rate
- Request throughput
- System health

**Charts:**
- Latency percentiles (time series)
- Error rate trend (line chart)
- Request volume (area chart)
- Service health (gauge)

**SQL Queries (Supabase):**

```sql
-- Latency percentiles
SELECT
    percentile_cont(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM ops.observability_metrics
WHERE created_at > NOW() - INTERVAL '1 hour';
```

## Integration with OdooOps Dashboard

### Embed Superset Charts in Next.js

**Install Superset SDK:**
```bash
cd web/odooops-dashboard
npm install @superset-ui/embedded-sdk
```

**Create API Route:**

```typescript
// app/api/superset/guest-token/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { dashboard_id } = await request.json();

  const supersetUrl = process.env.SUPERSET_URL || 'http://localhost:8088';
  const username = process.env.SUPERSET_USERNAME;
  const password = process.env.SUPERSET_PASSWORD;

  // 1. Login to Superset
  const loginRes = await fetch(`${supersetUrl}/api/v1/security/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, provider: 'db' }),
  });

  const { access_token } = await loginRes.json();

  // 2. Get guest token
  const guestRes = await fetch(`${supersetUrl}/api/v1/security/guest_token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({
      resources: [{ type: 'dashboard', id: dashboard_id }],
      rls: [],
      user: { username: 'guest', first_name: 'Guest', last_name: 'User' },
    }),
  });

  const guestToken = await guestRes.json();

  return NextResponse.json({ token: guestToken.token });
}
```

**Embed Component:**

```typescript
// components/SupersetDashboard.tsx
'use client';

import { embedDashboard } from '@superset-ui/embedded-sdk';
import { useEffect, useRef } from 'react';

export function SupersetDashboard({ dashboardId }: { dashboardId: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const getToken = async () => {
      const res = await fetch('/api/superset/guest-token', {
        method: 'POST',
        body: JSON.stringify({ dashboard_id: dashboardId }),
      });
      const { token } = await res.json();
      return token;
    };

    embedDashboard({
      id: dashboardId,
      supersetDomain: process.env.NEXT_PUBLIC_SUPERSET_URL || 'http://localhost:8088',
      mountPoint: ref.current,
      fetchGuestToken: getToken,
      dashboardUiConfig: {
        hideTitle: true,
        hideChartControls: false,
      },
    });
  }, [dashboardId]);

  return <div ref={ref} className="w-full h-[600px]" />;
}
```

**Use in Dashboard:**

```typescript
// app/observability/page.tsx
import { SupersetDashboard } from '@/components/SupersetDashboard';

export default function ObservabilityPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Observability</h1>
      <SupersetDashboard dashboardId="1" />
    </div>
  );
}
```

## Security Best Practices

### 1. Use Read-Only Users

**For Odoo:**
```sql
-- Create read-only user
CREATE USER superset_readonly WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE odoo_dev TO superset_readonly;
GRANT USAGE ON SCHEMA public TO superset_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_readonly;
```

**For Supabase:**
Use existing RLS policies or create a read-only role.

### 2. Store Credentials Securely

**Environment variables only:**
```bash
# .env (never commit)
SUPERSET_URL=http://localhost:8088
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=secure_password

ODOO_DB_PASSWORD=odoo_password
SUPABASE_DB_PASSWORD=supabase_password
```

### 3. Enable SSL Connections

**Supabase:** Always use `?sslmode=require`

**Odoo Production:** Configure SSL in PostgreSQL and use `?sslmode=require`

## Troubleshooting

### Connection Timeout

**Check network:**
```bash
nc -zv localhost 5432  # Odoo
nc -zv aws-0-us-east-1.pooler.supabase.com 5432  # Supabase
```

### Too Many Connections

**For Supabase:** Switch to pooler port 6543

**For Odoo:** Increase `max_connections` in `postgresql.conf`

### Permission Denied

**Check user permissions:**
```sql
-- Odoo
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_name='project_project';
```

## Documentation

- 📖 [Database Connections Guide](./DATABASE_CONNECTIONS.md)
- 📖 [Superset Official Docs](https://superset.apache.org/docs/intro)
- 📖 [Embedded SDK Docs](https://www.npmjs.com/package/@superset-ui/embedded-sdk)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./scripts/superset_db_connect.sh` | Test all database connections (bash) |
| `python3 scripts/superset_db_setup.py` | Test all database connections (python) |
| `http://localhost:8088` | Access Superset UI |
| `docs/superset/DATABASE_CONNECTIONS.md` | Full connection guide |

---

**Created:** 2026-02-14
**Status:** ✅ Ready to use
