# Canonical Linting Rules

**Purpose**: Enforcement rules for canonical structure with clear rationale

---

## 1. Module Naming Rules

### LINT-001: No Dots in Technical Names
**Rule**: Module technical names MUST NOT contain dots (`.`)
**Why**: Odoo's module system treats dots as path separators, causing import failures
**Detection**: `find addons/ipai -type d -name "*.*"`
**Fix**: Rename directory and update all references

**Example violation**:
```
addons/ipai/ipai_month_end_closing.backup/  ❌
```

**Fix**:
```bash
mv addons/ipai/ipai_month_end_closing.backup addons/ipai/ipai_month_end_closing_backup
# Update: __manifest__.py, __init__.py, depends lists, XML references
```

### LINT-002: IPAI Prefix Required
**Rule**: All custom modules MUST start with `ipai_`
**Why**: Distinguishes custom modules from core/OCA, prevents naming conflicts
**Detection**: `find addons/ipai -type d -maxdepth 1 ! -name "ipai_*" ! -name "ipai"`
**Fix**: Rename module and update all references

### LINT-003: Snake Case Only
**Rule**: Module names MUST be lowercase with underscores only
**Why**: Python import compatibility, cross-platform consistency
**Detection**: `find addons/ipai -type d -name "*[A-Z]*" -o -name "*-*"`
**Fix**: Convert to snake_case

---

## 2. View Syntax Rules (Odoo 18)

### LINT-011: Use `<list>` Not `<tree>`
**Rule**: All list views MUST use `<list>` tag (Odoo 18 syntax)
**Why**: `<tree>` is deprecated in Odoo 18, will break in future versions
**Detection**: `grep -r "<tree" addons/ipai --include="*.xml"`
**Fix**: Replace `<tree>` with `<list>`, `</tree>` with `</list>`

**Example violation**:
```xml
<tree string="Expenses">  ❌
    <field name="name"/>
</tree>
```

**Fix**:
```xml
<list string="Expenses">  ✅
    <field name="name"/>
</list>
```

### LINT-012: Use `view_mode="list"` Not `"tree"`
**Rule**: All action view_mode MUST use `list`, not `tree`
**Why**: Matches Odoo 18 terminology, prevents confusion
**Detection**: `grep -r 'view_mode.*tree' addons/ipai --include="*.xml"`
**Fix**: Replace `tree` with `list` in view_mode attributes

**Example violation**:
```xml
<field name="view_mode">tree,form</field>  ❌
```

**Fix**:
```xml
<field name="view_mode">list,form</field>  ✅
```

---

## 3. Asset Structure Rules

### LINT-021: Assets in `static/src/` Only
**Rule**: All asset files MUST be in `<module>/static/src/{js,xml,scss}/`
**Why**: Standard Odoo convention, asset compiler expects this structure
**Detection**: `find addons/ipai -path "*/static/*" ! -path "*/static/src/*" -type f`
**Fix**: Move files to correct location, update manifest

**Example violation**:
```
addons/ipai/ipai_module/static/js/script.js  ❌
```

**Fix**:
```
addons/ipai/ipai_module/static/src/js/script.js  ✅
```

### LINT-022: Assets Registered in Manifest
**Rule**: All asset files MUST be registered in `__manifest__.py` `assets` dict
**Why**: Odoo asset compiler only processes registered assets
**Detection**: Compare filesystem assets vs manifest entries
**Fix**: Add missing entries to manifest

**Example violation**:
```python
# File exists: static/src/js/script.js
# But manifest has no 'assets' key
```

**Fix**:
```python
'assets': {
    'web.assets_backend': [
        'ipai_module/static/src/js/script.js',
    ],
}
```

### LINT-023: No Inline Scripts in Views
**Rule**: Views MUST NOT contain inline `<script>` or `<link>` tags
**Why**: Bypasses asset compiler, causes CSP violations, breaks caching
**Detection**: `grep -r '<script\|<link.*\.js\|<link.*\.css' addons/ipai --include="*.xml"`
**Fix**: Extract to separate files, register in manifest

