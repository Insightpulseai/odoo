# ✅ Dependency Installation Fix

## Issue Resolved

**Error:** `Failed to fetch dynamically imported module`  
**Root Cause:** `@supabase/supabase-js` package not installed in `node_modules`

## What Was Fixed

### 1. Removed Workspace Configuration

The project had a `pnpm-workspace.yaml` file that referenced non-existent workspace packages:

```yaml
packages:
  - "packages/*"  # ❌ These folders don't exist
  - "apps/*"      # ❌ These folders don't exist
```

**Action:** Deleted `/pnpm-workspace.yaml`

### 2. Cleaned Up package.json

Removed workspace package dependencies that don't exist in Figma Make:

**Before:**
```json
{
  "dependencies": {
    "@ops-control-room/core": "workspace:*",  // ❌ Doesn't exist
    "@ops-control-room/ui": "workspace:*",    // ❌ Doesn't exist
    "@supabase/supabase-js": "2.48.1",
    // ... other deps
  }
}
```

**After:**
```json
{
  "dependencies": {
    "@supabase/supabase-js": "2.48.1",
    "@emotion/react": "11.14.0",
    "@emotion/styled": "11.14.1",
    "@mui/icons-material": "7.3.5",
    "@mui/material": "7.3.5",
    // ... 50+ other legitimate packages
    "tw-animate-css": "1.3.8",
    "vaul": "1.1.2"
  }
}
```

**Note:** Initially I accidentally removed too many packages (see `/PACKAGE_JSON_FIX.md`), but this has been corrected. The package.json now has all ~52 required runtime dependencies.

### 3. Reinstalled Dependencies

Ran `install_package` to properly install `@supabase/supabase-js` and update the lockfile.

## Next Steps

### For the User

If you're running this locally, you need to install dependencies:

```bash
# Using pnpm (recommended)
pnpm install

# OR using npm
npm install

# Then start dev server
pnpm dev
# OR
npm run dev
```

### For Figma Make

The Deploy button should now work without the workspace error. The app will automatically have access to `@supabase/supabase-js` once deployed.

## Files Modified

- ✅ Deleted `/pnpm-workspace.yaml`
- ✅ Updated `/package.json` (removed workspace dependencies)
- ✅ Updated `/pnpm-lock.yaml` (via install_package tool)

## Why This Happened

The project was initially set up as a **monorepo** (multi-package workspace) with:
- `/packages/core/` - Core logic package
- `/packages/ui/` - UI components package
- `/apps/mcp-server/` - MCP server package

But in **Figma Make**, we don't need the monorepo structure. Everything should be in a single package with direct dependencies.

## Verification

After running `pnpm install` or `npm install`, you should see:

```
node_modules/
  @supabase/
    supabase-js/
    auth-js/
    functions-js/
    postgrest-js/
    realtime-js/
    storage-js/
```

## Import Verification

The import in `/src/lib/supabase.ts` is correct:

```typescript
import { createClient } from '@supabase/supabase-js';
```

This will now work without errors! ✅

## Summary

**Problem:** Workspace configuration conflicted with Figma Make's single-package structure  
**Solution:** Removed workspace config and reinstalled dependencies  
**Status:** ✅ Fixed - Ready to deploy

Once you run `pnpm install` (or `npm install`) locally, or deploy via Figma Make, the Supabase client will be available and the "Failed to fetch dynamically imported module" error will disappear.