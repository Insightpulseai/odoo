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

### Banned phrases (never say)

* "Docker/CLI is not available in this environment"
* "I can't run commands here"
* "Follow these UI steps…" (clickpaths, screenshots, wizard instructions)
* "Go to the dashboard and click…"
* "Open Settings → …"

### Output format for actionable steps

All actionable steps must be in **fenced code blocks only**:

```bash
# CLI / shell steps - always generate these
git checkout -b feat/some-change
./scripts/apply_migration.sh
```

```yaml
# CI / deployment workflow
name: deploy-odoo
on: { push: { branches: [main] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_odoo.sh
```

If something is environment-specific, **generate a script with TODO comments**, not prose.

---

## Odoo / Odoo.sh Rules

### Prefer

* `addons/` modules + migrations
* `scripts/odoo_*.sh` wrappers
* `odoo.sh` / CI YAML for deploy
* `--stop-after-init` verification commands

### Avoid

* Explaining how to click through Odoo UI for installs or upgrades
* Manual Odoo.sh dashboard instructions
* "Go to Settings → Technical → …" guides

### Task completion for Odoo

Whenever an Odoo task is requested, generate:

1. The module / config changes
2. The CLI/CI script to install/update modules:
   ```bash
   docker compose exec odoo-core odoo -d odoo_core -u module_name --stop-after-init
   ```
3. A verification command:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
   ```

---

## Naming conventions (OCA-style)

* Modules: `ipai_ai_*` for AI-related addons; avoid generic "assistant/copilot" naming collisions.
* Docs: `docs/<domain>/...` and `docs/evidence/...` strictly.
* Workflows: prefer few "golden" workflows; delete redundant ones only with proof that replacements cover the same gates.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 18.0 → 19.0 + OCA + n8n + Mattermost + PostgreSQL 16 |
| **Node** | >= 18.0.0 (pnpm workspaces) |
| **Python** | 3.10+ (Odoo 18), 3.12+ (Odoo 19) |
| **Supabase** | `spdtwktxdalcfigzeqrz` (external integrations only) |
| **Hosting** | DigitalOcean (self-hosted, cost-minimized) |
| **EE Parity** | Target ≥80% via CE + OCA + ipai_* |

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
│                   InsightPulse AI Stack (Self-Hosted)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Mattermost ◄──► n8n ◄──► Odoo CE 18/19 ◄──► PostgreSQL 16         │
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

### Cost-Minimized Self-Hosted Philosophy

**We BUILD everything ourselves to minimize costs:**
- NO Azure, AWS, GCP managed services
- NO expensive SaaS subscriptions
- NO per-seat enterprise licensing

**Self-hosted stack:**
- **Hosting**: DigitalOcean droplets (~$50-100/mo vs $1000s cloud)
- **Database**: PostgreSQL 16 (self-managed, not RDS)
- **BI**: Apache Superset (free, self-hosted)
- **SSO**: Keycloak (free, self-hosted)
- **Automation**: n8n (self-hosted, not cloud)
- **Chat**: Mattermost (self-hosted)

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
├── infra/                     # Infrastructure templates (self-hosted)
│   ├── doctl/                 # DigitalOcean CLI templates
│   ├── superset/              # Apache Superset configs
│   └── terraform/             # Self-hosted infra IaC
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
│   ├── coordinator/           # MCP routing & aggregation
│   └── servers/               # MCP server implementations
│       ├── odoo-erp-server/   # Odoo ERP integration
│       ├── digitalocean-mcp-server/  # DO infrastructure
│       ├── superset-mcp-server/      # BI platform
│       ├── vercel-mcp-server/        # Deployments
│       ├── pulser-mcp-server/        # Agent orchestration
│       └── speckit-mcp-server/       # Spec enforcement
│
├── n8n/                       # n8n workflow templates
│
├── .claude/                   # Claude Code configuration
│   ├── project_memory.db      # SQLite config database
│   ├── query_memory.py        # Memory query script
│   ├── settings.json          # Allowed tools config
│   ├── mcp-servers.json       # MCP server configuration
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

## Enterprise Parity Strategy

**Goal**: Achieve ≥80% Odoo Enterprise Edition feature parity by **building custom replacements** using CE + OCA + ipai_* modules.

**Philosophy**: We do NOT deploy Odoo EE. We BUILD our own solutions that replicate and often exceed EE capabilities.

### Parity Formula

```
CE + OCA + ipai_* = Enterprise Parity (≥80%)

