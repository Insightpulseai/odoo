---
paths:
  - ".github/**"
  - "spec/**"
---

# CI/CD Pipelines, PR Discipline & OCA Workflow

> 355 workflows, commit conventions, OCA-style workflow, spec kit structure, GitHub Projects v2 limits.

---

## CI/CD Pipelines

> **355 total workflows** in `.github/workflows/` (audited 2026-03-08).

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

### PR Rules

1. Small, focused commits with descriptive messages
2. Run verification before pushing
3. Update docs + tests alongside code changes

---

## OCA-Style Workflow (Canonical)

### Purpose

Keep this repo aligned with **OCA tooling + conventions** while preserving the layered architecture:
- **Odoo CE runtime**
- **OCA addons** (managed via `oca.lock.json`, not tracked)
- **IPAI addons** (tracked, ship-ready)

### Non-Negotiables

- **Do NOT run** `copier` in the repo root (it will overwrite structure).
- Use `/tmp/oca-template/` to generate templates and **selectively port** only the needed files.
- New custom modules live under: `addons/ipai/<module_name>/`
- OCA repos cloned under: `addons/oca/*/` are **NOT tracked**.
- Changes must remain deterministic and CI-friendly.

### Standard Tooling (Must Stay Green)

**Pre-commit:**
```bash
pip install -r requirements.txt
pre-commit install
pre-commit run -a
```

**Local verification (mirror CI):**
```bash
./scripts/verify_local.sh
```

### Using OCA Template Safely (Selective Port Only)

```bash
rm -rf /tmp/oca-template && mkdir -p /tmp/oca-template
cd /tmp/oca-template
pipx install copier || true
copier copy https://github.com/OCA/oca-addons-repo-template.git/ repo --trust
```

**Allowed files to port**: `.pre-commit-config.yaml`, `pyproject.toml`, targeted workflow patterns.

**Forbidden**: Overwriting repo layout, introducing a second "root", moving existing directories.

### Fast Module Scaffolding (mrbob)

```bash
pipx install mrbob
pipx inject mrbob bobtemplates.odoo
mrbob bobtemplates.odoo:addon     # Create addon (move under addons/ipai/)
mrbob bobtemplates.odoo:model     # Create model scaffolding
```

---

## Testing

### Odoo Tests

```bash
./scripts/ci/run_odoo_tests.sh                    # Run all tests
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm   # Run module tests
./scripts/ci_smoke_test.sh                        # Smoke tests
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

## Spec Kit Structure

All significant features require a spec bundle:

```
spec/<feature-slug>/
+-- constitution.md   # Non-negotiable rules and constraints
+-- prd.md            # Product requirements document
+-- plan.md           # Implementation plan
+-- tasks.md          # Task checklist with status
```

### Current Spec Bundles (76 total)

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
- `kapa-plus` - Kapa+ documentation AI
- `workos-notion-clone` - WorkOS Notion clone
- See `spec/` directory for complete list

---

## GitHub Projects v2 -- API Limits

### Iteration Fields (Quarter/Sprint)

Iteration **values** (Quarter/Sprint) **CANNOT** be created via GitHub API as of 2026.

**Behavior when asked to configure iterations:**
1. Mark the step as: `PHASE_REQUIRES_UI(GitHub iterations API missing)`
2. Output a one-paragraph checklist only (no screen-by-screen guide)
3. Continue automating everything else (fields, statuses, syncing, labels)

**Manual UI Setup Required:**

For **Roadmap** (`Quarter` field): Length 3 months, start 2026-01-01, generate 4 cycles (Q1-Q4).
For **Execution Board** (`Sprint` field): Length 14 days, start next Monday, generate 12-26 cycles.

**What CAN be automated:** Project creation, field creation (including ITERATION type), single select fields, status fields, labels/milestones, issue/PR linking.

**What CANNOT be automated:** Iteration values/cycles, start dates, lengths.

---

## Enabled Skills

| Skill | Purpose | Contract |
|-------|---------|----------|
| Web Session Command Bridge | CLI-ready commands for Claude Web/CI/Docker | `skills/web-session-command-bridge/skill.md` |

Skills enforced via CI workflow `.github/workflows/skill-enforce.yml`.

---

*Last updated: 2026-03-16*
