# Vercel Monorepo — ops-console

## Contract

**One Vercel Project per deployable. Root Directory = `apps/ops-console`.**

This repo uses **pnpm workspaces + Turborepo**. Vercel's skip-unaffected behavior
requires the deployed app to be a registered workspace member with a unique package name.

---

## Workspace registration

`pnpm-workspace.yaml` at repo root includes `apps/*`:

```yaml
packages:
  - "apps/*"      # ← ops-console + any future apps/
  - "web/*"
  - "web/apps/*"
  - "pkgs/*"
  - "templates/*"
```

`apps/ops-console/package.json` name: **`odooops-console`** (unique, no conflicts).

---

## Skip-unaffected builds

`apps/ops-console/vercel.json` sets `ignoreCommand`:

```json
"ignoreCommand": "bash -lc 'BASE=${VERCEL_GIT_PREVIOUS_SHA:-origin/main}; git diff --name-only \"$BASE\" \"$VERCEL_GIT_COMMIT_SHA\" | grep -qE \"^apps/ops-console/\" && exit 1 || exit 0'"
```

**Exit code semantics (Vercel convention, opposite of UNIX norms):**
- `exit 0` → Vercel **skips** the build (nothing relevant changed)
- `exit 1` → Vercel **proceeds** with the build

**Logic**: diffs from `VERCEL_GIT_PREVIOUS_SHA` (base) to `VERCEL_GIT_COMMIT_SHA` (head).
Falls back to `origin/main` when the SHA env var isn't set. PR-safe because it uses
the actual base SHA, not `HEAD~1` which breaks on squash/rebase/shallow clones.

**When to expand the regex**: if `ops-console` starts importing `@ipai/*` workspace
packages from `pkgs/`, update the regex to `^(apps/ops-console|pkgs)/` so those
changes also trigger a rebuild.

**Shallow clone caveat**: Vercel shallow-clones at `--depth=10` by default. If your
base commit is more than 10 commits back, the diff may be incomplete. For most PR
workflows this is fine. For long-lived branches, increase depth in your CI or rely
on Vercel's own monorepo change detection instead of `ignoreCommand`.

**Upload scope**: `apps/ops-console/.vercelignore` excludes all unrelated monorepo
paths (addons, scripts, other apps, pkgs) from the Vercel upload, reducing bundle
size and deploy time.

---

## Internal workspace packages

Packages in `pkgs/` are available via `workspace:*` if ops-console ever needs them:

| Package | Name |
|---------|------|
| `pkgs/ipai-ai-sdk` | `@ipai/ai-sdk` |
| `pkgs/ipai-design-tokens` | `@ipai/design-tokens` |
| `pkgs/env-config` | (check package.json) |

To add one:
```bash
pnpm --filter odooops-console add @ipai/ai-sdk@workspace:*
```

---

## Linking via CLI (no UI)

```bash
# From repo root — link ops-console as its own Vercel Project
cd apps/ops-console
GITHUB_TOKEN="" vercel link --repo

# Set Root Directory in the linked project (first deploy only)
vercel env pull .env.local
```

Vercel automatically detects `pnpm-workspace.yaml` and sets the dependency graph.

---

## Environment variables

All secrets are managed via macOS Keychain locally and Supabase Vault in production.
Never commit `.env*` files.

```bash
# Regenerate .env.local from Keychain
./scripts/secrets/gen-env-local.sh

# Also sync AI/Vercel keys to Supabase Vault
./scripts/secrets/gen-env-local.sh --sync
```

Required env vars for Vercel Project settings:

| Variable | Source |
|----------|--------|
| `SUPABASE_MANAGEMENT_API_TOKEN` | Supabase dashboard → Account → Tokens |
| `NEXT_PUBLIC_SUPABASE_PROJECT_REF` | `spdtwktxdalcfigzeqrz` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase project → API settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase project → API settings |
| `AI_GATEWAY_API_KEY` | vercel.com/[team]/~/ai-gateway/api-keys |
| `VERCEL_API_TOKEN` | vercel.com/account/tokens |

---

## Previews

