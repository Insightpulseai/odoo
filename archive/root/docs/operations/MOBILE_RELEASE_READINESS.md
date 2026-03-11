# Mobile Release Readiness Workbook — Runbook

The Mobile Release Readiness workbook is an Ops Advisor extension that evaluates 10 rules
before iOS App Store submission. It surfaces pass/fail status with remediation guidance.

---

## What the Workbook Checks

| Rule ID | Pillar | Severity | Source |
|---------|--------|----------|--------|
| `ios-ci-green` | operational_excellence | critical | GitHub Actions |
| `fastlane-match-configured` | operational_excellence | high | Filesystem |
| `keychain-usage-declared` | security | high | Filesystem |
| `ats-https-only` | security | high | Filesystem |
| `build-submitted` | operational_excellence | critical | App Store Connect API |
| `privacy-nutrition-labels-complete` | security | high | App Store Connect API |
| `age-rating-set` | operational_excellence | medium | App Store Connect API |
| `screenshots-all-devices` | operational_excellence | medium | App Store Connect API |
| `testflight-external-group-exists` | operational_excellence | medium | App Store Connect API |
| `crash-free-rate-target-met` | reliability | high | App Store Connect API |

Checks are grouped into three categories:
- **CI/Filesystem** — evaluated server-side from the ops-console API route
- **App Store Connect** — evaluated via ASC API v1 (requires `ASC_KEY_ID` etc.)
- **Advisor run** — re-uses findings from the latest complete advisor scan

---

## How to Run the Workbook

### Via Ops Console UI

Navigate to `/advisor/workbooks/mobile` in the ops-console.
Results load automatically. Use **Export JSON** to download a report.

### Via API

```bash
curl /api/advisor/workbooks/mobile | jq .
```

Response shape:
```json
{
  "workbook_id": "mobile-release-readiness",
  "run_id": "uuid or null",
  "results": [
    { "rule": { "id": "ios-ci-green", ... }, "passed": true, "skipped": false }
  ],
  "pass_count": 8,
  "fail_count": 1,
  "skip_count": 1,
  "ready": false
}
```

---

## Enabling App Store Connect Checks

App Store Connect rules show `skipped` unless these env vars are set:

```bash
ASC_KEY_ID=           # API key ID from App Store Connect → Integrations → API Keys
ASC_ISSUER_ID=        # Issuer ID from the same page
ASC_KEY_CONTENT=      # Base64-encoded .p8 file: base64 -i AuthKey_KEYID.p8
ASC_APP_ID=           # Numeric app ID from App Store Connect app URL
```

Set these in `.env.local` for local development or as GitHub Actions secrets for CI.

---

## Adding Rules

1. Add a new entry to `platform/advisor/rulesets/mobile-release-readiness.yaml`.
2. If the rule requires a new external API, add a check function to
   `platform/advisor/sources/appstoreconnect.ts` (or create a new source file).
3. Add evaluation logic in `apps/ops-console/app/api/advisor/workbooks/mobile/route.ts`
   — map the rule `id` to the appropriate check.
4. Run `GET /api/advisor/workbooks/mobile` locally to verify the rule appears.
5. Commit with `feat(advisor): add mobile rule {id}`.

---

## Suppressing False Positives

Rules evaluated by the **advisor run** can only be suppressed by fixing the underlying issue.
Rules evaluated via **filesystem** or **ASC** can be conditionally skipped by:

1. Adding a `skip_reason` override in the route handler (document why).
2. Marking the rule with `severity: info` in the ruleset YAML (no remediation required).

---

## Related

- `platform/advisor/rulesets/mobile-release-readiness.yaml` — ruleset definition
- `platform/advisor/sources/appstoreconnect.ts` — ASC API source
- `apps/ops-console/app/advisor/workbooks/mobile/page.tsx` — workbook UI
- `apps/ops-console/app/api/advisor/workbooks/mobile/route.ts` — evaluation logic
- `docs/ops/ODOO_IOS_APP.md` — iOS app setup and Fastlane runbook
- `docs/catalog/mobile.catalog.json` — mobile catalog
