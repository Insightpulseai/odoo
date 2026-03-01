# Constitution — IPAI GitHub App Integration

> Governing principles for the GitHub App ↔ Supabase ↔ Odoo integration layer.
> Ratified: 2026-03-01

---

## 1. Purpose

Define non-negotiable rules for how this repo builds, deploys, and operates a first-class GitHub App integration using Supabase Edge Functions as the control plane, with an optional thin Odoo connector.

## 2. Constraints

| # | Constraint | Rationale |
|---|-----------|-----------|
| C1 | **Use a GitHub App, not PATs or OAuth Apps, for platform integration.** GitHub Apps provide centralized webhooks, scoped installation tokens, and don't require service-user accounts. | GitHub's recommended integration type for automation + webhooks. |
| C2 | **Supabase is the control plane; Odoo is a thin consumer.** GitHub App auth (JWT + installation tokens), webhook ingestion, and event processing live in Supabase Edge Functions. Odoo gets an optional `ipai_github_connector` for linking records to GitHub objects. | Keeps credentials + complexity out of the ERP; preserves SSOT boundaries. |
| C3 | **App private key MUST live in Supabase Vault only.** The RS256 private key used for JWT signing never appears in Git, logs, CI output, or Odoo database. | A leaked private key compromises all installations. |
| C4 | **Webhook signatures MUST be verified** using HMAC-SHA256 (`X-Hub-Signature-256`) before any payload is processed. | Prevents spoofed webhook injection. |
| C5 | **Idempotency by `X-GitHub-Delivery` header.** Every webhook handler must deduplicate on this UUID before executing side effects. | GitHub may redeliver; without dedupe, events process multiple times. |
| C6 | **Installation tokens are short-lived (1 hour).** Token broker must cache per `installation_id` with TTL < expiry. Never store installation tokens long-term. | Follows GitHub's security model; leaked tokens auto-expire. |
| C7 | **Least-privilege permissions.** Only request the permissions the app actually uses. Start minimal (e.g., `issues: read`, `pull_requests: read`, `checks: write`); expand only when a concrete use case requires it. | GitHub's official recommendation. |
| C8 | **Event allowlist.** Only subscribe to events the app processes. Do not subscribe to `*` or broad categories. | Reduces webhook volume and attack surface. |
| C9 | **Secrets registry.** All GitHub App secrets (`github_app_id`, `github_app_private_key_pem`, `github_webhook_secret`) must be registered in `ssot/secrets/registry.yaml` with consumers listed. | Aligns with repo secrets policy. |
| C10 | **No console-only config.** Every GitHub App setting (permissions, events, webhook URL) must have a corresponding artifact in the repo (SSOT YAML or doc). | Aligns with platform rule: no console-only infrastructure changes. |

## 3. Security

- GitHub App private key: Supabase Vault only. Never logged, never in `.env` files.
- Webhook secret: Supabase Vault + GitHub App settings. Rotated on compromise.
- Installation tokens: cached in-memory or KV with TTL; never persisted to disk/DB.
- No personal access tokens for automation; use installation tokens exclusively.

## 4. Quality Gates

| Gate | Requirement |
|------|-------------|
| PR merge | Webhook signature verification tests pass (valid/invalid/missing). |
| PR merge | No secrets in diff (checked by `ssot-surface-guard.yml`). |
| PR merge | `ssot/secrets/registry.yaml` has entries for all 3 GitHub App secrets. |
| Deploy | Webhook endpoint returns `200` for valid signed ping event. |

## 5. Governance

- Amendments require updating this file + PR review.
- Cross-boundary changes (GitHub ↔ Supabase ↔ Odoo) require a contract doc per Rule 9.
