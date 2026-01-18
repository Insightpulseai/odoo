# CLAUDE.md — odoo-dev-sandbox Project Instructions

## Purpose

This repository is a **clean, reproducible Odoo 18 CE development sandbox** for custom `ipai_*` modules with OCA integration.

**IMPORTANT**: All SuperClaude framework behavior (personas, wave mode, MCP servers, skills) is defined in `~/.claude/CLAUDE.md`. This file contains **only project-specific context** for routing and execution.

---

## Quick Reference

**Stack**: Odoo 18 CE + PostgreSQL 16 + OCA modules (24 dependencies)
**Primary Modules**: `ipai` (Enterprise Bridge), `ipai_enterprise_bridge` (CE → 19/EE parity)
**Purpose**: Local development with hot-reload, OCA compliance validation

**Key Documentation**:
- **Daily Operations**: `docs/runbooks/DEV_SANDBOX.md`
- **Audit Report**: `REPORT.md`
- **Global Framework**: `~/.claude/CLAUDE.md` (SuperClaude)

---

## Execution Rules (This Repo Only)

### What to Execute
- Use scripts in `scripts/dev/` for all operations
- Docker Compose for orchestration (no local Odoo install)
- Git for version control
- PostgreSQL via Docker (no local install)

### What CLIs Are Allowed
- `docker compose` (all operations)
- `git` (version control)
- `bash` (script execution)
- `psql` (via Docker exec only)
- `python3` (manifest validation only)

### What Is Prohibited
- Local Odoo installation (Docker only)
- Azure services
- Production database connections (dev sandbox only)
- Direct modification of OCA modules (use upstream or fork)

### Acceptance Gates
All changes must pass:
1. `./scripts/verify.sh` (local verification)
2. `.github/workflows/dev-sandbox-verify.yml` (CI checks)
3. `docker compose config` (valid syntax)
4. No deprecated `<tree>` in `view_mode` declarations (Odoo 18 convention)
5. All addon manifests valid Python syntax

---

## Auto-Activation Context

**Project Type**: Odoo 18 CE development sandbox
**Primary User**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
**Focus Areas**:
- Odoo 18 CE module development (OCA-compliant)
- Finance PPM (BIR compliance, logframe, month-end close)
- Enterprise feature parity (18 CE → 19/EE)
- OCA module integration and validation

**Skill Auto-Activation**:
- Keywords: "odoo module", "scaffold", "manifest", "view xml", "oca"
- File patterns: `addons/*/__manifest__.py`, `addons/*/views/*.xml`
- Context: Odoo development, BIR compliance, finance automation

**Persona Routing**:
- `odoo_developer` → Module development, OCA compliance, view debugging
- `finance_ssc_expert` → BIR forms, tax filing, multi-employee workflows
- `analyzer` → Root cause analysis, dependency mapping
- `devops_engineer` → Docker operations, deployment validation

**MCP Server Usage**:
- **Sequential**: Multi-step workflows, dependency analysis
- **Context7**: Odoo patterns, OCA guidelines, framework docs
- **Playwright**: (not used in this sandbox - no frontend testing)
- **Magic**: (not used - Odoo has its own UI framework)

---

## Repository Structure

```
odoo-dev-sandbox/
├── addons/                    # Custom modules (version-controlled)
│   ├── ipai/                  # Main module (18.0.1.0.0)
│   └── ipai_enterprise_bridge/ # Enterprise parity module
├── oca-addons/                # OCA dependencies (symlink/clone, git-ignored)
├── config/
│   └── odoo.conf              # Odoo configuration
├── docs/
│   └── runbooks/
│       └── DEV_SANDBOX.md     # Complete developer guide
├── scripts/
│   ├── dev/                   # Daily operation scripts
│   │   ├── up.sh              # Start services
│   │   ├── down.sh            # Stop services
│   │   ├── reset-db.sh        # Reset database (destructive)
│   │   ├── health.sh          # Health check
│   │   └── logs.sh            # View logs
│   └── verify.sh              # Local verification
├── .github/workflows/
│   └── dev-sandbox-verify.yml # CI verification
├── docker-compose.yml         # Stack definition
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── REPORT.md                  # Audit report (current state vs canonical)
└── CLAUDE.md                  # This file
```

