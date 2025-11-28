# CI/CD Troubleshooting Guide - GitHub Actions Database Connection

## 🚨 Current Issue
The GitHub Actions tests are failing on the `feature/add-expense-equipment-prd` branch with "fe_sendauth: no password supplied" error, even though PR #22 (Fix CI DB password handling) has been merged.

## 🔍 Root Cause Analysis

### 1. Which Workflow is Failing?
The failing workflow is likely **`ci-odoo-oca.yml`** because:
- It runs actual database tests with PostgreSQL service
- It has the PostgreSQL service configured with password `odoo`
- It's triggered on `push` and `pull_request` events

### 2. Why is it Still Failing?
Even though the fix was merged, the **feature branch environment** might have:
- **Cached workflow runs** using old configuration
- **Secrets not propagating** to the feature branch context
- **Transient service issues** with PostgreSQL container

## 🛠️ Immediate Solutions

### Solution 1: Manual Workflow Trigger (Recommended)
```bash
# Go to GitHub Actions in your repository:
# 1. Navigate to: https://github.com/jgtolentino/odoo-ce/actions
# 2. Select "Odoo 18 CE / OCA CI" workflow
# 3. Click "Run workflow"
# 4. Select branch: "feature/add-expense-equipment-prd"
# 5. Click "Run workflow"
```

### Solution 2: Check Workflow Configuration
The current workflow configuration in `.github/workflows/ci-odoo-oca.yml`:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo  # ✅ This is correct
      POSTGRES_DB: odoo
```

### Solution 3: Verify GitHub Secrets
Ensure these secrets are set in your repository:
- **Repository Settings → Secrets and variables → Actions**
- Required secrets for this workflow:
  - `N8N_CI_WEBHOOK_URL` (optional, for telemetry)

## 🔧 Technical Verification

### 1. Check Current Workflow Status
```bash
# View recent workflow runs
# Go to: https://github.com/jgtolentino/odoo-ce/actions

# Look for:
# - ✅ Green checkmarks = Success
# - ❌ Red X = Failure
# - ⏳ Yellow dot = In Progress
```

### 2. Verify PostgreSQL Service Configuration
The workflow uses GitHub Actions services:
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo  # This should work
    ports: ["5432:5432"]
```

### 3. Check Environment Variables
The workflow sets:
```yaml
env:
  PGHOST: localhost
  PGPORT: 5432
  PGUSER: odoo
  PGPASSWORD: odoo  # ✅ Matches service configuration
  PGDATABASE: odoo
```

## 🚀 Path to Green Status

### Step 1: Manual Trigger (Immediate)
1. Go to GitHub Actions
2. Select "Odoo 18 CE / OCA CI"
3. Run workflow on `feature/add-expense-equipment-prd`
4. Monitor the run

### Step 2: Check Run Details
If it still fails:
1. Click on the failed run
2. Expand the failing job (likely "tests")
3. Check the error logs
4. Look for "fe_sendauth: no password supplied"

### Step 3: Alternative Solutions
If manual trigger doesn't work:

**Option A: Push Empty Commit**
```bash
git checkout feature/add-expense-equipment-prd
git commit --allow-empty -m "Trigger CI with fixed DB password"
git push origin feature/add-expense-equipment-prd
```

**Option B: Create New PR**
```bash
git checkout -b feature/add-expense-equipment-prd-fixed
git push origin feature/add-expense-equipment-prd-fixed
# Create PR from new branch
```

## 📋 Verification Checklist

### Before Manual Trigger
- [ ] PostgreSQL password in workflow: `odoo`
- [ ] Environment variables match service configuration
- [ ] No syntax errors in workflow file
- [ ] Feature branch is up to date with main

### After Manual Trigger
- [ ] Workflow starts successfully
- [ ] PostgreSQL service initializes
- [ ] Tests run without database connection errors
- [ ] All jobs complete with green status

### Final Verification
- [ ] All tests pass (Unit, Integration, All Tests)
- [ ] Performance tests complete
- [ ] Repository structure check passes
- [ ] Coverage report generated (if applicable)

## 🔍 Common Failure Patterns

### Pattern 1: Service Not Ready
**Symptoms**: PostgreSQL connection timeout
**Solution**: Increase health check intervals in workflow

### Pattern 2: Password Mismatch
**Symptoms**: "fe_sendauth: no password supplied"
**Solution**: Ensure `PGPASSWORD` matches `POSTGRES_PASSWORD`

### Pattern 3: Port Conflict
**Symptoms**: "port 5432 already in use"
**Solution**: GitHub Actions manages ports automatically

### Pattern 4: Module Installation Issues
**Symptoms**: Module not found during installation
**Solution**: Check `addons/` directory structure

## 🛡️ Prevention for Future

### 1. Workflow Best Practices
```yaml
# Always include health checks
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    options: >-
      --health-cmd="pg_isready -U odoo"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=5
```

### 2. Environment Consistency
- Use same PostgreSQL version (15) across all environments
- Maintain consistent password (`odoo`) for CI
- Document all environment variables

### 3. Monitoring
- Set up GitHub Actions status badges
- Configure notifications for failed runs
- Regular review of test coverage

## 📞 Support Resources

### Documentation
- `POSTGRES_PASSWORD_SOLUTION.md` - Database connectivity solutions
- `INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md` - Complete configuration reference

### Tools
- `scripts/erp_config_cli.sh` - Local database testing
- GitHub Actions logs - Detailed error information

### Verification Commands
```bash
# Local database test (mimics CI)
docker run --rm -d --name test-postgres \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=odoo \
  -p 5432:5432 postgres:15

# Test connection
PGPASSWORD=odoo psql -h localhost -U odoo -d odoo -c 'SELECT version();'
```

## ✅ Expected Outcome

After following these steps, the GitHub Actions workflow should:
1. ✅ Start successfully with manual trigger
2. ✅ Initialize PostgreSQL service with password `odoo`
3. ✅ Run all tests without database connection errors
4. ✅ Complete all jobs with green status
5. ✅ Be ready for final PR merge to `main`

The feature branch will then be ready for the final release PR to `main` with all tests passing.