Every PR/branch push to a non-production branch automatically creates a **Preview deployment** with
its own unique URL. Previews are the primary review surface for UI changes.

- Preview URL is reported back to the PR via the Vercel for GitHub check.
- Reviewers use the **Vercel Toolbar** on the Preview URL to leave inline comments.
- All Preview comments must be resolved before merge (PR template enforces this).

Full details: `docs/ops/VERCEL_PREVIEWS.md`

---

## Related runbooks

| Doc | Purpose |
|-----|---------|
| `docs/ops/VERCEL_PREVIEWS.md` | Preview deployments, Toolbar comments, reviewer workflow |
| `docs/ops/SUPABASE_VERCEL.md` | Supabase↔Vercel env var sync, security rules, local workflow |
| `docs/ops/SUPABASE_N8N.md` | Automation plane: DB Webhooks → n8n → Slack/GitHub |
| `docs/ops/SUPABASE_PLATFORM_KIT.md` | Management API surfaces in ops-console (projects, branches, logs, security) |
| `docs/ops/SUPABASE_METRICS.md` | Prometheus Metrics API scrape endpoint + collector setup |
| `docs/ops/ODOO_SH_EQUIVALENT_MATRIX.md` | Full capability matrix: Odoo.sh vs Vercel Previews vs Supabase Platform Kit |
| `docs/ops/VERCEL_AI_OBS_TEAM.md` | AI Gateway (Team) + Observability constraints + ops.* fallback |
| `docs/ops/contracts/n8n_event.schema.json` | Canonical event payload schema for all automation triggers |
| `docs/ops/DIGITALOCEAN_OBSERVABILITY.md` | DO Monitoring API + droplet health scaffold pages |
| `docs/ops/VERCEL_TEMPLATES_EXAMPLES.md` | How to harvest Vercel templates/examples without forking |
| `docs/ops/VERCEL_PRODUCTION_CHECKLIST_SSOT.md` | Pre/post-deploy checklist, Core Web Vitals targets, rollback runbook |
| `docs/ops/SUPABASE_EXAMPLES_UI_ADOPTION.md` | Supabase examples + UI Library + Platform Kit adoption contract |
| `docs/agents/VERCEL_CLAUDE_CODE.md` | Route Claude Code through Vercel AI Gateway |
| `docs/ops/CLOUDFLARE_DNS_SSOT.md` | Cloudflare DNS SSOT, drift checker, SSL rules |

---

## Enterprise baseline (next-enterprise contracts)

PR gates aligned to the Blazity/next-enterprise standard:

| Gate | Workflow | What it checks |
|------|----------|----------------|
| Check | `.github/workflows/ops-console-check.yml` | ESLint + TypeScript typecheck + Prettier format |
| E2E | `.github/workflows/ops-console-playwright.yml` | Playwright smoke tests (chromium) |
| Bundle size | `.github/workflows/ops-console-bundle-size.yml` | Build size delta reported on every PR |

All three workflows are **path-filtered** to `apps/ops-console/**` — they only run when
ops-console files change.

**App-level configs added:**

| File | Purpose |
|------|---------|
| `apps/ops-console/eslint.config.mjs` | ESLint flat config (`next/core-web-vitals + typescript`) |
| `apps/ops-console/prettier.config.mjs` | Prettier formatting rules |
| `apps/ops-console/.prettierignore` | Prettier exclusions (`.next/`, `node_modules/`, etc.) |
| `apps/ops-console/instrumentation.ts` | OTel stub — activate by installing `@vercel/otel` + setting `OTEL_EXPORTER_OTLP_ENDPOINT` |

---

## Turbo pipeline

`turbo.json` at repo root handles build caching with `^build` dependencies.
Once ops-console is a workspace member, `turbo build --filter=odooops-console`
builds only ops-console and its upstream workspace deps.

```bash
pnpm --filter odooops-console build
pnpm --filter odooops-console dev
```

---

**See also**: `docs/ops/VERCEL_DOCS_SSOT.md` — canonical Vercel docs URLs (MCP, monorepos, previews, AI Gateway).