Where:
  CE      = Odoo Community Edition (base, free, open source)
  OCA     = Odoo Community Association modules (community-built)
  ipai_*  = InsightPulse AI CUSTOM-BUILT modules (our IP)

NEVER:
  - License Odoo Enterprise
  - Use odoo.com IAP services
  - Deploy proprietary EE modules
```

### EE Feature Mapping

| Odoo EE Feature | EE Module | CE/OCA/IPAI Replacement | Parity |
|-----------------|-----------|-------------------------|--------|
| **Accounting** | | | |
| Bank Reconciliation | `account_accountant` | `account_reconcile_oca` | 95% |
| Financial Reports | `account_reports` | `account_financial_report` | 90% |
| Asset Management | `account_asset` | `account_asset_management` | 90% |
| Budget Management | `account_budget` | `ipai_finance_ppm` | 85% |
| Consolidation | `account_consolidation` | `ipai_finance_consolidation` | 80% |
| **HR & Payroll** | | | |
| Payroll | `hr_payroll` | `ipai_hr_payroll_ph` | 100% |
| Attendance | `hr_attendance` | `ipai_hr_attendance` | 95% |
| Leave Management | `hr_holidays` | `ipai_hr_leave` | 95% |
| Expense Management | `hr_expense` | `hr_expense` (OCA) | 90% |
| Recruitment | `hr_recruitment` | `hr_recruitment` (OCA) | 85% |
| Appraisals | `hr_appraisal` | `ipai_hr_appraisal` | 80% |
| **Services** | | | |
| Helpdesk | `helpdesk` | `ipai_helpdesk` | 90% |
| Approvals | `approvals` | `ipai_approvals` | 95% |
| Planning | `planning` | `ipai_planning` | 85% |
| Timesheet Grid | `timesheet_grid` | `ipai_timesheet` | 85% |
| Field Service | `industry_fsm` | `ipai_field_service` | 75% |
| **Studio & Customization** | | | |
| Studio | `studio` | `ipai_dev_studio_base` | 70% |
| Spreadsheet | `spreadsheet` | `ipai_spreadsheet` + Superset | 80% |
| Dashboards | `spreadsheet_dashboard` | Superset + `ipai_dashboard` | 85% |
| **Documents & Knowledge** | | | |
| Documents | `documents` | `ipai_connector_supabase` | 80% |
| Knowledge | `knowledge` | `ipai_knowledge_base` | 75% |
| Sign | `sign` | `ipai_digital_signature` | 70% |
| **Marketing** | | | |
| Marketing Automation | `marketing_automation` | n8n + `ipai_marketing` | 85% |
| Social Marketing | `social` | `ipai_social_connector` | 70% |
| Events | `event_sale` | `event` (CE) + `ipai_events` | 80% |
| **Integrations** | | | |
| IoT | `iot` | `ipai_iot_connector` | 60% |
| VoIP | `voip` | `ipai_voip_connector` | 65% |
| **BIR Compliance (PH-specific)** | | | |
| 1601-C Generation | N/A | `ipai_bir_1601c` | 100% |
| 2316 Certificates | N/A | `ipai_bir_2316` | 100% |
| Alphalist Export | N/A | `ipai_bir_alphalist` | 100% |
| VAT Reports | N/A | `ipai_bir_vat` | 100% |

### Parity Validation

Run EE parity tests before any major release:

```bash
# Run parity test suite
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# Generate HTML report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

### Priority for EE Feature Development

1. **P0 - Critical** (must have for production)
   - Bank Reconciliation, Financial Reports, Payroll, Approvals
   - BIR Compliance (Philippines regulatory requirement)

2. **P1 - High** (needed for full operations)
   - Helpdesk, Planning, Timesheet, Asset Management

3. **P2 - Medium** (nice to have)
   - Documents, Knowledge, Spreadsheet integration

4. **P3 - Low** (future roadmap)
   - IoT, VoIP, advanced Marketing Automation

### Self-Hosted ipai_* Modules (Built In-House)

We BUILD everything ourselves using open-source tools on self-hosted infrastructure:

