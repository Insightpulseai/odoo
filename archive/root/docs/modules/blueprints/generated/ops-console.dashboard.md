<!-- AUTO-GENERATED from blueprints/ops-console.dashboard.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Ops Console Dashboard (Vercel Admin + shadcn baseline)

**ID**: `ops-console.dashboard`  
**Category**: `ops-console`  
**Target**: `apps/ops-console`

---

## Sources

- **vercel-template** — [https://vercel.com/templates/next.js/nextjs-shadcn-ui-admin-dashboard](https://vercel.com/templates/next.js/nextjs-shadcn-ui-admin-dashboard) (catalog id: `nextjs-shadcn-admin`)
- **vercel-example** — [https://github.com/vercel/next.js/tree/main/examples/with-supabase](https://github.com/vercel/next.js/tree/main/examples/with-supabase) (catalog id: `with-supabase`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_PROJECT_NAME` | Vercel project name for ops-console | `odooops-console` |
| `VERCEL_TEAM_ID` | Vercel team identifier | `team_xxxxxxxxxxx` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key (public, safe for browser) | `eyJhbGciOiJIUzI1...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (server-only) | `eyJhbGciOiJIUzI1...` |
| `SUPABASE_MANAGEMENT_API_TOKEN` | Supabase Management API token (server-only) | `sbp_xxxxxxx` |

---

## Automation Steps

### Step 1: scaffold_routes

Ensure all required top-level routes exist in app/

**Agent instruction**:

```
Create stub page.tsx files for any missing routes in apps/ops-console/app/:
- /overview (home dashboard with stat cards)
- /platform (Management API scaffold — already exists)
- /observability (already exists)
- /deployments (Vercel deployments list)
- /environments (Vercel env vars surface)
- /gates (CI gate status overview)
- /modules (Odoo module registry)
- /runbooks (links to docs/ops/ runbooks)
- /settings (project settings scaffold)
Each stub must use existing shadcn/ui Card + Badge primitives only.
```

### Step 2: wire_sidebar_nav

Add all routes to the sidebar navigation

**Agent instruction**:

```
Update the sidebar navigation component in apps/ops-console to list all routes
from the scaffold_routes step. Use lucide-react icons. Group as:
- Monitoring: Overview, Observability
- Platform: Platform (Supabase), Environments, Deployments
- Quality: Gates, Modules
- Reference: Runbooks, Settings
```

### Step 3: wire_env

Ensure env var placeholders follow server-only conventions

**Agent instruction**:

```
Audit apps/ops-console for any NEXT_PUBLIC_ prefix on server-only variables
(SUPABASE_SERVICE_ROLE_KEY, SUPABASE_MANAGEMENT_API_TOKEN, DIGITALOCEAN_API_TOKEN,
ANTHROPIC_AUTH_TOKEN). Remove NEXT_PUBLIC_ from any that appear there.
Add all required env vars to apps/ops-console/.env.agent.example.
```

### Step 4: add_ci

Verify app-scoped CI gates exist

**Agent instruction**:

```
Check that .github/workflows/ contains these path-filtered workflows for
apps/ops-console/**:
- ops-console-check.yml (ESLint + TypeScript + Prettier)
- ops-console-playwright.yml (Playwright smoke test)
- ops-console-bundle-size.yml (bundle size delta)
If any are missing, create them following the pattern in existing workflows.
```

---

## Verification

**Required CI checks:**

- `ops-console-check`
- `ops-console-playwright`
- `ops-console-bundle-size`
- `golden-path-summary`

**Preview expectations:**

- vercel-preview-url-posted-to-pr
- deployment-protection-enabled
- all-routes-render-without-500

---

## Rollback

**Strategy**: `revert_pr`

All changes are additive (new files + route stubs). Revert PR if issues arise.

---

## Minor Customization (manual steps after agent applies blueprint)

- Set Vercel Root Directory to apps/ops-console (vercel link --repo from apps/ops-console)
- Pull env vars from Vercel (vercel env pull .env.local) after linking
- Enable Deployment Protection in Vercel project settings for the team

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `ops-console.dashboard` from docs/catalog/blueprints/ops-console.dashboard.blueprint.yaml.

Variables to set before running:
  VERCEL_PROJECT_NAME: <value>
  VERCEL_TEAM_ID: <value>
  NEXT_PUBLIC_SUPABASE_URL: <value>
  NEXT_PUBLIC_SUPABASE_ANON_KEY: <value>
  SUPABASE_SERVICE_ROLE_KEY: <value>
  SUPABASE_MANAGEMENT_API_TOKEN: <value>

Steps to execute in order:
  1. scaffold_routes: Ensure all required top-level routes exist in app/
  2. wire_sidebar_nav: Add all routes to the sidebar navigation
  3. wire_env: Ensure env var placeholders follow server-only conventions
  4. add_ci: Verify app-scoped CI gates exist

After completing all steps:
  - Verify required checks pass: ops-console-check, ops-console-playwright, ops-console-bundle-size, golden-path-summary
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
