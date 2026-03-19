# Runbook: iOS Preview Builds CI

> **Branch**: `feat/ios-preview-builds`
> **Workflows**: `.github/workflows/ios-preview-builds.yml`, `.github/workflows/ios-appstore.yml`
> **Last updated**: 2026-03-02

---

## Overview

Two workflows gate iOS compilation and TestFlight distribution:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ios-preview-builds.yml` | push/PR → `main` | Path A: iOS compilation gate (`build-for-testing`)<br>Path B: TestFlight upload (main push only, gated on Path A) |
| `ios-appstore.yml` | push → `main`, `workflow_dispatch` | Standalone TestFlight build + IPA artifact |

Both workflows record truthful `ops.artifacts` rows via Supabase REST after every run
(`status: success | failed | skipped`).

---

## Expected VS Code Problems panel noise

**Do not change the workflows to silence these.** They are editor-only and do not affect CI.

### ❌ `Unrecognized named-value: 'secrets'` (Error)

- **Source**: `github.vscode-github-actions` extension expression parser bug.
- **Where**: Lines with `if: secrets.MATCH_GIT_URL != '' && ...` in both workflows.
- **Reality**: `secrets` context **is valid** in step-level `if:` expressions — explicitly documented
  in [GitHub Actions context availability](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/accessing-contextual-information-about-workflow-runs#context-availability).
- **Action**: None. The extension incorrectly flags this; runtime behaviour is correct.

### ⚠️ `Context access might be invalid: MATCH_GIT_URL` (and the other 6 Apple secrets) — Warning

- **Source**: Extension secrets resolver — the secrets are not yet provisioned in GitHub repo settings.
- **Where**: `env:` blocks of the `Build and upload to TestFlight` steps.
- **Reality**: These warnings are **intentionally correct**. The `if:` guard on the step prevents
  execution when the secrets are absent; the workflows skip cleanly.
- **Resolution**: Warnings clear automatically once the 7 Apple/Fastlane secrets are provisioned
  (see [Provisioning secrets](#provisioning-secrets-to-activate-testflight) below).

### ❌ `Unable to resolve action actions/checkout@v4` — Error (skill-\*.yml only)

- **Source**: Extension marketplace lookup failing when VS Code cannot reach `marketplace.visualstudio.com`.
- **Action**: None — offline/corporate-proxy false-positive. Do not pin or change action refs.

---

## Provisioning secrets to activate TestFlight

All 7 secrets live in `ssot/secrets/registry.yaml` (`status: not_provisioned`).
Add them in **GitHub → repo Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Where to find the value |
|--------|------------------------|
| `MATCH_GIT_URL` | URL of the private cert repo (e.g. `https://github.com/org/certificates`) |
| `MATCH_PASSWORD` | Encryption password chosen when `fastlane match init` was run |
| `APP_STORE_CONNECT_API_KEY_ID` | App Store Connect → Users and Access → Integrations → App Store Connect API |
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | Same page as Key ID |
| `APP_STORE_CONNECT_API_KEY_CONTENT` | Paste full `.p8` contents (including `-----BEGIN/END-----` lines) |
| `APPLE_ID` | Apple ID email used for ASC operations |
| `APP_IDENTIFIER` | iOS bundle ID (e.g. `com.insightpulseai.OdooMobile`) |

Once all 7 are present the `if:` guards evaluate to `true` and the TestFlight steps activate.
The VS Code `Context access might be invalid` warnings will clear on the next extension refresh.

---

## Architecture notes

### Why no `.xcodeproj` in the repo

`apps/odoo-mobile-ios/Package.swift` declares `OdooMobile` as a **`.library` product** — not
an executable app target. This means:

- `xcodebuild build-for-testing` validates iOS compilation without producing a `.app` bundle.
- A runnable `.app` requires adding an `@main` application target (tracked as follow-on work).
- `fastlane match` generates the `.xcodeproj` at CI time as part of the signing flow.

### Why `build-for-testing` instead of `build`

`build-for-testing` compiles all targets for the specified destination (`iOS Simulator`) and
produces test bundles. It validates iOS-specific code paths that `swift test` (macOS target) misses,
without requiring a committed `.xcodeproj`.

Requires **Xcode.app** (not just CLT) selected via `scripts/mobile/verify_xcode.sh` — Xcode.app
resolves SPM package schemes natively.

### ops.artifacts record strategy

Every CI run writes a truthful row regardless of outcome:

```
success  → iOS compilation passed
failed   → iOS compilation failed (reason: IOS_COMPILATION_FAILED | FASTLANE_FAILED | CANCELLED)
```

Idempotent via `Prefer: resolution=ignore-duplicates` + partial unique index
`(kind, sha, env, name) WHERE name IS NOT NULL`.

---

## Verification checklist

- [ ] `ios-preview-builds.yml` runs on every PR that touches `apps/odoo-mobile-ios/**`
- [ ] `simulator-build` job passes (build-for-testing compiles without error)
- [ ] `testflight` job **skips** when Apple secrets are absent (not fails — check job log shows "skipped")
- [ ] `ops.artifacts` row appears after each run: `GET /rest/v1/artifacts?kind=eq.ios_simulator_build`
- [ ] After provisioning secrets: TestFlight job uploads IPA and VS Code warnings clear

---

## Related

- `ssot/secrets/registry.yaml` — secret names, purpose, provisioning status
- `supabase/migrations/20260301000070_ops_artifacts.sql` — base table
- `supabase/migrations/20260301000071_ops_artifacts_hardening.sql` — status/reason/env/name columns
- `scripts/mobile/verify_xcode.sh` — Xcode 16.x selector script
- `apps/odoo-mobile-ios/Package.swift` — SPM package definition