| ipai_* Module | Replaces EE Feature | Self-Hosted Stack |
|---------------|---------------------|-------------------|
| `ipai_finance_reports` | EE Financial Reports | PostgreSQL + Superset |
| `ipai_finance_consolidation` | EE Consolidation | Custom Python + PostgreSQL views |
| `ipai_finance_forecast` | EE Forecasting | scikit-learn on DO droplet |
| `ipai_expense_intelligence` | EE Expense approval | Custom Python rules engine |
| `ipai_bir_validator` | (no EE equivalent) | Custom compliance pipelines |
| `ipai_approvals` | EE Approvals | Custom workflow engine |
| `ipai_helpdesk` | EE Helpdesk | OCA + custom enhancements |
| `ipai_planning` | EE Planning | OCA hr_planning + custom |

**Key Principle**: We own the code, we own the IP, we control the costs. No vendor lock-in.

### Parity Development Workflow

Every ipai_* module that claims EE parity must follow this workflow:

```
1. IDENTIFY   → Document which EE feature(s) are being replaced
2. SPECIFY    → Create spec bundle with acceptance criteria
3. IMPLEMENT  → Build using CE + OCA + custom code
4. TEST       → Verify against EE behavior checklist
5. MEASURE    → Run parity test, document score
6. CERTIFY    → Add to parity matrix, update CLAUDE.md
```

### Module Parity Certification Checklist

Before claiming parity for any ipai_* module:

```markdown
## Parity Certification: ipai_<module_name>

- [ ] **Spec Bundle**: spec/<module>/prd.md documents EE feature being replaced
- [ ] **Functional Tests**: tests/ cover 80%+ of EE feature behavior
- [ ] **UI/UX Parity**: User workflow matches or improves on EE
- [ ] **Data Model**: Compatible with EE migration path (if applicable)
- [ ] **Performance**: Benchmarked against EE baseline
- [ ] **Documentation**: User docs in docs/<module>/
- [ ] **CI Gate**: Added to scripts/test_ee_parity.py
```

### Parity CI Gate

The CI pipeline enforces parity thresholds:

```yaml
# .github/workflows/ee-parity-gate.yml
name: EE Parity Gate
on: [push, pull_request]
jobs:
  parity-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run parity tests
        run: python scripts/test_ee_parity.py --threshold 80
      - name: Fail if below threshold
        run: |
          score=$(cat docs/evidence/latest/parity_score.txt)
          if (( $(echo "$score < 80" | bc -l) )); then
            echo "❌ Parity score $score% below 80% threshold"
            exit 1
          fi
```

### EE Feature Replacement Patterns

| EE Capability | Self-Hosted Replacement Pattern |
|---------------|--------------------------------|
| **Reports/Dashboards** | PostgreSQL views + Superset dashboards |
| **Workflow Automation** | n8n workflows + `ipai_platform_workflow` |
| **Document Management** | Supabase Storage + `ipai_documents` |
| **Approval Workflows** | Custom state machine in `ipai_approvals` |
| **AI/ML Features** | scikit-learn + Hugging Face on DO droplet |
| **Real-time Sync** | Supabase Realtime + webhooks |
| **SSO/Auth** | Keycloak + `ipai_auth_keycloak` |
| **BI/Analytics** | Apache Superset (self-hosted) |
| **Scheduling** | n8n cron + `ipai_scheduler` |
| **Notifications** | Mattermost + `ipai_notifications` |

### Testing EE Parity Claims

```bash
# Run full parity test suite
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# Test specific module parity
python scripts/test_ee_parity.py --module ipai_finance_ppm

# Generate parity report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

### Parity Score Calculation

```python
# Weighted scoring by priority
weights = {
    "P0_critical": 3.0,   # Must-have for production
    "P1_high": 2.0,       # Needed for full operations
    "P2_medium": 1.0,     # Nice to have
    "P3_low": 0.5         # Future roadmap
}

# Score = Σ(feature_parity * weight) / Σ(weight)
# Target: ≥80% weighted parity score
```

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

**Architecture:**
```
Claude Desktop / VS Code / Agents
        ↓
MCP Coordinator (port 8766)
    ↓                    ↓
