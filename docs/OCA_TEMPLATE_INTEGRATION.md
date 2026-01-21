# OCA Template Integration Contract

**Repository**: `odoo-ce` (jgtolentino/odoo-ce)
**Template Source**: https://github.com/OCA/oca-addons-repo-template
**Supported Versions**: 18.0, 19.0
**Last Updated**: 2026-01-21
**Status**: Canonical baseline for all `ipai_*` addon repositories

---

## Repository & Layout Constraints

All Odoo addon code for CE+OCA+`ipai_*` must follow the official OCA template conventions.

### 1. OCA-Style Repo Creation

New addon repositories (for `ipai_*` modules, including `ipai_enterprise_bridge`) MUST be bootstrapped using the OCA template via Copier:

```bash
copier copy --UNSAFE https://github.com/OCA/oca-addons-repo-template.git <repo-name>
```

**Resulting Structure** (must be kept intact as baseline):
- `src/` - Addon source directory
- `tests/` - Test infrastructure
- `.github/workflows/` - CI workflows
- `version-specific/` - Version-specific configurations
- `pyproject.toml` - Python project metadata
- `setup.cfg` - Package configuration
- `.pre-commit-config.yaml` - OCA pre-commit hooks

### 2. Version Branching

Use OCA-standard branches:
- `18.0` - Odoo 18 series
- `19.0` - Odoo 19 series

**Rules**:
- 18.0-specific addons belong under the 18.0 branch
- 19.0-specific addons belong under the 19.0 branch
- No cross-version hacks inside the same branch

### 3. Addons Location

For **standalone OCA-style repos** (e.g., `odoo-ipai-addons`):
- Addons MUST be placed under the OCA-standard `src/` tree
- Example: `src/ipai_enterprise_bridge`, `src/ipai_mail_integration`
- No custom top-level layout; follow OCA decisions

For **this monorepo** (`odoo-ce`):
- Addons go in `/addons/ipai/<module_name>/`
- See [OCA_STYLE_CONTRACT.md](OCA_STYLE_CONTRACT.md) for detailed rules

### 4. CI & Pre-commit

- Respect and extend the CI and pre-commit setup provided by the template
- Integrate new CI checks into the existing structure
- Obey the **CI GREEN POLICY**: consolidate jobs rather than add endless new ones
- Use `copier update --UNSAFE` as the standard way to receive template updates

### 5. License & Contribution Model

- Primary license: **AGPL-3** (OCA default)
- Alternative: **LGPL-3** (for connector/library modules)
- Follow `CONTRIBUTING.md` rules where applicable

---

## Bootstrap Commands for New OCA-Style Repo

### Prerequisites

```bash
# Install copier + pre-commit (if not installed)
pipx install copier
pipx install pre-commit
pipx ensurepath
hash copier 2>/dev/null || echo "ERROR: copier not on PATH"
hash pre-commit 2>/dev/null || echo "ERROR: pre-commit not on PATH"
```

### Generate Repository

```bash
# Generate a new OCA-style repo for IPAI addons
copier copy --UNSAFE https://github.com/OCA/oca-addons-repo-template.git odoo-ipai-addons

cd odoo-ipai-addons

# Initialize git and pre-commit
git init
git add .
pre-commit install
pre-commit run -a
git commit -am "Bootstrap from OCA oca-addons-repo-template"
```

### Setup Version Branches

```bash
# Create 18.0 and 19.0 branches as per OCA conventions
git branch -M 18.0
git checkout -b 19.0

# Push to GitHub after adding remote
# git remote add origin git@github.com:jgtolentino/odoo-ipai-addons.git
# git push -u origin 18.0
# git push -u origin 19.0
```

### Add Addon Skeletons

For standalone repos using OCA template:
```bash
mkdir -p src/ipai_enterprise_bridge
mkdir -p src/ipai_mail_integration
mkdir -p src/ipai_iot_bridge
```

For this monorepo (`odoo-ce`):
```bash
# Create in the canonical location
mkdir -p addons/ipai/ipai_enterprise_bridge
mkdir -p addons/ipai/ipai_mail_integration
mkdir -p addons/ipai/ipai_iot_bridge
```

