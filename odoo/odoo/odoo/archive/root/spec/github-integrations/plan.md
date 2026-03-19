# GitHub Integrations — Implementation Plan

> **Version**: 1.0.0
> **Spec**: `spec/github-integrations/`
> **Status**: Active

---

## Overview

This plan covers setting up the `pulser-hub` GitHub App as the canonical automation
identity for the IPAI stack, with webhook ingestion via Supabase Edge Functions and
event normalization into `ops.*` tables.

---

## Phase 1: GitHub App Setup

1. Register `pulser-hub` GitHub App with permissions from PRD permissions matrix.
2. Install App on `Insightpulseai/odoo` repository.
3. Store credentials per FR-4 in `ssot/secrets/registry.yaml` (names only, values in vault).
4. Create `ssot/github/app-manifest.yaml` declaring permissions and subscribed events.

---

## Phase 2: Webhook Ingestion

1. Deploy `ops-github-webhook-ingest` Supabase Edge Function.
2. Implement `X-Hub-Signature-256` HMAC verification using `github_app_webhook_secret`.
3. Normalize incoming events and insert into `ops.webhook_events` (source = 'github').
4. Store unrecognized event types with `status = 'unhandled'` (never drop events).

---

## Phase 3: Event Normalization

1. Implement normalization for each supported event type per FR-3:
   - `issues` (opened/closed/assigned) to `ops.work_items`
   - `pull_request` (opened/merged/closed) to `ops.runs` (skill PRs)
   - `check_run` / `check_suite` to `ops.run_events`
   - `push` (to main) to `ops.deployments`
   - `installation` to `ops.audit_log`
2. Create `ops-workitems-processor` Edge Function for issue-to-Plane mirroring.
3. Create convergence scan trigger on push-to-main events.

---

## Phase 4: Token Minting

1. Deploy `github-app-auth` Edge Function as the JWT token-minting authority.
2. Implement short-lived installation token generation from App private key.
3. Agents request tokens from this function instead of using long-lived PATs.

---

## Phase 5: Validation

1. Verify webhook delivery via GitHub App settings (recent deliveries tab).
2. Confirm `ops.webhook_events` rows appear for test events.
3. Validate normalization by checking target tables (`ops.work_items`, etc.).
4. Confirm `github-app-auth` returns valid installation tokens.
5. Run `scripts/ci/check_github_app_manifest.sh` to verify manifest matches actual App config.

---

## Dependencies

- Supabase project `spdtwktxdalcfigzeqrz` must be accessible.
- GitHub App registration requires org admin access (one-time manual step).
- `ops.*` schema tables must exist (created by prior migrations).
