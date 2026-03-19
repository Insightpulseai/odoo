# Supabase + GitHub + Vercel Integration Setup

**Timestamp**: 2026-02-20 19:12+0800
**Project**: Insightpulseai/odoo
**Supabase**: spdtwktxdalcfigzeqrz

---

## ✅ Completed: Supabase ↔ GitHub Link

**Command**: `supabase link --project-ref spdtwktxdalcfigzeqrz`
**Status**: Linked
**Config Update**: Updated `supabase/config.toml` db.major_version 15 → 17

**Auto-Enabled**:
- Migration deployment via GitHub
- Database schema synchronization
- PR preview database branches
- Migration history tracking

---

## ⏳ Manual Required: Supabase ↔ Vercel Integration

**Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/integrations

### Steps (UI Required):
1. Navigate: Project Settings → Integrations → Vercel
2. Click "Install Integration" → Authorize Supabase
3. Select Vercel project: `ai-control-plane`
4. Auto-inject environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY` (server-only)
5. Enable "Preview Deployments" → Database branches for PRs
6. Confirm installation

**Outcome**: Vercel deployments automatically receive Supabase credentials, preview PRs get isolated databases.

---

## Environment Variables (Auto-Injected)

```bash
# Public (client-side)
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>

# Server-only
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# Direct connection (if needed)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres
```

---

## Deployment Flow

**GitHub Push** → **Supabase Migrations** → **Vercel Build** → **Live URL**

### PR Workflow:
1. Create PR with migration changes
2. Supabase creates preview database branch
3. Vercel deploys preview: `pr-<number>-<hash>.vercel.app`
4. Test with isolated database

### Production Deploy:
1. Merge PR to main
2. Supabase applies migrations to production
3. Vercel deploys: `erp.insightpulseai.com`
4. Production uses main database

---

## Next Actions

### 1. Apply Odoo.sh Migration
```bash
supabase db push  # After Vercel integration complete
```

### 2. Test Multi-Tenant Routing
- Deploy Next.js middleware to Vercel
- Test: `https://tenant1.app.insightpulseai.com`
- Verify `x-tenant-id` header

### 3. Configure Wildcard DNS
- Add `*.app.insightpulseai.com` to Vercel
- DNS CNAME: `*.app` → `cname.vercel-dns.com`
- Auto SSL enabled

---

**Integration Status**:
- ✅ Supabase ↔ GitHub: Linked
- ⏳ Supabase ↔ Vercel: Awaiting manual dashboard setup
- ⏳ Odoo.sh Tables: Ready to push after Vercel integration