---

## Integration with odoo-ce Monorepo

This monorepo uses a hybrid approach:

| Aspect | OCA Template (standalone) | odoo-ce Monorepo |
|--------|---------------------------|------------------|
| Addons root | `src/` | `addons/ipai/` |
| Pre-commit | Template-provided | Custom OCA-aligned |
| CI | Template workflows | Custom workflows |
| Version branches | 18.0, 19.0 | main (single branch) |

### When to Use Which Approach

**Use standalone OCA-style repo** when:
- Creating a new set of related addons for external distribution
- Modules need to be published to OCA or PyPI
- Independent versioning is required

**Use this monorepo** when:
- Creating IPAI-specific modules tightly coupled to the stack
- Modules integrate with multiple IPAI services
- Rapid iteration with shared CI/CD is needed

---

## OCA Module Scaffolding (mrbob)

For rapid module creation within this monorepo:

### Install

```bash
pipx install mrbob
pipx inject mrbob bobtemplates.odoo
```

### Create Addon

```bash
# Generate in temp location
cd /tmp
mrbob bobtemplates.odoo:addon

# Move to canonical location
mv <generated_module> /path/to/odoo-ce/addons/ipai/
```

### Create Model

```bash
# Inside module directory
cd addons/ipai/ipai_enterprise_bridge
mrbob bobtemplates.odoo:model
```

---

## Template Update Protocol

To receive upstream OCA template improvements:

```bash
# In standalone OCA-style repo
cd odoo-ipai-addons
copier update --UNSAFE

# Review changes
git diff
pre-commit run -a
git commit -am "chore(oca): update from OCA template"
```

**Note**: Never run `copier` in the odoo-ce monorepo root - it will overwrite the structure.

---

## Verification Commands

### For Standalone OCA-Style Repos

```bash
# Python & tooling checks from template
pytest
pre-commit run -a
```

### For This Monorepo

```bash
# OCA-style verification
pre-commit run -a
./scripts/verify_local.sh

# Module smoke test
docker compose exec odoo-core odoo -d odoo_core -i ipai_enterprise_bridge --stop-after-init
```

---

## Enterprise Bridge Modules

Three key modules for EE/IAP-free operation:

### ipai_enterprise_bridge

**Purpose**: EE/IAP-free bridge for IPAI CE+OCA stack
**Location**: `addons/ipai/ipai_enterprise_bridge/`
**Dependencies**: Core OCA modules (server-tools, web)

Key features:
- Enterprise feature stubs for compatibility
- IAP bypass configurations
- OCA-based alternatives routing

### ipai_mail_integration

**Purpose**: Mailgun/SMTP/OAuth mail integration without IAP
**Location**: `addons/ipai/ipai_mail_integration/`
**Dependencies**: `mail`, OCA mail modules

Key features:
- Direct SMTP/Mailgun integration
- OAuth2 authentication
- No odoo.com IAP dependencies

### ipai_iot_bridge

**Purpose**: IoT device bridge for CE+OCA without EE IoT dependencies
**Location**: `addons/ipai/ipai_iot_bridge/`
**Dependencies**: Base IoT modules

Key features:
- Direct device communication
- MQTT/REST protocols
- No Enterprise IoT box required

---

## Forbidden Patterns

- Running `copier` in the odoo-ce repo root
- Overwriting repo layout with template defaults
- Introducing a second "root" structure
- Moving existing directories to match the template
- Cross-version hacks in the same branch

---

## Quick Reference

| Item | Value |
|------|-------|
| Template | https://github.com/OCA/oca-addons-repo-template |
| Copier Command | `copier copy --UNSAFE <template> <dest>` |
| Update Command | `copier update --UNSAFE` |
| Scaffolder | `mrbob bobtemplates.odoo:addon` |
| Primary License | AGPL-3 |
| Version Branches | 18.0, 19.0 |

---

*This document supplements [OCA_STYLE_CONTRACT.md](OCA_STYLE_CONTRACT.md) with template-specific guidance.*
