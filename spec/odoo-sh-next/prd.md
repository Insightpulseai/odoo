# PRD: Odoo.sh Next (Improved Continuous Integration + Hosting for Odoo)

## 0) Summary

Odoo.sh Next is an API-first, reproducible, portable CI/CD + hosting platform for Odoo that keeps the core Odoo.sh ergonomics (dev/staging/prod branches, automated tests, SSH access, backups/monitoring) while eliminating UI dependency and adding modern delivery primitives: ephemeral preview envs, signed builds, policy-driven access, and infra portability.

## 1) Problem

Teams building Odoo customizations need:

- Fast feedback on every change
- Isolated environments per feature/PR
- Safe promotion to production with rollback
- Reliable backups + restore workflows
- SSH access for debugging with governance
- An automation surface suitable for CI runners, scripts, and agentic workflows

Current "CI-hosting" patterns often force manual UI steps, are hard to reproduce, or lock teams into a single vendor runtime model.

## 2) Goals

1. **Full automation surface**: 100% parity between UI and CLI/API for environment lifecycle.
2. **Ephemeral previews**: One preview per PR/branch with automated teardown and cost caps.
3. **Reproducible, signed releases**: Immutable artifacts + SBOM + provenance.
4. **Safe promotions**: Blue/green or canary + health gates + instant rollback.
5. **First-class data ops**: Snapshot/restore, masked clones, and promotion-safe database workflows.
6. **Portable runtime**: Managed SaaS OR self-hosted (K8s/VM) with same control plane.

## 3) Non-Goals

- Replacing Odoo's functional modules or business features
- Becoming a generic CI system for arbitrary stacks
- Supporting every possible custom system package (v1 focuses on Odoo-relevant buildpacks)

## 4) Target Users

- **Odoo implementers / dev shops** maintaining custom addons and OCA overlays
- **Product teams** shipping Odoo-based SaaS deployments
- **DevOps/platform engineers** needing policy, automation, and auditability

## 5) User Stories

### CI & Preview

- As a developer, I push a branch and get a live preview URL with test results.
- As a reviewer, I open a PR and see deployment status, logs, and a DB-seeded demo dataset.
- As QA, I can promote the same artifact from preview → staging without rebuilding.

### Production Safety

- As release manager, I deploy to production via a gated pipeline with health checks.
- As on-call, I can roll back to the previous artifact in < 2 minutes.
- As admin, I can rotate secrets without redeploying code.

### Data Ops

- As QA, I can restore a masked copy of production into staging.
- As compliance, I can prove access to production shell is audited and time-bound.
- As engineer, I can download/restore snapshots via CLI.

## 6) Requirements

### 6.1 Control Plane (API + CLI)

- REST + event stream (webhooks) for:
  - create/update/delete environment
  - trigger build
  - deploy artifact
  - promote artifact across envs
  - snapshot/restore database
  - tail logs, read metrics, open exec session
- CLI wraps API and outputs machine-readable JSON (`--json`) for agent runners.

### 6.2 Git Integration

- GitHub + GitLab:
  - PR status checks (build, tests, deploy, health gates)
  - environment URLs posted to PR
  - branch rules mapping to env types (dev/preview/stage/prod)

### 6.3 Build System

- Buildpacks for Odoo:
  - base Odoo image selection (CE/EE supported where licensed)
  - addons layering: custom + OCA + internal
  - python deps pinned (lockfile)
- Output:
  - immutable artifact (OCI image) + SBOM + provenance attestation

### 6.4 Environments

- Environment types:
  - **Dev** (cheap, ephemeral)
  - **Preview** (per PR/branch, TTL + budgets)
  - **Staging** (persistent, promotion target)
  - **Production** (SLO-backed)
- Each env has:
  - web URL + SSH/exec (policy-bound)
  - logs, metrics, traces
  - scheduled jobs controls (cron concurrency)

### 6.5 Data Management

- Snapshots:
  - scheduled (prod required)
  - manual (any env)
- Restore:
  - restore snapshot into staging/preview
  - "masked restore" option (PII scrub rules)
- Data seeding:
  - deterministic demo seed jobs for previews

### 6.6 Observability & SRE

- Metrics: latency, error rate, job durations, worker saturation
- Logs: structured, searchable, retention policies
- Traces: request tracing across proxy → Odoo → Postgres
- SLOs and alerting hooks (Slack/webhook)

### 6.7 Browser Automation & E2E Testing

**Integration Point**: See [`spec/odooops-browser-automation/`](../odooops-browser-automation/) for complete spec.

- **Playwright-first CI**: Every PR/branch triggers:
  1. Environment creation (via control plane API)
  2. E2E test suite against live environment
  3. Artifact upload (traces/videos/screenshots)
  4. Environment teardown (always)
- **Promotion Gate**: Staging/production promotions require:
  - Passing E2E suite for the same commit SHA
  - Test evidence linkable in PR checks
- **Extension Support (Phase 3)**: Optional Chrome extension runner mode
  - Headful Chromium via Xvfb in CI
  - Persistent context for extension pages
  - Idempotent for CI/local development parity
- **Evidence-First**:
  - Videos: `retain-on-failure`
  - Screenshots: `only-on-failure`
  - Traces: `on-first-retry`
  - All artifacts uploaded to GitHub Actions artifacts or platform storage

### 6.8 Security & Compliance

- RBAC with environment scopes
- Just-in-time privileged access (time boxed "break glass")
- Audit logs for:
  - exec/SSH sessions
  - restores, promotions, secret rotations
  - E2E test runs and artifacts
- Secret manager integration:
  - KMS-backed encryption
  - rotation workflows

### 6.9 Portability (Self-host + SaaS)

- Reference deployments:
  - K8s Helm chart
  - VM/docker-compose bundle
- Pluggable storage (S3-compatible) and Postgres (managed or in-cluster)

## 7) MVP Scope (90 days)

- GitHub integration (PR previews)
- Buildpack v1 (Odoo + addons layering)
- Preview envs with TTL + cost cap
- Staging + production with promote + rollback
- Snapshots + restore (prod→staging/preview) with optional masking
- CLI v1 + REST API v1
- Logs + basic metrics dashboard
- **E2E testing integration (Playwright)**: PR checks with environment lifecycle + artifacts
- **Promotion gates**: Require passing E2E before staging/prod promotion

## 8) Success Metrics

- Time from push → live preview: p50 < 6 minutes
- Rollback time: < 2 minutes
- Deploy failure rate (prod): < 5%
- % operations doable via CLI/API: 100% of MVP actions
- Mean time to diagnose (MTTD): reduced by 50% vs baseline

## 9) Risks & Mitigations

- **Odoo version compatibility**: isolate via container images + buildpacks; publish compatibility matrix.
- **Data leakage in masked restores**: require automated PII tests + policy gates.
- **Vendor lock perception**: self-host offering with identical API surface; export tooling.
- **Cost blowups from previews**: TTL defaults + budgets + auto-scale-down.

## 10) Competitive Notes

- Odoo.sh provides integrated Git workflows, automated testing, and SSH access across dev/staging/prod, plus backups/monitoring. Odoo.sh Next keeps these strengths while adding API-first automation, preview environments, signed artifacts, and portability.

## 11) Open Questions (Deferred)

- Multi-region active/active for production
- Advanced DB migration automation (zero-downtime schema deploy)
- Marketplace for buildpacks and addons
