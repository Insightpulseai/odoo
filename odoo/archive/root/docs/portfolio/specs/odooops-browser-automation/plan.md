# Plan — OdooOps Browser Automation Pack

## Phase A — CI wiring (Playwright default)
- Add scripts to create/poll/destroy env via OdooOps API
- Add GitHub Actions workflow running E2E

## Phase B — Evidence + stability
- Enable Playwright trace/video/screenshots
- Add retries + flake controls (only where justified)

## Phase C — Phase 3: Chrome/Extension Mode
- Add optional runner mode that loads Chrome extension in Chromium
- Run via Xvfb in CI

## Phase D — Promotion gate integration (platform-side)
- Record last green suite for env_id/commit_sha
- Require green suite before /promote operations
