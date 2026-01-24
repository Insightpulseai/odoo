# Supabase Preview Branches Configuration Diagnosis

**Date**: 2026-01-24 14:34 UTC
**Issue**: Supabase Preview Branches comment shows "ignored / no changes"
**Root Cause**: Dashboard misconfiguration - watching `supabase/supabase/` instead of `supabase/`
**Resolution**: Replaced with repo-owned CI preview workflow

## Findings

### Repository Structure (Correct)
```
supabase/
├── config.toml           ✓ Present
├── migrations/           ✓ 88 SQL files
├── functions/            ✓ 38 Edge Functions
├── seeds/                ✓ Present
└── .supabase-preview-config.json  ✓ Added
```

### Configuration
- **Project Ref**: `spdtwktxdalcfigzeqrz`
- **Repo Supabase Directory**: `supabase/`
- **Dashboard Expected Setting**: `supabase/`
- **Dashboard Actual Setting**: `supabase/supabase/` (MISCONFIGURED)

## Solution Implemented

Instead of fixing dashboard settings (UI-only, not automatable), implemented a **repo-owned CI preview workflow** that:

1. Spins up ephemeral Supabase local stack
2. Applies all migrations via `supabase db reset`
3. Runs smoke queries to validate schema
4. Uploads logs as workflow artifacts

This is fully deterministic and doesn't depend on dashboard configuration.

## Changes Shipped

### Commit 1: `bb03daf`
- `supabase/.supabase-preview-config.json` - Documents expected integration settings
- `scripts/ci/check_supabase_preview_config.sh` - CI gate to detect misconfiguration

### Commit 2: `6b254a1`
- `scripts/ci/supabase_preview.sh` - Main preview script (ephemeral local stack)
- `scripts/ci/needs_supabase_ci_preview.sh` - Change detection helper
- `.github/workflows/supabase-preview-ci.yml` - GitHub Actions workflow
- `.gitignore` - Added `.ci_artifacts/`

## Verification

The workflow triggers automatically on PRs that change `supabase/` directory.

To test locally (requires Supabase CLI):
```bash
supabase --version
./scripts/ci/supabase_preview.sh
```

## Workflow Trigger Paths

```yaml
on:
  pull_request:
    paths:
      - "supabase/**"
      - ".github/workflows/supabase-preview-ci.yml"
      - "scripts/ci/supabase_preview.sh"
```

## Dashboard Fix (Optional)

If you still want hosted Preview Branches, update:
1. https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/integrations
2. Change "Supabase directory" from `supabase/supabase` to `supabase/`
