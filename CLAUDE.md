# CLAUDE.md — Odoo Project (SSOT)

> This file is the **single source of truth** for AI agent behavior in this repo.
> Nested `CLAUDE.md` files may refine but never contradict these rules.
> Detailed reference docs live in `docs/ai/` — this file stays compact.

---

## Operating Contract

You are an execution agent. Take action, verify, commit. No guides, no tutorials.

1. **Execute** the change / deploy / migration
2. **Verify** with deterministic checks
3. **Evidence** in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
4. **Commit** with OCA-style message + push

**Output format**: Outcome (1-3 lines) + Evidence + Verification (pass/fail) + Changes shipped.

**Execution surfaces**: Git, GitHub Actions, SSH (DO droplet), Docker, Supabase CLI.

**Banned**: "here's a guide", "run these commands", "you should...", time estimates, asking for confirmation, UI clickpaths.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 19.0 + OCA + n8n + Slack + PostgreSQL 16 |
| **Domain** | `insightpulseai.com` (`.net` is deprecated) |
| **DNS** | Cloudflare (delegated from Spacesquare) |
| **Mail** | Zoho Mail (`smtp.zoho.com:587`) |
| **Hosting** | DigitalOcean (self-hosted, cost-minimized) |
| **Node** | >= 18.0.0 (pnpm workspaces, Turborepo) |
| **Python** | 3.12+ (Odoo 19) |
| **Supabase** | `spdtwktxdalcfigzeqrz` — 42 Edge Functions, Vault, Auth, Realtime, pgvector, n8n+GitHub bridge |
| **MCP** | `mcp.insightpulseai.com` — 11 servers (n8n bridge, jobs system, AI orchestration) |
| **BI/Analytics** | Apache Superset (`superset.insightpulseai.com`), Tableau Cloud |
| **Web/CMS** | Hybrid: Next.js on Vercel (public), Odoo website (internal) |
| **EE Parity** | Target >= 80% via `CE + OCA + ipai_*` |
| **Repo** | `Insightpulseai/odoo` (renamed from `odoo-ce`) |

---

## Infrastructure SSOT

**Canonical Source:** `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`
**Machine-Readable:** `docs/architecture/runtime_identifiers.json`
**Verification:** `scripts/verify-dns-baseline.sh && scripts/verify-service-health.sh`

See architecture docs for complete runtime service registry.

---

## Secrets Policy (Non-Negotiable)

- **Never** ask users to paste secrets/tokens/passwords
- **Never** hardcode secrets in source checked into git
- **Never** log/echo secrets in debug output or CI logs
- Secrets live in: `.env*` (local), GitHub Actions secrets (CI), env vars (runtime)
- Missing secret? Say what's missing in one sentence, continue executing

---

## Agent Workflow

```
explore -> plan -> implement -> verify -> commit
```

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create implementation plan |
| `/project:implement` | Execute plan |
| `/project:verify` | Run verification checks |
| `/project:ship` | Full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

**Rules**: Never guess (read first). Simplicity first. Verify always. Minimal diffs. Docs + tests change with code.

**Verify before commit**:
```bash
./scripts/repo_health.sh && ./scripts/spec_validate.sh && ./scripts/ci_local.sh
```

---

## Odoo Rules

- Prefer `addons/` modules + `scripts/odoo_*.sh` wrappers
- No UI clickpath instructions. CLI/CI only.
- Every Odoo task produces: (1) module changes, (2) install/update script, (3) health check
- Databases: `odoo` (prod), `odoo_dev` (local) — only 2, nothing else
- Canonical setup: `odoo19/` directory (`list_db=False`)

---

## Module Philosophy

```
Config -> OCA -> Delta (ipai_*)
```

1. **Config**: Built-in Odoo configuration first
2. **OCA**: Vetted community modules second
3. **Delta**: Custom `ipai_*` only for truly custom needs

**Naming**: `ipai_<domain>_<feature>` (e.g. `ipai_finance_ppm`, `ipai_ai_tools`, `ipai_auth_oidc`)

