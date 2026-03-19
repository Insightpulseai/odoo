# RLS Policy Templates

Templates for Row-Level Security policies. **DO NOT EXECUTE** — apply after review.

---

## Assumptions

- Tenant identifier: JWT claim `tenant_id`
- Pattern: `current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id'`
- Service role bypasses RLS by design

---

## 1. Tenant Isolation (SELECT)

```sql
CREATE POLICY tenant_select ON <schema>.<table>
  FOR SELECT
  TO authenticated
  USING (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );
```

---

## 2. Tenant Isolation (INSERT)

```sql
CREATE POLICY tenant_insert ON <schema>.<table>
  FOR INSERT
  TO authenticated
  WITH CHECK (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );
```

---

## 3. Tenant Isolation (UPDATE)

```sql
CREATE POLICY tenant_update ON <schema>.<table>
  FOR UPDATE
  TO authenticated
  USING (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  )
  WITH CHECK (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );
```

---

## 4. Tenant Isolation (DELETE)

```sql
CREATE POLICY tenant_delete ON <schema>.<table>
  FOR DELETE
  TO authenticated
  USING (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );
```

---

## 5. Role-Based Override (Finance Admin)

```sql
CREATE POLICY finance_admin_all ON <schema>.<table>
  FOR ALL
  TO authenticated
  USING (
    (current_setting('request.jwt.claims', true)::jsonb ->> 'user_role') = 'finance_admin'
  )
  WITH CHECK (
    (current_setting('request.jwt.claims', true)::jsonb ->> 'user_role') = 'finance_admin'
  );
```

---

## 6. Owner-Only Policy

```sql
CREATE POLICY owner_only ON <schema>.<table>
  FOR ALL
  TO authenticated
  USING (
    user_id = auth.uid()
  )
  WITH CHECK (
    user_id = auth.uid()
  );
```

---

## 7. Service Role Bypass

Service role (`service_role`) bypasses RLS by design in Supabase. No explicit policy needed.

For admin migrations and background tasks, use service role key.

---

## 8. Combined Tenant + Role Pattern

```sql
-- Enable RLS
ALTER TABLE expense.expense_reports ENABLE ROW LEVEL SECURITY;

-- Tenant scoped read
CREATE POLICY expense_reports_tenant_select
  ON expense.expense_reports
  FOR SELECT
  USING (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );

-- Tenant scoped write
CREATE POLICY expense_reports_tenant_write
  ON expense.expense_reports
  FOR INSERT, UPDATE, DELETE
  USING (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  )
  WITH CHECK (
    tenant_id = (current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id')::uuid
  );

-- Finance admin override
CREATE POLICY expense_reports_finance_admin
  ON expense.expense_reports
  FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::jsonb ->> 'user_role') = 'finance_admin'
  );
```

---

## Notes

- Replace `<schema>.<table>` before applying
- If tenant resolution is via `core.app_user`, use subquery:
  ```sql
  USING (tenant_id = (SELECT tenant_id FROM core.app_user WHERE id = auth.uid()))
  ```
- Review existing policies on `public.expense_reports` and map exact logic
- Test in staging before production

---

## Role Mapping

| Role | Schemas | Tables | Privileges |
|------|---------|--------|------------|
| finance_manager | expense, finance | expense_reports, expenses, monthly_close_tracker | SELECT, INSERT, UPDATE |
| scout_viewer | scout_*, gold | transactions, docs, doc_chunks | SELECT only |
| scout_admin | scout_* | All | ALL |
| project_manager | projects | projects, tasks, budgets | SELECT, INSERT, UPDATE |