External MCPs       Custom MCPs
(Supabase, GitHub)  (Odoo, DO, Superset)
```

**Configuration:** `.claude/mcp-servers.json`

**External MCP Servers (install via npx):**

| Server | Purpose | Required Env |
|--------|---------|--------------|
| `@supabase/mcp-server` | Schema, SQL, functions | `SUPABASE_ACCESS_TOKEN` |
| `@modelcontextprotocol/server-github` | Repos, PRs, workflows | `GITHUB_TOKEN` |
| `dbhub-mcp-server` | Direct Postgres access | `POSTGRES_URL` |
| `@anthropic/figma-mcp-server` | Design tokens, components | `FIGMA_ACCESS_TOKEN` |
| `@notionhq/notion-mcp-server` | Workspace docs, PRDs | `NOTION_API_KEY` |
| `@anthropic/firecrawl-mcp-server` | Web scraping, ETL | `FIRECRAWL_API_KEY` |
| `@huggingface/mcp-server` | Models, datasets | `HF_TOKEN` |
| `@anthropic/playwright-mcp-server` | Browser automation | (none) |

**Custom MCP Servers (in `mcp/servers/`):**

| Server | Purpose | Location |
|--------|---------|----------|
| `odoo-erp-server` | Odoo CE accounting, BIR compliance | `mcp/servers/odoo-erp-server/` |
| `digitalocean-mcp-server` | Droplets, apps, deployments | `mcp/servers/digitalocean-mcp-server/` |
| `superset-mcp-server` | Dashboards, charts, datasets | `mcp/servers/superset-mcp-server/` |
| `vercel-mcp-server` | Projects, deployments, logs | `mcp/servers/vercel-mcp-server/` |
| `pulser-mcp-server` | Agent orchestration | `mcp/servers/pulser-mcp-server/` |
| `speckit-mcp-server` | Spec bundle enforcement | `mcp/servers/speckit-mcp-server/` |
| `mcp-jobs` | **Canonical Jobs & Observability Backend** | `mcp/servers/mcp-jobs/` |

**Server Groups:**
- `core`: supabase, github, dbhub, odoo-erp
- `design`: figma, notion
- `infra`: digitalocean, vercel
- `automation`: pulser, speckit

**Building Custom Servers:**
```bash
cd mcp/servers/<server-name>
npm install
npm run build
```

### Figma Dev Mode Access

**Prerequisites:**
- Dev seat or Full seat on a paid Figma plan (Collab/View-only seats do NOT include Dev Mode)
- Personal Access Token with required scopes

**Seat Comparison:**

| Seat Type | Dev Mode | Variables API | Code Connect |
|-----------|----------|---------------|--------------|
| Full      | ✓        | Enterprise    | ✓            |
| Dev       | ✓        | Enterprise    | ✓            |
| Collab    | ✗        | ✗             | ✗            |
| View-only | ✗        | ✗             | ✗            |

**Setup Commands:**

```bash
# 1. Set environment variables
export FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxx
export FIGMA_FILE_KEY=your_file_key_here

# 2. Verify access
./scripts/figma/verify_dev_mode_access.sh

# 3. Install Code Connect CLI
npm install --global @figma/code-connect@latest

# 4. Publish component mappings
npx figma connect publish --token="$FIGMA_ACCESS_TOKEN"

# 5. Export variables (Enterprise only)
./scripts/figma/figma_export_variables.sh
```

**Hotkey:** Toggle Dev Mode in Figma with `Shift + D`

**Note:** The Variables REST API is only available to full members of Enterprise orgs. For non-Enterprise plans, use Code Connect or Figma Tokens Studio plugin.

---

## MCP Jobs System – Canonical Jobs & Observability Backend

**Repository**: `git@github.com:jgtolentino/mcp-jobs.git` (standalone service)
**Submodule**: `mcp/servers/mcp-jobs/` (integrated into odoo-ce)
**Deployed**: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/
**Purpose**: Shared job orchestration + observability service for all MCP-enabled apps (Odoo, n8n, Vercel apps, Supabase Edge Functions)

### Architecture

```
MCP-Enabled Apps (Odoo, n8n, Vercel, Edge Functions)
    ↓ HTTP POST /api/jobs/enqueue
v0 Next.js App (mcp-jobs UI)
    ↓ Supabase Client
Supabase PostgreSQL (mcp_jobs schema)
    ├── jobs (queue + state machine)
    ├── job_runs (execution history)
    ├── job_events (detailed logs)
    ├── dead_letter_queue (failed jobs after max retries)
    └── metrics (aggregated stats)
