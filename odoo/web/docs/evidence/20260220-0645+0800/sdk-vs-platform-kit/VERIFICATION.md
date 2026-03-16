# SDK vs Platform Kit Clarification Verification

## Timestamp
2026-02-20 06:45+0800

## Implementation Status: COMPLETE

## Verification Checklist

### ✅ Plan names exactly one canonical Platform Kit host app
- [x] Canonical host declared: `web/ai-control-plane/`
- [x] Plan includes "Supabase Platform Kit Placement" section
- [x] Installation method specified: `npx shadcn@latest add @supabase/platform-kit-nextjs`
- [x] Purpose clarified: Ops/admin console for project management (control plane)

### ✅ Docs clearly distinguish SDK vs Platform Kit
- [x] Created comprehensive guide: `docs/supabase/SDK_VS_PLATFORM_KIT.md` (232 lines)
- [x] SDK (data plane) vs Platform Kit (control plane) comparison table
- [x] Installation methods clearly different: npm install vs shadcn generator
- [x] Explains shadcn's role: distribution/installation mechanism for Platform Kit
- [x] Security sections for both SDK and Platform Kit
- [x] Installation checklists for both approaches
- [x] Common mistakes section to prevent confusion

### ✅ No package changes in this PR
- [x] Pure documentation/policy clarification
- [x] No package.json modifications
- [x] No code changes in Next.js apps
- [x] Changes limited to: docs/ and spec/ directories

### ✅ Security note is explicit
- [x] Management API token server-only requirement documented
- [x] Proxy route permission checks required (role + projectRef whitelist)
- [x] Example proxy route security code provided
- [x] Audit logging requirements specified
- [x] RLS vs Management API security models contrasted

## Files Changed Summary

| File | Lines Added | Purpose |
|------|-------------|---------|
| docs/supabase/SDK_VS_PLATFORM_KIT.md | 232 | Comprehensive SDK vs Platform Kit distinction guide |
| spec/odoo-ee-parity-seed/plan.md | +22 | Platform Kit placement section with canonical host |

**Total**: 2 files changed, 232 insertions(+)

## Key Clarifications Documented

### 1. Installation Method Distinction
- **SDK**: `npm install @supabase/supabase-js @supabase/ssr`
- **Platform Kit**: `npx shadcn@latest add @supabase/platform-kit-nextjs`

### 2. Purpose Distinction
- **SDK**: Data plane (Auth/RLS/DB/Storage/Realtime) for end-user applications
- **Platform Kit**: Control plane (project management UI) for ops consoles

### 3. shadcn's Role
- Platform Kit uses shadcn as a **distribution/installation mechanism**
- Not "installing a Supabase client" - it's scaffolding management UI + proxy routes
- shadcn generator installs: UI components, hooks, server proxy routes, optional AI SQL route

### 4. Canonical Host App
- **Declared**: `web/ai-control-plane/`
- **Verified**: Directory exists and is a Next.js app (package.json, next.config.js, tsconfig.json present)
- **Policy**: Platform Kit MUST be installed in exactly one app (control plane surface containment)

### 5. Security Model
- **SDK**: Anon key (client) + Service role (server with audit trail)
- **Platform Kit**: Management API token (server-only, never exposed to client)
- **Proxy routes**: Must enforce role checks + projectRef whitelist

## Commit Hash
65350e41f

## Evidence
- logs/commit.log: Full commit details with diff stats
- logs/diff-stat.log: 2 files changed, 232 insertions(+)
- logs/host-app-verification.log: Verification that web/ai-control-plane/ exists

## Status
STATUS=COMPLETE

SDK vs Platform Kit distinction fully documented with:
1. Comprehensive guide (232 lines) explaining both approaches
2. Canonical host app declared (web/ai-control-plane/)
3. Security models for both documented
4. Common mistakes section to prevent future confusion
5. Installation checklists for both SDK and Platform Kit

This clarification prevents agents from confusing:
- npm install (SDK) with shadcn generator (Platform Kit)
- Data plane (end-user apps) with control plane (ops console)
- Client-side token (anon key) with server-side token (Management API)
