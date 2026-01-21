# OCA-Style Repository Contract (Canonical)

**Repository**: `odoo-ce` (jgtolentino/odoo-ce)
**Odoo Series**: 18.0
**Convention Source**: OCA repo template + Dixmit blog + runtime introspection
**Last Updated**: 2026-01-11
**Status**: Canonical source of truth for all generators, validators, and deployment scripts

---

## 1. Repository Layout (Monorepo with OCA-Compatible Addons Root)

**Decision**: Option B - Monorepo with `/addons/` as the canonical addons root.

**Rationale**: Existing production deployment uses this structure, and changing to pure OCA layout (Option A) would require migration of 116 modules.

### Canonical Directory Structure

```text
odoo-ce/                                    # Repo root
├── addons/                                 # CANONICAL ADDONS ROOT (all tooling points here)
│   ├── ipai/                              # Primary namespace (85 modules)
│   │   ├── ipai_finance_ppm/
│   │   ├── ipai_theme_tbwa/
│   │   ├── ipai_workspace_core/
│   │   └── ...                            # (82 more modules)
│   ├── ipai_ask_ai/                       # Standalone modules (31 modules, legacy layout)
│   ├── ipai_ask_ai_chatter/
│   ├── ipai_bir_tax_compliance/
│   └── ...                                # (28 more standalone modules)
│   └── oca/                               # OCA vendor namespace (symlinks to external-src)
│       ├── account-financial-reporting/
│       ├── account-financial-tools/       # → ../../external-src/account-financial-tools
│       ├── server-tools/
│       └── ...                            # (14 OCA repos total)
├── external-src/                          # OCA module source (git submodules/aggregator)
├── apps/                                  # Node.js applications (19 apps)
├── packages/                              # Shared packages (3 packages)
├── scripts/                               # Automation scripts (90+ scripts)
├── deploy/                                # Deployment configurations
├── docs/                                  # Documentation
├── .github/workflows/                     # CI/CD pipelines (42 workflows)
├── .pre-commit-config.yaml                # OCA-style pre-commit hooks
└── pyproject.toml                         # Python project metadata
```

### Critical Path Mapping

| Component | Path | Purpose |
|-----------|------|---------|
| **Addons Root** | `/addons/` | Single source of truth for all module discovery |
| **Primary Namespace** | `/addons/ipai/` | New custom modules go here |
| **Legacy Modules** | `/addons/ipai_*/` | 31 standalone modules (deprecate over time) |
| **OCA Vendor** | `/addons/oca/` | Symlinks to external-src (read-only) |
| **Production Mount** | `/opt/odoo-ce/repo/addons` → `/mnt/extra-addons` (container) |

---

## 2. Module Naming Conventions (ipai_* Prefix)

**Canonical Rule**: All custom modules use `ipai_` prefix with domain-based naming.

### Naming Pattern

```text
ipai_<domain>_<feature>

Examples:
  ipai_finance_ppm          # Finance Project Portfolio Management
  ipai_theme_tbwa           # TBWA brand theme
  ipai_workspace_core       # Core workspace functionality
  ipai_bir_compliance       # BIR tax compliance
```

### Domain Categories

| Domain | Pattern | Examples |
|--------|---------|----------|
| **Finance** | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_bir_compliance` |
| **Platform** | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit` |
| **Workspace** | `ipai_workspace_*` | `ipai_workspace_core` |
| **Studio** | `ipai_dev_studio_*`, `ipai_studio_*` | `ipai_dev_studio_base`, `ipai_studio_ai` |
| **Industry** | `ipai_industry_*` | `ipai_industry_marketing_agency` |
| **WorkOS** | `ipai_workos_*` | `ipai_workos_core`, `ipai_workos_blocks` |
| **Theme** | `ipai_theme_*`, `ipai_web_theme_*` | `ipai_theme_tbwa_backend` |

### Technical Name Rules

- **Lowercase only**: `ipai_finance_ppm` ✅ | `ipai_Finance_PPM` ❌
- **Snake_case only**: `ipai_finance_ppm` ✅ | `ipai-finance-ppm` ❌
- **No version suffix**: `ipai_finance_ppm` ✅ | `ipai_finance_ppm_v2` ❌
- **Folder name == module name**: Directory name must match `__manifest__.py` `'name'` field

