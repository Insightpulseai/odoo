# Schema Fix V2 Summary

## Problem (Second Error)

After the first fix, the application was encountering new errors:
```
Error loading runs: {
  "code": "PGRST205",
  "details": null,
  "hint": null,
  "message": "Could not find the table 'public.ops.runs' in the schema cache"
}
```

## Root Cause

Using `'ops.runs'` as a table name (string literal) was being interpreted by PostgREST as:
- Schema: `public`
- Table: `ops.runs` (a table with a dot in its name)

Instead of:
- Schema: `ops`
- Table: `runs`

## Solution: Use `.schema('ops')` Method

The correct approach for Supabase JS client is to use the `.schema()` method **before** `.from()`:

```typescript
// ❌ Wrong - treats 'ops.runs' as a table name in public schema
await supabase.from('ops.runs').select('*')

// ✅ Correct - uses ops schema, runs table
await supabase.schema('ops').from('runs').select('*')
```

## Changes Made

### 1. `/src/lib/runs.ts`
Updated all 11 functions to use `.schema('ops')` before `.from()`:

```typescript
// Before
await supabase.from('ops.sessions').insert(...)

// After  
await supabase.schema('ops').from('sessions').insert(...)
```

**Functions updated:**
- ✅ `createSession()`
- ✅ `listSessions()`
- ✅ `updateSessionStatus()`
- ✅ `createRun()`
- ✅ `getRun()`
- ✅ `listRuns()`
- ✅ `getRunEvents()`
- ✅ `getRunArtifacts()`
- ✅ `updateRunStatus()`

**Realtime subscriptions** already use correct syntax (schema as separate property):
```typescript
supabase.channel('...').on('postgres_changes', {
  schema: 'ops',  // ✅ Already correct
  table: 'runs',
})
```

### 2. `/src/app/App.tsx`
Updated template and run queries:

```typescript
// Before
await supabase.from('ops.run_templates').select('*')
await supabase.from('ops.runs').select('*')

// After
await supabase.schema('ops').from('run_templates').select('*')
await supabase.schema('ops').from('runs').select('*')
```

### 3. `/src/app/components/RunLane.tsx`
Updated runs query:

```typescript
// Before
await supabase.from('ops.runs').select('...')

// After
await supabase.schema('ops').from('runs').select('...')
```

### 4. `/src/lib/supabase.ts`
Updated connection check:

```typescript
// Before
await supabase.from('ops.runs').select('count')

// After
await supabase.schema('ops').from('runs').select('count')
```

## How `.schema()` Works

The `.schema()` method tells the Supabase client which PostgreSQL schema to query:

```typescript
// Query ops.runs table
supabase.schema('ops').from('runs')

// Query public.users table
supabase.schema('public').from('users')

// Default (if not specified) is public schema
supabase.from('users') // same as .schema('public').from('users')
```

## Verification

After these changes, all queries should work correctly:

```typescript
// ✅ Sessions
await supabase.schema('ops').from('sessions').select('*')

// ✅ Runs
await supabase.schema('ops').from('runs').select('*')

// ✅ Run events
await supabase.schema('ops').from('run_events').select('*')

// ✅ Artifacts
await supabase.schema('ops').from('artifacts').select('*')

// ✅ Run templates
await supabase.schema('ops').from('run_templates').select('*')
```

## Files Changed

- ✅ `/src/lib/runs.ts` - All 11 query functions updated
- ✅ `/src/app/App.tsx` - Templates and runs queries updated
- ✅ `/src/app/components/RunLane.tsx` - Runs query updated
- ✅ `/src/lib/supabase.ts` - Connection check updated

## Key Takeaway

When working with custom PostgreSQL schemas in Supabase:

1. **REST API queries:** Use `.schema('schema_name').from('table_name')`
2. **Realtime subscriptions:** Use `{ schema: 'schema_name', table: 'table_name' }`
3. **RPC calls:** Schema is inferred from function definition (no need to specify)

## Testing

After applying these changes, you should be able to:

1. ✅ Load sessions in Runboard tab
2. ✅ Load templates in Templates tab
3. ✅ Load runs in Runs tab
4. ✅ Create new sessions and runs
5. ✅ Subscribe to realtime updates
6. ✅ Execute runbooks via edge function

All schema errors should now be resolved! 🎉
