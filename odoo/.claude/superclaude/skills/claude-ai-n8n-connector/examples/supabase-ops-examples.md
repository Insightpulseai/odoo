# Supabase Operations Examples

> **Tool**: `supabase_ops`
> **Purpose**: Execute SQL queries and RPC calls on Supabase PostgreSQL

---

## SQL Query Examples

### 1. Recent Task Completions

**Natural language**:
```
Show me tasks completed in the last 7 days
```

**Tool call**:
```json
{
  "operation": "sql",
  "query": "SELECT id, title, completed_at, assigned_to FROM tasks WHERE completed_at > NOW() - INTERVAL '7 days' ORDER BY completed_at DESC LIMIT 50"
}
```

---

### 2. User Activity Summary

**Natural language**:
```
Get user activity statistics for February 2026
```

**Tool call**:
```json
{
  "operation": "sql",
  "query": "SELECT user_id, COUNT(*) as actions, MAX(created_at) as last_active FROM user_activity WHERE created_at >= '2026-02-01' AND created_at < '2026-03-01' GROUP BY user_id ORDER BY actions DESC LIMIT 20"
}
```

---

### 3. Workflow Execution Logs

**Natural language**:
```
Find failed n8n workflow executions today
```

**Tool call**:
```json
{
  "operation": "sql",
  "query": "SELECT workflow_id, execution_id, error_message, created_at FROM workflow_executions WHERE status = 'error' AND created_at >= CURRENT_DATE ORDER BY created_at DESC LIMIT 100"
}
```

---

### 4. Data Sync Status

**Natural language**:
```
Check SSOT/SOR sync status for the last hour
```

**Tool call**:
```json
{
  "operation": "sql",
  "query": "SELECT sync_job_id, source, destination, records_synced, sync_status, started_at, completed_at FROM sync_jobs WHERE started_at > NOW() - INTERVAL '1 hour' ORDER BY started_at DESC"
}
```

---

### 5. Audit Log Query

**Natural language**:
```
Show all admin actions in the last 24 hours
```

**Tool call**:
```json
{
  "operation": "sql",
  "query": "SELECT user_id, action, resource_type, resource_id, metadata, created_at FROM audit_logs WHERE user_role = 'admin' AND created_at > NOW() - INTERVAL '24 hours' ORDER BY created_at DESC LIMIT 100"
}
```

---

## RPC Function Call Examples

### 1. Get Finance Summary

**Natural language**:
```
Generate a finance dashboard summary for this month
```

**Tool call**:
```json
{
  "operation": "rpc",
  "function_name": "get_finance_summary",
  "params": {
    "start_date": "2026-02-01",
    "end_date": "2026-02-29",
    "currency": "PHP"
  }
}
```

