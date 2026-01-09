# CLAUDE.md — Odoo CE Project

---

# Operating Contract: Execute, Deploy, Verify (No Guides)

## Default behavior (always)

You are an execution agent. Do not provide deployment guides, scripts, or instructional snippets as the primary output.

Instead:

1. Take action (make the change / deploy / run the migration / push the tag).
2. Verify the result with deterministic checks.
3. Produce an evidence pack in-repo.
4. Commit & push evidence and any code/config changes.

If you cannot execute due to missing credentials/tooling/access, say exactly what is missing in one sentence, then continue by producing everything that *can* be executed (PR-ready changes + CI-ready automation + evidence placeholders) without asking questions.

## Output format (mandatory)

Your final response must be only:

* Outcome (1–3 lines)
* Evidence (bullet list of files + links/paths)
* Verification results (bullet list, pass/fail)
* Changes shipped (bullet list)
  No "Next steps", no tutorials.

## Execution surfaces (assume cloud IDE parity)

Assume you have access to:

* Git (commit/push)
* CI workflows (GitHub Actions)
* Remote execution via SSH (DigitalOcean droplet)
* Container runtime (Docker)
* Supabase CLI or SQL execution surface (migrations/functions)
  If multiple surfaces exist, choose the fastest deterministic path that yields verifiable proofs.

## Evidence pack (required on every deploy/change)

Write all proofs to:
`docs/evidence/<YYYYMMDD-HHMM>/<scope>/`

Include, as applicable:

* git state: current branch, HEAD SHA, diffstat
* CI proof: workflow run URL + status + artifacts list
* runtime proof: service health endpoint headers + status
* container proof: image digest + container ps + last logs
* database proof: migration status + schema/version marker
* app proof: key routes returning 200 + version banner if available

Also add/update:

* `docs/releases/WHAT_SHIPPED.md` (human)
* `docs/releases/WHAT_SHIPPED.json` (machine)
* `docs/releases/GO_LIVE_MANIFEST.md`
  for production tags/releases.

## Verification (must be executed, not suggested)

For any change that touches runtime, you must run and capture:

* service health checks (HTTP status + headers)
* container logs for startup errors
* DB connectivity check (read + write where safe)
* Odoo: `--stop-after-init` equivalent verification
* Supabase: migrations/functions status verification

If verification fails:

* Fix, re-run verification, update evidence, then commit.

## Git rules

* One logical change-set per commit (plus evidence commit if needed).
* Commit message must include scope + intent (OCA-style).
* Push to a branch; open PR if not already on main.
* Never claim "deployed" without evidence files in-repo.

## Banned behaviors

* No "here's a guide"
* No "run these commands"
* No "you should…"
* No asking for confirmation to proceed
* No time estimates
* No unstated assumptions

## Naming conventions (OCA-style)

* Modules: `ipai_ai_*` for AI-related addons; avoid generic "assistant/copilot" naming collisions.
* Docs: `docs/<domain>/...` and `docs/evidence/...` strictly.
* Workflows: prefer few "golden" workflows; delete redundant ones only with proof that replacements cover the same gates.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 18.0 + OCA + n8n + Mattermost + PostgreSQL 15 |
| **Node** | >= 18.0.0 (pnpm workspaces) |
| **Python** | 3.10+ (Odoo 18 requirement) |
| **Supabase** | `spdtwktxdalcfigzeqrz` (external integrations only) |

> **Claude Code Web Users**: See [CLAUDE_CODE_WEB.md](./CLAUDE_CODE_WEB.md) for cloud sandbox execution contract.

### Common Commands

```bash
# Stack management
docker compose up -d                    # Start full stack
docker compose --profile init up        # Run with init profiles
docker compose logs -f odoo-core        # View logs

# Module deployment
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules

# Testing
./scripts/ci/run_odoo_tests.sh          # Run Odoo unit tests
./scripts/ci_local.sh                   # Run local CI checks

# Verification (always run before commit)
./scripts/repo_health.sh                # Check repo structure
./scripts/spec_validate.sh              # Validate spec bundles

# Node.js workspaces
pnpm install                            # Install dependencies
npm run dev:runner                      # Run pulser-runner
npm run dev:github-app                  # Run github-app
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         InsightPulse AI Stack                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Mattermost ◄──► n8n ◄──► Odoo CE 18 ◄──► PostgreSQL 15            │
│       │           │            │                                     │
│       │           │            ├── Core (8069)                       │
│       │           │            ├── Marketing (8070)                  │
│       │           │            └── Accounting (8071)                 │
│       │           │                                                  │
│       │           └──────────► Supabase (external integrations)      │
│       │                                                              │
│       └─────────────────────► AI Agents (Pulser, Claude, Codex)     │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Superset (BI)  │  Keycloak (SSO)  │  DigitalOcean (Hosting)        │
└─────────────────────────────────────────────────────────────────────┘
```

