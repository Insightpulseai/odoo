# Supabase Platform Kit Installation Verification

## Timestamp
2026-02-20 06:45+0800

## Implementation Status: COMPLETE

## Installation Summary

Successfully installed Supabase Platform Kit in the canonical host app (`web/ai-control-plane/`) via shadcn generator as documented.

## Files Created/Modified

### Total: 52 files changed, 5998 insertions(+), 21 deletions(-)

### Template Fix (Prerequisite)
- **templates/odooops-console/package.json**: Removed incorrect `@supabase/platform-kit-nextjs` npm dependency
  - **Why**: Platform Kit is NOT distributed via npm - only via shadcn generator
  - **Impact**: Unblocked pnpm workspace installation

### Tailwind CSS Setup (Prerequisite)
- **web/ai-control-plane/package.json**: Added tailwindcss, postcss, autoprefixer dev dependencies
- **web/ai-control-plane/tailwind.config.ts**: Created Tailwind configuration
- **web/ai-control-plane/postcss.config.js**: Created PostCSS configuration
- **web/ai-control-plane/app/globals.css**: Created with Tailwind directives (@tailwind base/components/utilities)
- **web/ai-control-plane/app/layout.tsx**: Added `import './globals.css'`

### shadcn Configuration
- **web/ai-control-plane/components.json**: Created shadcn configuration
  - Style: new-york
  - Base color: neutral
  - TSX: true
  - RSC: true
  - Icon library: radix
  - Registry: @supabase → https://supabase.com/ui/r/{name}.json

- **web/ai-control-plane/lib/utils.ts**: Created cn() utility function
- **Installed dependencies**: clsx, tailwind-merge

### Platform Kit Installation (52 files)

#### API Routes (2 files)
1. **app/api/supabase-proxy/[...path]/route.ts**: Management API proxy route
   - Purpose: Server-side proxy for Supabase Management API calls
   - Security: Management token never exposed to client
   - Required: Implement role checks + projectRef whitelist

2. **app/api/ai/sql/route.ts**: AI-powered SQL generation route
   - Purpose: SQL query generation assistance
   - Optional: Can be removed if not needed

#### Supabase Manager Components (8 files)
1. **components/supabase-manager/index.tsx**: Main manager dialog/drawer
2. **components/supabase-manager/auth.tsx**: Authentication management UI
3. **components/supabase-manager/database.tsx**: Database management UI
4. **components/supabase-manager/logs.tsx**: Logs viewer UI
5. **components/supabase-manager/secrets.tsx**: Secrets management UI
6. **components/supabase-manager/storage.tsx**: Storage management UI
7. **components/supabase-manager/users.tsx**: User management UI
8. **components/supabase-manager/suggestions.tsx**: Suggestions/recommendations UI

#### UI Components (16 shadcn/ui components)
- alert, badge, button, card, chart, command, dialog, drawer
- form, hover-card, input, label, popover, select, skeleton, switch
- table, toggle, toggle-group, tooltip

#### Hooks (8 files)
- hooks/use-auth.ts
- hooks/use-logs.ts
- hooks/use-run-query.ts
- hooks/use-secrets.ts
- hooks/use-storage.ts
- hooks/use-suggestions.ts
- hooks/use-tables.ts
- hooks/use-user-counts.ts

#### Utilities & Types (12 files)
- lib/management-api.ts (Management API client)
- lib/management-api-schema.d.ts (TypeScript types)
- lib/logs.ts (Log parsing utilities)
- lib/pg-meta/index.ts, lib/pg-meta/sql.ts, lib/pg-meta/types.ts (PostgreSQL metadata)
- lib/schemas/auth.ts, lib/schemas/secrets.ts (Zod schemas)
- contexts/SheetNavigationContext.tsx (Navigation context)

#### Helper Components (4 files)
- components/dynamic-form.tsx (Dynamic form builder)
- components/logo-supabase.tsx (Supabase logo SVG)
- components/results-table.tsx (Query results table)
- components/sql-editor.tsx (SQL editor component)

## Verification Checklist

### ✅ Installation Method Correct
- [x] Installed via `npx shadcn@latest add @supabase/platform-kit-nextjs` (NOT npm install)
- [x] shadcn generator successfully created 52 files
- [x] All components follow shadcn/ui patterns (vendored, not npm packages)

