# W9 Studio Booking Form - Supabase Integration (SSOT-Aligned)

**Date**: 2026-02-20 03:43+0800
**Status**: STATUS=COMPLETE
**Repo**: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
**Branch**: _git_aggregated
**Goal**: Wire W9 Studio booking form to Supabase with SSOT architecture

## Implementation Complete

All planned files created and integrated:

1. ✅ **Supabase Client** (`src/lib/supabase.ts`) - Environment validation + client initialization
2. ✅ **Bookings Service** (`src/lib/bookings.ts`) - submitBooking() with TypeScript interface
3. ✅ **Database Migration** (`supabase/migrations/20260220_create_bookings.sql`) - SSOT-aligned schema
4. ✅ **Environment Template** (`.env.local.example`) - Configuration guide
5. ✅ **UI Integration** (`src/components/ui/BookingSection.jsx`) - Already had all required changes

## SSOT Architecture Features

### Schema Design (ops.bookings)
- **Namespace**: `ops.*` schema (SSOT for operational events, not `public.*`)
- **Audit Trail**: `created_at`, `created_by`, `updated_at` fields
- **Integration Ready**: `odoo_invoice_id`, `odoo_synced_at` for future SOR bridge
- **Double-Booking Prevention**: Exclusion constraint on `(booking_date, time_slot)`

### Row-Level Security (RLS)
- **anon**: INSERT only (submit bookings)
- **authenticated**: SELECT own bookings (by email match)
- **admin role**: ALL operations (full management)

### SSOT/SOR Boundary
- **Supabase SSOT**: Booking requests, availability, operational data
- **Odoo SOR** (future): Invoices, payments, accounting ledger
- **Bridge**: `odoo_invoice_id` foreign key links SSOT → SOR when booking is invoiced

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/lib/supabase.ts` | Supabase client with env validation | 11 |
| `src/lib/bookings.ts` | submitBooking() + BookingPayload interface | 32 |
| `supabase/migrations/20260220_create_bookings.sql` | SSOT schema + RLS + audit triggers | 87 |
| `.env.local.example` | Environment template for developers | 6 |

## Files Modified

- **BookingSection.jsx**: Already had:
  - Import: `import { submitBooking } from '../../lib/bookings';`
  - State: `loading`, `submitError`, `validationError`
  - Handler: `handleSubmit` with validation + try/catch
  - UI: Error display, loading button state

## Next Steps (MANUAL_REQUIRED)

### Step 1: Run Database Migration

**What**: Execute SQL migration in Supabase SQL Editor
**Why**: Create `ops.bookings` table, RLS policies, audit triggers

**Minimal human action**:
1. Log into Supabase Dashboard: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
2. Go to **SQL Editor**
3. Copy `supabase/migrations/20260220_create_bookings.sql` contents
4. Paste and click **Run**
5. Verify: Query `SELECT * FROM ops.bookings LIMIT 1;` returns empty result (not error)

**Evidence**: Screenshot showing successful migration run

**Then**: Automation resumes at Step 2 (PostgREST configuration)

### Step 2: Configure PostgREST Schema Exposure

**What**: Expose `ops` schema to PostgREST API
**Why**: UI-only step - PostgREST schema config not available via API

**Minimal human action**:
1. In Supabase Dashboard → **Settings → API**
2. Find **Exposed schemas** section
3. Add `ops` to the list (currently likely just `public, storage`)
4. Click **Save**

**Verification**:
```bash
curl "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/bookings?select=id&limit=1" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
# Should return 200 (even if empty array)
```

**Then**: Automation resumes at Step 3 (environment setup)

### Step 3: Configure Local Environment

**What**: Create `.env.local` with Supabase credentials
**Why**: Vite requires `VITE_*` prefixed env vars for client-side access

**Minimal human action**:
```bash
cd sandbox/dev/.artifacts/rotor-kinetic
cp .env.local.example .env.local
# Edit .env.local with real credentials:
# VITE_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
# VITE_SUPABASE_ANON_KEY=<from Supabase Dashboard → Settings → API>
```

**Then**: Ready for runtime testing

## Verification Checklist

### Database Setup
- [ ] Migration executed successfully in Supabase SQL Editor
- [ ] `ops` schema created: `SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ops';`
- [ ] `ops.bookings` table exists: `\d ops.bookings`
- [ ] RLS enabled: `SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'ops' AND tablename = 'bookings';`
- [ ] Policies active: `SELECT policyname FROM pg_policies WHERE schemaname = 'ops' AND tablename = 'bookings';`

### PostgREST Configuration
- [ ] `ops` added to exposed schemas in Dashboard
- [ ] API responds to `/bookings` endpoint: `curl .../rest/v1/bookings?select=id&limit=1`

### Application Integration
- [ ] `.env.local` created with real Supabase credentials
- [ ] Build succeeds: `npm run build` (no TypeScript errors)
- [ ] Dev server starts: `npm run dev`
- [ ] Form submission creates row in `ops.bookings`
- [ ] Loading state shows during request
- [ ] Success UI appears on completion
- [ ] Error shown on validation failure
- [ ] Double-booking prevention works

### SSOT Verification
```sql
-- Check audit fields populated
SELECT id, studio_type, booking_date, status,
       created_at, created_by, updated_at
FROM ops.bookings
ORDER BY created_at DESC
LIMIT 1;

-- Verify created_at is auto-populated (not NULL)
-- Verify created_by is NULL (anon submission)
-- Verify odoo_invoice_id is NULL (not yet invoiced)
-- Verify updated_at is NULL (no updates yet)
```

## Evidence Logs

- `logs/git-status.log` - Working directory state
- `logs/git-diff-stat.log` - File change statistics
- `logs/files-created.log` - Created file listings

## SSOT Boundary Documentation

### Current State (SSOT Only)
- W9 Studio bookings live in `ops.bookings` (Supabase SSOT)
- Operational data: booking requests, availability, contact info
- No financial data: no prices, no invoices, no payments

### Future Phase: Odoo SOR Integration

When bookings need invoicing (e.g., deposit required, post-session billing):

**Workflow**:
1. Studio admin confirms booking in Supabase UI → `status = 'confirmed'`
2. Edge Function triggers on status change to 'confirmed'
3. Edge Function creates Odoo invoice via XML-RPC
4. Odoo returns invoice ID → update `ops.bookings.odoo_invoice_id`
5. Mark `odoo_synced_at` timestamp

**Files Not Implemented Yet**:
- `supabase/functions/sync-booking-to-odoo/index.ts` - Edge Function
- `src/lib/odoo-client.ts` - Odoo XML-RPC wrapper
- `ops.odoo_sync_log` - Integration audit trail
