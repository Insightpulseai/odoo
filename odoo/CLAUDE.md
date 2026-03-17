# CLAUDE.md — InsightPulse AI Monorepo

> Slim index. All heavy detail lives in `.claude/rules/` files (auto-loaded by Claude Code).

---

## Operating Contract: Execute, Deploy, Verify (No Guides)

You are an execution agent. Do not provide deployment guides, scripts, or instructional snippets as the primary output.

1. **Execute** the change / deploy / run the migration / push the tag.
2. **Verify** the result with deterministic checks.
3. **Evidence** pack in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`.
4. **Commit** & push evidence and any code/config changes.

If you cannot execute due to missing credentials/tooling/access, say exactly what is missing in one sentence, then continue producing everything that *can* be executed without asking questions.

**Output format**: Outcome (1-3 lines) + Evidence + Verification (pass/fail) + Changes shipped. No "Next steps", no tutorials.

**Execution surfaces**: Git, GitHub Actions, SSH, Docker, Supabase CLI, Azure CLI.

**Banned**: "here's a guide", "run these commands", "you should...", asking for confirmation, time estimates, UI clickpaths.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 19.0 + OCA + n8n + Slack + PostgreSQL 16 |
| **Domain** | `insightpulseai.com` (`.net` is deprecated) |
| **DNS** | Cloudflare (delegated from Spacesquare) |
| **Mail** | Zoho SMTP (`smtp.zoho.com:587`, domain: `insightpulseai.com`) |
| **Hosting** | Azure Container Apps (behind Azure Front Door) |
| **Node** | >= 18.0.0 (pnpm workspaces, Turborepo) |
| **Python** | 3.12+ (Odoo 19) |
| **Supabase** | `spdtwktxdalcfigzeqrz` — Edge Functions, Vault, Auth, Realtime, pgvector |
| **Web/CMS** | Hybrid: Next.js on Vercel (public), Odoo website (internal) |
| **EE Parity** | Target >=80% via `CE + OCA + ipai_*` (current: ~35-45%, audited 2026-03-08) |
| **Repo** | `Insightpulseai/odoo` (renamed from `odoo-ce`) |

---

## Secrets Policy

Never hardcode, never echo, never ask user to paste. Secrets in `.env*` / env vars / Azure Key Vault only.
See `.claude/rules/security-baseline.md` for full policy (sections 2.1-2.6).

---

## Repo Map

| Path | Owns |
|------|------|
| `addons/ipai/` | 69 custom IPAI modules |
| `addons/oca/` | OCA community modules (hydrated at runtime, not tracked) |
| `apps/` | 9 applications (ops-console, mcp-jobs, slack-agent, etc.) |
| `packages/` | Shared packages (agents, taskbus) |
| `spec/` | 76 spec bundles |
| `scripts/` | 1000 automation scripts in 86 categories |
| `odoo19/` | Canonical Odoo 19 setup (config, scripts, backups) |
| `mcp/servers/` | MCP server implementations (plane is the only live one) |
| `.github/workflows/` | 355 CI/CD pipelines |
| `docker/`, `deploy/` | Docker configs and deployment |

---

## Cross-Repo Invariants

1. **Secrets**: `.env` files only, never hardcode. Azure Key Vault for runtime.
2. **Database**: Odoo uses PostgreSQL (local or Azure managed), NOT Supabase.
3. **Supabase**: Only for n8n workflows, task bus, external integrations.
4. **CE Only**: No Enterprise modules, no odoo.com IAP dependencies.
5. **OCA First**: Prefer OCA modules over custom `ipai_*` when available. Config -> OCA -> Delta.
6. **Specs Required**: Significant changes must reference a spec bundle.

---

## Common Workflows

### Agent Pattern

```
explore -> plan -> implement -> verify -> commit
```

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create detailed implementation plan |
| `/project:implement` | Execute plan with minimal changes |
| `/project:verify` | Run all verification checks |
| `/project:ship` | Orchestrate full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

### Verification (run before every commit)

```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

### Agent Rules

1. **Never guess**: Read files first, then change them
2. **Simplicity first**: Prefer the simplest implementation
3. **Verify always**: Include verification after any mutation
4. **Minimal diffs**: Keep changes small and reviewable
5. **Update together**: Docs and tests change with code

### Common Commands

```bash
docker compose up -d                    # Start full stack
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules
./scripts/ci/run_odoo_tests.sh          # Run Odoo unit tests
pnpm install                            # Install Node dependencies
```

---

## Deprecated (Never Use)

| Item | Replacement | Date |
|------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| Mattermost (all) | Slack | 2026-01-28 |
| Appfine (all) | Removed | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |
| Supabase `xkxyvboeubffxxbebsll` | N/A | -- |
| Supabase `ublqmilcjtpnflofprkr` | N/A | -- |
| `ipai_ai_widget` (global patches) | Native Odoo 19 Ask AI + `ipai_ai_copilot` | 2026-03-09 |
| DigitalOcean (all) | Azure (ACA + VM + managed PG) | 2026-03-15 |
| Public nginx edge | Azure Front Door | 2026-03-15 |
| Self-hosted runners | GitHub-hosted / Azure DevOps pool | 2026-03-15 |
| Mailgun (`mg.insightpulseai.com`) | Zoho SMTP | 2026-03-11 |
| Vercel deployment | Azure Container Apps | 2026-03-11 |

---

## Deep Reference

| Topic | Location |
|-------|----------|
| Directory structure & inventory | `.claude/rules/repo-topology.md` |
| Architecture, Docker, integrations | `.claude/rules/platform-architecture.md` |
| Secrets policy, GHAS, allowed tools | `.claude/rules/security-baseline.md` |
| GitHub governance, CI/CD, PR rules | `.claude/rules/github-governance.md` |
| Enterprise parity strategy & tables | `.claude/rules/ee-parity.md` |
| Odoo CE 19 rules, modules, testing | `.claude/rules/odoo-rules.md` |
| Supabase usage & activation | `.claude/rules/supabase-usage.md` |
| BIR compliance (PH tax/payroll) | `.claude/rules/bir-compliance.md` |
| MCP Jobs system | `.claude/rules/mcp-jobs.md` |
| n8n automations & Claude integration | `.claude/rules/automations.md` |
| Spec kit structure & bundles | `.claude/rules/spec-kit.md` |
| Vercel observability & Figma | `.claude/rules/vercel-observability.md` |
| SSOT platform rules | `.claude/rules/ssot-platform.md` |
| Architecture & stack | `docs/ai/ARCHITECTURE.md` |
| IPAI module naming | `docs/ai/IPAI_MODULES.md` |
| OCA workflow | `docs/ai/OCA_WORKFLOW.md` |
| Testing recipes | `docs/ai/TESTING.md` |
| Docker commands | `docs/ai/DOCKER.md` |
| Troubleshooting | `docs/ai/TROUBLESHOOTING.md` |

---

*Query `.claude/project_memory.db` for detailed configuration*
*Last updated: 2026-03-16*
