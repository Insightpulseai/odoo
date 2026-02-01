# Project Constitution

**Project:** InsightPulseAI Odoo ERP
**Stack:** Odoo 18 CE (OCA Standards)
**Organization:** TBWA/InsightPulseAI
**Last Updated:** 2025-11-25

---

## 1. Golden Rules (Non-Negotiable)

These rules are **absolute** and must never be violated by any human or AI contributor.

### 1.1 Immutable Image Principle
All production deployments **MUST** use:
```
ghcr.io/jgtolentino/odoo-ce:latest
```
- We do **NOT** install modules manually on the server
- We do **NOT** modify code inside running containers
- All changes go through Git → CI/CD → Image Build → Deploy

### 1.2 OCA Compliance
All Python code in `/addons` **MUST** pass pre-commit checks:
- **Flake8:** PEP8 style compliance
- **Isort:** Import sorting
- **Black:** Code formatting (88 char line length)
- **OCA Hooks:** Manifest validation, XML lint, CSV checks

### 1.3 No Enterprise Dependencies
This is a **Community Edition** project. The following are **FORBIDDEN**:
- `odoo.addons.*_enterprise` imports
- `web_studio`, `documents`, `iap` module dependencies
- Any reference to `odoo.sh` or `odoo.com` SaaS features

### 1.4 Secrets Management
- **NEVER** hardcode passwords, API keys, or tokens
- **ALWAYS** use `os.environ.get('VAR_NAME')` or `.env` files
- Credentials **ONLY** in GitHub Secrets or `.env` (gitignored)

---

## 2. File Structure Enforcement

The AI and all contributors must strictly adhere to this tree:

```
odoo-ce/
├── addons/                 # Custom business logic modules ONLY
│   ├── ipai_*/            # InsightPulseAI modules (OCA-compliant)
│   └── tbwa_*/            # TBWA-specific integrations
├── oca/                   # OCA modules (Git Submodules, read-only)
├── deploy/                # Docker and Nginx configurations ONLY
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── odoo.conf
├── scripts/               # CI/CD and utility scripts
├── docs/                  # Markdown documentation
├── .github/workflows/     # GitHub Actions CI/CD
├── Dockerfile             # Target image build definition
├── requirements.txt       # Python development dependencies
├── .pre-commit-config.yaml
└── constitution.md        # THIS FILE (AI rulebook)
```

### Forbidden Locations
- **NO** code in project root (except config files)
- **NO** custom modules outside `addons/`
- **NO** documentation in `addons/` (use `docs/`)

---

## 3. Technology Constraints

### 3.1 Database
- **Engine:** PostgreSQL 16 (Alpine)
- **Host:** `db` (Docker service name) or external managed PostgreSQL
- **Supabase:** Used for external integrations ONLY, not for Odoo core data

### 3.2 Reverse Proxy
- **Server:** Nginx (handling SSL termination)
- **Port Binding:** `127.0.0.1:8069` (never expose directly)
- **SSL:** Let's Encrypt via Certbot

### 3.3 Python Version
- **Minimum:** Python 3.10
- **Package Manager:** pip (no conda, no poetry in production)

### 3.4 Odoo Version
- **Version:** 18.0 (Community Edition)
- **Source:** `odoo:18.0` official Docker image
- **OCA Compatibility:** 18.0 branch only

---

## 4. Module Development Standards

### 4.1 Naming Conventions
| Component | Convention | Example |
|-----------|------------|---------|
| Module name | `<prefix>_<domain>_<feature>` | `ipai_finance_ppm` |
| Model name | `<prefix>.<domain>.<model>` | `ipai.finance.task` |
| Field (Many2One) | `*_id` suffix | `project_id` |
| Field (One2Many/Many2Many) | `*_ids` suffix | `task_ids` |
| Computed field method | `_compute_<field>` | `_compute_total` |

### 4.2 Manifest Requirements
Every `__manifest__.py` must include:
```python
{
    "name": "Module Name",
    "version": "18.0.X.Y.Z",  # OCA versioning
    "license": "AGPL-3",      # Required for OCA
    "author": "InsightPulseAI",
    "depends": [...],         # Explicit dependencies
    "data": [
        "security/ir.model.access.csv",  # Security FIRST
        ...
    ],
}
```

### 4.3 Security Requirements
- **Every model** must have `ir.model.access.csv` entries
- **Record rules** for multi-tenant data isolation
- **No `sudo()`** without explicit justification in comments

---

## 5. AI Agent Behavior Rules

When an AI agent (Claude, GPT, Copilot) operates on this codebase:

### 5.1 Code Generation
- **MUST** use OCA-compliant patterns
- **MUST** generate tests for new models (`tests/test_*.py`)
- **MUST NOT** invent new module prefixes (only `ipai_*` or `tbwa_*`)

### 5.2 Deployment Tasks
When asked to "Deploy":
1. Generate `docker build` command for target image
2. Generate `docker push` command to GHCR
3. Generate `docker compose pull && up -d` for server
4. **NEVER** suggest `pip install` on production server

### 5.3 Bug Fixes
When asked to "Fix Code":
1. Run `pre-commit run --all-files` locally first
2. Verify fix doesn't break existing tests
3. Increment module version in `__manifest__.py`
4. **NEVER** modify OCA modules directly (fork or extend)

### 5.4 Documentation
When asked to "Document":
1. Update `docs/*.md` files
2. Add docstrings to Python methods
3. **NEVER** create README.md in module directories (use `docs/`)

---

## 6. Integration Points

### 6.1 Supabase (Project: spdtwktxdalcfigzeqrz)
- **Purpose:** External data sync, n8n workflows, analytics
- **Connection:** Via `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- **Rule:** Odoo is source of truth; Supabase is read replica for external access

### 6.2 n8n Automation
- **Purpose:** Workflow automation, notifications, ETL
- **Connection:** Webhook endpoints in Odoo controllers
- **Rule:** n8n triggers Odoo; Odoo does not call n8n directly

### 6.3 Mattermost
- **Purpose:** Team notifications, ChatOps
- **Connection:** Incoming webhooks
- **Rule:** Notifications only; no data persistence in Mattermost

---

## 7. CI/CD Pipeline Rules

### 7.1 Branch Protection
- `main` branch is **protected**
- All changes via Pull Request
- CI must pass before merge

### 7.2 Pipeline Stages
1. **Lint:** Pre-commit hooks (OCA compliance)
2. **Test:** Odoo unit tests with `--test-enable`
3. **Build:** Docker image creation
4. **Push:** To GHCR (only on main merge)
5. **Deploy:** Manual trigger or auto-deploy

### 7.3 Rollback
- Every image tagged with commit SHA
- Rollback = change image tag in docker-compose.prod.yml
- Database rollback via Odoo backup/restore

---

## 8. Canonical References

| Resource | Location |
|----------|----------|
| Target Image | `ghcr.io/jgtolentino/odoo-ce:latest` |
| Supabase Project | `spdtwktxdalcfigzeqrz` |
| GitHub Repo | `github.com/jgtolentino/odoo-ce` |
| Production URL | `https://erp.insightpulseai.com` |
| Documentation | `docs/` directory |

---

**This constitution is binding for all contributors, human and AI.**
**Violations must be flagged in code review.**
