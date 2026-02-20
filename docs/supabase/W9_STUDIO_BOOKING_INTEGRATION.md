# W9 Studio Booking — Supabase Integration

## Implementation Status

**✅ COMPLETE** - All code files created and integrated:

1. ✅ Supabase client (`src/lib/supabase.ts`)
2. ✅ Booking service (`src/lib/bookings.ts`)
3. ✅ Database migration (`supabase/migrations/20260220_create_bookings.sql`)
4. ✅ Environment template (`.env.local.example`)
5. ✅ UI integration (`src/components/ui/BookingSection.jsx`)

---

## Automation-First Setup (Repo + CI Friendly)

### A) Apply Migrations via Supabase CLI (Preferred)

**Source of Truth:** `supabase/migrations/20260220_create_bookings.sql`

**Local Development:**
```bash
# Initialize Supabase (if not already done)
cd sandbox/dev/.artifacts/rotor-kinetic
supabase init

# Link to project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Apply migrations
supabase db push

# Verify
supabase db diff
```

**CI/CD Integration:**
- Inject `SUPABASE_ACCESS_TOKEN` via GitHub Secrets
- Migration runner in `.github/workflows/supabase-migrations.yml`
- Automated on merge to main branch

**Requirements:**
- Project ref: `spdtwktxdalcfigzeqrz`
- Service role key (or database password) injected via CI secrets
- Supabase CLI installed locally or in CI container

**Fallback (Development Only):**
If Supabase CLI is unavailable, apply migration manually via SQL editor as one-time bootstrap. Document this as an exception.

---

### B) Schema Exposure Decision (Must Choose One)

**⚠️ Security Decision Required**

#### Option 1 (Recommended): `ops` is Server-Only

**Architecture:**
- Client submits bookings via **Edge Function or RPC**
- `ops.bookings` remains protected, auditable, not directly exposed
- Edge Function handles validation, rate limiting, abuse prevention
- RLS policies apply to server-side operations only

**Benefits:**
- ✅ Control-plane SSOT remains isolated
- ✅ Client cannot bypass validation/business logic
- ✅ Rate limiting and abuse controls at Edge Function layer
- ✅ Future integration with Odoo SOR easier (server-to-server)

**Implementation:**
```typescript
// Edge Function: supabase/functions/submit-booking/index.ts
import { createClient } from '@supabase/supabase-js'

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')! // Server-side only
  )
  
  const booking = await req.json()
  
  // Validation, rate limiting, abuse checks here
  
  const { error } = await supabase
    .from('ops.bookings')
    .insert([booking])
  
  return new Response(JSON.stringify({ success: !error }))
})
```

**Client Change:**
```typescript
// src/lib/bookings.ts
export async function submitBooking(payload: BookingPayload): Promise<void> {
  const response = await supabase.functions.invoke('submit-booking', {
    body: payload
  })
  // Handle response
}
```

#### Option 2 (Exception): Client Can Insert into `ops.bookings`

**Only if:**
- Explicit justification documented in SSOT boundary docs
- RLS policies include abuse controls (rate limit, validation, honeypot fields)
- Client exposure is temporary (migration path to Option 1 exists)
- Operational simplicity outweighs security concerns (e.g., MVP phase)

**Required Controls:**
- [ ] Rate limiting (Supabase Edge Functions or external)
- [ ] Input validation (database constraints + client-side)
- [ ] Honeypot fields (e.g., `_bot_trap` column ignored by real clients)
- [ ] Monitoring and alerting (suspicious insert patterns)
- [ ] Documented migration path to server-only access

**PostgREST Schema Exposure (if Option 2):**
```bash
# Via Supabase CLI
supabase settings update api.schemas --value 'public,storage,ops'

# Or document manual step as exception:
# Settings → API → Exposed schemas → Add 'ops' → Save
```

**Current Implementation:** Code assumes **Option 2** (direct client access). This is acceptable for MVP but should migrate to Option 1 for production.