```

### Core Components

**Database Schema** (`mcp_jobs`):
- **jobs**: Main job queue with state machine (queued → processing → completed | failed | cancelled)
- **job_runs**: Execution history for each run/retry
- **job_events**: Detailed event log (started, progress, completed, failed)
- **dead_letter_queue**: Failed jobs after max retries exhausted
- **metrics**: Aggregated job metrics per hour

**RPCs** (Supabase functions):
- `enqueue_job()`: Add new job to queue
- `claim_next_job()`: Worker claims next available job (atomic with SKIP LOCKED)
- `complete_job()`: Mark job as completed
- `fail_job()`: Mark job as failed, retry or move to DLQ

**API Routes** (Next.js v0 app):
- POST `/api/jobs/enqueue` - Enqueue new job
- GET `/api/jobs/list` - List jobs with filters (source, jobType, status)
- GET `/api/jobs/[id]` - Get job details with runs and events
- DELETE `/api/jobs/[id]` - Cancel queued job

**TypeScript Client** (`lib/supabaseJobsClient.ts`):
- Type-safe interfaces for Job, JobRun, JobEvent
- Helper functions: `enqueueJob()`, `listJobs()`, `getJob()`, `getJobStats()`

### Integration Patterns

**From Odoo** (Python XML-RPC):
```python
import os
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def enqueue_discovery_job(source: str, payload: dict):
    """Enqueue infrastructure discovery job"""
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/enqueue_job",
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        json={
            'p_source': source,
            'p_job_type': 'discovery',
            'p_payload': payload,
            'p_priority': 5
        }
    )
    response.raise_for_status()
    return response.json()
```

**From n8n Workflow** (HTTP Request node):
```json
{
  "nodes": [{
    "parameters": {
      "url": "={{ $env.SUPABASE_URL }}/rest/v1/rpc/enqueue_job",
      "authentication": "headerAuth",
      "sendBody": true,
      "bodyParameters": {
        "parameters": [
          { "name": "p_source", "value": "n8n" },
          { "name": "p_job_type", "value": "sync" },
          { "name": "p_payload", "value": "={{ $json }}" }
        ]
      }
    },
    "name": "Enqueue Job",
    "type": "n8n-nodes-base.httpRequest"
  }]
}
```

**From Vercel App** (Next.js API route):
```typescript
import { enqueueJob } from '@/lib/supabaseJobsClient'

export async function POST(req: Request) {
  const body = await req.json()
  const jobId = await enqueueJob(body.source, body.jobType, body.payload)
  return NextResponse.json({ ok: true, jobId })
}
```

### Vercel AI Gateway Integration

All LLM calls from MCP Jobs workers **MUST** route through Vercel AI Gateway for centralized model management. See `docs/infra/VERCEL_AI_GATEWAY_INTEGRATION.md` for complete integration strategy.

**Job Classification** (OpenAI GPT-4o-mini):
```typescript
import { generateText } from 'ai'

export async function classifyJobType(payload: unknown): Promise<JobType> {
  const result = await generateText({
    model: 'openai/gpt-4o-mini',
    prompt: `Classify this job payload: ${JSON.stringify(payload)}`
  })
  return result.text.trim() as JobType
}
```

**Failure Analysis** (Anthropic Claude Sonnet 4.5):
```typescript
export async function analyzeJobFailure(
  job: Job,
  error: string
): Promise<{ shouldRetry: boolean; reason: string }> {
  const result = await generateObject({
    model: 'anthropic/claude-sonnet-4.5',
    schema: z.object({
      shouldRetry: z.boolean(),
      reason: z.string()
    }),
    prompt: `Analyze this job failure: ${error}`
  })
  return result.object
}
```

### Deployment

**Supabase Schema**:
```bash
psql "$POSTGRES_URL" -f supabase/migrations/20260120_mcp_jobs_schema.sql
# OR
supabase db push
```

**Vercel App** (already deployed):
- URL: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/
- Environment: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `NEXT_PUBLIC_SUPABASE_URL`

**Test Endpoints**:
```bash
# Enqueue test job
curl -X POST "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{"source": "test", "jobType": "discovery", "payload": {"test": true}}'

# List jobs
curl "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/list?limit=10"
```

### Monitoring

**Key Metrics** (SQL queries):
```sql
-- Job queue depth by source
SELECT source, status, COUNT(*) as count
FROM mcp_jobs.jobs
WHERE status IN ('queued', 'running')
GROUP BY source, status;

-- Success rate by source
SELECT source, job_type,
  COUNT(*) FILTER (WHERE status = 'completed') as completed,
  COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM mcp_jobs.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY source, job_type;

