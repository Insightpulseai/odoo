# Supabase UI Components

This directory contains wrapper components around Supabase UI Library and Supabase UI Platform Kit.

## Why wrappers (not direct imports)

- Single place to swap implementation if Supabase UI API changes
- Enforces consistent prop signatures across ops-console
- Avoids component sprawl — all Supabase-derived components live here

## Adoption contract

See `docs/ops/SUPABASE_EXAMPLES_UI_ADOPTION.md` for the full governance rules.

## Import convention

Always import from the barrel export, not from individual files:

```typescript
// ✅ correct
import { DataTable, StatusBadge } from '@/components/supabase-ui'

// ❌ wrong — imports internal file directly
import { DataTable } from '@/components/supabase-ui/DataTable'
```

## Adding a new component

1. Create `ComponentName.tsx` in this directory
2. Export from `index.ts`
3. Add to the "Allowed components" table in `docs/ops/SUPABASE_EXAMPLES_UI_ADOPTION.md`
4. Use only for the approved use cases listed in the adoption contract

## Current components

| Component | Source | Use case |
|-----------|--------|---------|
| _(none yet — scaffold)_ | — | — |

## Naming conventions

- Files: `PascalCase.tsx` (e.g., `DataTable.tsx`)
- Exports: named exports (no default exports)
- Props: extend the source component's prop type where possible

## Security reminder

Never use `service_role` or `SUPABASE_MANAGEMENT_API_TOKEN` in components here.
These are client-rendered components — only `anon` key data is safe.
