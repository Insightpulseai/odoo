# Supabase Best Practices Integration

> **Source**: [supabase/agent-skills](https://github.com/supabase/agent-skills)
> **Applied to**: InsightPulse AI Odoo project (`spdtwktxdalcfigzeqrz`)
> **Last Updated**: 2026-02-13

---

## Overview

This document applies official Supabase Postgres best practices to our production setup, focusing on connection management for Edge Functions, security/RLS for multi-environment isolation, and query optimization.

**Project Context**:
- **Supabase Project**: `spdtwktxdalcfigzeqrz`
- **Edge Functions**: 42 functions (using `supabase/functions/_shared/env.ts` resolver)
- **Environment Isolation**: STAGE__/PROD__ prefixed secrets on single project
- **Primary Use Case**: n8n workflows, task bus, external integrations (NOT Odoo's main database)

---

## 🔌 Connection Management (CRITICAL)

### Problem Statement

Postgres connections consume 1-3MB RAM each. Direct connections from Edge Functions create scalability bottlenecks:
- **Without pooling**: 500 concurrent users = 500 active connections = database crash
- **With pooling**: 500 concurrent users = 10 pooled connections = sustainable load

### Recommended Configuration

**Connection Pool Sizing**:
```
max_connections = (CPU cores × 2) + spindle_count
```

For typical Supabase project (4 cores): **~10 pooled connections**

**Pool Modes**:

| Mode | Use Case | Edge Function Fit |
|------|----------|-------------------|
| **Transaction** | Stateless requests (recommended) | ✅ Most Edge Functions |
| **Session** | Prepared statements, temp tables | ⚠️ Only if needed |

### Edge Function Best Practices

```typescript
// ✅ CORRECT: Use Supabase client (auto-pooled)
import { createClient } from '@supabase/supabase-js'
import { getEnvSecret } from '../_shared/env.ts'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = getEnvSecret('SUPABASE_SERVICE_ROLE_KEY')

const supabase = createClient(supabaseUrl, supabaseKey)
const { data, error } = await supabase.from('tasks').select('*')
```

```typescript
// ❌ WRONG: Direct Postgres connections
import { Client } from 'postgres'

const client = new Client({
  host: 'db.project.supabase.co',
  port: 5432,  // Direct connection, no pooling!
  // ...
})
```

**Connection String Usage**:
- **Direct (port 5432)**: Only for migrations, admin tasks
- **Pooler (port 6543)**: Default for all Edge Functions and application code

### Verification

```bash
# Check current connection count
supabase db pool check --project-ref spdtwktxdalcfigzeqrz

# Monitor active connections
supabase db logs --project-ref spdtwktxdalcfigzeqrz | grep "connection"
```

---

## 🛡️ Security & RLS (CRITICAL)

### Multi-Environment Isolation Strategy

Our single-project setup uses **application-level** environment prefixing (STAGE__/PROD__) for secrets. Database-level isolation requires RLS policies for data segregation.

**Recommended RLS Pattern**:

```sql
-- 1. Enable RLS on all tables
alter table tasks enable row level security;
alter table tasks force row level security;  -- Prevent owner bypass

-- 2. Environment-based policies
create policy "staging_isolation" on tasks
  for all
  to authenticated
  using (
    environment = 'staging'
    and auth.jwt() ->> 'environment' = 'staging'
  );

create policy "prod_isolation" on tasks
  for all
  to authenticated
  using (
    environment = 'prod'
    and auth.jwt() ->> 'environment' = 'prod'
  );
```

**Service Role Bypass** (for Edge Functions):

Edge Functions using `SUPABASE_SERVICE_ROLE_KEY` **bypass RLS by default**. Implement application-level checks:

```typescript
// Edge Function pattern with environment validation
import { getEnvSecret, getEnvironment } from '../_shared/env.ts'

const environment = getEnvironment() // 'staging' or 'prod'

// Explicit environment filtering in queries
const { data, error } = await supabase
  .from('tasks')
  .select('*')
  .eq('environment', environment)  // ✅ Manual filter required
```

### Authentication Integration

```typescript
// User-scoped RLS (for authenticated requests)
const supabase = createClient(supabaseUrl, anonKey)
  .auth.setSession({ access_token, refresh_token })

// RLS policy automatically applies using auth.uid()
const { data } = await supabase.from('user_data').select('*')
// Only returns rows where user_id = auth.uid()
```

### Verification

```sql
-- Test RLS policy
set role authenticated;
set request.jwt.claims to '{"sub": "user-id", "environment": "staging"}';

select * from tasks;  -- Should only return staging rows

reset role;
```

---

## ⚡ Query Performance

### Missing Index Detection

```sql
-- Find queries missing indexes (pg_stat_statements extension required)
select
  query,
  calls,
  total_exec_time,
  mean_exec_time
from pg_stat_statements
where query not like '%pg_stat%'
order by mean_exec_time desc
limit 10;
```

### Index Recommendations for Common Edge Function Queries

**Task Queue Pattern**:
```sql
-- Frequent query: fetch pending tasks by environment
create index idx_tasks_environment_status
  on tasks(environment, status)
  where status = 'pending';  -- Partial index for active records only
```

**N+1 Query Prevention**:
```typescript
// ❌ WRONG: N+1 queries
const tasks = await supabase.from('tasks').select('id')
for (const task of tasks.data) {
  const { data } = await supabase.from('logs').select('*').eq('task_id', task.id)
}

// ✅ CORRECT: Single join query
const tasks = await supabase
  .from('tasks')
  .select(`
    *,
    logs (*)
  `)
```

### EXPLAIN ANALYZE Usage

```sql
-- Add to any slow query for performance diagnosis
explain (analyze, buffers, verbose)
select * from tasks where environment = 'prod' and status = 'pending';

-- Look for:
-- - Seq Scan (missing index)
-- - High execution time
-- - Many buffer reads
```

---

## 📊 Schema Design

### Data Type Optimization

```sql
-- ✅ CORRECT: Appropriate types for environment flag
create table tasks (
  id uuid primary key default gen_random_uuid(),
  environment text not null check (environment in ('staging', 'prod')),  -- Constrained
  status text not null check (status in ('pending', 'processing', 'completed', 'failed')),
  created_at timestamptz default now(),
  payload jsonb  -- JSONB for indexed JSON queries
);

-- ❌ WRONG: Oversized types
create table tasks (
  id varchar(255),  -- UUID as varchar wastes space
  environment varchar(50),  -- No constraint validation
  payload text  -- TEXT prevents JSON indexing
);
```

### Foreign Key Index Rule

**Every foreign key MUST have an index** (Postgres doesn't auto-create them):

```sql
-- ✅ CORRECT: Index on FK column
create table task_logs (
  id uuid primary key,
  task_id uuid references tasks(id) on delete cascade
);
create index idx_task_logs_task_id on task_logs(task_id);  -- Required!

-- ❌ WRONG: FK without index (slow deletes/joins)
create table task_logs (
  id uuid primary key,
  task_id uuid references tasks(id) on delete cascade
);
-- Missing index = full table scan on every join/cascade delete
```

### Lowercase Identifier Convention

```sql
-- ✅ CORRECT: Lowercase, underscores
create table user_sessions (
  user_id uuid,
  session_token text
);

-- ❌ WRONG: Mixed case requires quoting
create table "UserSessions" (
  "UserId" uuid,  -- Now you must always quote: select * from "UserSessions"
  "SessionToken" text
);
```

---

## 🔍 Monitoring & Diagnostics

### Essential Queries

**Active Connections**:
```sql
select count(*), state
from pg_stat_activity
group by state;
```

**Long-Running Queries**:
```sql
select pid, now() - query_start as duration, query
from pg_stat_activity
where state != 'idle'
  and now() - query_start > interval '1 minute'
order by duration desc;
```

**Table Bloat (requires VACUUM)**:
```sql
select
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  n_dead_tup as dead_tuples
from pg_stat_user_tables
where n_dead_tup > 1000
order by n_dead_tup desc;
```

### Supabase Dashboard Monitoring

1. **Database → Logs**: Real-time query performance
2. **Database → Reports**: Slow queries, missing indexes
3. **Database → Roles**: Connection pool status

---

## 🚀 Edge Function Optimization Checklist

**Before Deploying Edge Functions**:

- [ ] Uses Supabase client (not direct Postgres connection)
- [ ] Implements environment filtering (`eq('environment', getEnvironment())`)
- [ ] Avoids N+1 queries (use joins/batch operations)
- [ ] Handles connection errors gracefully
- [ ] Includes error logging for diagnostics
- [ ] Tests with realistic concurrent load
- [ ] Validates RLS policies (if using anon/authenticated keys)
- [ ] Indexes exist for all WHERE/JOIN columns
- [ ] Uses partial indexes for status/flag columns

---

## 📚 Reference

**Official Supabase Agent Skills**:
- Repository: https://github.com/supabase/agent-skills
- Skill: `supabase-postgres-best-practices`
- Version: 1.1.0 (MIT License)

**Related Internal Docs**:
- `docs/security/SECRET_MANAGEMENT.md` - SSOT secret registry
- `docs/security/ENV_SECRET_PREFIXING.md` - Environment isolation policy
- `supabase/functions/_shared/env.ts` - Runtime environment resolver

**Key References**:
- [Connection Pooling](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/conn-pooling.md)
- [RLS Basics](https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/references/security-rls-basics.md)
- [Query Performance](https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices/references)

---

**Last Validated**: 2026-02-13
**Validation Command**: `supabase db pool check --project-ref spdtwktxdalcfigzeqrz`
