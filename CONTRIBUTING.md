# Contributing to InsightPulse AI

## Prerequisites

- Docker (with Compose v2)
- Git
- Node.js >= 18.0.0 (pnpm workspaces)
- Python 3.12+

## Local Setup

```bash
git clone https://github.com/Insightpulseai/odoo.git
cd odoo
docker compose up -d
# Odoo available at http://localhost:8069 (database: odoo_dev)
```

## Branch Convention

- Create feature branches off `main`
- Name branches descriptively: `feat/copilot-markdown`, `fix/tax-rounding`, `docs/readme-rewrite`
- Keep branches short-lived; rebase on `main` before opening a PR

## Commit Convention

Follow the conventional commit format:

```
feat|fix|refactor|docs|test|chore(scope): description
```

Examples:
- `feat(copilot): add markdown rendering to chat`
- `fix(finance): correct BIR tax rounding`
- `docs(architecture): update target state diagram`
- `chore(oca): update submodule pins`
- `test(ppm): add PPM import wizard tests`

## Pull Request Process

- Squash merge to `main`
- PR title follows the same commit convention
- Include a summary of what changed and why
- Link related issues or spec bundles when applicable

## Module Philosophy

When adding Odoo functionality, follow this priority:

1. **Config** -- use built-in Odoo configuration first
2. **OCA** -- use vetted OCA community modules second
3. **Delta** -- create custom `ipai_*` modules only for truly custom needs

Custom modules use the naming convention `ipai_<domain>_<feature>` (e.g., `ipai_finance_ppm`).

## Testing

- Every test run uses a disposable database: `test_<module_name>`
- Never use `odoo_dev`, `odoo_staging`, or `odoo` (production) for tests
- Classify test results per the failure matrix in [CLAUDE.md](CLAUDE.md)

## Code Style

- Python: follow [Odoo 19 coding guidelines](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)
- TypeScript: standard ESLint + Prettier
- No secrets in source -- use `.env` files (gitignored) or Azure Key Vault

## AI Agent Instructions

This repo uses Claude Code for AI-assisted development. Agent behavior is governed by [CLAUDE.md](CLAUDE.md).

## Architecture Decisions

Architecture docs live in [`docs/architecture/`](docs/architecture/). Review relevant docs before making structural changes.

## License

By contributing, you agree that your contributions will be licensed under LGPL-3.0. See [LICENSE](LICENSE).