-- Dead letter queue (unresolved failures)
SELECT source, job_type, COUNT(*) as count
FROM mcp_jobs.dead_letter_queue
WHERE NOT resolved
GROUP BY source, job_type;
```

**Alert Thresholds**:
- **Critical**: Queue depth >100 jobs, DLQ >10 unresolved, success rate <80%
- **Warning**: Queue depth >50 jobs, DLQ >5 unresolved, success rate <90%

### Documentation

- **Complete System Docs**: `docs/infra/MCP_JOBS_SYSTEM.md`
- **AI Gateway Strategy**: `docs/infra/VERCEL_AI_GATEWAY_INTEGRATION.md`
- **Spec Kit**: `mcp/servers/mcp-jobs/spec/mcp-jobs/` (constitution, prd, plan, tasks)

---

## GitHub Projects v2 – API Limits

### Iteration Fields (Quarter/Sprint)

Iteration **values** (Quarter/Sprint) **CANNOT** be created via GitHub API as of 2026.

**Behavior when asked to configure iterations:**
1. Mark the step as: `PHASE_REQUIRES_UI(GitHub iterations API missing)`
2. Output a one-paragraph checklist only (no screen-by-screen guide)
3. Continue automating everything else (fields, statuses, syncing, labels)

**Manual UI Setup Required:**

For **Roadmap** (`Quarter` field):
- Length: 3 months
- Start date: 2026-01-01
- Generate: 4 cycles (Q1–Q4)

For **Execution Board** (`Sprint` field):
- Length: 14 days
- Start date: Next Monday
- Generate: 12–26 cycles

**What CAN be automated:**
- Project creation (`gh project create`)
- Field creation (`gh project field-create --data-type ITERATION`)
- Single select fields with options
- Status fields
- Labels and milestones
- Issue/PR linking

**What CANNOT be automated:**
- Iteration values/cycles
- Iteration start dates
- Iteration lengths

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

**Permission errors (SCSS compilation failures)**
```bash
# Symptom: "Style compilation failed" errors in Odoo
# Root cause: Addons owned by wrong user, Odoo container can't read SCSS files

# Auto-fix permissions (recommended)
./scripts/verify-addon-permissions.sh

# Manual fix on server
ssh root@178.128.112.214
cd /opt/odoo-ce/repo/addons
chown -R 100:101 ipai ipai_theme_tbwa*
chmod -R 755 ipai ipai_theme_tbwa*
docker restart odoo-prod
```

---

## Enabled Skills

Agent capabilities enforced via repo-level skill contracts:

| Skill | Purpose | Contract |
|-------|---------|----------|
| Web Session Command Bridge | Ensures all changes produce CLI-ready commands for Claude Web/CI/Docker | [skills/web-session-command-bridge/skill.md](skills/web-session-command-bridge/skill.md) |

### Skill Enforcement

Skills are enforced via CI workflow `.github/workflows/skill-enforce.yml`.

To check skill compliance locally:
```bash
./scripts/skill_web_session_bridge.sh
```

---

---

## Custom Module Decision Framework

Build custom modules based on payment status and need:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     BUILD CUSTOM MODULE WHEN:                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ❌ NOT PAYING + NEED FEATURE → Replace it                          │
│     └── Odoo EE features → ipai_enterprise_parity                   │
│                                                                     │
│  ✅ PAYING + WANT MAX ROI → Build connector                         │
│     └── Vercel Observability Plus → ipai_connector_vercel           │
│                                                                     │
│  ❌ NOT PAYING + WORKS AS-IS → No module needed                     │
│     └── Supabase free tier → Just use SDK/API directly              │
│     └── n8n self-hosted → Just webhooks, no module                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Summary

| Service | Paying? | Module | Purpose |
|---------|---------|--------|---------|
| Odoo EE | ❌ No | `ipai_enterprise_parity` | Replace EE-only features |
| Vercel Observability+ | ✅ Yes ($10/mo) | `ipai_connector_vercel` | Maximize ROI |
| Supabase | ❌ No (free/pro) | None | Use SDK directly |
| n8n | ❌ No (self-hosted) | None | Just webhooks |

---

## GitHub Integration

### Recommended: GitHub Team ($4/user/mo)

Stay on GitHub Team - it provides everything needed:

| Feature | Free | Team | Enterprise | Our Approach |
|---------|------|------|------------|--------------|
| Protected branches | ❌ | ✅ | ✅ | Use Team |
| Required reviewers | ❌ | ✅ | ✅ | Use Team |
| CODEOWNERS | ❌ | ✅ | ✅ | Use Team |
| Draft PRs | ❌ | ✅ | ✅ | Use Team |
| Actions minutes | 2,000 | 3,000 | 50,000 | Self-hosted runners |
| Secret scanning | ❌ | ❌ | $19/user | GitLeaks (free) |
| Code scanning | ❌ | ❌ | $30/user | Semgrep (free) |
| SAML SSO | ❌ | ❌ | ✅ | Keycloak (free) |

**Annual savings**: ~$6,600/year vs Enterprise + GHAS

### GitHub App: pulser-hub

```
App ID: 2191216
Client ID: Iv23liwGL7fnYySPPAjS
Webhook URL: https://n8n.insightpulseai.net/webhook/github-pulser
```

**Capabilities:**
- Webhooks → n8n → Odoo task creation
- OAuth → "Sign in with GitHub" for apps
- Installation tokens → Secure API access

### Self-Hosted Security Pipeline

Replace GitHub Advanced Security with free tools:

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  secrets:
    runs-on: self-hosted  # Your DO droplet = unlimited minutes
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2

  sast:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: p/owasp-top-ten p/python

  deps:
    runs-on: self-hosted
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

### Self-Hosted Runner Setup

```bash
# On DigitalOcean droplet (178.128.112.214)
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.321.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz
./config.sh --url https://github.com/jgtolentino/odoo-ce --token YOUR_TOKEN
sudo ./svc.sh install && sudo ./svc.sh start
```

---

## Supabase Maximization (Pro Plan)

### Current Usage

| Feature | Status | Action |
|---------|--------|--------|
| Database | ✅ 208 tables | Well utilized |
| Functions | ✅ 59 functions | Well utilized |
| pgvector | ✅ Installed | Use for AI search |
| Auth | ⚠️ 9 req/24h | Underutilized |
| Storage | ❌ 0 usage | Activate! |
| Realtime | ❌ 0 usage | Activate! |
| Edge Functions | ❓ Check | Evaluate |

### Features to Activate (FREE with Pro)

**Realtime** - Live dashboards:
```typescript
supabase
  .channel('odoo-sync')
  .on('postgres_changes',
    { event: '*', schema: 'odoo_mirror', table: '*' },
    (payload) => console.log('Change:', payload)
  )
  .subscribe()
