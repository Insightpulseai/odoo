<!-- AUTO-GENERATED from blueprints/vercel.saas-microservices.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Vercel SaaS Microservices (multi-tenant + Edge middleware)

**ID**: `vercel.saas-microservices`  
**Category**: `ops-console`  
**Target**: `apps/ops-console`

---

## Sources

- **vercel-template** — [https://vercel.com/templates/next.js/microservices-starter](https://vercel.com/templates/next.js/microservices-starter) (catalog id: `vercel-saas-microservices`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_PROJECT_REF` | Supabase project ref used in tenant resolver middleware. | `` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL (public, safe to expose). | `` |

---

## Automation Steps

### Step 1: lift_middleware

Lift Edge middleware for per-tenant routing

### Step 2: lift_api_layer

Lift shared API route handler pattern

### Step 3: catalog_item_link

Ensure catalog item exists with blueprint_id=vercel.saas-microservices

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`

**Preview expectations:**

- middleware-ts-exists
- tenant-resolver-uses-env-var
- no-hardcoded-project-refs

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- Update tenant resolver to use SUPABASE_PROJECT_REF env var (not hardcoded ref).
- Remove Stripe integration if not needed — only lift middleware + API handler pattern.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `vercel.saas-microservices` from docs/catalog/blueprints/vercel.saas-microservices.blueprint.yaml.

Variables to set before running:
  SUPABASE_PROJECT_REF: <value>
  NEXT_PUBLIC_SUPABASE_URL: <value>

Steps to execute in order:
  1. lift_middleware: Lift Edge middleware for per-tenant routing
  2. lift_api_layer: Lift shared API route handler pattern
  3. catalog_item_link: Ensure catalog item exists with blueprint_id=vercel.saas-microservices

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
