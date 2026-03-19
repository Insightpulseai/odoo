# Secrets Policy

> Non-negotiable rules for secret management across the Insightpulseai stack.

## Core Rules

1. **Never commit secrets to git** — no passwords, tokens, API keys, JWTs, or private keys
2. **Each platform owns its secrets** — no cross-pollination
3. **Separate secret sets per environment** — dev/staging/prod must not share keys
4. **Rotation must not require full redeploy** — prefer platform-native secret stores

---

## Secret-of-Record Model

### Supabase Vault + Edge Function Secrets

**Use for:**
- Edge Function runtime secrets (service keys, API tokens, webhook secrets)
- Database-side secrets (if using Vault patterns)
- Anything that must never leave Supabase execution context

**Rule:** Supabase secrets are authoritative for Supabase code (Edge Functions + DB tasks).
Do not mirror these into GitHub/Vercel.

### Vercel Environment Variables

**Use for:**
- Next.js runtime secrets needed by Vercel (server routes, ISR, cron, middleware)
- Supabase public config (`SUPABASE_URL`, anon key) + Vercel-only integrations
- OAuth client secrets only if the OAuth flow runs in Vercel

**Rule:** Vercel secrets are authoritative for Vercel apps.
Vercel should not hold `service_role` unless there is a specific, controlled need.

### GitHub Actions Secrets

**Use for:**
- CI-only credentials (deploy tokens, environment bootstrapping tokens)
- Automation secrets for GitHub workflows

**Rule:** GitHub secrets are for CI/CD, not application runtime.
They should not become an accidental "master vault."

### DigitalOcean / Container Env

**Use for:**
- Odoo runtime secrets (DB credentials, admin passwords)
- Superset runtime secrets (`SUPERSET_SECRET_KEY`, DB connection strings)
- n8n credentials

**Rule:** Runtime secrets injected via DO env vars or container environment only.

---

## What Goes Where

| Secret Type | Store In | Why |
|---|---|---|
| Supabase `service_role` | Supabase Edge secrets (preferred) | Keep privileged key server-side, close to DB |
| Supabase `anon` + `SUPABASE_URL` | Vercel env | Public-ish app config |
| Third-party API keys (backend logic) | Supabase Edge secrets / Vault | Centralized, least exposure |
| OAuth client secret (Next.js auth) | Vercel env | Needed at Next.js runtime |
| GitHub deploy token / PAT | GitHub Actions secrets | CI-only |
| Slack webhook/signing secret | Supabase Edge secrets | Webhook validation at ingress |
| n8n credentials | n8n runtime (not git) | Keep out of repo/CI |
| Odoo DB credentials | DO env vars / container env | Runtime injection only |
| Superset secrets | DO env vars / container env | See `infra/superset/env/.env.superset.example` |

---

## Patterns to Follow

### Pattern A: Supabase as Broker

If a Vercel app needs to call third-party APIs, do not put those keys in Vercel.

```
Vercel → calls Supabase Edge Function → Edge Function holds the secret → returns sanitized response
```

This keeps secrets centralized and reduces blast radius.

### Pattern B: Vercel Owns User-Facing Auth Secrets

If auth callback + session handling is in Next.js:
- Keep OAuth client secret in Vercel env
- Keep `SUPABASE_URL`/anon in Vercel env (expected)
- Avoid `service_role` in Vercel unless unavoidable

### Pattern C: GitHub Only for Deployment Plumbing

If GitHub needs to push migrations / deploy functions:
- GitHub stores a token that can deploy to Supabase/Vercel
- GitHub does not store every downstream API key

---

## Environment Strategy

Separate secret sets per env in each platform:

| Platform | Dev | Staging | Prod |
|---|---|---|---|
| Supabase | project_dev secrets | project_staging secrets | project_prod secrets |
| Vercel | `development` env vars | `preview` env vars | `production` env vars |
| GitHub | `dev` environment secrets | `staging` environment secrets | `prod` environment secrets |
| DO/Containers | dev container env | staging container env | prod container env |

**Never share the same API key across envs unless the provider forces you to.**

---

## Repo Enforcement

- `.gitignore` patterns prevent committing real env files
- `.github/workflows/secrets-scan.yml` runs gitleaks/trufflehog or regex gate on PRs
- CI fails if any secret pattern is detected in diff
- Only `.env.example` and `.env.*.example` files are committed (placeholders only)

---

## Footguns to Avoid

1. **`service_role` in Vercel** — #1 footgun. Prefer Edge Function brokering.
2. **GitHub as master vault** — GitHub secrets should not hold every downstream API key.
3. **Shared keys across envs** — dev key in prod is a blast-radius amplifier.
4. **Secrets in docker-compose** — use env_file references to gitignored files only.
5. **Secrets in CI logs** — mask all secret references in workflow outputs.