### ✅ Canonical Host App
- [x] Installed in `web/ai-control-plane/` (as documented in plan.md)
- [x] No other apps have Platform Kit installed
- [x] Template fixed to remove incorrect npm dependency

### ✅ Prerequisites Satisfied
- [x] Tailwind CSS installed and configured
- [x] shadcn configured with components.json
- [x] lib/utils.ts created with cn() utility
- [x] clsx and tailwind-merge installed

### ✅ Security Setup Required (Next Steps)
- [ ] Set SUPABASE_MANAGEMENT_API_TOKEN in .env.local (server-only)
- [ ] Implement proxy route security in app/api/supabase-proxy/[...path]/route.ts:
  - [ ] Add role/permission check (admin/ops only)
  - [ ] Add projectRef whitelist (deny-by-default)
  - [ ] Add audit logging (ops.run_events)
- [ ] Configure allowed Supabase project refs
- [ ] Test Management API proxy with valid token

### ✅ Documentation Alignment
- [x] Follows SDK_VS_PLATFORM_KIT.md guidance (shadcn generator, not npm)
- [x] Implements plan.md Platform Kit placement section
- [x] ai-control-plane confirmed as canonical host

## Installation Process

1. **Fixed template** (removed incorrect Platform Kit npm dependency)
2. **Installed Tailwind CSS** (`pnpm add -D tailwindcss postcss autoprefixer`)
3. **Created Tailwind config** (tailwind.config.ts, postcss.config.js, globals.css)
4. **Created shadcn config** (components.json, lib/utils.ts)
5. **Installed dependencies** (`pnpm add clsx tailwind-merge`)
6. **Ran Platform Kit generator** (`npx shadcn@latest add @supabase/platform-kit-nextjs`)
7. **Verified 52 files created** (API routes, components, hooks, types)

## Commit Hash
a52696a45

## Evidence
- logs/commit.log: Full commit with 52 file changes
- logs/diff-stat.log: 52 files changed, 5998 insertions(+), 21 deletions(-)
- logs/install-output.log: Platform Kit installation output
- logs/supabase-manager-files.log: List of Supabase Manager components

## Next Steps (Security Setup)

### 1. Get Management API Token
```bash
# From Supabase Dashboard → Settings → API
# Create Personal Access Token (PAT)
# Copy token to .env.local
```

### 2. Configure Environment
```bash
cd web/ai-control-plane
echo "SUPABASE_MANAGEMENT_API_TOKEN=sbp_..." >> .env.local
echo "ALLOWED_PROJECT_REFS=spdtwktxdalcfigzeqrz" >> .env.local
```

### 3. Implement Proxy Security
Edit `app/api/supabase-proxy/[...path]/route.ts`:
```typescript
// Add role check
const session = await getServerSession()
if (session?.user?.role !== 'admin') {
  return new Response('Unauthorized', { status: 401 })
}

// Add projectRef whitelist
const allowedRefs = process.env.ALLOWED_PROJECT_REFS?.split(',') || []
if (!allowedRefs.includes(projectRef)) {
  return new Response('Forbidden project', { status: 403 })
}

// Add audit logging
await supabase.from('ops.run_events').insert({
  run_id: crypto.randomUUID(),
  event_type: 'management_api_call',
  message: `User ${session.user.id} accessed ${path}`,
  metadata: { projectRef, path }
})
```

### 4. Test Installation
```bash
cd web/ai-control-plane
pnpm dev
# Visit http://localhost:3100
# Test Supabase Manager dialog
```

## Status
STATUS=COMPLETE

Platform Kit successfully installed in canonical host app (web/ai-control-plane/) following documented best practices:
1. Fixed incorrect npm dependency in template (prevented workspace installation)
2. Installed via shadcn generator (correct method, not npm)
3. Created 52 files (API routes, components, hooks, types)
4. Documented security setup requirements for next steps

**This installation demonstrates the correct distinction between:**
- ❌ WRONG: `npm install @supabase/platform-kit-nextjs` (doesn't work, not in registry)
- ✅ CORRECT: `npx shadcn@latest add @supabase/platform-kit-nextjs` (shadcn generator)
