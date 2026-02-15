# Odoo Repository Scope Policy

**Purpose:** Define what belongs in this repository vs. organization-level repos.

**Last Updated:** 2026-02-15

---

## Repository Identity

**Name:** `Insightpulseai/odoo`

**Purpose:** Odoo CE 19 ERP system with OCA modules + IPAI custom modules

**Scope:** Odoo-specific code, configuration, deployment, and documentation

---

## What MUST Be In This Repo

### Runtime Entrypoints (Root Only)
- `docker-compose.yml` - SSOT for Odoo stack
- `docker-compose.dev.yml` - Optional dev overlay
- `Makefile` - Build and dev commands
- `odoo-bin` - Odoo executable
- `Dockerfile` - Container image definition

### Configuration (Root + config/)
- `config/` - Odoo configuration files
- `pyproject.toml`, `requirements*.txt` - Python dependencies
- `package.json`, `pnpm-*.yaml` - Node dependencies (for tooling)
- `.env*.example` - Environment templates

### Core Directories
- `addons/` - Odoo modules (IPAI custom + third-party)
- `addons/ipai/` - IPAI custom modules (43+ modules)
- `oca-parity/` - OCA modules organized by functional area
- `third_party/` - Other third-party addons
- `config/` - Odoo and service configurations
- `docker/` - Dockerfiles and compose overlays
- `scripts/` - Operational scripts (install, update, deploy, CI)
- `tests/` - Test suites
- `docs/` - All documentation
- `spec/` - Spec Kit feature specifications
- `infra/` - Infrastructure as code (Terraform, Ansible)
- `deploy/` - Deployment configurations
- `.devcontainer/` - VS Code Dev Container setup
- `.github/` - GitHub Actions workflows and configs

---

## What MUST NOT Be In This Repo

### Organization-Level Concerns (Move to Separate Repos)

**Platform Services** → `Insightpulseai/platform`
- `apps/` - Standalone applications
- `platform/`, `platform-kit/` - Platform infrastructure
- `api/` - Platform APIs
- `services/` - Microservices

**Frontend/Design** → `Insightpulseai/design-system`
- `web/` - Standalone web apps
- `frontend-fluent/` - UI frameworks
- `design/`, `design-tokens/` - Design systems
- `branding/` - Brand assets
- `figma/` - Design files

**Agent Infrastructure** → `Insightpulseai/agents`
- `agent-library/`, `agent-library-pack/` - Agent catalogs
- `contains-studio-agents/` - Agent development

**Deprecated Services**
- `mattermost/` - Migrated to Slack (deprecated 2026-01-28)
- `notion-n8n-monthly-close/` - Legacy integration
- `affine/`, `appfine/` - Removed services

---

## Root Directory Rules

### Allowed at Root

**Standard Files:**
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`
- `CLAUDE.md` - AI agent instructions

**Entrypoints:**
- `docker-compose.yml`, `docker-compose.dev.yml`
- `Makefile`, `odoo-bin`, `Dockerfile`

**Tooling Configs:**
- `pyproject.toml`, `requirements*.txt`, `package.json`, `pnpm-*.yaml`, `turbo.json`
- `.gitignore`, `.pre-commit-config.yaml`, `.python-version`
- `.env*.example` (templates only)

**Special:**
- `llms.txt` - LLM context file

### Disallowed at Root

**Documentation:** `*.md` files except standard ones → Move to `docs/`
**Scripts:** `*.sh`, `*.py` files → Move to `scripts/`
**Data:** `*.csv`, `*.json` (except configs), `*.html` → Move to `artifacts/` or `docs/evidence/`
**Code Directories:** Any directory not in canonical list → Move to appropriate location or `archive/root/`

---

## Directory Taxonomy

### `docs/` - All Documentation

```
docs/
├── policy/          # Governance, constraints, repo rules
├── guides/          # How-to, setup, user guides
├── runbooks/        # Operational procedures, deployment
├── architecture/    # System design, diagrams, snapshots
├── evidence/        # Timestamped execution evidence
│   └── YYYYMMDD-HHMM-<slug>/
└── ai/              # AI agent documentation
```

### `scripts/` - Operational Scripts

```
scripts/
├── dev/             # Development tools
├── ops/             # Operations scripts
├── ci/              # CI validation scripts
└── <category>/      # Domain-specific scripts
```

### `artifacts/` - Build & Execution Artifacts

```
artifacts/
├── reports/         # Generated reports
├── exports/         # Data exports
└── builds/          # Build outputs
```

---

## Migration Strategy

### Phase 1: Foundation (Current)
- ✅ Establish root allowlist
- ✅ Create CI enforcement
- ✅ Document scope policy

### Phase 2: Move Loose Files (Next)
- Move root `*.md` files to `docs/`
- Move root scripts to `scripts/`
- Move data files to `artifacts/` or `docs/evidence/`

### Phase 3: Archive Out-of-Scope Directories
- Move `apps/`, `web/`, `platform/` to `archive/root/` with migration plan
- Create separate org repos for these concerns
- Update CI to prevent re-introduction

### Phase 4: Continuous Enforcement
- CI fails on new root violations
- Quarterly review of `archive/root/` for extraction
- Document org-level repo structure

---

## Enforcement

**CI Workflow:** `.github/workflows/repo-root-allowlist.yml`
**Allowlist:** `.insightpulse/repo-root-allowlist.json`
**Validation Script:** `scripts/ci/check_root_allowlist.py`

**Process:**
1. PR adds new root file/dir
2. CI runs allowlist check
3. If not in allowlist → CI fails with helpful message
4. Developer either:
   - Moves to appropriate directory
   - Adds to allowlist with justification in PR

---

## Questions & Exceptions

**Q: Can I add a temporary script at root?**
**A:** No. Use `scripts/dev/` or `scripts/ops/` with a descriptive name.

**Q: Where do one-off reports go?**
**A:** `artifacts/reports/` or `docs/evidence/YYYYMMDD-HHMM-<slug>/`

**Q: What if I need a config file at root?**
**A:** Add to allowlist with justification. Must be a true runtime entrypoint.

**Q: How do I move code that doesn't belong?**
**A:** First to `archive/root/`, then plan extraction to separate repo.

---

## Related Documents

- [Docker Compose SSOT](../../docker/README.md)
- [Root Allowlist](.insightpulse/repo-root-allowlist.json)
- [Spec Kit Structure](../../spec/README.md)
- [Contributing Guide](../../CONTRIBUTING.md)
