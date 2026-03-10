<!-- AUTO-GENERATED from blueprints/odoo.ios-app.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Odoo iOS App Store Client (SwiftUI skeleton + Fastlane CI)

**ID**: `odoo.ios-app`  
**Category**: `ops-console`  
**Target**: `apps/odoo-mobile-ios`

---

## Sources

- **doc** — [https://developer.apple.com/documentation/swiftui](https://developer.apple.com/documentation/swiftui) (catalog id: `apple-swiftui-docs`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `MATCH_GIT_URL` | Private git repo URL for Fastlane match code signing certificates. | `` |
| `MATCH_PASSWORD` | Encryption password for Fastlane match certificate repo. | `` |
| `APP_STORE_CONNECT_API_KEY_ID` | App Store Connect API Key ID for CI automation. | `` |
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | Issuer ID for the App Store Connect API key. | `` |
| `APP_STORE_CONNECT_API_KEY_CONTENT` | Base64-encoded .p8 key file content for CI (set as GitHub secret). | `` |
| `APPLE_ID` | Apple ID email used for Fastlane match authentication. | `` |

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_IDENTIFIER` | Bundle ID (default com.insightpulseai.odoo-mobile). | `` |

---

## Automation Steps

### Step 1: create_swift_skeleton

Create SwiftUI app skeleton in apps/odoo-mobile-ios/

### Step 2: create_fastlane

Create Fastlane configuration (Fastfile, Appfile, Matchfile, .env.example)

### Step 3: create_ci_workflow

Create .github/workflows/ios-appstore.yml

### Step 4: create_spec_bundle

Create spec/odoo-mobile/ spec bundle

### Step 5: catalog_item_link

Add item to docs/catalog/mobile.catalog.json and blueprint

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`

**Preview expectations:**

- package-swift-exists
- fastfile-exists
- ci-workflow-exists
- spec-bundle-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- Set OdooBaseURL and OdooOIDCClientID in Info.plist after creating Xcode project.
- Run fastlane match init once to create the certificate repo.
- Set all GitHub Actions secrets before first CI run.
- Update bundle ID if using a different Apple Developer team.
- Phase 0 is skeleton only — implement TODO stubs in phases 1-5.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `odoo.ios-app` from docs/catalog/blueprints/odoo.ios-app.blueprint.yaml.

Variables to set before running:
  MATCH_GIT_URL: <value>
  MATCH_PASSWORD: <value>
  APP_STORE_CONNECT_API_KEY_ID: <value>
  APP_STORE_CONNECT_API_KEY_ISSUER_ID: <value>
  APP_STORE_CONNECT_API_KEY_CONTENT: <value>
  APPLE_ID: <value>

Steps to execute in order:
  1. create_swift_skeleton: Create SwiftUI app skeleton in apps/odoo-mobile-ios/
  2. create_fastlane: Create Fastlane configuration (Fastfile, Appfile, Matchfile, .env.example)
  3. create_ci_workflow: Create .github/workflows/ios-appstore.yml
  4. create_spec_bundle: Create spec/odoo-mobile/ spec bundle
  5. catalog_item_link: Add item to docs/catalog/mobile.catalog.json and blueprint

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
