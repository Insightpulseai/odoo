# Tasks: Odoo.sh Next

## A) Spec & Governance

- [ ] Add `spec/odoo-sh-next/adr/0001-initial-architecture.md`
- [ ] Add `spec/odoo-sh-next/security/threat-model.md`
- [ ] Add `spec/odoo-sh-next/openapi.yaml` (API v1 stub)
- [ ] Add `spec/odoo-sh-next/glossary.md`

## B) API v1 (M1)

- [ ] Auth: JWT + RBAC (org/project/env)
- [ ] Endpoints:
  - [ ] POST /projects
  - [ ] POST /envs
  - [ ] POST /builds
  - [ ] POST /deploys
  - [ ] POST /promotions
  - [ ] POST /snapshots
  - [ ] POST /restores
  - [ ] GET /logs/tail
- [ ] Webhooks + event schema
- [ ] Audit log append-only store

## C) Runner + Buildpack v1 (M2)

- [ ] Buildpack: base Odoo + addons layering
- [ ] Cache: python deps + addons artifacts
- [ ] Publish OCI images
- [ ] SBOM generation + provenance signing
- [ ] Unit tests for build graph + cache correctness

## D) Runtime + Routing (M3)

- [ ] Preview env provisioning with TTL
- [ ] Staging env provisioning
- [ ] Production env provisioning
- [ ] Blue/green release switch
- [ ] Exec session broker with audit

## E) Data Ops (M4)

- [ ] Snapshot scheduler
- [ ] Restore prod snapshot to staging/preview
- [ ] Masking rules engine + validation tests
- [ ] Export/import tooling

## F) Observability (M5)

- [ ] Structured logs
- [ ] Metrics + dashboards
- [ ] Tracing plumbing
- [ ] Health gates + release markers

## G) CLI + GitHub Integration (M6)

- [ ] CLI scaffolding + config
- [ ] `odoo-sh-next preview up/down`
- [ ] `odoo-sh-next deploy promote`
- [ ] GitHub PR status checks + comment bot
- [ ] Auto teardown on PR close/merge

## H) Browser Automation & E2E Testing (M7)

**Reference**: See [`spec/odooops-browser-automation/`](../odooops-browser-automation/) for detailed tasks.

- [ ] **API Integration Scripts**:
  - [ ] `scripts/odooops/env_create.sh` (create preview env via API)
  - [ ] `scripts/odooops/env_wait_ready.sh` (poll readiness + get URL)
  - [ ] `scripts/odooops/env_destroy.sh` (cleanup env)
- [ ] **Playwright Harness**:
  - [ ] `tests/e2e/playwright.config.ts` (base config)
  - [ ] `tests/e2e/specs/smoke.spec.ts` (health + login)
  - [ ] Add module-specific E2E specs (as needed)
- [ ] **CI Workflow**:
  - [ ] `.github/workflows/e2e-playwright.yml` (full lifecycle)
  - [ ] Artifact upload (traces/videos/screenshots)
  - [ ] PR check integration with pass/fail status
- [ ] **Phase 3: Chrome Extension Mode** (optional):
  - [ ] Extension runner mode with Xvfb support
  - [ ] Headful Chromium with `--load-extension` args
  - [ ] Persistent context fixture
- [ ] **Promotion Gate**:
  - [ ] Record E2E pass/fail per env_id + commit_sha
  - [ ] Block staging/prod promotion unless E2E green
  - [ ] Evidence links in promotion API/UI
