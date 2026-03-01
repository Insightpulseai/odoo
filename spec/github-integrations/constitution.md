# spec/github-integrations/constitution.md
# GitHub Integrations Constitution
# Non-negotiable rules for all GitHub API integrations in the IPAI stack.
#
# Spec: spec/github-integrations/
# Status: active

## Rules (non-negotiable)

1. **Automation identity = GitHub App** — No PATs in CI for automation. All
   background jobs (FixBot, PPM rollups, ops-console ingestion, convergence
   scan) must use a GitHub App installation token, not a personal access token.

2. **OAuth App only for user-delegated actions** — If end-user login via GitHub
   or user-initiated "act as me" flows are needed, an OAuth App is appropriate.
   OAuth is never used for background automation.

3. **Tokens are short-lived installation tokens** — App private key signs a JWT
   (10-minute max), exchanged for an installation token (1-hour max). No static
   tokens survive in secrets stores beyond the private key itself.

4. **Least-privilege permissions** — GitHub App permissions must be declared
   explicitly in the App manifest. Request only what the current integration
   consumes. Expand only via a PR that updates `spec/github-integrations/prd.md`
   permissions table.

5. **Webhook signature verification is mandatory** — Every inbound GitHub webhook
   payload must be verified with HMAC-SHA256 (`X-Hub-Signature-256`) before
   processing. Unverified payloads are rejected with HTTP 401.

6. **Event routing via ops-github-webhook-ingest** — All GitHub webhook events
   enter the stack through `supabase/functions/ops-github-webhook-ingest/`.
   No GitHub webhooks point directly to Next.js API routes or n8n.

7. **Credentials registered in SSOT** — All GitHub App credentials
   (`github_app_id`, `github_app_private_key`, `github_app_client_id`,
   `github_app_client_secret`, `github_app_webhook_secret`) must appear in
   `ssot/secrets/registry.yaml` with status and storage declared.

8. **No console-only changes** — GitHub App settings (permissions, events,
   webhook URL) must be mirrored as comments in the SSOT and provably match.
   The App manifest at `ssot/github/app-manifest.yaml` is the declared intent.

## Non-negotiables

- Never hardcode `GITHUB_APP_ID` or `GITHUB_PRIVATE_KEY` as inline literals in
  any tracked file. They come from environment variables or Supabase Vault only.
- Never log the private key, installation token, or client secret — even in
  error output or debug CI steps.
- Never subscribe to webhook events that are not listed in `prd.md §Permissions`.
- The `github-app-auth` Edge Function is the only code permitted to mint
  installation tokens. All other functions call it or receive the token
  as a caller-supplied header.