---

## Daily Workflow

### Start Development
```bash
./scripts/dev/up.sh
```

### Make Changes
Edit files in `addons/ipai/` or `addons/ipai_enterprise_bridge/`
Hot-reload automatically restarts Odoo (watch logs: `./scripts/dev/logs.sh odoo`)

### Verify Changes
```bash
./scripts/verify.sh
```

### Stop Development
```bash
./scripts/dev/down.sh
```

---

## Odoo 18 Conventions (Enforced)

**View Mode**: Use `list` instead of `tree` in action declarations
```xml
<!-- ✅ Correct (Odoo 18) -->
<field name="view_mode">list,form</field>

<!-- ❌ Deprecated (Odoo 17 and earlier) -->
<field name="view_mode">tree,form</field>
```

**Note**: Inline `<tree>` tags within form fields (one2many/many2many) remain valid.

**Validation**: CI automatically checks for deprecated usage:
```bash
grep -r 'view_mode.*tree' addons/*/views/*.xml | grep -v '<tree'
```

---

## Secret Management

**Storage**: Environment variables only (no secrets committed)
- **Development**: `.env` (git-ignored)
- **CI**: GitHub Secrets
- **Production**: Referenced in `~/.claude/CLAUDE.md` (not this file)

**Template**: See `.env.example` for all configurable variables

---

## OCA Module Dependencies

The `ipai` module depends on **24 OCA modules**. These must be available in `oca-addons/` directory.

**Recommended Approach**: Symlink to canonical OCA location
```bash
ln -s ~/Documents/GitHub/odoo-ce/addons/external/oca oca-addons
```

**Alternative**: Git submodules or manual clones (see `docs/runbooks/DEV_SANDBOX.md`)

**Required Modules**:
```
project_timeline, project_timeline_hr_timesheet, project_timesheet_time_control,
project_task_dependencies, project_task_parent_completion_blocking,
project_task_parent_due_auto, project_type, project_template, hr_timesheet_sheet,
hr_timesheet_sheet_autodraft, hr_timesheet_sheet_policy_project_manager,
hr_timesheet_sheet_warning, hr_timesheet_task_domain, helpdesk_mgmt,
helpdesk_mgmt_project, helpdesk_ticket_type, base_territory, fieldservice,
fieldservice_project, fieldservice_portal, maintenance, quality_control,
mgmtsystem, mgmtsystem_quality, dms, knowledge, mis_builder
```

---

## Canonical SSOT Reference

This repository is **derived from** but **not identical to** the canonical dev sandbox:

**Canonical Location**: `~/Documents/GitHub/odoo-ce/sandbox/dev/`
**SSOT Document**: `infra/docker/DOCKER_DESKTOP_SSOT.yaml`

**Key Differences**:
- This repo: Standalone, version-controlled, portable
- Canonical: Integrated with full `odoo-ce` repo, shared OCA modules

See `REPORT.md` for detailed comparison.

---

## CI/CD Integration

**GitHub Actions Workflow**: `.github/workflows/dev-sandbox-verify.yml`

**Checks**:
1. Docker Compose syntax validation
2. Required files exist (config, .env.example, scripts)
3. Script permissions (all scripts executable)
4. Odoo config structure (has [options], addons_path)
5. Odoo 18 conventions (no deprecated `tree` in view_mode)
6. Addon manifest validation (Python syntax)
7. Shellcheck linting (non-blocking warnings)

**Local Equivalent**: `./scripts/verify.sh`

---

## Troubleshooting

**See**: `docs/runbooks/DEV_SANDBOX.md` → Troubleshooting section

**Common Issues**:
- Database connection refused → Reset DB container
- Module install fails → Check OCA modules present in `oca-addons/`
- Hot-reload not working → Hard refresh (Ctrl+Shift+R) or restart container
- Port conflicts → Change ports in `.env`

---

## Support & Links

**Odoo Documentation**: https://www.odoo.com/documentation/18.0
**OCA Guidelines**: https://github.com/OCA/odoo-community.org
**SuperClaude Framework**: `~/.claude/CLAUDE.md`

---

**Last Updated**: 2026-01-18
**Version**: 1.0.0
