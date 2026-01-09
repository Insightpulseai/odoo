# Copilot Instructions for InsightPulse Odoo CE

You are working in an Odoo 18 CE + OCA-first monorepo.

## Non-negotiable Rules

- **Prefer CE config → OCA modules → existing addons** before adding any custom module
- If a requested feature exists in OCA, implement by enabling/configuring OCA, NOT by custom code
- Custom modules are last resort: only for new business objects, unavoidable workflow constraints, or required API/UI glue
- Never weaken security: respect Odoo ACL + record rules; no `sudo()` for user actions unless explicitly requested
- Keep changes atomic and reviewable (small PRs)
- No Enterprise modules, no `odoo.com` IAP dependencies

## Install Order Contract

```
1) CE core (base/web/mail + chosen business apps)
2) OCA repos (sale-workflow, purchase-workflow, helpdesk, contract, project, timesheet, etc.)
3) IPAI platform addons (bridges/integrations)
4) Custom modules (only if still required)
```

## Project Architecture

- **Stack**: Odoo CE 18.0 + OCA + n8n + Mattermost + PostgreSQL 15
- **Custom modules**: Located in `addons/ipai/` (80+ modules with `ipai_` prefix)
- **OCA modules**: Added as git submodules in `addons/oca/`
- **OCR Integration**: `ocr-adapter/` bridges Odoo expense form to external OCR

### Key Module Hierarchy

```
ipai_dev_studio_base           # Base dependencies (install first)
    └── ipai_workspace_core    # Core workspace functionality
        └── ipai_ce_branding   # CE branding layer
            ├── ipai_ai_core   # AI core framework
            ├── ipai_finance_ppm       # Finance PPM
            └── [other modules]
```

## Engineering Requirements

- Add/adjust tests when behavior changes (unit/integration where applicable)
- Update manifests, README, and any install/gating docs touched by the change
- Avoid "big bang" refactors - split into multiple issues/PRs if needed
- Run verification before committing:
  ```bash
  ./scripts/repo_health.sh       # Check repo structure
  ./scripts/spec_validate.sh     # Validate spec bundles
  ./scripts/ci_local.sh          # Run local CI checks
  ```

## PR Expectations

- Include: what changed, why, how to verify (commands), rollback notes if applicable
- Prefer deterministic scripts and CI checks over manual steps
- Follow commit convention: `feat|fix|refactor|docs|test|chore(scope): description`

## Developer Workflows

- **Stack management**:
  ```bash
  docker compose up -d                    # Start full stack
  docker compose --profile init up        # Run with init profiles
  docker compose logs -f odoo-core        # View logs
  ```
- **Module deployment**: `./scripts/deploy-odoo-modules.sh`
- **Testing**: `./scripts/ci/run_odoo_tests.sh`

## Key Files & Directories

| Directory | Purpose |
|-----------|---------|
| `addons/ipai/` | IPAI custom modules |
| `addons/oca/` | OCA community modules |
| `spec/` | Spec bundles (32 feature specs) |
| `scripts/` | Automation scripts (160+) |
| `deploy/` | Deployment configurations |
| `.github/workflows/` | CI/CD pipelines (47 workflows) |

## Examples

### Add OCA module
```bash
git submodule add https://github.com/OCA/account-financial-tools.git addons/oca/account-financial-tools
docker compose restart odoo-core
```

### CI/CD failure triggers
- Enterprise module detected in `addons/`
- `odoo.com` links in user-facing code
- Spec bundle validation fails
- Repository health check fails

---

For unclear or missing conventions, review `CLAUDE.md`, `README.md`, and `.github/workflows/`. Ask the team for undocumented patterns.
