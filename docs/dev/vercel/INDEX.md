# Vercel Docs Index — Insightpulseai/odoo

> Curated reference: Vercel documentation pages mapped to concrete repo actions.
> Generated: 2026-03-02 | Updated: 2026-03-02 | Source: `ssot/docs/vercel_docs.yaml`
> Update: edit this file + `ssot/docs/vercel_docs.yaml` together.

---

## Index

| Area | Doc page | URL | Why it matters | Repo action | Key setting / file |
|------|----------|-----|----------------|-------------|-------------------|
| **Deployments** | Deployments overview | <https://vercel.com/docs/deployments/overview> | Three environments: **Production** (`main` branch, promoted), **Preview** (all other branches — unique URL per commit), **Development** (`vercel dev` local). Every PR auto-generates a stable preview URL. The `apps/ops-console` Next.js app deploys to Vercel via git push on `main` → production. Root `vercel.json` targets the Python serverless API at `infra/vercel/api/ask.py` — a separate project scope. These two deployments are distinct Vercel projects. | Confirm `infra/vercel/projects/ops-console.json` records `rootDirectory: apps/ops-console`, `productionBranch: main`. Verify no `apps/ops-console/vercel.json` overrides conflict with auto-detection. | `infra/vercel/projects/ops-console.json`; `apps/ops-console/vercel.json` |
| **Deployments** | Git integration — branch-to-environment | <https://vercel.com/docs/git> | Vercel maps `main` → Production, every other branch → Preview. Each Preview deployment gets a stable URL (`ops-console-<hash>-tbwa.vercel.app`) that persists for PR reviews. `VERCEL_GIT_COMMIT_SHA`, `VERCEL_ENV`, `VERCEL_URL` are auto-injected system env vars — do not redefine them. | Ensure `.github/workflows/` has **no** `vercel --prod` CLI calls for `main` (Git integration handles it). If emergency hotfix bypasses GitHub: `vercel deploy --prod --force --token=$VERCEL_TOKEN`. | `productionBranch` in project settings; `VERCEL_ENV` system var |
| **Deployments** | Managing deployments — promote, roll back | <https://vercel.com/docs/deployments/managing-deployments> | Cancel, retry, promote preview to production, or roll back to previous production deployment without a re-build. `vercel promote <deployment-url>` makes a previous deployment the new production in seconds. `vercel rollback` is an alias for the most recent previous deployment. | For rollback: `vercel rollback --token=$VERCEL_TOKEN` (rolls back to previous production). For targeted: `vercel promote <url> --token=$VERCEL_TOKEN`. Record rolled-back deployment URL in `web/docs/evidence/<stamp>/deploy/logs/rollback.log`. | `vercel rollback`; `vercel promote <url>` |
| **Deployments** | Troubleshooting deployments | <https://vercel.com/docs/deployments/troubleshoot-a-deployment> | Deployment failures surface in Build Logs (available in dashboard + `vercel logs <url>`). Common causes: missing env var (`@`-ref not found), `pnpm install --frozen-lockfile` failing on stale lock file, build command exiting non-zero, Edge Function bundle >4 MB. The current all-failing deployments (~22-25s errors) match the `@openai-api-key` missing pattern. | Verify all `@`-referenced vars exist: `vercel env ls --token=$VERCEL_TOKEN`. Fetch live logs: `vercel logs <deployment-url> --token=$VERCEL_TOKEN`. Check `pnpm-lock.yaml` is committed and matches `package.json`. | `vercel logs <url>`; `vercel env ls` |
| **Configuration** | vercel.json configuration reference | <https://vercel.com/docs/project-configuration> | Controls `installCommand`, `buildCommand`, `outputDirectory`, `functions` (max duration, memory, runtime), `rewrites`, `redirects`, `headers`, `regions`, and the env var `@`-reference syntax. The `@`-ref syntax (`"OPENAI_API_KEY": "@openai-api-key"`) pulls from **Vercel project env vars** — completely separate from GitHub Actions secrets. Changing an `@`-ref only takes effect if the referenced var exists in the Vercel project. | Audit root `vercel.json` for every `@<name>` reference and verify each exists in the Vercel project env vars. Current `@`-refs: `@supabase-url`, `@supabase-service-role-key`, `@openai-api-key`, `@supabase-anon-key`. Run: `vercel env ls --token=$VERCEL_TOKEN \| grep -E "supabase\|openai"`. | `vercel.json`; `apps/ops-console/vercel.json` |
| **Configuration** | Build configuration — rootDirectory, framework | <https://vercel.com/docs/deployments/configure-a-build> | `rootDirectory` is the most common monorepo misconfiguration: when null, Vercel builds from repo root (which runs `pnpm install --frozen-lockfile` at root and fails). When set to `apps/ops-console`, Vercel cd's into that directory first. `framework` detector auto-selects Next.js build. `installCommand` at project level overrides the one in `vercel.json`. | Verify `rootDirectory: apps/ops-console` is set in Vercel project settings AND recorded in `infra/vercel/projects/ops-console.json` (SSOT). If `rootDirectory` was ever reset to null, it causes the ~22-25s failure pattern. | `rootDirectory` in project settings; `infra/vercel/projects/ops-console.json` |
| **Environment Variables** | Environment variables | <https://vercel.com/docs/environment-variables> | Three scopes: **Production**, **Preview**, **Development**. Types: **Plain** (visible in logs), **Secret** (encrypted, redacted in UI), **Sensitive** (never shown after creation). System vars (`VERCEL_URL`, `VERCEL_ENV`, `NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA`) are auto-injected. GitHub Actions secrets and Vercel env vars are **entirely separate namespaces** — a GitHub secret `OPENAI_API_KEY` does not satisfy a Vercel `@openai-api-key` reference. | Add missing env vars: `vercel env add OPENAI_API_KEY production --token=$VERCEL_TOKEN`. List all: `vercel env ls --token=$VERCEL_TOKEN`. The Supabase x Vercel integration auto-syncs `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` from Supabase project. | `vercel env add`; `vercel env ls`; Vercel project dashboard |
| **Environment Variables** | Shared environment variables | <https://vercel.com/docs/environment-variables/shared-environment-variables> | Team-level env vars that propagate to **all projects** in the team. Changes update all subscribed projects on next deploy. Useful for shared `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `OPENAI_API_KEY` — avoids per-project duplication and ensures single rotation point. If a project has its own var with the same name, it overrides the shared one. | Check team shared vars: `vercel.com/tbwa/~/settings/environment-variables`. Add shared vars for `SUPABASE_URL` and `SUPABASE_ANON_KEY` if identical across projects. For secrets that differ per project (e.g. `SUPABASE_SERVICE_ROLE_KEY`), keep project-scoped. | vercel.com/tbwa/~/settings/environment-variables |
| **Domains** | Domains overview | <https://vercel.com/docs/domains> | Custom domain assignment, DNS verification (CNAME to `cname.vercel-dns.com`), and SSL/TLS auto-provisioned via Let's Encrypt. Domains can be pinned to Production, a specific branch (staging alias), or a preview alias pattern (`*.ipai-preview.com`). Cloudflare proxy mode: use DNS-only (grey cloud) for `cname.vercel-dns.com` — orange cloud breaks SSL issuance. | All new Vercel subdomains: (1) add to `infra/dns/subdomain-registry.yaml`, (2) run `scripts/dns/generate-dns-artifacts.sh`, (3) register in Vercel project domains. Track in `infra/vercel/projects/*.json`. DNS: `ops-console` → CNAME `cname.vercel-dns.com` (DNS-only in Cloudflare). | `infra/dns/subdomain-registry.yaml`; Vercel project → Domains |
| **Security** | Deployment Protection | <https://vercel.com/docs/security/deployment-protection> | Four protection modes for deployments: **Vercel Authentication** (SSO/email, Team-member only), **Password Protection** (single shared password), **ShareLink** (per-URL token, shareable), **Trusted IPs** (IP allowlist). Preview deployments are publicly accessible by default. Vercel Authentication on Previews limits to team members — prevents leaking staging data. | Enable "Only GitHub users who have collaborator access" or Vercel Authentication for `ops-console` Preview deployments. Production: rely on Next.js auth layer (`supabase/functions` + Supabase Auth). Document in `infra/vercel/projects/ops-console.json`. | Vercel Project Settings → Deployment Protection |
| **Security** | Vercel Firewall (WAF + DDoS) | <https://vercel.com/docs/security/vercel-firewall> | Edge-network WAF with managed OWASP Top 10 rulesets, bot detection, rate limiting, and Attack Mode (blocks all non-human traffic instantly). Custom rules available via `vercel.json` `"firewall"` block or dashboard rule builder. Webhook event `firewall.attack` fires on Attack Mode activation (see Webhooks row). | Add WAF rule for `ops-console`: rate-limit `/api/*` paths to 60 req/min per IP. Configure `firewall.attack` webhook → n8n → Slack `#security` alert. Monitor via Vercel dashboard → Security tab. | `vercel.json` `"firewall"` block; vercel.com/tbwa/~/settings/webhooks |
| **Observability** | Logging and Log Drains | <https://vercel.com/docs/observability/log-drains/log-drains-overview> | Runtime function logs, build logs, and edge middleware logs. Without Log Drains, logs are ephemeral (7-day retention on Pro tier). Log Drains forward to Datadog, Splunk, or custom HTTPS endpoint (e.g. a Supabase Edge Function). `vercel logs <deployment-url>` streams live; `vercel logs <url> --since=<ts>` for historical. | Create `supabase/functions/ops-vercel-log-ingest/` (follows same HMAC-verify pattern as `ops-github-webhook-ingest`). Configure Log Drain in Vercel project → Observability. Use `vercel logs <url> --follow --token=$VERCEL_TOKEN` for real-time debugging. | `vercel logs <url>`; Vercel project → Observability → Log Drains |
| **Webhooks** | Webhooks overview + event catalog | <https://vercel.com/docs/observability/webhooks-overview> | Signed POST (SHA-1 HMAC, header `x-vercel-signature`) on events: `deployment.created`, `deployment.succeeded`, `deployment.error`, `deployment.promoted`, `deployment.ready`, `deployment.canceled`, `project.env-variable.created`, `project.env-variable.removed`, `firewall.attack`, `alerts.triggered`, `domain.purchased`. Team-level registration at `vercel.com/tbwa/~/settings/webhooks`. | Create `supabase/functions/ops-vercel-webhook-ingest/index.ts` — verify `x-vercel-signature` with HMAC-SHA1, route `deployment.error` → Slack alert, `deployment.succeeded` → `ops.platform_events` insert. Register endpoint URL under Team webhooks. | `supabase/functions/ops-vercel-webhook-ingest/`; vercel.com/tbwa/~/settings/webhooks |
| **CLI** | Vercel CLI reference | <https://vercel.com/docs/cli> | Primary automation surface for non-Git-triggered operations: `deploy`, `env`, `domains`, `logs`, `projects`, `pull`, `link`, `rollback`, `promote`, `bisect`. Auth via `vercel login` (browser) or `VERCEL_TOKEN` env var (CI/non-interactive). Rate limit: 12 API calls/min on Free, 120/min on Pro. `vercel pull` downloads env vars into `.vercel/.env.*` for local dev. | Install: `pnpm add -g vercel@latest`. In CI: `--token=${{ secrets.VERCEL_TOKEN }}`. List projects: `vercel projects ls --token=$VERCEL_TOKEN`. Never hardcode token — `ssot/secrets/registry.yaml` tracks `vercel_token` name. | `VERCEL_TOKEN` in GitHub Actions secrets; `ssot/secrets/registry.yaml` |
| **CLI** | Deploying from CLI | <https://vercel.com/docs/cli/deploying-from-cli> | `vercel` → Preview deploy (non-prod). `vercel --prod` → Production deploy. `vercel build` → local build without deploying (testing purposes). Flags: `--force` (skip cache), `--no-wait` (async deploy, returns URL immediately), `--archive=tgz` (send only changed files). In monorepos, run CLI from the app subdirectory or set `rootDirectory`. | Preferred: Vercel GitHub integration handles all deploys automatically. Use CLI only for emergency hotfixes: `cd apps/ops-console && vercel deploy --prod --force --token=$VERCEL_TOKEN`. Note: CLI deploys bypass GitHub PR flow and branch protection. | `vercel deploy --prod`; `vercel build` |
| **CLI** | Project linking (`vercel link`) | <https://vercel.com/docs/cli/project-linking> | `vercel link` creates `.vercel/project.json` (contains `projectId` + `orgId`) in the current directory. This file enables `vercel env pull`, `vercel deploy`, and `vercel logs` to target the correct project without interactive prompts. Commit `.vercel/project.json` to the repo (no secrets). In CI, `VERCEL_ORG_ID` + `VERCEL_PROJECT_ID` env vars override the JSON file. | Create `apps/ops-console/.vercel/project.json` by running `vercel link` in that directory. Commit the file. Set `VERCEL_ORG_ID=team_wphKJ7lHA3QiZu6VgcotQBQM` and `VERCEL_PROJECT_ID=prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX` as GitHub Actions secrets. | `apps/ops-console/.vercel/project.json`; `VERCEL_ORG_ID`; `VERCEL_PROJECT_ID` |
| **Authentication** | Sign In With Vercel | <https://vercel.com/docs/sign-in-with-vercel> | Vercel acts as an OAuth 2.0 / OIDC provider. Allows third-party apps to authenticate users via their Vercel accounts. Scopes: `openid`, `profile`, `email`, `read:deployment`, `write:deployment`. Distinct from using `VERCEL_TOKEN` for service-account CI/CD automation. Useful if `ops-console` needs to take Vercel API actions on behalf of individual team members (e.g. trigger deploys, read logs). | If `ops-console` needs Vercel OAuth: register app at `vercel.com/account/tokens` → "OAuth App". Store client secret in Supabase Vault (`vercel_oauth_client_secret`). For CI automation, use `VERCEL_TOKEN` (service account) — not OAuth. | Vercel Account → OAuth Apps; Supabase Vault for OAuth client secret |
| **Integrations** | Supabase × Vercel integration | <https://vercel.com/integrations/supabase> | First-party integration: auto-syncs `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (and JWT secret) into Vercel env vars on connection. With **Supabase Branching** enabled, creates a separate Supabase preview branch per Vercel preview deployment (requires Pro plan + `supabase/config.toml` branching block). Integration already active for `spdtwktxdalcfigzeqrz`. | Verify sync: `vercel env ls --token=$VERCEL_TOKEN \| grep SUPABASE`. For branching: add `[branching]\nenabled = true\nexperimental = true` to `supabase/config.toml`. This ties every Vercel Preview URL to an isolated Supabase preview DB. | `supabase/config.toml` branching block; Vercel integrations dashboard |
| **AI** | AI SDK (Vercel AI SDK) | <https://vercel.com/docs/ai-sdk> | TypeScript SDK for streaming AI UIs — `streamText`, `generateObject`, `generateText`, `useChat`, `useCompletion`. Unified provider interface supports OpenAI, Anthropic, Google, Groq without vendor lock-in. `generateObject` with Zod schema produces structured data directly from LLM calls — useful for Odoo record creation from natural language. | Check `apps/ops-console/package.json` for `ai` package version (target `^4.x`). Use `generateObject` for AI-assisted Odoo field population. Streaming reduces perceived latency for expense report generation. AI calls should route through AI Gateway (see next row). | `apps/ops-console/package.json`; `ai` npm package |
| **AI** | AI Gateway | <https://vercel.com/docs/ai-gateway> | **Already active** — 5 named keys provisioned (kit, n8n, GEMINI, saricoach). Unified API endpoint (`https://ai-gateway.vercel.sh/v1`) for hundreds of LLM models. One `AI_GATEWAY_API_KEY` replaces per-provider keys. Model format: `provider/model-name` (e.g. `anthropic/claude-sonnet-4.5`, `openai/gpt-5.2`). Key features: **zero token markup**, automatic retry/fallback, embeddings, spend monitoring, BYOK. The `n8n` key confirms n8n workflows already route AI calls through Gateway — not directly to OpenAI/Anthropic. Compatible with AI SDK, OpenAI SDK, Anthropic SDK, cURL. | Per consumer: create named key at `vercel.com/tbwa/~/ai-gateway/keys`. For `ops-console`: set `AI_GATEWAY_API_KEY` Vercel env var from the `kit` key (or new key). Update AI SDK: `model: 'anthropic/claude-sonnet-4.5'`. Legacy `"AI Gateway v0 Key"` (28d old) — retire it. Track key names (never values) in `ssot/docs/vercel_docs.yaml`. | `AI_GATEWAY_API_KEY`; `https://ai-gateway.vercel.sh/v1`; `ssot/docs/vercel_docs.yaml` |
| **AI** | Agents, MCP Servers, and Sandboxes | <https://vercel.com/docs/ai/agents-and-tools/mcp> | Vercel hosts MCP servers as serverless functions (Next.js Route Handlers or Edge Functions). `v0` agent can create UI from prompts. Sandboxes provide isolated execution environments for AI-generated code. Vercel-hosted MCP could replace the current DigitalOcean-hosted `mcp.insightpulseai.com` (`pulse-hub-web-an645.ondigitalocean.app`) for lower cold-start latency. | Evaluate: migrate lightweight MCP tools from DigitalOcean App Platform to Vercel Functions for cost and latency reduction. SSOT for MCP server definitions: `mcp/servers/`. Each Vercel-hosted MCP function must use `VERCEL_TOKEN` or `SUPABASE_SERVICE_ROLE_KEY` from Vercel env vars (no hardcoded secrets). | `mcp/servers/`; Vercel project → Functions |

