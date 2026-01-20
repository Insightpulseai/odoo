# Developer Guide

Conventions, branching, testing, and CI/CD workflows.

## Branching Strategy

```
main
 ├── feature/*     # New features
 ├── fix/*         # Bug fixes
 ├── chore/*       # Maintenance
 ├── docs/*        # Documentation
 └── claude/*      # AI-assisted development
```

## Commit Convention

Follow conventional commits (OCA-style):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code refactoring |
| `docs` | Documentation |
| `test` | Tests |
| `chore` | Maintenance |

### Scopes

| Scope | When to Use |
|-------|-------------|
| `oca` | OCA layer changes |
| `ipai_*` | IPAI module changes |
| `ci` | CI/CD workflows |
| `deps` | Dependencies |
| `deploy` | Deployment configs |
| `repo` | Repository maintenance |

### Examples

```bash
feat(ipai_finance_ppm): add month-end close wizard
fix(workspace): resolve portal access issue
docs(claude): update CLAUDE.md with architecture
chore(ci): add spec validation workflow
```

## Code Style

### Python (Odoo)

```bash
# Format
black addons/ipai/

# Sort imports
isort addons/ipai/

# Lint
flake8 addons/ipai/

# Type check
python3 -m py_compile addons/ipai/**/*.py
```

### JavaScript/TypeScript

```bash
# Lint
npm run lint

# Type check
npm run typecheck

# Format
npm run format
```

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

### Local CI

```bash
# Run full local CI suite
./scripts/ci_local.sh

# Verify repo structure
./scripts/repo_health.sh

# Validate spec bundles
./scripts/spec_validate.sh
```

## Module Development

### Naming Convention

All custom modules use the `ipai_` prefix:

| Domain | Pattern | Example |
|--------|---------|---------|
| AI/Agents | `ipai_ai_*` | `ipai_ai_agents` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |

### Module Structure

```
addons/ipai/ipai_my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── my_data.xml
└── static/
    └── description/
        └── icon.png
```

### Module Philosophy

```
Config → OCA → Delta (ipai_*)
```

1. **Config**: Use Odoo's built-in configuration first
2. **OCA**: Use vetted OCA community modules second
3. **Delta**: Only create ipai_* modules for truly custom needs

## CI/CD Pipelines

### Core Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-odoo-ce.yml` | Push/PR | Main Odoo CE tests |
| `ci-odoo-oca.yml` | Push/PR | OCA compliance |
| `spec-kit-enforce.yml` | Push/PR | Spec validation |

### Quality Gates

All PRs must pass:

1. Lint checks
2. Type checks
3. Unit tests
4. Spec validation
5. Repo structure check

## Pull Request Process

1. Create feature branch from `main`
2. Make changes with conventional commits
3. Run local verification: `./scripts/ci_local.sh`
4. Push and create PR
5. Wait for CI gates to pass
6. Request review
7. Squash merge to `main`

## Environment Variables

See `.env.example` for all required variables. Never commit secrets.

## Useful Commands

```bash
# Stack management
docker compose up -d                    # Start stack
docker compose logs -f odoo-core        # View logs

# Module deployment
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules

# Testing
./scripts/ci/run_odoo_tests.sh          # Run tests
./scripts/ci_local.sh                   # Run local CI

# Verification
./scripts/repo_health.sh                # Check structure
./scripts/spec_validate.sh              # Validate specs
```
