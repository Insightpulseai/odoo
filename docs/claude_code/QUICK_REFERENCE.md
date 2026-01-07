# Claude Code Quick Reference Card

**One-page guide for immediate productivity**

## Installation

```bash
curl -fsSL https://claude.ai/install.sh | bash
cd ~/odoo-ce
claude
```

## Essential Commands

| Task | Command |
|------|---------|
| **Verify changes** | `./scripts/verify.sh` |
| **Quick syntax check** | `./scripts/verify.sh --quick` |
| **Start stack** | `docker compose up -d` |
| **Deploy modules** | `./scripts/deploy-odoo-modules.sh` |
| **View logs** | `docker compose logs -f odoo-core` |

## Claude Code Prompts

### Odoo Module Creation

```bash
claude -p "Scaffold OCA-compliant Odoo 18 CE module: ipai_<name>
- Add models, views, security
- Include tests
- Update deployment scripts
Run: ./scripts/verify.sh"
```

### Control Room UI Component

```bash
claude -p "Add Fluent UI component to Control Room: [ComponentName]
- Use TBWA branding (#F1C100, #000000)
- Responsive design
- TypeScript + makeStyles
Test: pnpm build"
```

### Finance PPM Dashboard

```bash
claude -p "Add ECharts chart to Finance PPM dashboard: [metric]
- Controller endpoint: /ipai/finance/ppm/api/[metric]
- Backend service method
- Update dashboard template
Run: ./scripts/verify.sh"
```

### n8n Workflow

```bash
claude -p "Create n8n workflow: [workflow-name]
- Odoo XML-RPC nodes
- Mattermost notifications
- Error handling
Output: automations/n8n/workflows/[workflow].json"
```

### Fix CI Failure

```bash
claude -p "Fix CI job: [job-name]
- Read .github/workflows/[job].yml
- Fix root cause (don't skip tests)
- Verify locally: ./scripts/verify.sh"
```

## Project Structure

```
odoo-ce/
├── addons/ipai/              # Custom Odoo modules
├── apps/control-room/        # Next.js dashboard
├── scripts/                  # Automation
│   └── verify.sh            # Main verification
├── docs/                    # Documentation
└── spec/                    # Spec bundles
```

## Quality Gates

**Always run before commit:**

```bash
./scripts/verify.sh
```

**What it checks:**
1. ✅ Repo structure (`repo_health.sh`)
2. ✅ Spec validation (`spec_validate.sh`)
3. ✅ Python syntax
4. ✅ Formatting (black, isort)
5. ✅ Local CI

## File Locations

| What | Where |
|------|-------|
| **Odoo modules** | `addons/ipai/<module>/` |
| **UI components** | `apps/control-room/src/components/` |
| **Finance PPM** | `addons/ipai/ipai_finance_ppm/` |
| **n8n workflows** | `automations/n8n/workflows/` |
| **Spec bundles** | `spec/<feature-slug>/` |
| **Verification** | `scripts/verify.sh` |

## TBWA Branding

```typescript
// Fluent UI tokens
const tbwaYellow = "#F1C100";
const tbwaBlack = "#000000";

// Usage in makeStyles
backgroundColor: tbwaYellow,
color: tbwaBlack,
```

## OCA Module Structure

```
addons/ipai/ipai_<module>/
├── __init__.py
├── __manifest__.py          # AGPL-3 license
├── models/                  # Business logic
├── views/                   # XML views
├── security/
│   └── ir.model.access.csv # Permissions
├── tests/                   # Unit tests
└── README.rst              # Documentation
```

## Spec-Kit Pattern

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiables
├── prd.md            # Requirements
├── plan.md           # Implementation
└── tasks.md          # Checklist
```

## Common Issues

### "Module not found"

```bash
# Check manifest
python scripts/validate_manifests.py

# Test install
docker compose exec odoo-core odoo -d odoo_core -i <module> --stop-after-init
```

### "Build failed"

```bash
# Check specific step
./scripts/verify.sh --quick  # Syntax only
./scripts/repo_health.sh     # Structure
pnpm build                   # Frontend build
```

### "CI failing"

```bash
# Run locally
./scripts/ci_local.sh

# Check workflow
cat .github/workflows/<workflow>.yml
```

## Agent Commands

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create implementation plan |
| `/project:implement` | Execute plan |
| `/project:verify` | Run verification |
| `/project:ship` | Full workflow |

## Stack Quick Ref

- **Odoo**: CE 18.0 + OCA
- **Frontend**: Next.js 14 + Fluent UI v9
- **Database**: PostgreSQL 15
- **Automation**: n8n + Mattermost
- **Host**: DigitalOcean

## Resources

| Resource | Path |
|----------|------|
| **Setup Guide** | `docs/CLAUDE_CODE_SETUP.md` |
| **Project Rules** | `CLAUDE.md` |
| **Index** | `docs/claude_code/README.md` |
| **llms.txt** | `docs/llms.txt` |

## Keyboard Shortcuts

```bash
# Claude Code session
claude                    # Start interactive
claude -p "..."           # One-shot prompt
claude -h                 # Help

# Verification
make lint                 # Python format
make test                 # Run tests
make docs                 # Generate docs
```

---

**Pro Tip**: Start every task with `./scripts/verify.sh` to ensure clean state.