---

## 3. Module Manifest Standards

### Canonical `__manifest__.py` Template

```python
# -*- coding: utf-8 -*-
{
    'name': 'IPAI Finance PPM',                    # Human-readable name
    'version': '18.0.1.0.0',                       # OCA version format: SERIES.MAJOR.MINOR.PATCH
    'category': 'Finance',
    'summary': 'Project Portfolio Management for Finance Operations',
    'description': """
Finance PPM Module
==================
Comprehensive project portfolio management for finance operations.
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',                           # OCA standard (or LGPL-3)
    'depends': [
        'base',
        'project',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',            # Security first
        'views/finance_ppm_views.xml',
        'data/finance_ppm_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,                           # True only for top-level apps
    'auto_install': False,
}
```

### Version Format (OCA Standard)

```text
18.0.x.y.z

Where:
  18.0   = Odoo series (matches branch name)
  x      = Major version (breaking changes)
  y      = Minor version (new features, backward compatible)
  z      = Patch version (bug fixes)

Examples:
  18.0.1.0.0  - Initial release for Odoo 18.0
  18.0.1.1.0  - Added new feature (minor)
  18.0.1.1.1  - Bug fix (patch)
  18.0.2.0.0  - Breaking change (major)
```

### License Standards

- **Primary**: `AGPL-3` (OCA default for most modules)
- **Alternative**: `LGPL-3` (for connector/library modules)
- **Forbidden**: Proprietary, Enterprise-only, or custom licenses

---

## 4. Module Directory Structure

### Standard Layout (OCA-Compliant)

```text
ipai_finance_ppm/
├── __init__.py                 # Import models, controllers
├── __manifest__.py             # Module metadata (see template above)
├── README.rst                  # Documentation (reStructuredText)
├── models/                     # Business logic
│   ├── __init__.py
│   ├── finance_logframe.py
│   └── bir_schedule.py
├── views/                      # XML views
│   ├── finance_ppm_views.xml
│   └── bir_schedule_views.xml
├── security/                   # Access control
│   └── ir.model.access.csv
├── data/                       # Seed data (non-demo)
│   └── finance_ppm_seed.xml
├── demo/                       # Demo data (optional)
│   └── finance_ppm_demo.xml
├── static/                     # Frontend assets
│   ├── src/
│   │   ├── js/
│   │   ├── scss/
│   │   └── xml/
│   └── description/
│       ├── icon.png            # 128x128 module icon
│       └── index.html          # Module documentation
├── i18n/                       # Translations
│   ├── ipai_finance_ppm.pot
│   ├── en.po
│   └── fil.po                  # Filipino translations
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_finance_ppm.py
└── migrations/                 # Version upgrades
    └── 18.0.1.1.0/
        ├── pre-migration.py
        └── post-migration.py
```

---

## 5. Addons Path Configuration

### Production Configuration (Canonical)

**Source**: Production runtime introspection (178.128.112.214:odoo-prod)

```ini
# /etc/odoo/odoo.conf (inside container)
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/var/lib/odoo/addons/18.0,/mnt/extra-addons
```

**Resolution Order**:
1. `/usr/lib/python3/dist-packages/odoo/addons` - Odoo CE core (18.0)
2. `/var/lib/odoo/addons/18.0` - Odoo data directory (empty in production)
3. `/mnt/extra-addons` - Bind mount to `/opt/odoo-ce/repo/addons`

**Module Discovery**:
- Odoo scans `/mnt/extra-addons/` for folders with `__manifest__.py`
- Discovers:
  - `/mnt/extra-addons/ipai/ipai_finance_ppm/` ✅
  - `/mnt/extra-addons/ipai_ask_ai/` ✅
  - `/mnt/extra-addons/oca/server-tools/` ✅ (symlink followed)

### CI/Local Development

```bash
# Scripts must expand addons_path deterministically
python3 scripts/gen_addons_path.py

# Output (example):
/usr/lib/python3/dist-packages/odoo/addons,\
/var/lib/odoo/addons/18.0,\
/path/to/repo/addons/ipai,\
/path/to/repo/addons/oca/account-financial-reporting,\
/path/to/repo/addons/oca/server-tools,\
...
```