---

## Quick reference: highest-leverage settings per file

### `infra/vercel/projects/ops-console.json` (SSOT — do not edit Vercel dashboard without syncing here)

```json
{
  "projectId": "prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX",
  "orgId": "team_wphKJ7lHA3QiZu6VgcotQBQM",
  "name": "ops-console",
  "rootDirectory": "apps/ops-console",
  "framework": "nextjs",
  "productionBranch": "main",
  "installCommand": "pnpm install --frozen-lockfile",
  "nodeVersion": "20.x"
}
```

### `apps/ops-console/.vercel/project.json` (commit this — no secrets)

```json
{
  "projectId": "prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX",
  "orgId": "team_wphKJ7lHA3QiZu6VgcotQBQM"
}
```

### `vercel.json` (root — targets Python serverless API only)

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "version": 2,
  "installCommand": "pnpm install --frozen-lockfile",
  "framework": null,
  "functions": {
    "infra/vercel/api/ask.py": { "runtime": "python3.11", "maxDuration": 30 }
  },
  "env": {
    "SUPABASE_URL": "@supabase-url",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase-service-role-key",
    "OPENAI_API_KEY": "@openai-api-key"
  }
}
```

⚠️ All `@`-referenced env vars must exist in the Vercel project before deploy or it fails instantly.
Verify: `vercel env ls --token=$VERCEL_TOKEN | grep -E "supabase|openai"`

### GitHub Actions workflow: Vercel deploy (emergency manual)

```yaml
name: Emergency Vercel Deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        type: choice
        options: [production, preview]
        default: preview

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - run: pnpm install --frozen-lockfile
        working-directory: apps/ops-console
      - run: |
          vercel deploy ${{ inputs.environment == 'production' && '--prod' || '' }} \
            --token=$VERCEL_TOKEN \
            --yes
        working-directory: apps/ops-console
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

