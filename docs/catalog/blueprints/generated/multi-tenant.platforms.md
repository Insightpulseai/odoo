<!-- AUTO-GENERATED from blueprints/multi-tenant.platforms.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Multi-tenant Platform (subdomain routing + tenant-scoped DB)

**ID**: `multi-tenant.platforms`  
**Category**: `multi-tenant`  
**Target**: `apps/ops-console`

---

## Sources

- **vercel-example** — [https://github.com/vercel/platforms](https://github.com/vercel/platforms) (catalog id: `platforms-starter-kit`)
- **supabase-example** — [https://github.com/supabase/supabase/tree/master/examples/auth/nextjs](https://github.com/supabase/supabase/tree/master/examples/auth/nextjs) (catalog id: `nextjs-with-supabase`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `ROOT_DOMAIN` | Root domain for subdomain routing | `insightpulseai.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for tenant lookup (server-only) | `eyJhbGciOiJIUzI1...` |

---

## Automation Steps

### Step 1: add_subdomain_middleware

Add subdomain-based tenant routing middleware

**Agent instruction**:

```
Update apps/ops-console/middleware.ts to:
- Extract the subdomain from req.nextUrl.hostname
- If subdomain is a known tenant (lookup from Supabase tenants table),
  rewrite to /tenant/[slug] routing
- If not, continue to normal routing
- Keep existing Supabase auth session refresh logic
Pattern: vercel/platforms middleware.ts approach
```

### Step 2: add_tenant_routing

Add tenant-scoped page routing

**Agent instruction**:

```
Create apps/ops-console/app/tenant/[slug]/ directory with:
- layout.tsx: fetch tenant metadata from Supabase (tenant slug → tenant row)
- page.tsx: tenant dashboard scaffold
- Tenant context via React Context or layout-level RSC prop drilling
No wildcard catch-all at top level — only /tenant/[slug] for now.
```

### Step 3: add_tenant_rls

Document RLS pattern for tenant data isolation

**Agent instruction**:

```
Create a Supabase migration (supabase migration new add_tenant_rls) that adds:
- tenants table: id (uuid), slug (text unique), name (text), created_at
- tenant_members table: tenant_id (uuid fk), user_id (uuid fk), role (text)
- RLS policy template on tenant_members:
  tenant_id IN (SELECT tenant_id FROM tenant_members WHERE user_id = auth.uid())
Document the pattern in a comment at the top of the migration file.
```

---

## Verification

**Required CI checks:**

- `ops-console-check`
- `golden-path-summary`

**Preview expectations:**

- subdomain-routing-works-in-vercel-preview
- tenant-data-isolated-by-rls

---

## Rollback

**Strategy**: `revert_pr`

Migration rollback required if tenants/tenant_members tables were created.

---

## Minor Customization (manual steps after agent applies blueprint)

- Add wildcard subdomain to Vercel project domains (*.insightpulseai.com)
- Add wildcard CNAME in Cloudflare (*.insightpulseai.com → Vercel) — update infra/cloudflare SSOT YAML
- Set ROOT_DOMAIN env var in Vercel project settings

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `multi-tenant.platforms` from docs/catalog/blueprints/multi-tenant.platforms.blueprint.yaml.

Variables to set before running:
  ROOT_DOMAIN: <value>
  NEXT_PUBLIC_SUPABASE_URL: <value>
  SUPABASE_SERVICE_ROLE_KEY: <value>

Steps to execute in order:
  1. add_subdomain_middleware: Add subdomain-based tenant routing middleware
  2. add_tenant_routing: Add tenant-scoped page routing
  3. add_tenant_rls: Document RLS pattern for tenant data isolation

After completing all steps:
  - Verify required checks pass: ops-console-check, golden-path-summary
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
