# Odoo iOS App — Runbook

Native SwiftUI iOS 17+ client for Odoo ERP. See `apps/odoo-mobile-ios/` for source code.

---

## Bundle ID

`com.insightpulseai.odoo-mobile`

---

## Fastlane Setup

### Prerequisites

1. Ruby 3.2+ and Bundler: `gem install bundler`
2. Xcode 15.2+ with iOS 17 SDK
3. Apple Developer account (individual or organization)
4. App Store Connect API key (JSON key file, `.p8`)
5. Private git repo for Fastlane match certificates

### First-time Setup

```bash
# From repo root
cd odoo/
bundle install          # Installs fastlane + gems

# Initialize match (run once, creates match git repo)
bundle exec fastlane match init

# Fetch existing certificates
bundle exec fastlane match appstore
```

### Create `.env` from example

```bash
cp fastlane/.env.example fastlane/.env
# Edit fastlane/.env with your values (never commit .env)
```

---

## Running Lanes

```bash
# Run unit tests
bundle exec fastlane ios test

# Build and upload to TestFlight
bundle exec fastlane ios build_testflight

# Submit to App Store (after TestFlight approval)
bundle exec fastlane ios release_appstore
```

---

## TestFlight Workflow

1. Merge feature to `main` → CI triggers `build_testflight` lane
2. Build uploads automatically; wait for App Store processing (~15 min)
3. Add external beta testers in App Store Connect → TestFlight
4. Collect feedback; iterate until crash-free rate ≥ 99.5%

---

## App Store Submission Checklist

Before running `release_appstore`:

- [ ] Privacy Nutrition Labels complete (all data categories declared)
- [ ] App icon (1024×1024 PNG, no alpha, no rounded corners)
- [ ] Screenshots: 6.7" iPhone 15 Pro Max, 5.5" iPhone 8 Plus
- [ ] Age rating questionnaire complete
- [ ] Support URL set to `https://insightpulseai.com/support`
- [ ] Privacy Policy URL set
- [ ] Crash-free rate ≥ 99.5% in TestFlight (check Xcode Organizer → Crashes)
- [ ] Mobile Release Readiness workbook passes in ops-console

---

## Required GitHub Actions Secrets

| Secret | Purpose |
|--------|---------|
| `MATCH_GIT_URL` | Private git repo URL for match certificates |
| `MATCH_PASSWORD` | Encryption password for match repo |
| `APP_STORE_CONNECT_API_KEY_ID` | ASC API Key ID |
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | ASC API Key Issuer ID |
| `APP_STORE_CONNECT_API_KEY_CONTENT` | Base64-encoded `.p8` key content |
| `APPLE_ID` | Apple ID email (for match username) |
| `APP_IDENTIFIER` | Bundle ID (`com.insightpulseai.odoo-mobile`) |

---

## OIDC Configuration

The app uses Odoo's OIDC endpoint for SSO. Required Odoo server configuration:

1. Enable `auth_oidc` OCA module on the Odoo instance
2. Register `odoomobile://oauth/callback` as a redirect URI
3. Set `OdooBaseURL` and `OdooOIDCClientID` in the app's `Info.plist`

---

## Universal Links

For deep links from push notifications, configure `apple-app-site-association` on the Odoo server:

```json
{
  "applinks": {
    "apps": [],
    "details": [{
      "appID": "TEAMID.com.insightpulseai.odoo-mobile",
      "paths": ["/web/*"]
    }]
  }
}
```

---

## Related

- `apps/odoo-mobile-ios/` — source code + Package.swift
- `spec/odoo-mobile/` — spec bundle (constitution, prd, plan, tasks)
- `fastlane/` — Fastfile, Appfile, Matchfile
- `.github/workflows/ios-appstore.yml` — CI workflow
- `docs/ops/MOBILE_RELEASE_READINESS.md` — pre-submission workbook
- `/advisor/workbooks/mobile` — ops-console workbook UI
