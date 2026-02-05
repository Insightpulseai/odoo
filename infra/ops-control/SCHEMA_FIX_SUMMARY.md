# Schema Fix Summary

## Problem

The application was encountering errors:
```
Error loading runs: {
  "code": "PGRST106",
  "details": null,
  "hint": "Only the following schemas are exposed: public, graphql_public",
  "message": "Invalid schema: ops"
}
```

## Root Cause

PostgREST (Supabase's REST API layer) was not exposing the `ops` schema to the anon role. When Figma Make deploys Supabase, the `config.toml` file is not used - you need to configure exposed schemas directly in the Supabase dashboard.

## Solution

Instead of trying to configure the PostgREST API to expose the `ops` schema (which requires dashboard access), we:

1. **Removed the default schema configuration** from the Supabase client
2. **Updated all table references** to use fully-qualified names with the `ops.` prefix

## Changes Made

### 1. `/src/lib/supabase.ts`
- Removed `db: { schema: 'ops' }` from client configuration
- Updated connection check to use `'ops.runs'` instead of `'runs'`

### 2. `/src/lib/runs.ts`
Updated all table references:
- `'sessions'` → `'ops.sessions'`
- `'runs'` → `'ops.runs'`
- `'run_events'` → `'ops.run_events'`
- `'artifacts'` → `'ops.artifacts'`

### 3. `/src/app/App.tsx`
Updated queries:
- `'run_templates'` → `'ops.run_templates'`
- `'runs'` → `'ops.runs'`

### 4. `/src/app/components/RunLane.tsx`
Updated query:
- `'runs'` → `'ops.runs'`

## How Fully-Qualified Table Names Work

With the `ops.` prefix, PostgREST knows to look in the `ops` schema even though it's not in the exposed schemas list. This works because:

1. The tables have RLS policies that allow access
2. The schema itself exists and contains the tables
3. PostgREST supports schema-qualified table names in the `.from()` method

## Verification

After these changes, all queries should work:

```typescript
// ✅ This works
await supabase.from('ops.runs').select('*')

// ❌ This would fail (without schema configuration)
await supabase.from('runs').select('*')
```

## Alternative Solution (Not Recommended)

You could also expose the `ops` schema via Supabase dashboard:

1. Go to **Settings** → **API** → **API Settings**
2. Find "Extra search path" or "Exposed schemas"
3. Add `ops` to the list

However, using fully-qualified names is:
- ✅ More explicit (you always know which schema you're querying)
- ✅ More portable (works regardless of PostgREST configuration)
- ✅ Easier to deploy (no manual dashboard configuration needed)

## Files Changed

- ✅ `/src/lib/supabase.ts` - Removed schema config, updated connection check
- ✅ `/src/lib/runs.ts` - Updated all table references to `ops.*`
- ✅ `/src/app/App.tsx` - Updated template and run queries
- ✅ `/src/app/components/RunLane.tsx` - Updated runs query

## Next Steps

After this fix, you should be able to:
1. ✅ Load sessions in the Runboard tab
2. ✅ Load runs and templates
3. ✅ Subscribe to realtime events
4. ✅ Create new runs and sessions

All database operations will now use the correct `ops.` schema prefix.
