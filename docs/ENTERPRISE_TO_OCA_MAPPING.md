# Enterprise to OCA/CE Replacement Mapping (Odoo 18)

_Generated: 2026-01-14_

## Enterprise Conflicts Detected (10 occurrences)

### 1. `documents` (5 occurrences)
**Enterprise Module**: `documents` - Document Management System

**OCA Replacement (Odoo 18)**:
- **Primary**: `dms` (Document Management System) from OCA/dms
  - Repo: https://github.com/OCA/dms
  - Module: `dms`
  - Features: Folder hierarchy, file versioning, access rights, tags

**Installation**:
```bash
# Clone OCA dms repo
git clone -b 18.0 https://github.com/OCA/dms.git addons/oca/dms

# Install module
docker exec odoo-dev odoo -d odoo_dev -i dms --stop-after-init
```

**Affected Modules**:
- `addons/ipai/ipai_agent_core/__manifest__.py`
- `addons/ipai/ipai_ask_ai_chatter/__manifest__.py`
- `addons/ipai/ipai_dev_studio_base/__manifest__.py`
- `addons/ipai/ipai_document_ai/__manifest__.py`
- `addons/ipai_ocr_gateway/__manifest__.py`

**Action Required**: Replace `documents` dependency with `dms` in manifests

---

### 2. `studio` (3 occurrences)
**Enterprise Module**: `studio` - Odoo Studio (Visual App Builder)

**CE Alternative**:
- **Native CE**: Use standard Odoo development (no direct replacement)
- **OCA Alternative**: `base_view_inheritance_extension` from OCA/server-tools
  - Repo: https://github.com/OCA/server-tools
  - Module: `base_view_inheritance_extension`
  - Features: Advanced view inheritance capabilities

**Installation**:
```bash
# Clone OCA server-tools repo
git clone -b 18.0 https://github.com/OCA/server-tools.git addons/oca/server-tools

# Install module
docker exec odoo-dev odoo -d odoo_dev -i base_view_inheritance_extension --stop-after-init
```

**Affected Modules**:
- `addons/ipai/ipai_dev_studio_base/__manifest__.py`
- `addons/ipai/ipai_studio_ai/__manifest__.py`
- `addons/ipai/ipai_ai_studio/__manifest__.py`

**Action Required**:
- Remove `studio` dependency (not required for runtime)
- Add `base_view_inheritance_extension` if advanced view inheritance needed

---

### 3. `sign` (1 occurrence)
**Enterprise Module**: `sign` - Electronic Signature

**OCA Replacement**:
- **No direct OCA replacement for Odoo 18 yet**
- **Alternative Approaches**:
  1. Use external service integration (DocuSign, HelloSign API)
  2. Simple approval workflows with `base_automation` (CE)
  3. Wait for OCA/contract module to add e-signature support

**Affected Modules**:
- `addons/ipai_finance_ppm_golive/__manifest__.py`

**Action Required**:
- Remove `sign` dependency
- Implement approval workflow using `project` + `mail` features
- Consider external e-signature API integration if needed

---

### 4. `web_enterprise` (1 occurrence)
**Enterprise Module**: `web_enterprise` - Enterprise Web UI Features

**OCA Replacement**:
- **Primary**: `web_responsive` from OCA/web
  - Repo: https://github.com/OCA/web
  - Module: `web_responsive`
  - Features: Responsive design, mobile-friendly interface

- **Additional**: `web_dialog_size` from OCA/web
  - Module: `web_dialog_size`
  - Features: Configurable dialog sizes

**Installation**:
```bash
# Clone OCA web repo
git clone -b 18.0 https://github.com/OCA/web.git addons/oca/web

# Install modules
docker exec odoo-dev odoo -d odoo_dev -i web_responsive,web_dialog_size --stop-after-init
```

**Affected Modules**:
- `addons/ipai_theme_tbwa_backend/__manifest__.py`

**Action Required**: Replace `web_enterprise` with `web_responsive` + `web_dialog_size`

---

## Summary Table

| Enterprise Module | OCA Replacement | OCA Repo | Odoo 18 Available | Action |
|-------------------|-----------------|----------|-------------------|--------|
| `documents` | `dms` | OCA/dms | ✅ Yes | Replace in 5 manifests |
| `studio` | `base_view_inheritance_extension` | OCA/server-tools | ✅ Yes | Remove (dev-only) |
| `sign` | None (use workflow) | N/A | ❌ No | Remove, use approval workflow |
| `web_enterprise` | `web_responsive` + `web_dialog_size` | OCA/web | ✅ Yes | Replace in 1 manifest |

---

## Installation Order

```bash
# 1. Clone required OCA repos (Odoo 18.0 branch)
cd ~/Documents/GitHub/odoo-ce
git clone -b 18.0 https://github.com/OCA/dms.git addons/oca/dms
git clone -b 18.0 https://github.com/OCA/server-tools.git addons/oca/server-tools
git clone -b 18.0 https://github.com/OCA/web.git addons/oca/web

# 2. Install OCA modules
docker exec odoo-dev odoo -d odoo_dev -i \
  dms,\
  base_view_inheritance_extension,\
  web_responsive,\
  web_dialog_size \
  --stop-after-init

# 3. Update module list
docker exec odoo-dev odoo -d odoo_dev -u base --stop-after-init
```

---

## Manifest Updates Required

### documents → dms (5 files)

**Files to update:**
1. `addons/ipai/ipai_agent_core/__manifest__.py`
2. `addons/ipai/ipai_ask_ai_chatter/__manifest__.py`
3. `addons/ipai/ipai_dev_studio_base/__manifest__.py`
4. `addons/ipai/ipai_document_ai/__manifest__.py`
5. `addons/ipai_ocr_gateway/__manifest__.py`

**Change**: Replace 'documents' with 'dms' in depends list

### studio → remove or replace (3 files)

**Files to update:**
1. `addons/ipai/ipai_dev_studio_base/__manifest__.py`
2. `addons/ipai/ipai_studio_ai/__manifest__.py`
3. `addons/ipai/ipai_ai_studio/__manifest__.py`

**Change**: Remove 'studio' or replace with 'base_view_inheritance_extension'

### sign → remove (1 file)

**File to update:**
1. `addons/ipai_finance_ppm_golive/__manifest__.py`

**Change**: Remove 'sign' from depends list

### web_enterprise → web_responsive (1 file)

**File to update:**
1. `addons/ipai_theme_tbwa_backend/__manifest__.py`

**Change**: Replace 'web_enterprise' with 'web_responsive', 'web_dialog_size'

---

## Verification Commands

```bash
# Verify OCA modules installed
docker exec odoo-dev odoo shell -d odoo_dev <<'PYEOF'
modules = env['ir.module.module'].search([
    ('name', 'in', ['dms', 'base_view_inheritance_extension', 'web_responsive', 'web_dialog_size'])
])
for m in modules:
    print(f"{m.name}: {m.state}")
PYEOF

# Verify no enterprise dependencies
docker exec odoo-dev odoo shell -d odoo_dev <<'PYEOF'
enterprise_mods = env['ir.module.module'].search([
    ('name', 'in', ['documents', 'studio', 'sign', 'web_enterprise']),
    ('state', '!=', 'uninstalled')
])
if enterprise_mods:
    print("ERROR: Enterprise modules still installed:")
    for m in enterprise_mods:
        print(f"  - {m.name}: {m.state}")
else:
    print("✅ No enterprise modules installed")
PYEOF
```
