<!-- AUTO-GENERATED from blueprints/supabase.platform-kit.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Supabase Platform Kit (Management API live data in /platform)

**ID**: `supabase.platform-kit`  
**Category**: `platform-kit`  
**Target**: `apps/ops-console`

---

## Sources

- **supabase-platform-kit** — [https://supabase.com/blog/supabase-ui-platform-kit](https://supabase.com/blog/supabase-ui-platform-kit) (catalog id: `supabase-ui-platform-kit`)
- **supabase-example** — [https://github.com/supabase/supabase/tree/master/examples](https://github.com/supabase/supabase/tree/master/examples) (catalog id: `nextjs-with-supabase`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_MANAGEMENT_API_TOKEN` | Management API token with read access (server-only) | `sbp_xxxxxxx` |
| `NEXT_PUBLIC_SUPABASE_PROJECT_REF` | Supabase project reference (non-secret) | `spdtwktxdalcfigzeqrz` |

---

## Automation Steps

### Step 1: wire_projects_list

Connect /platform Projects card to live Management API

**Agent instruction**:

```
In apps/ops-console/app/platform/page.tsx:
- Change the page to a server component (remove 'use client')
- Import the Management API client: import { client } from '@/lib/management-api'
- Fetch projects: const { data } = await client.GET('/v1/projects')
- Replace the scaffold SurfaceCard with a real projects list showing:
  name, region, status (active/inactive/paused), health badges
- Keep the existing card layout; populate with real data or fall back to
  scaffold if SUPABASE_MANAGEMENT_API_TOKEN is not set
```

### Step 2: wire_branches_list

Connect Branches card to live Management API

**Agent instruction**:

```
In apps/ops-console/app/platform/page.tsx:
- Fetch branches for the project:
  const { data } = await client.GET('/v1/projects/{ref}/branches', { params: { path: { ref: projectRef } } })
- Show branch name, status, git_branch, created_at
- Add a "Create DEV branch" action (POST /v1/projects/{ref}/branches) as a
  server action (no direct client access to SUPABASE_MANAGEMENT_API_TOKEN)
```

### Step 3: wire_logs_query

Connect Logs card to live Management API

**Agent instruction**:

```
Add a server action in apps/ops-console/app/platform/actions.ts:
- queryLogs(projectRef, sql) → POST /v1/projects/{ref}/analytics/endpoints/logs.all
- Return the first 50 rows
Add a basic log query panel in the Logs card:
- Preset SQL queries (last 100 errors, last 100 auth events)
- Display results in a simple table
- No direct user-provided SQL (XSS risk) — use preset queries only
```

### Step 4: wire_security_advisor

Connect security advisor

**Agent instruction**:

```
Fetch security advisor findings:
  const { data } = await client.GET('/v1/projects/{ref}/advisors/security', ...)
Display findings grouped by severity (ERROR, WARN, INFO).
Add a "Block merge if security advisor returns ERROR" note in the UI.
```

---

## Verification

**Required CI checks:**

- `ops-console-check`
- `golden-path-summary`

**Preview expectations:**

- platform-page-shows-real-project-data
- no-management-token-in-client-bundle
- security-advisor-visible

---

## Rollback

**Strategy**: `revert_pr`

No schema changes. Revert PR if Management API calls cause issues.

---

## Minor Customization (manual steps after agent applies blueprint)

- Add SUPABASE_MANAGEMENT_API_TOKEN to Vercel project env vars (server-only)
- Verify the token has read access for /v1/projects and /v1/projects/{ref}/branches
- Test with: curl -H 'Authorization: Bearer $TOKEN' https://api.supabase.com/v1/projects

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `supabase.platform-kit` from docs/catalog/blueprints/supabase.platform-kit.blueprint.yaml.

Variables to set before running:
  SUPABASE_MANAGEMENT_API_TOKEN: <value>
  NEXT_PUBLIC_SUPABASE_PROJECT_REF: <value>

Steps to execute in order:
  1. wire_projects_list: Connect /platform Projects card to live Management API
  2. wire_branches_list: Connect Branches card to live Management API
  3. wire_logs_query: Connect Logs card to live Management API
  4. wire_security_advisor: Connect security advisor

After completing all steps:
  - Verify required checks pass: ops-console-check, golden-path-summary
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