```

**Storage** - Replace S3/Cloudinary:
```typescript
await supabase.storage
  .from('documents')
  .upload(`bir/${year}/${form_type}/${filename}`, file)
```

**pg_cron** - Replace n8n for DB-only jobs:
```sql
SELECT cron.schedule(
  'refresh-gold-views',
  '0 2 * * *',
  $$SELECT scout.refresh_gold_materialized_views()$$
);
```

### Security Fixes (Run Immediately)

```sql
-- Fix function search_path (200+ functions)
DO $$
DECLARE func_record RECORD;
BEGIN
    FOR func_record IN
        SELECT n.nspname, p.proname, pg_get_function_identity_arguments(p.oid) as args
        FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    LOOP
        EXECUTE format('ALTER FUNCTION %I.%I(%s) SET search_path = %I, pg_temp',
            func_record.nspname, func_record.proname, func_record.args, func_record.nspname);
    END LOOP;
END $$;

-- Enable RLS on unprotected tables
ALTER TABLE public."SsoDetails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."UserOrganization" ENABLE ROW LEVEL SECURITY;
```

---

## BIR Compliance (Philippines)

### 2025 Contribution Tables

**SSS (Social Security System)**
```python
# 15% total: 5% employee, 10% employer
# Maximum Monthly Salary Credit: ₱35,000
sss_base = min(gross_wage, 35000)
sss_ee = sss_base * 0.05
sss_er = sss_base * 0.10
```

**PhilHealth**
```python
# 5% total: 2.5% each
# Minimum base: ₱10,000, Maximum: ₱100,000
ph_base = min(max(gross_wage, 10000), 100000)
philhealth_ee = ph_base * 0.025
philhealth_er = ph_base * 0.025
```

**Pag-IBIG**
```python
# 2% each, maximum base: ₱5,000
pi_base = min(gross_wage, 5000)
pagibig_ee = pi_base * 0.02
pagibig_er = pi_base * 0.02
```

### TRAIN Law Tax Table (Monthly)

```python
def compute_bir_tax(taxable_income):
    """2025 Monthly Withholding Tax (TRAIN Law)"""
    if taxable_income <= 20833:
        return 0
    elif taxable_income <= 33333:
        return (taxable_income - 20833) * 0.15
    elif taxable_income <= 66667:
        return 1875 + (taxable_income - 33333) * 0.20
    elif taxable_income <= 166667:
        return 8542 + (taxable_income - 66667) * 0.25
    elif taxable_income <= 666667:
        return 33542 + (taxable_income - 166667) * 0.30
    else:
        return 183542 + (taxable_income - 666667) * 0.35