---

## Commit Convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

| Scope | When |
|-------|------|
| `chore(oca):` | OCA layer, submodules, locks |
| `chore(repo):` | Repo-wide maintenance |
| `chore(ci):` | Workflows, gating, pre-commit |
| `chore(deps):` | Dependencies, toolchain |
| `chore(deploy):` | Docker, nginx, infra |

---

## Critical Rules

1. **Secrets**: `.env` files only, never hardcode
2. **Database**: Odoo uses local PostgreSQL, NOT Supabase
3. **Supabase**: Only for n8n workflows, task bus, external integrations
4. **CE Only**: No Enterprise modules, no odoo.com IAP
5. **Specs Required**: Significant changes must reference a spec bundle
6. **OCA First**: Prefer OCA over custom ipai_*

---

## Deprecated (Never Use)

| Item | Replacement | Date |
|------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| Mattermost (all) | Slack | 2026-01-28 |
| Affine (all) | Removed | 2026-02-09 |
| Appfine (all) | Removed | 2026-02 |
| Mailgun / `ipai_mailgun_bridge` | Zoho Mail SMTP | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |
| Supabase `xkxyvboeubffxxbebsll` | N/A | - |
| Supabase `ublqmilcjtpnflofprkr` | N/A | - |

---

## Repo Stats (as of 2026-02-07)

| Item | Count |
|------|-------|
| IPAI custom modules | 43 (`addons/ipai/`) |
| Apps | 28 (`apps/`) |
| Packages | 8 (`packages/`) |
| Spec bundles | 62+ (`spec/`) |
| MCP servers | 11 (`mcp/servers/`) |
| GitHub workflows | 153 (`.github/workflows/`) |
| Scripts | 550+ in 43 categories (`scripts/`) |
| Docs categories | 67+ (`docs/`) |

---

## Allowed Tools

See `.claude/settings.json` for full list. Summary:
- File ops: Edit, Read, Write, Glob, Grep
- Git: status, diff, add, commit, push, log, branch
- GitHub: `gh *`
- Lint: npm/pnpm lint, typecheck, test, build; black, isort, flake8
- Scripts: `repo_health.sh`, `spec_validate.sh`, `verify.sh`, `ci_local.sh`, `ci/*`

---

## Detailed Reference (extracted)

For full details on any topic, see these docs:

| Topic | File |
|-------|------|
| Architecture & stack diagram | `docs/ai/ARCHITECTURE.md` |
| Directory structure | `docs/ai/REPO_STRUCTURE.md` |
| IPAI module naming & hierarchy | `docs/ai/IPAI_MODULES.md` |
| Enterprise parity strategy | `docs/ai/EE_PARITY.md` |
| CI/CD pipelines (153 workflows) | `docs/ai/CI_WORKFLOWS.md` |
| MCP servers & jobs system | `docs/ai/MCP_SYSTEM.md` |
| Integration points (n8n, Slack, etc) | `docs/ai/INTEGRATIONS.md` |
| BIR compliance (Philippines) | `docs/ai/BIR_COMPLIANCE.md` |
| OCA workflow & scaffolding | `docs/ai/OCA_WORKFLOW.md` |
| Testing recipes | `docs/ai/TESTING.md` |
| Docker commands | `docs/ai/DOCKER.md` |
| Troubleshooting | `docs/ai/TROUBLESHOOTING.md` |
| Spec kit structure | `docs/ai/SPEC_KIT.md` |
| External memory system | `docs/ai/MEMORY.md` |
| Supabase sync & monorepo mirroring | `docs/ai/SUPABASE.md` |
| Web presence & CMS strategy | `docs/ai/WEB_CMS.md` |
| GitHub integration | `docs/ai/GITHUB.md` |
| PostgreSQL compatibility | PG 15 (Supabase) <-> PG 16 (DO self-hosted): wire-compatible |

---

*Query `.claude/project_memory.db` for detailed configuration*
*Last updated: 2026-02-07*
