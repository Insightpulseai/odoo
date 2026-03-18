<!-- AUTO-GENERATED from blueprints/ops.advisor-ui.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Ops Advisor UI (Azure Advisor-like dashboard)

**ID**: `ops.advisor-ui`  
**Category**: `ops-console`  
**Target**: `apps/ops-console/app/advisor`

---

## Sources

- **supabase-platform-kit** — [https://supabase.com/docs/guides/platform](https://supabase.com/docs/guides/platform) (catalog id: `supabase-platform-kit`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL (PostgREST base URL for ops.* schema queries). | `` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for server-only advisor API routes and scorer CLI. | `` |

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_API_TOKEN` | Vercel API token used by the scorer Vercel source module. | `` |
| `DO_ACCESS_TOKEN` | DigitalOcean API token used by the scorer DO source module. | `` |
| `SUPABASE_MANAGEMENT_TOKEN` | Supabase Management API token for project health checks. | `` |

---

## Automation Steps

### Step 1: apply_migration

Apply ops schema migration to Supabase

### Step 2: create_platform_scorer

Create platform/advisor/ scorer, ruleset, and source modules

### Step 3: create_ui_routes

Create 4 UI routes in apps/ops-console/app/advisor/

### Step 4: create_api_routes

Create 2 API routes (server-only, no supabase-js)

### Step 5: catalog_item_link

Ensure catalog item exists with blueprint_id=ops.advisor-ui

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`
- `build-gate`

**Preview expectations:**

- advisor-page-exists
- api-runs-route-exists
- api-findings-route-exists
- migration-exists
- scorer-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local before local testing.
- Set VERCEL_API_TOKEN, DO_ACCESS_TOKEN, SUPABASE_MANAGEMENT_TOKEN for live scoring.
- Run scorer manually via tsx platform/advisor/scorer.ts or POST /api/advisor/runs.
- Workbooks page is scaffold only — populated by ops.mobile-release-workbook blueprint.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `ops.advisor-ui` from docs/catalog/blueprints/ops.advisor-ui.blueprint.yaml.

Variables to set before running:
  SUPABASE_URL: <value>
  SUPABASE_SERVICE_ROLE_KEY: <value>

Steps to execute in order:
  1. apply_migration: Apply ops schema migration to Supabase
  2. create_platform_scorer: Create platform/advisor/ scorer, ruleset, and source modules
  3. create_ui_routes: Create 4 UI routes in apps/ops-console/app/advisor/
  4. create_api_routes: Create 2 API routes (server-only, no supabase-js)
  5. catalog_item_link: Ensure catalog item exists with blueprint_id=ops.advisor-ui

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate, build-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
