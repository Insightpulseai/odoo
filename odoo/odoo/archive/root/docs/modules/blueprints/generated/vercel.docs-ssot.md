<!-- AUTO-GENERATED from blueprints/vercel.docs-ssot.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Vercel Docs SSOT (pinned canonical URLs)

**ID**: `vercel.docs-ssot`  
**Category**: `ops-console`  
**Target**: `docs/ops`

---

## Sources

- **doc** — [https://vercel.com/docs](https://vercel.com/docs) (catalog id: `vercel-docs-home`)
- **doc** — [https://vercel.com/docs/llms-full.txt](https://vercel.com/docs/llms-full.txt) (catalog id: `vercel-docs-llms`)

---

## Required Variables

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `NONE` | No runtime variables required for this doc-only blueprint. | `` |

---

## Automation Steps

### Step 1: create_ssot_doc

Create docs/ops/VERCEL_DOCS_SSOT.md as a tight bookmark file

### Step 2: cross_link_from_existing_runbooks

Add VERCEL_DOCS_SSOT reference to related runbooks

### Step 3: catalog_item_link

Ensure catalog item exists with blueprint_id=vercel.docs-ssot

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`

**Preview expectations:**

- docs-generated-no-drift
- vercel-docs-ssot-md-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- None — doc-only blueprint; no tokens or env vars required after merge.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `vercel.docs-ssot` from docs/catalog/blueprints/vercel.docs-ssot.blueprint.yaml.

Variables to set before running:

Steps to execute in order:
  1. create_ssot_doc: Create docs/ops/VERCEL_DOCS_SSOT.md as a tight bookmark file
  2. cross_link_from_existing_runbooks: Add VERCEL_DOCS_SSOT reference to related runbooks
  3. catalog_item_link: Ensure catalog item exists with blueprint_id=vercel.docs-ssot

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