### Multi-Edition Docker Architecture

The stack supports 3 Odoo editions sharing a single PostgreSQL instance:

| Edition | Port | Database | Module Focus |
|---------|------|----------|--------------|
| Core | 8069 | odoo_core | Base CE + IPAI workspace |
| Marketing | 8070 | odoo_marketing | Marketing agency extensions |
| Accounting | 8071 | odoo_accounting | Accounting firm extensions |

---

## Agent Workflow (Mandatory)

All changes must follow this pattern:

```
explore → plan → implement → verify → commit
```

### Role Commands

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create detailed implementation plan |
| `/project:implement` | Execute plan with minimal changes |
| `/project:verify` | Run all verification checks |
| `/project:ship` | Orchestrate full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

### Verification Sequence

Always run before committing:

```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

### Agent Rules

1. **Never guess**: Read files first, then change them
2. **Simplicity first**: Prefer the simplest implementation that solves the task
3. **Verify always**: Include verification after any mutation
4. **Minimal diffs**: Keep changes small and reviewable
5. **Update together**: Docs and tests change with code

---

## Directory Structure

```
odoo-ce/
├── addons/                    # Odoo modules
│   ├── ipai/                  # IPAI custom modules (80+ modules)
│   │   ├── ipai_dev_studio_base/
│   │   ├── ipai_workspace_core/
│   │   ├── ipai_finance_ppm/
│   │   ├── ipai_master_control/
│   │   ├── ipai_ai_agents/
│   │   ├── ipai_approvals/
│   │   └── ...
│   ├── OCA/                   # OCA community modules (12 repos)
│   └── oca/                   # OCA submodules
│
├── apps/                      # Applications (20 apps)
│   ├── pulser-runner/         # Automation runner
│   ├── control-room/          # Control plane UI
│   ├── control-room-api/      # Control plane API
│   ├── bi-architect/          # BI analytics
│   ├── mcp-coordinator/       # MCP coordination
│   ├── web/                   # Web frontend
│   └── ...
│
├── packages/                  # Shared packages (3 packages)
│   ├── agent-core/            # Core agent framework
│   ├── github-app/            # GitHub App integration
│   └── ipai-design-tokens/    # Design system tokens
│
├── spec/                      # Spec bundles (32 feature specs)
│   ├── constitution.md        # Root non-negotiable rules
│   ├── prd.md                 # Root product requirements
│   ├── pulser-master-control/ # Example spec bundle
│   └── ...
│
├── scripts/                   # Automation scripts (160+ scripts)
│   ├── ci/                    # CI-specific scripts
│   ├── deploy-odoo-modules.sh
│   ├── repo_health.sh
│   ├── spec_validate.sh
│   └── ...
│
├── docker/                    # Docker configurations
│   ├── Dockerfile.seeded
│   ├── Dockerfile.unified
│   └── nginx/
│
├── deploy/                    # Deployment configurations
│   ├── docker-compose.yml     # Production compose
│   └── nginx/
│
├── infra/                     # Infrastructure templates
│   ├── azure/
│   ├── databricks/
│   ├── superset/
│   └── doctl/
│
├── db/                        # Database management
│   ├── schema/                # Schema definitions
│   ├── migrations/            # Migration scripts
│   ├── seeds/                 # Seed data
│   └── rls/                   # Row-level security
│
├── docs/                      # Documentation
│   ├── architecture/
│   ├── data-model/            # DBML, ERD, ORM maps
│   └── ...
│
├── mcp/                       # Model Context Protocol
│   ├── coordinator/
│   └── servers/odoo-erp-server/
│
├── n8n/                       # n8n workflow templates
│
├── .claude/                   # Claude Code configuration
│   ├── project_memory.db      # SQLite config database
│   ├── query_memory.py        # Memory query script
│   ├── settings.json          # Allowed tools config
│   └── commands/              # Slash commands
│
├── .github/workflows/         # CI/CD pipelines (47 workflows)
│
├── docker-compose.yml         # Main compose file
├── package.json               # Node.js monorepo config
├── turbo.json                 # Turbo CI/CD config
└── oca.lock.json             # OCA module lock
```

---

## IPAI Module Naming Convention

All custom modules use the `ipai_` prefix organized by domain:

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI/Agents | `ipai_ai_*`, `ipai_agent_*` | `ipai_ai_agents`, `ipai_ai_core`, `ipai_agent_core` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_bir_compliance`, `ipai_finance_month_end` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit`, `ipai_platform_approvals` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |
| Studio | `ipai_dev_studio_*`, `ipai_studio_*` | `ipai_dev_studio_base`, `ipai_studio_ai` |
| Industry | `ipai_industry_*` | `ipai_industry_marketing_agency`, `ipai_industry_accounting_firm` |
| WorkOS | `ipai_workos_*` | `ipai_workos_core`, `ipai_workos_blocks`, `ipai_workos_canvas` |
| Theme/UI | `ipai_theme_*`, `ipai_web_*`, `ipai_ui_*` | `ipai_theme_tbwa_backend`, `ipai_ui_brand_tokens` |
| Integrations | `ipai_*_connector` | `ipai_n8n_connector`, `ipai_mattermost_connector`, `ipai_superset_connector` |
| PPM | `ipai_ppm_*` | `ipai_ppm`, `ipai_ppm_monthly_close`, `ipai_ppm_a1` |

### Key Module Hierarchy

```
ipai_dev_studio_base           # Base dependencies (install first)
    └── ipai_workspace_core    # Core workspace functionality
        └── ipai_ce_branding   # CE branding layer
            ├── ipai_ai_core   # AI core framework
            │   ├── ipai_ai_agents     # Agent system
            │   └── ipai_ai_prompts    # Prompt management
            ├── ipai_finance_ppm       # Finance PPM
            │   └── ipai_finance_month_end
            └── [other modules]
