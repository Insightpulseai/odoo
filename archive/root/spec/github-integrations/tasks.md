# GitHub Integrations — Tasks

> **Spec**: `spec/github-integrations/`
> **Status**: Active
> **Last updated**: 2026-03-07

---

## Phase 1: GitHub App Setup

- [ ] **T-01** Register `pulser-hub` GitHub App with least-privilege permissions
- [ ] **T-02** Install App on `Insightpulseai/odoo` repository
- [ ] **T-03** Register all 5 credential names in `ssot/secrets/registry.yaml`
- [ ] **T-04** Create `ssot/github/app-manifest.yaml` with permissions and event subscriptions

## Phase 2: Webhook Ingestion

- [ ] **T-05** Create `ops-github-webhook-ingest` Edge Function scaffold
- [ ] **T-06** Implement `X-Hub-Signature-256` HMAC verification
- [ ] **T-07** Insert normalized rows into `ops.webhook_events` (source = 'github')
- [ ] **T-08** Handle unrecognized event types with `status = 'unhandled'`

## Phase 3: Event Normalization

- [ ] **T-09** Normalize `issues` events to `ops.work_items`
- [ ] **T-10** Normalize `pull_request` events to `ops.runs` (skill PRs by branch name)
- [ ] **T-11** Normalize `check_run` / `check_suite` events to `ops.run_events`
- [ ] **T-12** Normalize `push` (to main) events to `ops.deployments`
- [ ] **T-13** Normalize `installation` events to `ops.audit_log`
- [ ] **T-14** Create `ops-workitems-processor` Edge Function for issue-to-Plane mirroring

## Phase 4: Token Minting

- [ ] **T-15** Create `github-app-auth` Edge Function for JWT-based token minting
- [ ] **T-16** Implement short-lived installation token generation
- [ ] **T-17** Migrate existing agent PAT usage to App installation tokens

## Phase 5: Validation

- [ ] **T-18** Verify webhook delivery in GitHub App recent deliveries
- [ ] **T-19** Confirm `ops.webhook_events` rows for all supported event types
- [ ] **T-20** Validate normalization outputs in target tables
- [ ] **T-21** Create `scripts/ci/check_github_app_manifest.sh` manifest drift check
