# IPAI Install Profiles

**Purpose**: Define deterministic module installation profiles for different use cases
**Status**: ✅ All module names validated against repository (`addons/ipai/`)

---

## Profile Philosophy

**Core Principle**: Install **Odoo CE + OCA baseline first**, then **one profile** based on business need.

**Anti-Pattern**: Installing all 79 IPAI modules at once → dependency hell, asset conflicts, performance degradation

---

## Profile: `finance_prod` (Production Finance)

**Use Case**: Philippine finance operations with BIR compliance, month-end closing, and BI integration

**Module Count**: 10 IPAI modules (87% reduction from 79 total)

**Validation**: ✅ All module names confirmed to exist in `addons/ipai/`

### Install Order

#### Step 1: Odoo CE Core (Baseline)
```bash
# Auto-installed with Odoo
base, web, mail, account, sale_management, project, hr
```

#### Step 2: OCA Foundation (CE Branding + Advanced Features)
```bash
odoo -d production -i \
  remove_odoo_enterprise \
  disable_odoo_online \
  server_environment \
  base_user_role
```

**Why**:
- `remove_odoo_enterprise`: Clean CE branding (no Enterprise upsell)
- `disable_odoo_online`: Remove odoo.com integration
- `server_environment`: Multi-environment config management
- `base_user_role`: Advanced permission management

#### Step 3: IPAI Platform Services (2 modules)
```bash
odoo -d production -i \
  ipai_platform_theme \
  ipai_approvals
```

**Modules**:
- `ipai_platform_theme` - Design tokens (CSS variables, SCSS maps)
- `ipai_approvals` - Approval workflows for finance operations

**Why**: Core services that other IPAI modules depend on

#### Step 4: IPAI Finance Core (4 modules)
```bash
odoo -d production -i \
  ipai_finance_ppm \
  ipai_ppm_monthly_close \
  ipai_finance_ppm_closing \
  ipai_finance_bir_compliance
```

**Modules**:
- `ipai_finance_ppm` - Finance PPM dashboard
- `ipai_ppm_monthly_close` - Monthly close scheduler
- `ipai_finance_ppm_closing` - Closing task generator (canonical)
- `ipai_finance_bir_compliance` - BIR tax filing (canonical)

**Why**: PH finance-specific workflows and BIR compliance

#### Step 5: IPAI Integrations (2 modules)
```bash
odoo -d production -i \
  ipai_superset_connector \
  ipai_ocr_expense
```

**Modules**:
- `ipai_superset_connector` - Apache Superset BI integration
- `ipai_ocr_expense` - OCR expense processing

**Why**: External service integrations (BI, OCR)

#### Step 6: IPAI AI Layer (1 module - Optional)
```bash
odoo -d production -i \
  ipai_ask_ai
```

**Modules**:
- `ipai_ask_ai` - AI chat interface for Odoo

**Why**: AI chat interface (optional, can be skipped)

#### Step 7: IPAI Theme (1 module - Install LAST)
```bash
odoo -d production -i \
  ipai_theme_tbwa_backend
```

**Modules**:
- `ipai_theme_tbwa_backend` - TBWA corporate branding

**Why**: Install AFTER all functional modules to avoid asset conflicts

### Complete Install Command

```bash
#!/bin/bash
# scripts/install_finance_prod.sh

DB="${1:-production}"

echo "Installing finance_prod profile to database: $DB"

# Step 1: OCA Foundation
echo "Step 1/6: Installing OCA Foundation..."
odoo -d "$DB" -i remove_odoo_enterprise,disable_odoo_online,server_environment,base_user_role --stop-after-init

# Step 2: IPAI Platform
echo "Step 2/6: Installing IPAI Platform..."
odoo -d "$DB" -i ipai_platform_theme,ipai_approvals --stop-after-init

# Step 3: IPAI Finance
echo "Step 3/6: Installing IPAI Finance..."
odoo -d "$DB" -i ipai_finance_ppm,ipai_ppm_monthly_close,ipai_finance_ppm_closing,ipai_finance_bir_compliance --stop-after-init

# Step 4: IPAI Integrations
echo "Step 4/6: Installing IPAI Integrations..."
odoo -d "$DB" -i ipai_superset_connector,ipai_ocr_expense --stop-after-init

# Step 5: IPAI AI
echo "Step 5/6: Installing IPAI AI..."
odoo -d "$DB" -i ipai_ask_ai --stop-after-init

# Step 6: IPAI Theme (LAST)
echo "Step 6/6: Installing IPAI Theme..."
odoo -d "$DB" -i ipai_theme_tbwa_backend --stop-after-init

echo "✅ finance_prod profile installed successfully"
```

