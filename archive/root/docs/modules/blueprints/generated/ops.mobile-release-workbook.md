<!-- AUTO-GENERATED from blueprints/ops.mobile-release-workbook.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Mobile Release Readiness Workbook (Ops Advisor extension)

**ID**: `ops.mobile-release-workbook`  
**Category**: `ops-console`  
**Target**: `apps/ops-console/app/advisor/workbooks/mobile`

---

## Sources

- **doc** — [https://developer.apple.com/app-store/review/guidelines/](https://developer.apple.com/app-store/review/guidelines/) (catalog id: `apple-app-review-guidelines`)

---

## Required Variables

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `ASC_KEY_ID` | App Store Connect API Key ID for evaluating ASC-based rules. | `` |
| `ASC_ISSUER_ID` | Issuer ID for the App Store Connect API key. | `` |
| `ASC_KEY_CONTENT` | Base64-encoded .p8 key content for App Store Connect API. | `` |
| `ASC_APP_ID` | Numeric app ID from App Store Connect for the Odoo mobile app. | `` |

---

## Automation Steps

### Step 1: create_ruleset

Create platform/advisor/rulesets/mobile-release-readiness.yaml

### Step 2: create_asc_source

Create platform/advisor/sources/appstoreconnect.ts

### Step 3: create_workbook_ui

Create apps/ops-console/app/advisor/workbooks/mobile/page.tsx

### Step 4: create_api_route

Create apps/ops-console/app/api/advisor/workbooks/mobile/route.ts

### Step 5: catalog_item_link

Add item to docs/catalog/mobile.catalog.json

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`
- `build-gate`

**Preview expectations:**

- ruleset-yaml-exists
- workbook-page-exists
- workbook-api-route-exists
- asc-source-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- Set ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_CONTENT, ASC_APP_ID to enable ASC checks.
- Without ASC env vars, all appstoreconnect-source rules show as skipped.
- Crash-free rate check requires App Store Connect Analytics API — stub returns null until implemented.
- Add workbook to WORKBOOKS list in apps/ops-console/app/advisor/workbooks/page.tsx.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `ops.mobile-release-workbook` from docs/catalog/blueprints/ops.mobile-release-workbook.blueprint.yaml.

Variables to set before running:

Steps to execute in order:
  1. create_ruleset: Create platform/advisor/rulesets/mobile-release-readiness.yaml
  2. create_asc_source: Create platform/advisor/sources/appstoreconnect.ts
  3. create_workbook_ui: Create apps/ops-console/app/advisor/workbooks/mobile/page.tsx
  4. create_api_route: Create apps/ops-console/app/api/advisor/workbooks/mobile/route.ts
  5. catalog_item_link: Add item to docs/catalog/mobile.catalog.json

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate, build-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