---

## 6. CI/CD Discovery Rules

### Pre-Commit Hooks (Lint/Format)

```yaml
# .pre-commit-config.yaml (OCA-style)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    hooks:
      - id: black
        files: ^addons/

  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
        files: ^addons/
```

### Module Discovery for Tests

```bash
# CI must scan ALL addons roots:
ADDON_PATHS=(
  "addons/ipai"              # Primary namespace
  "addons/oca"               # OCA vendor (test OCA modules separately)
  "addons/ipai_*"            # Legacy standalone modules
)

# Example CI test command:
pytest addons/ipai/*/tests/ addons/ipai_*/tests/
```

---

## 7. Scaffolder Rules (Module Generation)

### New Module Creation Contract

```bash
# ALWAYS create modules inside /addons/ipai/
./scripts/scaffold_module.sh ipai_new_module

# Output:
addons/ipai/ipai_new_module/
  __init__.py
  __manifest__.py
  README.rst
  models/
  views/
  security/
  tests/
```

### Forbidden Patterns

❌ **DO NOT** create modules at repo root:
```text
odoo-ce/
├── ipai_new_module/          # WRONG - not OCA-style
```

❌ **DO NOT** create modules in `/addons/` root (unless migrating legacy):
```text
addons/
├── ipai_new_module/          # DISCOURAGED - legacy pattern
```

✅ **ALWAYS** create modules in `/addons/ipai/`:
```text
addons/ipai/
├── ipai_new_module/          # CORRECT - canonical namespace
```

---

## 8. Validator Rules (Quality Gates)

### Manifest Validation

```python
# scripts/validate_manifest.py
def validate_manifest(manifest_path):
    """Validate __manifest__.py against OCA standards."""
    required_keys = ['name', 'version', 'license', 'author', 'depends']

    # Version format: 18.0.x.y.z
    assert re.match(r'^18\.0\.\d+\.\d+\.\d+$', manifest['version'])

    # License must be OCA-approved
    assert manifest['license'] in ['AGPL-3', 'LGPL-3']

    # Technical name == folder name
    assert manifest_path.parent.name == manifest['name'].lower().replace(' ', '_')
```

### Naming Convention Validation

```bash
# Enforce ipai_ prefix for all custom modules
for module in addons/ipai/*/; do
  [[ $(basename "$module") == ipai_* ]] || exit 1
done
```

---

## 9. Deployment Contract

### Production Deployment (Canonical)

**Host**: 178.128.112.214
**Container**: `odoo-prod`
**Deploy Script**: `/opt/odoo-ce/repo/scripts/deploy-odoo-modules.sh`

```bash
# Deployment workflow:
1. rsync /addons/ipai/* to /opt/odoo-ce/repo/addons/ipai/
2. chown -R 100:101 /opt/odoo-ce/repo/addons/ipai/
3. docker restart odoo-prod
4. Verify: curl https://erp.insightpulseai.net/web/login
```

### Permission Requirements

- **Container User**: UID 100:GID 101 (`odoo:odoo` inside container)
- **Host Ownership**: Must match container user for bind mounts
- **Verification**: `./scripts/verify-addon-permissions.sh`

---

## 10. Migration Strategy (Legacy → Canonical)

### Current State

- **Primary**: 85 modules in `/addons/ipai/` ✅
- **Legacy**: 31 modules in `/addons/ipai_*/` ⚠️ (standalone, non-namespaced)
- **OCA**: 14 repos in `/addons/oca/` ✅

### Migration Plan

```bash
# Phase 1: Identify active legacy modules
psql "$POSTGRES_URL" -c "
  SELECT name FROM ir_module_module
  WHERE name LIKE 'ipai_%' AND state = 'installed'
  AND name NOT IN (SELECT name FROM addons_ipai_namespace);
"

# Phase 2: Move to ipai/ namespace
for module in addons/ipai_*/; do
  git mv "$module" addons/ipai/
done

# Phase 3: Update deployment scripts
# (Remove references to standalone paths)

# Phase 4: Verify CI/pre-commit still work
pre-commit run --all-files
pytest addons/ipai/*/tests/
```