**Expected RPC function**:
```sql
CREATE OR REPLACE FUNCTION get_finance_summary(
  start_date DATE,
  end_date DATE,
  currency TEXT DEFAULT 'PHP'
)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_revenue', SUM(CASE WHEN type = 'revenue' THEN amount ELSE 0 END),
    'total_expenses', SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END),
    'net_income', SUM(CASE WHEN type = 'revenue' THEN amount ELSE -amount END)
  ) INTO result
  FROM financial_transactions
  WHERE transaction_date BETWEEN start_date AND end_date
    AND currency_code = currency;

  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

### 2. Calculate AR Aging

**Natural language**:
```
Calculate accounts receivable aging buckets
```

**Tool call**:
```json
{
  "operation": "rpc",
  "function_name": "calculate_ar_aging",
  "params": {
    "as_of_date": "2026-02-20"
  }
}
```

**Expected RPC function**:
```sql
CREATE OR REPLACE FUNCTION calculate_ar_aging(
  as_of_date DATE
)
RETURNS TABLE(
  bucket TEXT,
  amount NUMERIC,
  invoice_count INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    CASE
      WHEN days_overdue <= 0 THEN 'Current'
      WHEN days_overdue <= 30 THEN '1-30 days'
      WHEN days_overdue <= 60 THEN '31-60 days'
      WHEN days_overdue <= 90 THEN '61-90 days'
      ELSE 'Over 90 days'
    END as bucket,
    SUM(amount_residual) as amount,
    COUNT(*)::INTEGER as invoice_count
  FROM (
    SELECT
      invoice_id,
      amount_residual,
      (as_of_date - invoice_date_due)::INTEGER as days_overdue
    FROM invoices
    WHERE payment_state != 'paid'
      AND invoice_date_due <= as_of_date
  ) subquery
  GROUP BY bucket
  ORDER BY
    CASE bucket
      WHEN 'Current' THEN 1
      WHEN '1-30 days' THEN 2
      WHEN '31-60 days' THEN 3
      WHEN '61-90 days' THEN 4
      ELSE 5
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

### 3. Trigger Data Sync

**Natural language**:
```
Trigger an incremental sync from Supabase to Odoo for the invoices table
```

**Tool call**:
```json
{
  "operation": "rpc",
  "function_name": "trigger_sync_job",
  "params": {
    "source": "supabase",
    "destination": "odoo",
    "sync_type": "incremental",
    "table_name": "invoices"
  }
}
```

**Expected RPC function**:
```sql
CREATE OR REPLACE FUNCTION trigger_sync_job(
  source TEXT,
  destination TEXT,
  sync_type TEXT,
  table_name TEXT
)
RETURNS JSON AS $$
DECLARE
  job_id UUID;
BEGIN
  -- Insert sync job
  INSERT INTO sync_jobs (source, destination, sync_type, table_name, status)
  VALUES (source, destination, sync_type, table_name, 'pending')
  RETURNING id INTO job_id;

  -- Trigger n8n webhook via pg_notify
  PERFORM pg_notify('sync_trigger', json_build_object(
    'job_id', job_id,
    'source', source,
    'destination', destination,
    'sync_type', sync_type,
    'table_name', table_name
  )::TEXT);

  RETURN json_build_object(
    'job_id', job_id,
    'status', 'triggered'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

### 4. Get User Permissions

**Natural language**:
```
Check what permissions user ID 'abc123' has
```

**Tool call**:
```json
{
  "operation": "rpc",
  "function_name": "get_user_permissions",
  "params": {
    "user_id": "abc123"
  }
}
```

**Expected RPC function**:
```sql
CREATE OR REPLACE FUNCTION get_user_permissions(
  user_id TEXT
)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_agg(
    json_build_object(
      'resource', resource,
      'actions', actions,
      'granted_by', granted_by,
      'granted_at', granted_at
    )
  ) INTO result
  FROM user_permissions
  WHERE user_id = $1
    AND (expires_at IS NULL OR expires_at > NOW());

  RETURN COALESCE(result, '[]'::JSON);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## Advanced SQL Patterns

### 1. JSON Aggregation

**Query**: Aggregate workflow execution stats by workflow ID

```sql
SELECT
  workflow_id,
  json_build_object(
    'total_executions', COUNT(*),
    'success_rate', ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2),
    'avg_duration_ms', ROUND(AVG(duration_ms)),
    'last_execution', MAX(created_at)
  ) as stats
FROM workflow_executions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY workflow_id
ORDER BY workflow_id;
```

---

### 2. Window Functions

**Query**: Calculate rolling 7-day average of task completions

```sql
SELECT
  completion_date,
  tasks_completed,
  ROUND(AVG(tasks_completed) OVER (
    ORDER BY completion_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ), 2) as rolling_7day_avg
FROM (
  SELECT
    DATE(completed_at) as completion_date,
    COUNT(*) as tasks_completed
  FROM tasks
  WHERE completed_at > NOW() - INTERVAL '30 days'
  GROUP BY DATE(completed_at)
) daily_completions
ORDER BY completion_date DESC;
```

---

### 3. Common Table Expressions (CTEs)

**Query**: Find users with above-average activity

```sql
WITH activity_stats AS (
  SELECT
    user_id,
    COUNT(*) as action_count
  FROM user_activity
  WHERE created_at > NOW() - INTERVAL '7 days'
  GROUP BY user_id
),
avg_activity AS (
  SELECT AVG(action_count) as avg_actions
  FROM activity_stats
)
SELECT
  u.id,
  u.email,
  a.action_count,
  ROUND(100.0 * a.action_count / avg.avg_actions, 2) as pct_of_avg
FROM activity_stats a
JOIN users u ON u.id = a.user_id
CROSS JOIN avg_activity avg
WHERE a.action_count > avg.avg_actions
ORDER BY a.action_count DESC
LIMIT 20;
```

---

## Security Considerations

### Read-Only SQL Enforcement

**Tool restriction**: Only `SELECT` statements allowed

**Blocked operations**:
- ❌ `INSERT`, `UPDATE`, `DELETE`
- ❌ `CREATE`, `ALTER`, `DROP`
- ❌ `GRANT`, `REVOKE`

**Validation**: n8n workflow validates query before execution

---

### Row-Level Security (RLS)

**Scenario**: Users should only see their own tasks

**RLS Policy**:
```sql
CREATE POLICY "Users can view own tasks"
  ON tasks
  FOR SELECT
  USING (assigned_to = auth.uid());
```

**Effect**: Even if SQL query requests all tasks, Supabase filters by `auth.uid()`

---

### Function Security

**Best practices**:
1. Use `SECURITY DEFINER` for controlled privilege escalation
2. Validate all input parameters
3. Limit query complexity (row limits, timeouts)
4. Audit all RPC calls

**Example**:
```sql
CREATE OR REPLACE FUNCTION safe_get_user_data(
  target_user_id TEXT
)
RETURNS JSON AS $$
BEGIN
  -- Validate caller has permission
  IF NOT has_admin_role(auth.uid()) THEN
    RAISE EXCEPTION 'Insufficient permissions';
  END IF;

  -- Return user data
  RETURN (
    SELECT row_to_json(u)
    FROM users u
    WHERE u.id = target_user_id
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## Performance Tips

### 1. Use Indexes

**Before**:
```sql
SELECT * FROM tasks WHERE assigned_to = 'user123';  -- Slow (seq scan)
```

**Add index**:
```sql
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
```

**After**: Query uses index (fast)

---

### 2. Limit Result Sets

**❌ Unbounded query**:
```sql
SELECT * FROM workflow_executions;  -- Could return millions of rows
```

**✅ Bounded query**:
```sql
SELECT * FROM workflow_executions
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;
```

---

### 3. Avoid SELECT *

**❌ All columns**:
```sql
SELECT * FROM large_table LIMIT 100;  -- Fetches all 50 columns
```

**✅ Specific columns**:
```sql
SELECT id, name, created_at FROM large_table LIMIT 100;
```

---

## Common Supabase Tables (Example Schema)

| Table | Description | Common Columns |
|-------|-------------|----------------|
| `tasks` | User tasks and TODOs | id, title, assigned_to, completed_at |
| `user_activity` | Activity tracking | user_id, action, resource_type, created_at |
| `workflow_executions` | n8n execution logs | workflow_id, status, duration_ms, error_message |
| `sync_jobs` | SSOT/SOR sync tracking | source, destination, sync_type, records_synced |
| `audit_logs` | Security audit trail | user_id, action, resource_type, metadata |

---

*For more examples, see `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`*
