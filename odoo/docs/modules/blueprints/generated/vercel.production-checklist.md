<!-- AUTO-GENERATED from blueprints/vercel.production-checklist.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Vercel Production Checklist SSOT

**ID**: `vercel.production-checklist`  
**Category**: `ops-console`  
**Target**: `docs/ops`

---

## Sources

- **doc** — [https://vercel.com/docs/deployments/environments](https://vercel.com/docs/deployments/environments) (catalog id: `vercel-docs-home`)
- **doc** — [https://vercel.com/docs/deployment-protection](https://vercel.com/docs/deployment-protection) (catalog id: `vercel-docs-home`)

---

## Required Variables

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `NONE` | No runtime variables required for this doc-only blueprint. | `` |

---

## Automation Steps

### Step 1: create_checklist_doc

Create docs/ops/VERCEL_PRODUCTION_CHECKLIST_SSOT.md

### Step 2: cross_link_from_monorepo

Add cross-link to VERCEL_MONOREPO.md related runbooks table

### Step 3: catalog_item_link

Ensure catalog item exists with blueprint_id=vercel.production-checklist

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`

**Preview expectations:**

- docs-generated-no-drift
- vercel-production-checklist-ssot-md-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- None — doc-only blueprint; update health endpoint URL and Slack channel name after merge.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `vercel.production-checklist` from docs/catalog/blueprints/vercel.production-checklist.blueprint.yaml.

Variables to set before running:

Steps to execute in order:
  1. create_checklist_doc: Create docs/ops/VERCEL_PRODUCTION_CHECKLIST_SSOT.md
  2. cross_link_from_monorepo: Add cross-link to VERCEL_MONOREPO.md related runbooks table
  3. catalog_item_link: Ensure catalog item exists with blueprint_id=vercel.production-checklist

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
