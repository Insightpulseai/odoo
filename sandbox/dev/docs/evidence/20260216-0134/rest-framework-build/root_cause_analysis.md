# REST Framework Installation — Root Cause Analysis

## Issue
`base_rest` remains uninstallable despite Python dependencies (apispec, cerberus, pyquerystring, parse-accept-language) being correctly installed at build time.

## Root Cause
**Version Mismatch:** rest-framework repository is on Odoo 18.0 branch, not 19.0

### Evidence

**base_rest manifest version:**
```
"version": "18.0.1.1.1"
```

**Other OCA modules (correct):**
```
web_responsive: "19.0.1.0.1"
auditlog: "19.0.1.0.1"
```

**base_rest dependencies (from manifest):**
```
"depends": ["component", "web"]
```

**Missing dependency:** `component` module not found in current OCA repos

## Diagnosis

1. **OCA rest-framework** repository for Odoo 19.0 either:
   - Doesn't exist yet (OCA hasn't released it)
   - Wasn't aggregated correctly (git-aggregator fell back to 18.0)

2. **component module** (from OCA/connector) is required but:
   - Not present in aggregated modules
   - Likely also version 18.0 only

3. **Odoo 18.x modules may not be compatible with Odoo 19 runtime**

## Solutions

### Option 1: Check OCA rest-framework 19.0 availability
```bash
# Check if 19.0 branch exists
curl -s https://api.github.com/repos/OCA/rest-framework/branches | jq -r '.[].name' | grep 19.0
```

### Option 2: Wait for OCA 19.0 release
Monitor: https://github.com/OCA/rest-framework

### Option 3: Use alternative REST implementation
- Odoo native HTTP controllers
- Custom REST wrapper for Odoo 19

### Option 4: Install component dependency (risky)
- Add OCA/connector to oca-aggregate.yml
- Hope for Odoo 18→19 cross-compatibility
- Not recommended for production

## Verification Status

✅ Python dependencies installed correctly (apispec, cerberus, etc.)
✅ Docker image build works
✅ Dependencies available in container
❌ base_rest uninstallable due to missing `component` dependency
❌ rest-framework on wrong Odoo version (18.0 vs required 19.0)

## Recommendation

**Hold on REST framework installation** until:
1. OCA releases rest-framework for Odoo 19.0, OR
2. Verify component module exists for Odoo 19 and add to oca-aggregate.yml

**Success achieved:**
- ✅ Deterministic Python dependency packaging (SSOT)
- ✅ Build-time installation (no runtime drift)
- ✅ 3/3 web modules installed (web_responsive, web_environment_ribbon, web_dialog_size)

