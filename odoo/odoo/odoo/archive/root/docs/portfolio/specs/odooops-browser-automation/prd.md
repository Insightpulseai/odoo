# PRD — OdooOps Browser Automation Pack

## 0) Summary
This pack integrates E2E automation into OdooOps (Odoo.sh clone) so every branch/PR can spawn a preview environment and run Playwright tests, with an optional Chromium extension mode for flows that require an extension runtime.

## 1) Goals
- G1: PR → preview env → Playwright E2E → PR status (pass/fail) with artifacts
- G2: Promote gates: staging requires passing E2E suite from the same build artifact
- G3: Extension-compatible runner (Phase 3): run Playwright with a loaded Chrome extension in headful Chromium (CI-friendly via Xvfb)
- G4: Evidence-first: traces/videos/screenshots uploaded per run

## 2) Non-goals
- Building a custom extension UI harness (we support loading an existing extension)
- Depending on interactive Chrome UI for automation

## 3) Platform Integration Points
### 3.1 Control Plane APIs (contract)
- POST /projects/{id}/envs  -> create env for branch/stage (returns env_id)
- GET  /envs/{env_id}       -> returns url, readiness, commit_sha, metadata
- POST /envs/{env_id}/destroy
- (Optional) POST /envs/{env_id}/exec for smoke probes

### 3.2 CI Runner Contract
CI gets:
- ODOOOPS_API_BASE
- ODOOOPS_PROJECT_ID
- ODOOOPS_TOKEN
CI performs:
1) create env (branch/sha)
2) poll readiness + get env URL
3) run Playwright with BASE_URL
4) upload artifacts
5) destroy env (always)

## 4) Chrome/Extension Mode (Phase 3)
- Provide a runner that launches Chromium with:
  - --disable-extensions-except=<path>
  - --load-extension=<path>
- Use Playwright persistent context to control pages and (if needed) extension pages
- Use Xvfb in CI for headful mode when extension requires it

## 5) Acceptance Criteria
- PR checks show: env URL + E2E pass/fail + artifacts
- Staging promotion blocked unless suite passes on same commit artifact
- Extension mode runnable in CI (Linux) and locally