```

---

## Spec Kit Structure

All significant features require a spec bundle:

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiable rules and constraints
├── prd.md            # Product requirements document
├── plan.md           # Implementation plan
└── tasks.md          # Task checklist with status
```

### Current Spec Bundles (32)

- `pulser-master-control` - Master control plane
- `close-orchestration` - Month-end close workflows
- `bir-tax-compliance` - BIR tax compliance
- `expense-automation` - Expense automation
- `hire-to-retire` - HR lifecycle management
- `ipai-control-center` - Control center UI
- `odoo-mcp-server` - MCP server integration
- `adk-control-room` - ADK control room
- `auto-claude-framework` - Auto Claude framework
- `ipai-ai-platform` - AI platform core
- `ipai-ai-platform-odoo18` - Odoo 18 AI platform
- `kapa-plus` - Kapa+ documentation AI
- `workos-notion-clone` - WorkOS Notion clone
- See `spec/` directory for complete list

---

## External Memory (Just-in-Time Retrieval)

Project configuration is stored in SQLite to reduce context usage:

```bash
python .claude/query_memory.py config       # Supabase/DB config
python .claude/query_memory.py arch         # Architecture components
python .claude/query_memory.py commands     # All commands
python .claude/query_memory.py rules        # Project rules
python .claude/query_memory.py deprecated   # Deprecated items
python .claude/query_memory.py all          # Everything
```

---

## CI/CD Pipelines

### Core Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-odoo-ce.yml` | Push/PR | Main Odoo CE tests |
| `ci-odoo-oca.yml` | Push/PR | OCA module compliance |
| `spec-kit-enforce.yml` | Push/PR | Validate spec bundle structure |
| `repo-structure.yml` | Push/PR | Verify repo structure |
| `all-green-gates.yml` | Push/PR | All gates must pass |

### Build & Deploy

| Workflow | Purpose |
|----------|---------|
| `build-unified-image.yml` | Build unified Docker image |
| `build-seeded-image.yml` | Build pre-seeded image |
| `deploy-production.yml` | Production deployment |
| `deploy-odoo-prod.yml` | Odoo-specific deployment |

### Quality Gates

| Workflow | Purpose |
|----------|---------|
| `seeds-validate.yml` | Validate seed data |
| `spec-validate.yml` | Validate spec completeness |
| `spec-and-parity.yml` | Enterprise parity checks |
| `infra-validate.yml` | Infrastructure templates |

### Monitoring

| Workflow | Purpose |
|----------|---------|
| `health-check.yml` | Health check execution |
| `finance-ppm-health.yml` | Finance PPM checks |
| `ipai-prod-checks.yml` | IPAI production checks |

---

## Allowed Tools (Safety)

Claude Code is restricted to these tools (see `.claude/settings.json`):