### Vercel CLI: common operations

```bash
# Install / update CLI
pnpm add -g vercel@latest

# Link project (run once per machine/directory; creates .vercel/project.json)
cd apps/ops-console && vercel link --token=$VERCEL_TOKEN

# Pull env vars for local dev (creates .vercel/.env.development.local — gitignored)
cd apps/ops-console && vercel env pull .vercel/.env.development.local --token=$VERCEL_TOKEN

# List current env vars
vercel env ls --token=$VERCEL_TOKEN

# Add missing env var (prompts for value)
vercel env add OPENAI_API_KEY production --token=$VERCEL_TOKEN

# Deploy preview
cd apps/ops-console && vercel deploy --token=$VERCEL_TOKEN

# Deploy to production (emergency only — prefer Git integration)
cd apps/ops-console && vercel deploy --prod --force --token=$VERCEL_TOKEN

# Rollback to previous production deployment
vercel rollback --token=$VERCEL_TOKEN

# Promote a preview URL to production
vercel promote https://ops-console-abc123-tbwa.vercel.app --token=$VERCEL_TOKEN

# Tail live function logs
vercel logs https://ops-console.vercel.app --follow --token=$VERCEL_TOKEN

# List deployments
vercel list --token=$VERCEL_TOKEN
```

### AI Gateway — integration patterns