```

### BIR Forms (ipai_* modules)

| Form | Module | Purpose |
|------|--------|---------|
| 1601-C | `ipai_bir_1601c` | Monthly Withholding Tax |
| 2316 | `ipai_bir_2316` | Certificate of Compensation |
| Alphalist | `ipai_bir_alphalist` | Annual Employee List |
| 2550M/Q | `ipai_bir_vat` | Monthly/Quarterly VAT |

---

## Vercel Observability Plus Integration

**Cost**: $10/mo + usage
**Module**: `ipai_connector_vercel`

### What You Get

| Feature | Value |
|---------|-------|
| 30-day retention | Historical data access |
| Function latency (p75) | Performance metrics |
| Path breakdown | Per-route analytics |
| External API metrics | Third-party call tracking |
| Runtime logs (30d) | Error debugging |

### Integration Pattern

```python
# ipai_connector_vercel/models/vercel_sync.py
class VercelConfig(models.Model):
    _name = "ipai.vercel.config"

    workspace_url = fields.Char(required=True)
    api_token = fields.Char(required=True)
    error_rate_threshold = fields.Float(default=5.0)
    latency_p75_threshold = fields.Integer(default=3000)

    def _cron_sync_metrics(self):
        """Sync Vercel metrics → create Odoo tasks for alerts"""
        # Fetch from Vercel API
        # Create project.task if threshold exceeded
```

---

## n8n Automation Layer

### GitHub Events Handler

```
┌─────────────────────────────────────────────────────────────────────┐
│                    n8n.insightpulseai.net                           │
├─────────────────────────────────────────────────────────────────────┤
│  GitHub Webhooks (via pulser-hub app)                               │
│  ├── Push to main → Deploy to erp.insightpulseai.net               │
│  ├── PR opened → Odoo task + Slack notification                    │
│  ├── Issue labeled "ai" → Claude Code agent workflow               │
│  ├── @claude comment → Queue for AI processing                     │
│  └── CI failure → 🔴 Immediate Slack alert                         │
│                                                                     │
│  Scheduled Jobs                                                     │
│  ├── Daily: Export Actions logs → Supabase audit_logs              │
│  ├── Weekly: Dependency update digest → Email                      │
│  └── Monthly: Compliance report → Superset snapshot                │
└─────────────────────────────────────────────────────────────────────┘
```

### Event Routing

```javascript
// n8n webhook receives GitHub events
const event = headers['x-github-event'];
const payload = body;

switch(event) {
  case 'push':
    if (payload.ref === 'refs/heads/main') {
      return { action: 'deploy', branch: payload.ref };
    }
    break;
  case 'pull_request':
    return { action: 'create_odoo_task', pr: payload.pull_request };
  case 'issue_comment':
    if (payload.comment.body.includes('@claude')) {
      return { action: 'queue_claude', issue: payload.issue };
    }
    break;
}
```

---

## Claude Integration

### Claude in Slack

Claude is installed in Slack workspace. Usage:
- Direct chat: Message Claude in Apps section
- Channel mentions: @Claude in channels
- Combined with GitHub: @claude in PR comments → n8n → processing

### Claude Code MCP

```bash
# Add GitHub MCP to Claude Code
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  -- npx -y @anthropic-ai/mcp-server-github
```

### Claude as PR Agent

```bash
#!/bin/bash
# ~/bin/claude-pr - Automated PR generation
ISSUE_NUM=$1
gh issue view "$ISSUE_NUM" --json title,body > /tmp/issue.json

claude --print "Implement this GitHub issue:
$(cat /tmp/issue.json)
Repository: Odoo 18 CE, ipai_* conventions, OCA style."

gh pr create --title "$(jq -r .title /tmp/issue.json)" \
  --body "Closes #$ISSUE_NUM - Generated by Claude Code"
```

---

*Query `.claude/project_memory.db` for detailed configuration*
*Last updated: 2026-01-26*