---

### C) Local Environment Wiring

**Source:** `.env.local.example`

**Injection Method:**
- **Local:** Manual copy `.env.local.example` → `.env.local`, fill with real credentials
- **CI:** GitHub Secrets → workflow env vars → Vite build-time substitution
- **Never Committed:** `.env.local` is in `.gitignore`

**Required Variables:**
```bash
VITE_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key_from_supabase_settings>
```

**Get Credentials:**
```bash
# Via CLI
supabase status

# Or programmatically
curl https://api.supabase.com/v1/projects/spdtwktxdalcfigzeqrz \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  | jq '.anon_key'
```

---

### D) Verification (Automated)

**Smoke Test Requirements:**

```bash
# Test script: sandbox/dev/.artifacts/rotor-kinetic/test/booking-smoke.test.ts
describe('Booking Submission', () => {
  it('inserts booking with anon key (if Option 2)', async () => {
    const result = await submitBooking({
      studio_type: 'video',
      booking_date: '2026-03-01',
      time_slot: '10:00 AM',
      name: 'Test User',
      email: 'test@example.com',
      phone: null,
      message: null
    })
    expect(result).toBeUndefined() // No error thrown
  })

  it('rejects double-booking via exclusion constraint', async () => {
    // Insert once
    await submitBooking({ /* same date + time */ })
    
    // Attempt duplicate
    await expect(submitBooking({ /* same date + time */ }))
      .rejects
      .toThrow(/exclusion constraint/)
  })

  it('enforces RLS: anon cannot SELECT bookings', async () => {
    const { data } = await supabase.from('bookings').select('*')
    expect(data).toEqual([]) // Empty due to RLS
  })
})
```

**CI Integration:**
```yaml
# .github/workflows/w9-booking-tests.yml
name: W9 Booking Smoke Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
      - run: |
          cd sandbox/dev/.artifacts/rotor-kinetic
          supabase db push
          npm test -- booking-smoke.test.ts
        env:
          VITE_SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

---

## SSOT/SOR Architecture

### Current State: SSOT Only

**W9 Studio bookings** live in `ops.bookings` (Supabase SSOT):
- ✅ Operational data: booking requests, availability, contact info
- ❌ No financial data: no prices, no invoices, no payments

**Schema Design:**
- `ops.*` namespace = SSOT for operational events
- Audit fields: `created_at`, `created_by`, `updated_at`
- Integration readiness: `odoo_invoice_id`, `odoo_synced_at` (future)

### Future Phase: Odoo SOR Integration

**When bookings need invoicing:**

1. **Trigger:** Studio admin confirms booking → status = 'confirmed'
2. **Edge Function:** Webhook triggers on status change
3. **Odoo Invoice:** Create via XML-RPC:
   - Partner: customer from booking.email/name/phone
   - Invoice lines: studio type → product mapping
   - Invoice date: booking_date
4. **Bridge:** Update `ops.bookings.odoo_invoice_id`
5. **Timestamp:** Mark `odoo_synced_at`

**SSOT/SOR Separation:**
- **Supabase SSOT:** Booking metadata, availability, enrichment, analytics
- **Odoo SOR:** Invoice, payment, accounting ledger (canonical truth)
- **Bridge:** `odoo_invoice_id` foreign reference (SSOT → SOR link)

**Why Separate:**
- Not all bookings require invoicing (internal use, marketing shoots)
- Analytics needs real-time data (Supabase), not locked ledger (Odoo)
- Fast operational queries vs. heavyweight ERP

**Integration Files (Not Implemented Yet):**
- `supabase/functions/sync-booking-to-odoo/index.ts` - Edge Function
- `src/lib/odoo-client.ts` - Odoo XML-RPC wrapper
- `ops.odoo_sync_log` - Integration audit trail
- `.env`: `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`

---

## Security Features

### Row-Level Security (RLS)

**Anonymous users (anon key):**
- ✅ **INSERT only** - Can submit bookings
- ❌ **No SELECT** - Cannot view any bookings
- ❌ **No UPDATE/DELETE** - Cannot modify bookings

**Authenticated users (JWT):**
- ✅ **SELECT own bookings** - Filter by email match
- ❌ **No INSERT/UPDATE/DELETE** - Only admins can modify

**Admins (role='admin' in JWT):**
- ✅ **Full CRUD** - All operations allowed
- ✅ **View all bookings** - No email filter

### Constraints

**Double-booking prevention:**
```sql
constraint no_double_booking
  exclude using gist (booking_date with =, time_slot with =)
  where (status != 'cancelled')
