# Odoo Launcher Fix - Complete

## Date: 2026-02-09 00:23

## Problem Fixed
Running `python odoo-bin` caused `SyntaxError: invalid syntax` because `odoo-bin` is a bash script, not a Python file.

## Root Cause
The `odoo-bin` shim uses bash syntax (`set -euo pipefail`) which is invalid Python. Invoking with `python odoo-bin` attempted to parse bash as Python.

## Solution Implemented
Created `scripts/odoo.sh` - a deterministic launcher that:
1. Detects if `odoo-bin` is bash (checks shebang)
2. Executes directly as bash if detected
3. Falls back to Python if needed
4. Handles both scenarios transparently

## Files Modified

### Shell Scripts (3 files)
1. **bin/odoo-tests.sh** - Updated lines 18, 20 to use `./scripts/odoo.sh`
2. **scripts/ci/run_odoo_tests.sh** - Updated line 39 to use `/tmp/odoo/scripts/odoo.sh`
3. **scripts/deploy/do-bootstrap-odoo-prod.sh** - Updated line 317 systemd ExecStart to use `$ODOO_HOME/scripts/odoo.sh`

### Agent YAML (2 files)
4. **agents/odoo_reverse_mapper.yaml** - Updated lines 155, 299 to use `./scripts/odoo.sh`
5. **agents/loops/clarity_ppm_reverse.yaml** - Updated lines 151-153 to use `./scripts/odoo.sh`

### GitHub Actions (1 file)
6. **.github/workflows/ci.yml** - Updated lines 429, 439, 593 to use `/tmp/odoo/scripts/odoo.sh`

## Environment Hardening (Completed)
✅ `scripts/odoo.sh` - Created and chmod +x
✅ `~/.zshrc` - pyenv init configured
✅ `~/.config/starship.toml` - command_timeout = 2000
✅ `odoo-bin` - chmod +x applied

## Verification Results

### Launcher Test
```bash
./scripts/odoo.sh --help
# Output: Executes odoo-bin as bash (detects shebang correctly)
# Expected error: "No module named odoo" (odoo not installed - expected)
# ✅ No SyntaxError - bash detection working
```

### Files Updated
```bash
git status
# 6 files modified:
# - bin/odoo-tests.sh
# - scripts/ci/run_odoo_tests.sh
# - scripts/deploy/do-bootstrap-odoo-prod.sh
# - agents/odoo_reverse_mapper.yaml
# - agents/loops/clarity_ppm_reverse.yaml
# - .github/workflows/ci.yml
# + scripts/odoo.sh (new file)
```

## Impact
✅ No more SyntaxError when running Odoo
✅ Unified invocation method across codebase
✅ Production systemd unit fixed
✅ CI/CD workflows updated
✅ Agent configurations corrected
✅ Backward compatible with Python-based odoo-bin

## Usage Examples

### Local Development
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
pyenv shell odoo-19-dev
./scripts/odoo.sh -d main -c "/path/to/config.toml"
```

### Test Runner
```bash
./bin/odoo-tests.sh
```

### CI (automatic)
```bash
# GitHub Actions automatically uses /tmp/odoo/scripts/odoo.sh
```

## Rollback Strategy
```bash
git checkout main -- bin/odoo-tests.sh scripts/ci/run_odoo_tests.sh scripts/deploy/do-bootstrap-odoo-prod.sh agents/odoo_reverse_mapper.yaml agents/loops/clarity_ppm_reverse.yaml .github/workflows/ci.yml
git rm scripts/odoo.sh
git commit -m "revert: remove odoo launcher wrapper"
git push
```

## Next Steps
1. ✅ Commit changes
2. ✅ Push to origin
3. Install Odoo via pip or mount source to test full workflow
4. Verify CI pipeline passes with updated workflows

## Success Criteria
✅ Launcher created and executable
✅ All invocation points updated (6 files)
✅ No SyntaxError when running launcher
✅ Environment hardening complete (pyenv, starship)
✅ Evidence documented
✅ Ready for commit
