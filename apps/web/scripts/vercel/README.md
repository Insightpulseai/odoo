# Vercel API Scripts

CLI-free Vercel project management and deployment log retrieval using REST API.

## Prerequisites

**Required Environment Variable:**
```bash
export VERCEL_TOKEN="your_vercel_personal_access_token"
```

**Get and Provision Token:**

1. **Create Token** (manual, one-time):
   - Go to https://vercel.com/account/tokens
   - Click "Create Token"
   - Name: "CLI/API Access"
   - Scope: Full Account
   - Copy token value

2. **Provision Token** (automated):
   ```bash
   # Set in current shell
   export VERCEL_TOKEN="vercel_xxx..."

   # Persist to env file + GitHub Actions
   ./scripts/vercel/provision_token.sh
   ```

   This script:
   - Persists to `.env.platform.local`
   - Sets GitHub Actions secret `VERCEL_TOKEN`
   - Validates successful provisioning

**Project Details:**
- Team ID: `team_wphKJ7lHA3QiZu6VgcotQBQM`
- Project ID: `prj_PFdFRARO9YQ0CRBkuwp5jAbfKYwe`
- Project Name: `web`

---

## Scripts

### 1. `fix_root_directory.sh`

**Purpose**: Set Vercel project `rootDirectory` to fix monorepo build issues.

**Usage:**
```bash
# Set rootDirectory to apps/web (fixes pnpm workspace detection)
TEAM_ID=team_wphKJ7lHA3QiZu6VgcotQBQM \
PROJECT_ID=prj_PFdFRARO9YQ0CRBkuwp5jAbfKYwe \
ROOT_DIR=apps/web \
./scripts/vercel/fix_root_directory.sh
```

**What It Does:**
1. PATCH `/v9/projects/{projectId}` with `{"rootDirectory":"apps/web"}`
2. GET project to confirm setting
3. Display project name and rootDirectory

**Why This Matters:**
- Vercel auto-detects framework from repository root by default
- In monorepos, this causes wrong directory for `pnpm install`
- Setting `rootDirectory` tells Vercel: "build context is `apps/web`"
- Fixes: "No Next.js version detected", pnpm workspace issues

**Rollback:**
```bash
# Reset to repository root
ROOT_DIR=. ./scripts/vercel/fix_root_directory.sh
```

---

### 2. `latest_deploy_logs.sh`

**Purpose**: Fetch build logs for failed deployments without Vercel CLI.

**Usage:**
```bash
TEAM_ID=team_wphKJ7lHA3QiZu6VgcotQBQM \
PROJECT_ID=prj_PFdFRARO9YQ0CRBkuwp5jAbfKYwe \
./scripts/vercel/latest_deploy_logs.sh
```

**What It Does:**
1. List recent deployments via `/v13/deployments`
2. Get deployment details for newest deployment
3. Extract build ID from deployment
4. Fetch build events via `/v3/deployments/{id}/events`
5. Display stderr/fatal/exit events (build errors)

**Output Files:**
- `/tmp/vercel_deployments.json` - List of recent deployments
- `/tmp/vercel_deployment.json` - Latest deployment details
- `/tmp/vercel_events.json` - Build events (logs)

**Example Output:**
```
[1/4] List recent deployments
[2/4] Deployment id: dpl_xxx
[3/4] Get deployment details (to discover build id)
[4/4] Fetch deployment events (build logs). Build id: bld_xxx
--- stderr ---
ERR_PNPM_OUTDATED_LOCKFILE Cannot install with frozen-lockfile
--- exit ---
Command "pnpm install --frozen-lockfile" exited with 1
```

---

## Common Workflows

### Fix Monorepo Build Issues
```bash
# 1. Set rootDirectory
./scripts/vercel/fix_root_directory.sh

# 2. Trigger new deployment
git commit --allow-empty -m "chore: trigger vercel deploy"
git push origin main

# 3. Wait 60 seconds for build
sleep 60

# 4. Check logs
./scripts/vercel/latest_deploy_logs.sh
```

### Debug Failed Deployment
```bash
# Get logs
./scripts/vercel/latest_deploy_logs.sh

# View full event stream
cat /tmp/vercel_events.json | jq '.[] | select(.type | IN("stderr","fatal","exit"))'

# Check deployment state
cat /tmp/vercel_deployment.json | jq '{state, readyState, error}'
```

### Verify Production
```bash
# After successful deployment
curl -sS https://insightpulseai.com/api/auth/health | jq '.'
```

---

## API References

- [Update Project](https://vercel.com/docs/rest-api/reference/endpoints/projects/update-an-existing-project) - PATCH rootDirectory
- [List Deployments](https://vercel.com/docs/rest-api/endpoints/deployments#get-a-list-of-deployments) - Get recent deploys
- [Get Deployment](https://vercel.com/docs/rest-api/endpoints/deployments#get-a-deployment-by-id-or-url) - Deployment details
- [Deployment Events](https://vercel.com/docs/rest-api/endpoints/deployments#get-deployment-events) - Build logs

---

## Troubleshooting

**Error: 403 Forbidden**
- **Cause**: Missing or invalid VERCEL_TOKEN
- **Fix**: Generate new token at https://vercel.com/account/tokens

**Error: Project not found**
- **Cause**: Wrong TEAM_ID or PROJECT_ID
- **Fix**: Verify IDs in `.vercel/project.json` or Vercel dashboard URL

**Error: Deployment not ready**
- **Cause**: Deployment still building or just failed
- **Fix**: Wait 30-60 seconds, retry `latest_deploy_logs.sh`

**No build logs in events**
- **Cause**: Build failed before logging started
- **Fix**: Check deployment state in `/tmp/vercel_deployment.json`

---

## Current State (as of 2026-02-10)

**Issue**: Deployments failing with lockfile drift error
**Fix Applied**: Lockfile regenerated and pushed (commit `983c76f8`)
**Remaining**: Need to set `rootDirectory: apps/web` via API
**Blocker**: VERCEL_TOKEN is placeholder value

**Next Steps:**
1. Set valid VERCEL_TOKEN in environment
2. Run `fix_root_directory.sh` to set rootDirectory
3. Wait for auto-deploy or trigger manual deploy
4. Run `latest_deploy_logs.sh` to verify success
5. Verify production: `curl https://insightpulseai.com/api/auth/health`
