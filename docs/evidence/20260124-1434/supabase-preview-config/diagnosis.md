# Supabase Preview Branches Configuration Diagnosis

**Date**: 2026-01-24 14:34 UTC
**Issue**: Supabase Preview Branches comment shows "ignored / no changes"
**Root Cause**: Dashboard misconfiguration - watching `supabase/supabase/` instead of `supabase/`

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

## Fix Required

**PHASE_REQUIRES_UI(Supabase Dashboard)**

Update the Supabase GitHub Integration settings:
1. Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/integrations
2. Under GitHub Integration > Preview Branches, change "Supabase directory" from `supabase/supabase` to `supabase/`

## Changes Shipped

1. `supabase/.supabase-preview-config.json` - Documents expected integration settings
2. `scripts/ci/check_supabase_preview_config.sh` - CI gate to detect misconfiguration

## Verification

```bash
./scripts/ci/check_supabase_preview_config.sh
```

Output confirms:
- ✓ No nested `supabase/supabase/` directory
- ✓ Standard Supabase CLI structure detected
- ✓ Project ID: spdtwktxdalcfigzeqrz