### Module Breakdown

| Tier | Category | Module Count | Modules |
|------|----------|--------------|---------|
| 2 | Platform | 2 | `ipai_platform_theme`, `ipai_approvals` |
| 3 | Finance | 4 | `ipai_finance_ppm`, `ipai_ppm_monthly_close`, `ipai_finance_ppm_closing`, `ipai_finance_bir_compliance` |
| 4 | Integrations | 2 | `ipai_superset_connector`, `ipai_ocr_expense` |
| 5 | AI | 1 | `ipai_ask_ai` |
| 6 | Theme | 1 | `ipai_theme_tbwa_backend` |
| **Total** | | **10** | |

---

## Profile: `workos_experimental` (Development/Testing)

**Status**: ⚠️ **NOT AVAILABLE** - WorkOS modules don't exist in repository yet

**Original Plan**: AFFiNE/WorkOS integration development and testing (9 modules)

**Reality**: None of the planned WorkOS modules exist in `addons/ipai/`:
- `ipai_workos_affine` ❌
- `ipai_workos_core` ❌
- `ipai_workos_blocks` ❌
- `ipai_workos_canvas` ❌
- `ipai_workos_collab` ❌
- `ipai_workos_db` ❌
- `ipai_workos_search` ❌
- `ipai_workos_templates` ❌
- `ipai_workos_views` ❌

**Action**: This profile cannot be created until WorkOS modules are implemented

---

## Profile Enforcement

### CI Validation

```yaml
# .github/workflows/profile-validation.yml
name: Profile Validation

on:
  pull_request:
    paths:
      - 'addons/ipai/**/__manifest__.py'
      - 'scripts/install_*.sh'

jobs:
  validate-finance-prod:
    runs-on: ubuntu-latest
    steps:
      - name: Validate finance_prod Profile
        run: |
          python3 - <<'PY'
          import pathlib, sys

          FINANCE_PROD = [
              'ipai_platform_theme',
              'ipai_approvals',
              'ipai_finance_ppm',
              'ipai_ppm_monthly_close',
              'ipai_finance_ppm_closing',
              'ipai_finance_bir_compliance',
              'ipai_superset_connector',
              'ipai_ocr_expense',
              'ipai_ask_ai',
              'ipai_theme_tbwa_backend',
          ]

          repo_modules = set([p.name for p in pathlib.Path("addons/ipai").iterdir() if p.is_dir()])
          errors = []

          # Check all modules exist
          for mod in FINANCE_PROD:
              if mod not in repo_modules:
                  errors.append(f"{mod}: Module not found")

          # Check all modules are installable
          import re
          for mod in FINANCE_PROD:
              manifest = f"addons/ipai/{mod}/__manifest__.py"
              try:
                  with open(manifest) as f:
                      content = f.read()
                      if not re.search(r"['\"]installable['\"]\s*:\s*True", content):
                          errors.append(f"{mod}: Must be installable for finance_prod")
              except FileNotFoundError:
                  errors.append(f"{mod}: Manifest not found")

          if errors:
              print("❌ finance_prod profile validation failed:")
              for e in errors:
                  print(f"  - {e}")
              sys.exit(1)

          print(f"✅ finance_prod profile valid ({len(FINANCE_PROD)} modules)")
          PY
```

---

## Install Scripts

### Location
```
scripts/
├── install_finance_prod.sh      # Production profile
└── deprecate_modules.sh          # Deprecation automation
```

### Usage