---

## 4. Dependency Rules

### LINT-031: Explicit Dependencies
**Rule**: All module dependencies MUST be explicitly declared in `depends` list
**Why**: Auto-install can cause unpredictable installation order
**Detection**: Import analysis vs manifest depends
**Fix**: Add missing dependencies to manifest

**Example violation**:
```python
# Module uses 'sale.order' model
# But manifest has: 'depends': ['base']  ❌
```

**Fix**:
```python
'depends': ['base', 'sale']  ✅
```

### LINT-032: No Circular Dependencies
**Rule**: Module dependency graph MUST be acyclic (DAG)
**Why**: Circular dependencies cause installation failures
**Detection**: Graph cycle detection in audit script
**Fix**: Refactor modules to break cycles

---

## 5. Design Token Rules

### LINT-041: Centralized Tokens
**Rule**: Design tokens (colors, spacing, typography) MUST be in `ipai_platform_theme`
**Why**: Single source of truth, consistent theming, easy updates
**Detection**: Search for color/font definitions outside platform_theme
**Fix**: Move token definitions to `ipai_platform_theme`, import elsewhere

**Example violation**:
```scss
/* In ipai_custom_module/static/src/scss/style.scss */
$primary-color: #007bff;  ❌
```

**Fix**:
```scss
/* In ipai_platform_theme/static/src/scss/tokens.scss */
$primary-color: #007bff;  ✅

/* In ipai_custom_module/static/src/scss/style.scss */
@import 'ipai_platform_theme/static/src/scss/tokens';
```

### LINT-042: AI UI Isolation
**Rule**: AI assistant UI MUST only be in `ipai_ask_ai` or `ipai_ask_ai_chatter`
**Why**: Clear ownership, prevents scattered AI features
**Detection**: Search for AI-related components outside designated modules
**Fix**: Move components to correct module

---

## 6. Database Schema Rules

### LINT-051: Scout Namespace Consistency
**Rule**: Scout tables MUST use canonical schema prefixes
**Why**: Clear layer separation (bronze/silver/gold/platinum)
**Detection**: Query database for scout.* tables without standard prefixes
**Fix**: Rename tables, update queries and models

**Expected schemas**:
- `scout.bronze_*` - Raw ingestion
- `scout.silver_*` - Cleaned/validated
- `scout.gold_*` - Business logic applied
- `scout.platinum_*` - Aggregated/enriched
- `scout.deep_research_*` - AI/ML features

### LINT-052: Odoo Standard Schema
**Rule**: Odoo models MUST use standard `public` schema unless isolation required
**Why**: Odoo ORM expects public schema, custom schemas need special handling
**Detection**: Check model `_table` attribute for non-standard schemas
**Fix**: Remove custom schema prefix or justify requirement

---

## 7. Runtime Identifier Rules

### LINT-061: Canonical Container Names
**Rule**: Docker containers MUST use `-prod` suffix for production
**Why**: Clear production vs dev/staging distinction
**Detection**: `docker ps --format '{{.Names}}'` vs canonical list
**Fix**: Update docker-compose.yml service names

**Canonical names**:
- `odoo-prod` (not `odoo-erp-prod` or `odoo`)
- `postgres-prod` (not `db` or `postgres`)
- `nginx-prod`, `n8n-prod`, `superset-prod`

### LINT-062: Volume Persistence
**Rule**: Odoo filestore MUST be mounted to named volume or bind mount
**Why**: Prevents data loss on container recreation
**Detection**: `docker inspect odoo-prod --format '{{json .Mounts}}'`
**Fix**: Add volume mount to docker-compose.yml

**Expected mount**:
```yaml
volumes:
  - odoo-web-data:/var/lib/odoo  ✅
```

---

## 8. CI Enforcement

