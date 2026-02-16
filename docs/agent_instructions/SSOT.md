# Agent Instructions (SSOT)

> **Single Source of Truth** for all AI agent behaviors in this repository.
> This file is the only hand-edited source. Tool-specific files (CLAUDE.md, AGENTS.md, GEMINI.md) are generated mirrors.
>
> **To update instructions**: Edit this file, then run `scripts/agents/sync_agent_instructions.py`

---

## Project Output Contract

### Structured Output Envelope

When producing terminal output intended to be pasted into ChatGPT, ALWAYS format it exactly as:

**[CONTEXT]**
- repo: <git root absolute path OR "not a git repo">
- branch: <git branch or "detached/unknown">
- cwd: <pwd>
- goal: <single line>
- stamp: <ISO8601 timestamp with timezone>

**[CHANGES]**
- <path>: <one-line intent>
- ...

**[EVIDENCE]**
- command: <cmd>
  result: <PASS/FAIL + 1-3 key lines>
  saved_to: <path to log file if available>

**[DIFF SUMMARY]**
- <path>: <why this changed>

**[BLOCKERS]** (only if needed)
- <what is blocked>
- <deterministic remediation steps (no questions)>

**[NEXT - DETERMINISTIC]**
- step 1: <action>
- step 2: <action>

### Output Rules

- **Timezone for stamps**: Asia/Manila (UTC+08:00)
- **Evidence location**: `docs/evidence/<YYYYMMDD-HHMM+0800>/<task>/logs/`
- Always include: `git status --porcelain` AND `git diff --stat` in final output (or save to evidence logs if large)
- No interactive questions - choose deterministic Branch A/B/C when applicable
- Never claim "0 errors / tests pass / secure" without citing evidence line(s) or saved log
- Prefer repo-relative paths in CHANGES/DIFF SUMMARY; absolute paths allowed in EVIDENCE logs

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
| **Stack** | Odoo CE 19.0 + OCA + PostgreSQL 16 |
| **Domain** | `insightpulseai.com` (`.net` deprecated) |
| **Python** | 3.12+ (Odoo 19) |
| **Supabase** | `spdtwktxdalcfigzeqrz` |
| **Repo** | `Insightpulseai/odoo` |
| **Workspace** | `ipai` (Docker, DevContainer, all dev tools) |

**Workspace Naming**: "ipai" is the canonical identifier across all platforms (Docker project, network, volumes, DevContainer). See `docs/ai/WORKSPACE_NAMING.md` for complete convention.

---

## Infrastructure SSOT

**DNS Single Source of Truth:**
- **SSOT File**: `infra/dns/subdomain-registry.yaml` (edit this, never edit generated files)
- **Generator**: `scripts/generate-dns-artifacts.sh` (generates Terraform + JSON)
- **CI Enforcement**: `.github/workflows/dns-sync-check.yml` (validates sync)
- **Generated Artifacts**:
  - `infra/cloudflare/envs/prod/subdomains.auto.tfvars` (Terraform input)
  - `docs/architecture/runtime_identifiers.json` (runtime reference)
  - `infra/dns/dns-validation-spec.json` (CI validation)

**Workflow**: Edit YAML → Run generator → Commit all → CI validates → Terraform apply

**Verification:** `scripts/verify-dns-baseline.sh && scripts/verify-service-health.sh`

See `infra/dns/README.md` for complete DNS SSOT workflow.

---

## Secrets Policy (Non-Negotiable)

- **Never** ask users to paste secrets/tokens/passwords
- **Never** hardcode secrets in source checked into git
- **Never** log/echo secrets in debug output or CI logs
- Secrets live in: `.env*` (local), GitHub Actions secrets (CI), env vars (runtime)
- Missing secret? Say what's missing in one sentence, continue executing

---

## Agent Constitution & Execution Constraints

**Canonical Reference**: `spec/agent/constitution.md`

**Key Constraints for Claude Code Web**:
- ❌ **Forbidden**: Docker/containers, apt/brew, systemctl, sudo (not available in Web environment)
- ✅ **Allowed**: File edits, git operations, CI workflow generation, remote API calls
- 📋 **Capabilities**: Only claim capabilities verified in `agents/capabilities/manifest.json`

**Response Pattern**: If user requests forbidden operation (e.g., "run docker-compose"), acknowledge constraint and provide correct alternative (CI workflow, deployment docs, or remote execution).

**See constitution for**: Complete constraint catalog, response patterns, capability verification, examples.

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

## Spec Kit (Spec-Driven Development)

> Integrated from [github/spec-kit](https://github.com/github/spec-kit).
> Specs are executable — they generate implementations, not just describe them.

### Spec Bundle Structure

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiable rules and constraints
├── prd.md            # Product requirements (the WHAT)
├── plan.md           # Implementation plan (the HOW)
├── tasks.md          # Task breakdown (the WORK)
├── checklist.md      # Quality validation (optional)
└── research.md       # Unknowns resolved (optional)
```

### Slash Commands

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Create governance principles for a feature |
| `/speckit.specify` | Define product requirements (PRD) |
| `/speckit.clarify` | Resolve ambiguities before planning |
| `/speckit.plan` | Create implementation plan from spec |
| `/speckit.tasks` | Generate task breakdown from plan |
| `/speckit.analyze` | Cross-artifact consistency check (read-only) |
| `/speckit.checklist` | Generate quality validation checklist |
| `/speckit.implement` | Execute implementation following tasks |

### Workflow

```
/speckit.constitution → /speckit.specify → /speckit.clarify (optional)
    → /speckit.plan → /speckit.tasks → /speckit.analyze
    → /speckit.checklist → /speckit.implement
```

### Key Files

| Path | Purpose |
|------|---------|
| `.specify/templates/` | Scaffolding templates for spec artifacts |
| `.specify/memory/` | Spec-kit state and context |
| `scripts/speckit-scaffold.sh` | Create new spec bundles from CLI |
| `scripts/check-spec-kit.sh` | Validate spec bundle completeness |

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
| Mattermost (all) | Slack | 2026-01-28 |
| Affine (all) | Removed | 2026-02-09 |
| Appfine (all) | Removed | 2026-02 |
| Mailgun / `ipai_mailgun_bridge` | Zoho Mail SMTP | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |

---

*Detailed reference documentation lives in `docs/ai/` — this SSOT stays compact and focused.*
