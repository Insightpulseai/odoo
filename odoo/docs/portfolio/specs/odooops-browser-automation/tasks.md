# Tasks — OdooOps Browser Automation Pack

## T1: OdooOps API contract usage in CI
- [ ] Implement scripts/odooops/env_create.sh
- [ ] Implement scripts/odooops/env_wait_ready.sh
- [ ] Implement scripts/odooops/env_destroy.sh

## T2: Playwright E2E harness
- [ ] Add tests/e2e/playwright.config.ts
- [ ] Add example smoke test (health/login)

## T3: CI workflow
- [ ] Add .github/workflows/e2e-playwright.yml
- [ ] Upload artifacts (trace/video/screenshots)

## T4: Phase 3 (Chrome/Extension mode)
- [ ] Add extension runner flags + Xvfb support
- [ ] Provide placeholder extension directory hook

## T5: Platform promotion gate (later)
- [ ] Persist E2E pass status per env_id/commit_sha
- [ ] Block promotion unless passing
