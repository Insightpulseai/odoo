# spec/github-integrations/prd.md
# GitHub Integrations — Product Requirements
#
# Spec: spec/github-integrations/
# Status: active

## Context

The IPAI stack interacts with GitHub as a platform via three surfaces:
1. **Inbound events** — GitHub sends webhooks (issues, PRs, checks, pushes)
2. **Outbound API calls** — Agents open PRs, post comments, trigger checks
3. **User auth** (optional) — End-user login to ops-console via GitHub

The GitHub App `pulser-hub` (App ID registered in `ssot/secrets/registry.yaml`)
is the canonical identity for all automation.

## Functional Requirements

### FR-1: GitHub App Identity
- GitHub App `pulser-hub` must be installed on `Insightpulseai/odoo`
- App generates short-lived installation tokens via JWT signing
- `github-app-auth` Edge Function is the token-minting authority

### FR-2: Webhook Ingestion
- All GitHub webhook events route to `ops-github-webhook-ingest` Edge Function
- Function verifies `X-Hub-Signature-256` before any processing
- Normalized rows stored in `ops.webhook_events` (source = 'github')
- Unrecognized event types stored with `status = 'unhandled'` (never dropped)

### FR-3: Event Normalization
Supported events and their normalization targets:

| GitHub Event | Normalized Table | Notes |
|---|---|---|
| `issues` (opened/closed/assigned) | `ops.work_items` | Mirror to Plane via ops-workitems-processor |
| `pull_request` (opened/merged/closed) | `ops.runs` (if skill PR) | via `skill_id` match on branch name |
| `check_run` / `check_suite` | `ops.run_events` | VERIFY step evidence |
| `push` (to main) | `ops.deployments` | Convergence scan trigger |
| `installation` | `ops.audit_log` | App install/uninstall tracking |

### FR-4: Secrets SSOT Coverage
All five GitHub App credentials must be registered:
- `github_app_id` — numeric App ID (not secret; public)
- `github_app_private_key` — RSA private key (critical secret)
- `github_app_client_id` — OAuth client ID (not secret; public)
- `github_app_client_secret` — OAuth client secret (secret)
- `github_app_webhook_secret` — HMAC secret for inbound webhooks (secret)

### FR-5: App Manifest SSOT
- `ssot/github/app-manifest.yaml` declares the App's permissions and subscribed
  events. This is the declared intent; the actual GitHub App settings must match.

## Permissions Matrix (least privilege)

| Permission | Level | Required for |
|---|---|---|
| `issues` | Read & Write | FR-3: issue sync, comment posting |
| `pull_requests` | Read & Write | FR-3: PR open/close, agent PR creation |
| `checks` | Read & Write | FR-3: check_run evidence |
| `contents` | Read | FR-3: push events, file read for diff analysis |
| `metadata` | Read | Required by all Apps |
| `repository_hooks` | Read & Write | Webhook management (if App manages its own hook) |

## Subscribed Webhook Events
- `issues`
- `pull_request`
- `check_run`
- `check_suite`
- `push`
- `installation`

## Out of Scope
- GitHub Actions workflow management (handled by `chore(ci):` commits)
- GitHub Packages (not used)
- GitHub Dependabot alerts via webhook (use Dependabot's own notification channel)
- Copilot API (separate `m365-copilot-broker` function)