```bash
# Production install
./scripts/install_finance_prod.sh production

# Development install (same profile for now)
./scripts/install_finance_prod.sh development
```

---

## Migration from "Install Everything"

If you currently have all modules installed:

### Option 1: Fresh Install (Recommended)

1. **Export data**:
```bash
odoo-bin -d old_db --stop-after-init --data-export > production_data.json
```

2. **Create new database**:
```bash
createdb production_clean
```

3. **Install finance_prod profile**:
```bash
./scripts/install_finance_prod.sh production_clean
```

4. **Import data**:
```bash
odoo-bin -d production_clean --stop-after-init --data-import < production_data.json
```

### Option 2: Uninstall Unwanted Modules

```bash
# Uninstall deprecated modules
odoo -d production -u ipai_finance_month_end,ipai_finance_monthly_closing,ipai_bir_compliance

# Note: WorkOS modules don't exist, so nothing to uninstall

# Verify
python3 - <<'PY'
import pathlib

FINANCE_PROD = [
    "ipai_platform_theme",
    "ipai_approvals",
    "ipai_finance_ppm",
    "ipai_ppm_monthly_close",
    "ipai_finance_ppm_closing",
    "ipai_finance_bir_compliance",
    "ipai_superset_connector",
    "ipai_ocr_expense",
    "ipai_ask_ai",
    "ipai_theme_tbwa_backend",
]

repo_modules = set([p.name for p in pathlib.Path("addons/ipai").iterdir() if p.is_dir()])
missing = [m for m in FINANCE_PROD if m not in repo_modules]

if missing:
    print("❌ Missing modules:")
    for m in missing:
        print(f"  - {m}")
else:
    print("✅ All finance_prod modules exist")
PY
```

---

## Troubleshooting

### Common Issues

**Module not found**
```bash
# Ensure module is in addons path
ls addons/ipai/ | grep -E "ipai_platform_theme|ipai_approvals"

# Update module list
docker compose exec odoo-core odoo -d production -u base
```

**Asset 500 Errors**

**Symptom**: `web.assets_*.min.{css,js}` return 500 errors

**Cause**: Multiple theme modules installed, conflicting asset bundles

**Fix**:
```bash
# Uninstall conflicting theme (if any other theme is installed)
odoo -d production -u ipai_chatgpt_sdk_theme

# Keep only: ipai_platform_theme (tokens) + ipai_theme_tbwa_backend (skin)

# Regenerate assets
odoo -d production --stop-after-init
docker restart odoo-core
```

**Circular Dependencies**

**Symptom**: `Module 'A' depends on 'B', which depends on 'A'`

**Cause**: Improper module design

**Fix**:
```bash
# Check dependency graph
python3 scripts/generate_dependency_graph.py

# Follow install order from this documentation (Tiers 2-6)
```

---

## Best Practices

### ✅ Do
- Install profiles in documented order (OCA → Platform → Finance → Integrations → AI → Theme)
- Use finance_prod profile for production (10 modules only)
- Test profile install on clean database before production
- Keep theme modules last to avoid asset conflicts

### ❌ Don't
- Install all 79 modules at once
- Skip OCA foundation modules
- Install multiple backend themes simultaneously
- Install WorkOS modules (they don't exist yet)

---

## Machine-Readable Profile

**File**: `docs/ipai/profiles/finance_prod.txt`

```
# Finance Production Profile - Corrected Module Names
# Total: 10 modules (validated against actual repo)
# Last updated: 2025-01-09

# Platform (2 modules)
ipai_platform_theme
ipai_approvals

# Finance Core (4 modules)
ipai_finance_ppm
ipai_ppm_monthly_close
ipai_finance_ppm_closing
ipai_finance_bir_compliance

# Integrations (2 modules)
ipai_superset_connector
ipai_ocr_expense

# AI (1 module)
ipai_ask_ai

# Theme (1 module)
ipai_theme_tbwa_backend
```

---

**Last Updated**: 2026-01-09
**Maintained By**: InsightPulse AI DevOps Team
**Validation Status**: ✅ All module names confirmed against repository