**TypeScript (AI SDK v5/v6) — provider-prefixed model name:**

```typescript
import { generateText, streamText } from 'ai';

// model = "provider/model-name"
const { text } = await generateText({
  model: 'anthropic/claude-sonnet-4.5',
  prompt: 'Summarise this Odoo expense report...',
});

// structured output (Zod schema → typed object)
import { generateObject } from 'ai';
import { z } from 'zod';
const { object } = await generateObject({
  model: 'openai/gpt-5.2',
  schema: z.object({ vendor: z.string(), amount: z.number(), currency: z.string() }),
  prompt: 'Extract expense fields from receipt text...',
});
```

**OpenAI SDK compat (Python or Node) — swap baseURL:**

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('AI_GATEWAY_API_KEY'),
    base_url='https://ai-gateway.vercel.sh/v1',
)
response = client.chat.completions.create(
    model='anthropic/claude-sonnet-4.5',  # provider-prefixed
    messages=[{'role': 'user', 'content': '...'}],
)
```

**cURL (direct API):**

```bash
curl -X POST "https://ai-gateway.vercel.sh/v1/chat/completions" \
  -H "Authorization: Bearer $AI_GATEWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "anthropic/claude-sonnet-4.5", "messages": [{"role":"user","content":"..."}]}'
```

**Add gateway key to Vercel project:**

```bash
vercel env add AI_GATEWAY_API_KEY production --token=$VERCEL_TOKEN
vercel env add AI_GATEWAY_API_KEY preview --token=$VERCEL_TOKEN
```

---

### `supabase/config.toml` — Supabase Branching block (for Vercel preview isolation)

```toml
[branching]
enabled = true
experimental = true
```

---

## Related files in this repo

| File | Purpose |
|------|---------|
| `infra/vercel/projects/ops-console.json` | Vercel project settings SSOT (projectId, orgId, rootDirectory) |
| `vercel.json` | Root Vercel config — Python serverless API (`infra/vercel/api/ask.py`) |
| `apps/ops-console/vercel.json` | ops-console Next.js Vercel config |
| `apps/ops-console/.vercel/project.json` | CLI project link file (to be committed) |
| `infra/dns/subdomain-registry.yaml` | DNS SSOT — source for all Vercel domain CNAME records |
| `supabase/config.toml` | Supabase project config — branching block ties to Vercel previews |
| `ssot/docs/vercel_docs.yaml` | Machine-readable SSOT for this docs index |
| `ssot/secrets/registry.yaml` | Tracks `vercel_token`, `vercel_org_id`, `vercel_project_id` names |
| `supabase/functions/ops-vercel-webhook-ingest/` | Vercel webhook handler (to be created) |
| `.github/workflows/` | 153 workflows — search for `vercel` to find CLI-based deploy steps |
| GitHub Actions secrets `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | CLI auth for non-Git-triggered deploys |

---

## See also

- [`docs/dev/github/INDEX.md`](../github/INDEX.md) — GitHub documentation reference
- [`docs/dev/vscode/INDEX.md`](../vscode/INDEX.md) — VS Code tooling reference
- [`docs/runbooks/SUPABASE_VERCEL_INTEGRATION_HEALTH.md`](../../runbooks/SUPABASE_VERCEL_INTEGRATION_HEALTH.md) — Integration health runbook
- [`ssot/docs/vercel_docs.yaml`](../../../ssot/docs/vercel_docs.yaml) — Machine-readable catalog
- [`infra/vercel/projects/ops-console.json`](../../../infra/vercel/projects/ops-console.json) — Project SSOT