### Local Validation
```bash
# Run full audit
python scripts/canonical_audit.py --all

# Fix auto-fixable issues
python scripts/canonical_audit.py --all --fix

# Strict mode (fail on any violation)
python scripts/canonical_audit.py --all --strict
```

### CI Gate
**Workflow**: `.github/workflows/canonical-gate.yml`
**Trigger**: All PRs
**Steps**:
1. Run `canonical_audit.py --all --strict`
2. Odoo install check: `odoo -d test --stop-after-init`
3. Asset build check: `odoo -d test --dev assets`
4. Fail PR if any violations

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e
python scripts/canonical_audit.py --all --strict
echo "✅ Canonical audit passed"
```

---

## 9. Violation Severity

### Critical (Block PR)
- LINT-001: Dotted module names (causes import failures)
- LINT-022: Unregistered assets (breaks asset compiler)
- LINT-032: Circular dependencies (installation failures)
- LINT-062: Missing filestore mount (data loss risk)

### High (Fix Soon)
- LINT-011: `<tree>` usage (deprecated, future breaking)
- LINT-012: `view_mode="tree"` (deprecated)
- LINT-031: Missing dependencies (unpredictable behavior)
- LINT-041: Scattered design tokens (maintainability)

### Medium (Technical Debt)
- LINT-002: Non-IPAI prefix (naming confusion)
- LINT-021: Assets outside `static/src/` (convention violation)
- LINT-042: Scattered AI UI (organizational)
- LINT-051: Inconsistent Scout schemas (clarity)

### Low (Nice to Have)
- LINT-003: Non-snake_case names (convention)
- LINT-023: Inline scripts (best practice)
- LINT-052: Non-standard Odoo schemas (rare use case)

---

## 10. Automated Fixes

### Safe Auto-Fixes (No Manual Review)
- LINT-011: `<tree>` → `<list>` replacement
- LINT-012: `view_mode="tree"` → `view_mode="list"`
- LINT-021: Move assets to `static/src/` (preserve directory structure)

### Manual Review Required
- LINT-001: Module renames (affects dependencies)
- LINT-031: Dependency additions (verify correctness)
- LINT-032: Circular dependency breaks (requires refactoring)
- LINT-041: Token consolidation (test thoroughly)

### No Auto-Fix
- LINT-062: Volume mounts (infrastructure change)
- LINT-051: Schema migrations (data migration required)

---

## 11. Exclusions

### Excluded Paths
```python
EXCLUDED_PATHS = [
    'addons/ipai/*/tests/',         # Test fixtures
    'addons/ipai/*/migrations/',    # Migration scripts
    'addons/ipai/*/static/lib/',    # Third-party libraries
    'addons/oca/',                  # OCA modules (external)
]
```

### Grandfathered Violations
```python
GRANDFATHERED = {
    'LINT-041': ['ipai_legacy_module'],  # Legacy tokens, migration planned
}
```

---

## 12. Reporting

### Human-Readable Report
```
=== Canonical Audit Report ===
Total violations: 127
Critical: 2
High: 45
Medium: 60
Low: 20

LINT-001 (Critical): 1 violation
  - addons/ipai/ipai_module.backup/ (dotted name)

LINT-011 (High): 71 violations
  - addons/ipai/ipai_finance_ppm/views/logframe_views.xml:45
  - addons/ipai/ipai_workspace_core/views/task_views.xml:12
  ...
```

### JSON Report (CI Integration)
```json
{
  "version": "1.0.0",
  "timestamp": "2026-01-08T15:30:00Z",
  "summary": {
    "total": 127,
    "critical": 2,
    "high": 45,
    "medium": 60,
    "low": 20
  },
  "violations": [
    {
      "rule": "LINT-001",
      "severity": "critical",
      "path": "addons/ipai/ipai_module.backup/",
      "message": "Module name contains dots",
      "fix": "Rename to ipai_module_backup"
    }
  ]
}
```

---

**Last Updated**: 2026-01-08
**Version**: 1.0.0
