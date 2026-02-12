# Constitution — OdooOps Browser Automation Pack

## Purpose
Make browser automation (Playwright E2E + optional Chrome-extension mode) a **platform-native**, reproducible gate tied to environment lifecycle (preview/staging/prod).

## Non-negotiables
1. **Playwright-first**: default runner uses Playwright in CI; no manual extension UI.
2. **Deterministic env-to-tests contract**: tests run against an immutable build (commit SHA).
3. **Idempotent automation**: env create → wait ready → run tests → collect artifacts → teardown.
4. **Zero secrets in repo**: all tokens via CI secrets or platform vault.
5. **Evidence**: videos/traces/screenshots are stored as build artifacts and linkable in PR checks.