---

## 11. Canonical Checklist (Copy/Paste for PRs)

Use this checklist for all module-related PRs:

```markdown
## OCA-Style Compliance Checklist

- [ ] Module created in `/addons/ipai/` (not repo root or `/addons/` root)
- [ ] Technical name follows `ipai_<domain>_<feature>` pattern
- [ ] Folder name == module name (lowercase snake_case)
- [ ] `__manifest__.py` version format: `18.0.x.y.z`
- [ ] License is `AGPL-3` or `LGPL-3`
- [ ] Standard folders present: `models/`, `views/`, `security/`
- [ ] `ir.model.access.csv` exists in `security/`
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Tests exist in `tests/` directory
- [ ] Module installs without errors (`odoo -i <module> --stop-after-init`)
- [ ] Deployment script updated if new namespace added
```

---

## 12. Quick Reference Commands

```bash
# Generate addons_path
python3 scripts/gen_addons_path.py

# Validate all manifests
python3 scripts/validate_manifests.py addons/ipai/

# Check naming conventions
./scripts/validate_naming.sh

# Verify permissions (production)
./scripts/verify-addon-permissions.sh

# Deploy to production
./scripts/deploy-odoo-modules.sh ipai_finance_ppm

# Run OCA-style CI locally
./scripts/ci_local.sh

# Pre-commit checks
pre-commit run --all-files
```

---

## 13. Common Anti-Patterns (Forbidden)

| Anti-Pattern | Why Forbidden | Correct Pattern |
|--------------|---------------|-----------------|
| `addons/my_module/` | Not in namespace | `addons/ipai/ipai_my_module/` |
| `ipai-new-module` | Dashes not allowed | `ipai_new_module` |
| `ipai_NewModule` | Uppercase not allowed | `ipai_new_module` |
| `version: '1.0.0'` | Wrong format | `version: '18.0.1.0.0'` |
| `license: 'MIT'` | Not OCA-approved | `license: 'AGPL-3'` |
| Hardcoded addons_path | Not deterministic | `python3 scripts/gen_addons_path.py` |
| Manual module install | Not CI-ready | `./scripts/odoo_update_modules.sh` |

---

## 14. Decision Record

**Date**: 2026-01-11
**Decision**: Adopt **Option B - Monorepo with OCA-compatible addons root**

**Rationale**:
- Production already uses `/addons/` structure (116 modules)
- Migration to pure OCA layout (Option A) would require:
  - Moving 116 modules to repo root
  - Updating all CI/deployment scripts
  - Changing production mount paths
  - Risk of breaking existing deployments
- Option B preserves compatibility while enforcing OCA standards

**Constraints**:
- `/addons/` is the **ONLY** addons root (no exceptions)
- All new modules **MUST** go in `/addons/ipai/`
- Legacy `/addons/ipai_*/` modules will be migrated over time
- OCA modules stay in `/addons/oca/` (vendor namespace)

**Enforcement**:
- CI validates all modules are in approved namespaces
- Scaffolder only creates modules in `/addons/ipai/`
- Pre-commit hooks enforce naming conventions
- Deployment script verifies module paths

---

## 15. OCA Template Integration

For creating standalone OCA-style addon repositories (outside this monorepo),
see [OCA_TEMPLATE_INTEGRATION.md](OCA_TEMPLATE_INTEGRATION.md) for:

- Copier-based repository bootstrapping
- Version branching (18.0, 19.0)
- CI and pre-commit setup from OCA template
- Module scaffolding with mrbob
- Template update protocol

### Enterprise Bridge Modules

Three key modules provide EE/IAP-free operation:

| Module | Purpose |
|--------|---------|
| `ipai_enterprise_bridge` | EE feature stubs, IAP bypass, OCA routing |
| `ipai_mail_integration` | Direct SMTP/Mailgun without IAP mail |
| `ipai_iot_bridge` | Direct device communication without EE IoT |

---

**This document is the canonical source of truth. All generators, validators, scaffolders, and deployment scripts must conform to these rules.**