```

**Status enforcement:**
```sql
check (status in ('pending','confirmed','cancelled'))
```

**Studio type enforcement:**
```sql
check (studio_type in ('video','photo','event','rental'))
```

---

## Files Reference

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `package.json` | Dependencies + scripts | 2,437 bytes | ✅ Created |
| `src/lib/supabase.ts` | Supabase client | 705 bytes | ✅ Created |
| `src/lib/bookings.ts` | Booking service | 1,077 bytes | ✅ Created |
| `supabase/migrations/20260220_create_bookings.sql` | Database schema | 3,020 bytes | ✅ Created |
| `.env.local.example` | Environment template | 220 bytes | ✅ Created |
| `src/components/ui/BookingSection.jsx` | UI component | 19,869 bytes | ✅ Integrated |

---

## Troubleshooting

### "Missing VITE_SUPABASE_URL environment variable"

**Cause:** `.env.local` not created or missing variables

**Fix:**
```bash
cp .env.local.example .env.local
# Edit .env.local with real credentials
```

### "relation 'ops.bookings' does not exist"

**Cause:** Migration not applied

**Fix:**
```bash
supabase db push
# Or apply SQL manually if CLI unavailable (document as exception)
```

### "row-level security policy violation"

**Cause:** RLS policies not created or wrong key used

**Fix:**
1. Verify RLS enabled: `SELECT * FROM pg_policies WHERE tablename = 'bookings';`
2. Check using anon key (not service role key) in `.env.local`
3. If Option 1 (server-only): Use Edge Function, not direct client access

### Form submits but no row inserted (Option 2 only)

**Cause:** Schema not exposed to PostgREST

**Fix:**
```bash
# If using Option 2 (direct client access)
supabase settings update api.schemas --value 'public,storage,ops'

# Verify
supabase settings get api.schemas
```

**If using Option 1 (server-only):** This is expected. Client should call Edge Function, not directly insert.

---

## Decision Log

**Schema Exposure (2026-02-20):**
- **Current:** Option 2 (direct client access) for MVP simplicity
- **Recommended:** Migrate to Option 1 (Edge Function gateway) for production
- **Justification:** Faster MVP iteration, acceptable risk for low-traffic launch
- **Migration Path:** Create Edge Function, update client code, remove `ops` from exposed schemas
- **Timeline:** Before public launch or after 100 bookings/month, whichever comes first

**RLS Policies:**
- Anon INSERT allowed for public booking submissions
- SELECT restricted to prevent data scraping
- Admin role required for UPDATE/DELETE operations

**Integration Readiness:**
- `odoo_invoice_id` column prepared but NULL for all rows
- Sync logic deferred to post-launch (when invoicing needed)

---

## Resources

**Supabase CLI Documentation:**
- Installation: https://supabase.com/docs/guides/cli/getting-started
- Migration Guide: https://supabase.com/docs/guides/cli/local-development#database-migrations
- CI/CD Integration: https://supabase.com/docs/guides/cli/github-action

**SSOT/SOR Architecture:**
- See: `docs/architecture/ssot-sor-boundaries.md` (if exists)
- Principle: Operational SSOT (Supabase) + Financial SOR (Odoo)