```json
{
  "allowedTools": [
    "Edit", "Read", "Write", "Glob", "Grep",
    "Bash(git status)", "Bash(git diff*)", "Bash(git add*)",
    "Bash(git commit*)", "Bash(git push*)", "Bash(git log*)",
    "Bash(git branch*)", "Bash(gh *)",
    "Bash(npm run lint*)", "Bash(npm run typecheck*)",
    "Bash(npm run test*)", "Bash(npm run build*)",
    "Bash(pnpm -s lint*)", "Bash(pnpm -s typecheck*)",
    "Bash(pnpm -s test*)", "Bash(pnpm -s build*)",
    "Bash(python3 -m py_compile*)",
    "Bash(black --check*)", "Bash(black *)",
    "Bash(isort --check*)", "Bash(isort *)", "Bash(flake8*)",
    "Bash(./scripts/repo_health.sh)",
    "Bash(./scripts/spec_validate.sh)",
    "Bash(./scripts/verify.sh)",
    "Bash(./scripts/ci_local.sh*)",
    "Bash(./scripts/ci/*)"
  ],
  "agentCommands": {
    "plan": ".claude/commands/plan.md",
    "implement": ".claude/commands/implement.md",
    "verify": ".claude/commands/verify.md",
    "ship": ".claude/commands/ship.md",
    "fix-github-issue": ".claude/commands/fix-github-issue.md"
  }
}
```

---

## Critical Rules

### Must Follow

1. **Secrets**: Use `.env` files only, never hardcode (see `.env.example`)
2. **Database**: Odoo uses local PostgreSQL (`db`), NOT Supabase
3. **Supabase**: Only for n8n workflows, task bus, external integrations
4. **CE Only**: No Enterprise modules, no odoo.com IAP dependencies
5. **Specs Required**: All significant changes must reference a spec bundle
6. **OCA First**: Prefer OCA modules over custom ipai_* when available

### Deprecated (Never Use)

- Supabase project `xkxyvboeubffxxbebsll`
- Supabase project `ublqmilcjtpnflofprkr`
- Any `odoo.com` Enterprise module references

### Module Philosophy

```
Config → OCA → Delta (ipai_*)
```

1. **Config**: Use Odoo's built-in configuration first
2. **OCA**: Use vetted OCA community modules second
3. **Delta**: Only create ipai_* modules for truly custom needs

---

## OCA-Style Workflow (Canonical)

### Purpose

Keep this repo aligned with **OCA tooling + conventions** while preserving the existing layered architecture:
- **Odoo CE runtime**
- **OCA addons** (managed via `oca.lock.json`, not tracked)
- **IPAI addons** (tracked, ship-ready)

### Non-Negotiables

- **Do NOT run** `copier` in the repo root (it will overwrite structure).
- Use `/tmp/oca-template/` to generate templates and **selectively port** only the needed files.
- New custom modules live under: `addons/ipai/<module_name>/`
- OCA repos cloned under: `addons/oca/*/` are **NOT tracked** (only keep base marker files per `.gitignore`).
- Changes must remain deterministic and CI-friendly (no "works on my machine" steps).

### Standard Tooling (Must Stay Green)

#### Pre-commit

Install + run:

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run -a
```

#### Local verification (mirror CI)

Run:

```bash
./scripts/verify_local.sh
```

### Using OCA Template Safely (Selective Port Only)

#### Generate OCA template in a temp directory

```bash
rm -rf /tmp/oca-template && mkdir -p /tmp/oca-template
cd /tmp/oca-template
pipx install copier || true
copier copy https://github.com/OCA/oca-addons-repo-template.git/ repo --trust
```

#### Allowed files to port (only if beneficial)

* `.pre-commit-config.yaml` (rules/tools)
* `pyproject.toml` (lint/format defaults)
* targeted `.github/workflows/*` patterns (lint/test hygiene)

#### Forbidden

* Overwriting repo layout
* Introducing a second "root" structure
* Moving existing directories to match the template

### Fast Module Scaffolding (mrbob)

#### Install

```bash
pipx install mrbob
pipx inject mrbob bobtemplates.odoo
```

#### Create addon (then move under addons/ipai/)

```bash
mrbob bobtemplates.odoo:addon
# move generated module into addons/ipai/<module_name>/
```

#### Create model scaffolding inside addon

```bash
mrbob bobtemplates.odoo:model
```

### Commit Rules (OCA-style)

* Use conventional commits: `chore(oca): ...`, `feat(ipai_*): ...`, `fix(ci): ...`
* One feature = one commit whenever possible.
* Always include proof commands (logs/status) after changes that affect runtime or CI.

---

## Testing

### Odoo Tests

```bash
# Run all tests
./scripts/ci/run_odoo_tests.sh

# Run tests for specific module
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm

# Smoke tests
./scripts/ci_smoke_test.sh
```

### Python Linting

```bash
black --check addons/ipai/
isort --check addons/ipai/
flake8 addons/ipai/
python3 -m py_compile addons/ipai/**/*.py
```

### Node.js

```bash
npm run lint
npm run typecheck
npm run build
```

---

## PR Discipline

### Commit Convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

Examples:
- `feat(finance-ppm): add month-end close wizard`
- `fix(workspace): resolve portal access issue`
- `docs(claude): update CLAUDE.md with architecture`
- `chore(ci): add spec validation workflow`

### Chore Scope Conventions (OCA-style)

| Scope | When to Use |
|-------|-------------|
| `chore(oca):` | OCA layer: submodules, `oca.lock.json`, `oca-aggregate.yml`, pins |
| `chore(repo):` | Repo-wide maintenance (docs regen, formatting, housekeeping) |
| `chore(ci):` | Workflows, gating, pre-commit, drift checks |
| `chore(deps):` | Python/Node deps, devcontainer, toolchain pins |
| `chore(deploy):` | Docker compose, nginx, env templates, infra docs |

See [docs/OCA_CHORE_SCOPE.md](docs/OCA_CHORE_SCOPE.md) for full conventions.

### PR Requirements

1. Small, focused commits with descriptive messages
2. All CI gates must pass (green status)
3. Update docs + tests alongside code changes
4. Never push directly to main without verification
5. Reference spec bundle in PR description when applicable

---

## Docker Commands

### Development

```bash
# Start core services
docker compose up -d postgres odoo-core

