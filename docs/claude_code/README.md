# Claude Code Project Index

**Auto-generated index for Claude Code AI assistant**

## Quick Navigation

| Resource | Path | Purpose |
|----------|------|---------|
| **Setup Guide** | `docs/CLAUDE_CODE_SETUP.md` | Complete setup instructions and prompt pack |
| **Project Rules** | `CLAUDE.md` | Non-negotiable project conventions |
| **Verification** | `scripts/verify.sh` | Unified quality gate script |
| **External Memory** | `.claude/query_memory.py` | Configuration database |

## Project Structure

```
odoo-ce/
├── addons/                  # Odoo modules
│   ├── ipai/               # Custom IPAI modules
│   │   ├── ipai_finance_ppm/      # Finance PPM umbrella
│   │   ├── ipai_ask_ai/           # AI assistant integration
│   │   ├── ipai_workos_*/         # Notion parity modules
│   │   └── [50+ more modules]
│   └── oca/                # OCA community modules
├── apps/                    # Node.js applications
│   ├── control-room/       # Next.js 14 + Fluent UI dashboard
│   ├── pulser-runner/      # Agent orchestration
│   └── [10+ more apps]
├── docs/                    # Documentation
│   ├── modules/            # Per-module guides
│   ├── architecture/       # System design
│   └── deployment/         # Deployment guides
├── scripts/                 # Automation scripts
│   ├── verify.sh           # Main verification
│   ├── repo_health.sh      # Structure check
│   └── spec_validate.sh    # Spec bundle validation
└── spec/                    # Spec-kit bundles
```

## Common Tasks

### 1. Odoo Module Development

**Files to know**:
- `addons/ipai/<module>/__manifest__.py` - Module definition
- `addons/ipai/<module>/models/` - Business logic
- `addons/ipai/<module>/views/` - UI definitions
- `addons/ipai/<module>/security/ir.model.access.csv` - Permissions

**Prompt**:
```bash
claude -p "Scaffold OCA-compliant Odoo 18 CE module: ipai_<name>"
```

### 2. Control Room UI Development

**Files to know**:
- `apps/control-room/src/app/` - Next.js 14 App Router pages
- `apps/control-room/src/components/` - Reusable components
- `apps/control-room/src/app/theme/tbwaFluentTheme.ts` - Branding tokens

**Prompt**:
```bash
claude -p "Add new page to Control Room: /[route-name]"
```

### 3. Finance PPM Enhancement

**Files to know**:
- `addons/ipai/ipai_finance_ppm/` - Core PPM module
- `addons/ipai/ipai_finance_ppm_dashboard/` - ECharts dashboards
- `addons/ipai/ipai_finance_ppm_closing/` - Month-end automation
- `config/finance/Month-end Closing Task and Tax Filing (7).xlsx` - Calendar

**Prompt**:
```bash
claude -p "Add ECharts visualization to Finance PPM dashboard: [metric]"
```

### 4. n8n Workflow Automation

**Files to know**:
- `automations/n8n/workflows/` - Workflow definitions
- `automations/n8n/README_*.md` - Workflow documentation

**Prompt**:
```bash
claude -p "Create n8n workflow for: [automation task]"
```

## Key Concepts

### Medallion Architecture

Data flows through quality layers:
- **Bronze**: Raw data from sources
- **Silver**: Cleaned and normalized
- **Gold**: Business-ready aggregates
- **Platinum**: AI-enhanced insights

### Spec-Kit System

All non-trivial work requires a spec bundle:
```
spec/<feature-slug>/
├── constitution.md   # Non-negotiables
├── prd.md            # Requirements
├── plan.md           # Implementation plan
└── tasks.md          # Checklist
```

### OCA Compliance

All Odoo modules must follow OCA standards:
- AGPL-3 license
- Proper module structure
- Security (ir.model.access.csv)
- Tests in tests/ directory
- README.rst documentation

## Environment

### Stack

- **Odoo**: CE 18.0 with OCA modules
- **Frontend**: Next.js 14 + Fluent UI v9 + Tailwind
- **Database**: PostgreSQL 15
- **Automation**: n8n + Mattermost
- **Hosting**: DigitalOcean (production)
- **Storage**: Supabase (external integrations)

### Credentials Location

See `.env.example` for required variables. Never commit secrets.

Credentials stored in:
- `~/.zshrc` (local development)
- GitHub Secrets (CI/CD)
- Supabase Vault (production)

## Quality Gates

Before any commit:

```bash
./scripts/verify.sh
```

This runs:
1. Repo structure check (`repo_health.sh`)
2. Spec validation (`spec_validate.sh`)
3. Python syntax check
4. Formatting (black, isort)
5. Local CI checks

## AI Agent Commands

### Role-Based Commands

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create implementation plan |
| `/project:implement` | Execute plan |
| `/project:verify` | Run verification |
| `/project:ship` | Full workflow |

### Persona Auto-Activation

Agents auto-activate based on context:
- **odoo_developer**: Odoo module work
- **finance_ssc_expert**: BIR compliance, Finance PPM
- **bi_architect**: Superset, analytics
- **devops_engineer**: Docker, deployment

## Documentation Index

### Architecture

- `docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md`
- `docs/data-model/ODOO_CANONICAL_SCHEMA.dbml`
- `docs/db/DB_TARGET_ARCHITECTURE.md`

### Deployment

- `docs/deployment/DEPLOYMENT_EXECUTION_GUIDE.md`
- `docs/deployment/WORKOS_DEPLOYMENT_PACKAGE.md`
- `docs/GO_LIVE_CHECKLIST.md`

### Modules

- `docs/modules/INDEX.md` - All module docs
- `docs/ipai/ARCHITECTURE.md` - IPAI stack overview

### Finance PPM

- `docs/ppm/architecture.md`
- `docs/ppm/data-dictionary.md`
- `docs/ppm/runbook.md`

## Troubleshooting

### Build Failures

```bash
# Check Docker logs
docker compose logs -f odoo-core

# Check module status
docker compose exec odoo-core odoo -d odoo_core --list-db
```

### Module Install Errors

```bash
# Validate manifest
python scripts/validate_manifests.py

# Test install
docker compose exec odoo-core odoo -d odoo_core -i <module> --stop-after-init
```

### CI Failures

```bash
# Run local CI
./scripts/ci_local.sh

# Check specific workflow
cat .github/workflows/<workflow>.yml
```

## External Resources

- **Odoo 18 Docs**: https://www.odoo.com/documentation/18.0/
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org
- **Fluent UI v9**: https://react.fluentui.dev/
- **Next.js 14**: https://nextjs.org/docs

## Contributing

1. Read `CLAUDE.md` for project rules
2. Create spec bundle for non-trivial work
3. Follow verification workflow
4. Submit PR with clear description

---

**Last Updated**: 2026-01-06
**Claude Code Version**: Latest