# Run init profiles (first-time setup)
docker compose --profile ce-init up    # Install CE modules
docker compose --profile init up       # Install IPAI modules

# View logs
docker compose logs -f odoo-core

# Restart service
docker compose restart odoo-core
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U odoo -d odoo_core

# Backup database
docker compose exec postgres pg_dump -U odoo odoo_core > backup.sql
```

---

## Key Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/deploy-odoo-modules.sh` | Deploy IPAI modules to Odoo |
| `scripts/repo_health.sh` | Verify repository structure |
| `scripts/spec_validate.sh` | Validate spec bundle completeness |
| `scripts/ci_local.sh` | Run full local CI suite |
| `scripts/verify_local.sh` | OCA-style local verification (mirrors CI) |
| `scripts/ci/run_odoo_tests.sh` | Execute Odoo unit tests |
| `scripts/ci/module_drift_gate.sh` | Check for module drift |
| `scripts/ce_oca_audit.py` | Comprehensive OCA/CE audit |
| `scripts/generate_odoo_dbml.py` | Generate data model artifacts |
| `scripts/gen_repo_tree.sh` | Auto-generate repo structure docs |
| `scripts/web_sandbox_verify.sh` | Claude Code Web sandbox verification |
| `scripts/db_verify.sh` | Database health verification script |

---

## Data Model Artifacts

Located in `docs/data-model/`:

| File | Format | Purpose |
|------|--------|---------|
| `ODOO_CANONICAL_SCHEMA.dbml` | DBML | Schema for dbdiagram.io |
| `ODOO_ERD.mmd` | Mermaid | Entity-relationship diagram |
| `ODOO_ERD.puml` | PlantUML | UML diagram |
| `ODOO_ORM_MAP.md` | Markdown | Comprehensive ORM field mapping |
| `ODOO_MODEL_INDEX.json` | JSON | Machine-readable model index |

Regenerate with:
```bash
python scripts/generate_odoo_dbml.py
```

---

## Integration Points

### n8n Workflows

- Located in `n8n/` directory
- Deploy with: `./scripts/deploy-n8n-workflows.sh`
- Activate with: `./scripts/activate-n8n-workflows.sh`

### Mattermost ChatOps

- Runbooks in `mattermost/`
- Webhooks for alerts and notifications
- AI assistant integrations

### MCP Servers

- Coordinator in `mcp/coordinator/`
- Odoo ERP server in `mcp/servers/odoo-erp-server/`
- Configuration in `mcp/agentic-cloud.yaml`

---

## Troubleshooting

### Common Issues

**Module not found**
```bash
# Ensure module is in addons path
docker compose exec odoo-core ls /mnt/extra-addons/ipai/

# Update module list
docker compose exec odoo-core odoo -d odoo_core -u base
```

**Database connection issues**
```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres
```

**Permission errors**
```bash
# Fix addon permissions
chmod -R 755 addons/ipai/
```

---

*Query `.claude/project_memory.db` for detailed configuration*
*Last updated: 2026-01-09*
