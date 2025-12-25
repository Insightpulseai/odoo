# Git Worktree Strategy for Parallel Deployment

## Overview

Git worktrees allow multiple working directories from a single repository, enabling parallel development and testing without switching branches or stashing changes.

## Use Cases for Finance PPM Deployment

### 1. Parallel Testing Environments
Test different deployment phases simultaneously without branch switching.

### 2. Rollback Capability
Keep production version accessible while testing new deployment scripts.

### 3. Concurrent Debugging
Debug deployment issues in one worktree while continuing development in another.

### 4. CI/CD Development
Test GitHub Actions workflow changes without affecting main development.

## Worktree Structure

```
odoo-ce/                          # Main worktree (development)
├─ .github/workflows/
├─ addons/
├─ scripts/
└─ ...

../odoo-ce-deploy/                # Deployment worktree
├─ .github/workflows/
├─ scripts/ci/                    # CI deployment scripts
└─ ...

../odoo-ce-staging/               # Staging worktree
├─ addons/                        # Test module changes
└─ ...

../odoo-ce-hotfix/                # Hotfix worktree
└─ scripts/                       # Emergency fixes
```

## Setup Commands

### Create Deployment Worktree

```bash
# Navigate to main repository
cd /Users/tbwa/Documents/GitHub/odoo-ce

# Create deployment worktree from main branch
git worktree add ../odoo-ce-deploy main

# Create feature branch for CI/CD work
git worktree add ../odoo-ce-ci-pipeline feature/ci-pipeline

# Create staging worktree for testing
git worktree add ../odoo-ce-staging staging
```

### Verify Worktrees

```bash
# List all worktrees
git worktree list

# Expected output:
# /Users/tbwa/Documents/GitHub/odoo-ce              main
# /Users/tbwa/Documents/GitHub/odoo-ce-deploy       main
# /Users/tbwa/Documents/GitHub/odoo-ce-ci-pipeline  feature/ci-pipeline
# /Users/tbwa/Documents/GitHub/odoo-ce-staging      staging
```

## Parallel Deployment Testing Workflow

### Phase 1: OCA Module Installation Testing

**Worktree 1** (main): Continue development
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce
git checkout main
# Continue normal development
```

**Worktree 2** (deployment): Test OCA installation
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
git checkout feature/oca-deployment

# Test OCA installation script locally
ssh root@159.223.75.148 'bash -s' < scripts/ci/install-oca-modules.sh

# Monitor logs
ssh root@159.223.75.148 'docker logs -f odoo-accounting'
```

**Worktree 3** (verification): Run verification checks
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-staging
git checkout feature/verification

# Test verification script
ssh root@159.223.75.148 'bash -s' < scripts/ci/verify-deployment.sh
```

### Phase 2: IPAI Module Deployment Testing

**Worktree 1** (main): Module development
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce
# Edit addons/ipai_finance_ppm/models/finance_ppm.py
```

**Worktree 2** (deployment): Test XML-RPC activation
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
# Test IPAI deployment script
ssh root@159.223.75.148 \
  "ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD bash -s" < scripts/ci/deploy-ipai-modules.sh
```

**Worktree 3** (verification): Validate module state
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-staging
# Check module installation status
ssh root@159.223.75.148 'docker exec odoo-accounting odoo-bin shell -d odoo_accounting'
```

### Phase 3: n8n Workflow Import Testing

**Worktree 1** (main): Workflow development
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce
# Edit workflows/finance_ppm/bir_deadline_alert.json
```

**Worktree 2** (deployment): Test workflow import
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
# Test n8n import script
ssh root@159.223.75.148 \
  "N8N_API_KEY=$N8N_API_KEY bash -s" < scripts/ci/import-n8n-workflows.sh
```

**Worktree 3** (verification): Verify workflow activation
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce-staging
# Query n8n API for active workflows
curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://ipa.insightpulseai.net/api/v1/workflows" | jq '.data | length'
```

## Advanced Worktree Patterns

### Rollback Strategy

Keep production version in separate worktree:
```bash
# Create production worktree
git worktree add ../odoo-ce-production production

# Tag production version
cd /Users/tbwa/Documents/GitHub/odoo-ce-production
git tag -a v1.0.0-production -m "Production release before Finance PPM deployment"

# If deployment fails, rollback:
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
git checkout production
ssh root@159.223.75.148 'bash -s' < scripts/ci/rollback-deployment.sh
```

### CI/CD Development Isolation

Test GitHub Actions changes without affecting main:
```bash
# Create CI/CD worktree
git worktree add ../odoo-ce-cicd feature/github-actions

cd /Users/tbwa/Documents/GitHub/odoo-ce-cicd

# Edit GitHub Actions workflow
vim .github/workflows/deploy-finance-ppm.yml

# Push to test branch (triggers workflow)
git add .github/workflows/deploy-finance-ppm.yml
git commit -m "test: validate deployment pipeline"
git push origin feature/github-actions

# Monitor workflow: https://github.com/[YOUR_ORG]/odoo-ce/actions
```

### Concurrent Debugging

Debug deployment issues while main development continues:
```bash
# Main worktree: Continue development
cd /Users/tbwa/Documents/GitHub/odoo-ce
git checkout main
# Normal development work

# Debug worktree: Investigate deployment failure
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
git checkout feature/debug-deployment

# Add debugging output to scripts
vim scripts/ci/deploy-ipai-modules.sh
# Add: set -x  # Enable bash debugging

# Test with verbose output
ssh root@159.223.75.148 'bash -xs' < scripts/ci/deploy-ipai-modules.sh 2>&1 | tee deployment-debug.log
```

## Performance Optimization

### Share Build Artifacts

All worktrees share the same `.git` directory, reducing disk usage:
```bash
# Check disk usage
du -sh /Users/tbwa/Documents/GitHub/odoo-ce/.git
du -sh /Users/tbwa/Documents/GitHub/odoo-ce-deploy/.git

# Only .git/worktrees/ is duplicated (minimal)
```

### Parallel Operations

Run deployment phases in parallel across worktrees:
```bash
# Terminal 1: Install OCA modules
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
ssh root@159.223.75.148 'bash -s' < scripts/ci/install-oca-modules.sh &

# Terminal 2: Prepare n8n workflows
cd /Users/tbwa/Documents/GitHub/odoo-ce-staging
ssh root@159.223.75.148 'mkdir -p /root/odoo-ce/workflows/finance_ppm'
scp workflows/finance_ppm/*.json root@159.223.75.148:/root/odoo-ce/workflows/finance_ppm/ &

# Terminal 3: Monitor verification
cd /Users/tbwa/Documents/GitHub/odoo-ce-verify
watch -n 5 'ssh root@159.223.75.148 "docker ps && docker logs --tail 20 odoo-accounting"'

# Wait for all background jobs
wait
```

## Cleanup

### Remove Worktree

```bash
# List worktrees
git worktree list

# Remove specific worktree
git worktree remove ../odoo-ce-deploy

# Or force remove (with uncommitted changes)
git worktree remove --force ../odoo-ce-deploy

# Prune stale worktree references
git worktree prune
```

### Complete Cleanup

```bash
# Remove all worktrees except main
cd /Users/tbwa/Documents/GitHub/odoo-ce

for worktree in $(git worktree list --porcelain | grep worktree | awk '{print $2}' | grep -v "$(pwd)"); do
  git worktree remove --force "$worktree"
done

# Prune worktree metadata
git worktree prune

# Clean up branches
git branch -D feature/ci-pipeline
git branch -D feature/oca-deployment
git branch -D feature/verification
```

## Best Practices

### 1. Naming Conventions
Use descriptive worktree directory names:
```bash
# Good
../odoo-ce-deploy
../odoo-ce-staging
../odoo-ce-production

# Bad
../temp
../test
../new
```

### 2. Branch Management
Create dedicated branches for each worktree:
```bash
git worktree add ../odoo-ce-deploy -b feature/deployment
git worktree add ../odoo-ce-staging -b feature/staging
```

### 3. Isolation
Keep worktrees isolated for specific purposes:
- **Main**: Active development
- **Deploy**: Deployment testing only
- **Staging**: Pre-production validation
- **Hotfix**: Emergency fixes

### 4. Documentation
Document worktree purpose in README:
```bash
cd ../odoo-ce-deploy
echo "# Deployment Testing Worktree" > README_WORKTREE.md
echo "Purpose: Test CI/CD deployment scripts" >> README_WORKTREE.md
echo "Branch: feature/deployment" >> README_WORKTREE.md
```

### 5. Automation
Create helper scripts for worktree management:
```bash
# Create script: scripts/worktree-setup.sh
#!/bin/bash
set -euo pipefail

echo "Setting up Finance PPM deployment worktrees..."

git worktree add ../odoo-ce-deploy -b feature/deployment
git worktree add ../odoo-ce-staging -b feature/staging
git worktree add ../odoo-ce-production production

echo "✅ Worktrees created successfully"
git worktree list
```

## Integration with CI/CD Pipeline

### Test Workflow in Isolated Worktree

```bash
# Create CI/CD testing worktree
git worktree add ../odoo-ce-cicd feature/cicd-test

cd ../odoo-ce-cicd

# Edit workflow
vim .github/workflows/deploy-finance-ppm.yml

# Test locally with act (GitHub Actions local runner)
brew install act  # macOS
act workflow_dispatch -s DROPLET_SSH_KEY="$(cat ~/.ssh/finance_ppm_deploy)"

# If tests pass, merge to main
git push origin feature/cicd-test
# Create PR and merge
```

### Parallel Deployment Testing

```bash
# Terminal 1: Main development
cd /Users/tbwa/Documents/GitHub/odoo-ce
git checkout main
# Continue development

# Terminal 2: Deploy OCA modules
cd /Users/tbwa/Documents/GitHub/odoo-ce-deploy
git checkout feature/oca-deployment
./scripts/ci/install-oca-modules.sh

# Terminal 3: Deploy IPAI modules
cd /Users/tbwa/Documents/GitHub/odoo-ce-staging
git checkout feature/ipai-deployment
./scripts/ci/deploy-ipai-modules.sh

# Terminal 4: Verify deployment
cd /Users/tbwa/Documents/GitHub/odoo-ce-verify
git checkout feature/verification
./scripts/ci/verify-deployment.sh
```

## Troubleshooting

### Worktree Lock Issues

**Symptom**: `fatal: 'path' is already locked`

**Solution**:
```bash
# Remove lock file
rm .git/worktrees/<worktree-name>/locked

# Or force remove worktree
git worktree remove --force ../odoo-ce-deploy
```

### Branch Conflicts

**Symptom**: `fatal: 'branch' is already checked out`

**Solution**:
```bash
# Use detached HEAD
git worktree add ../odoo-ce-deploy --detach

# Or create new branch
git worktree add ../odoo-ce-deploy -b feature/deployment-new
```

### Disk Space Issues

**Symptom**: `No space left on device`

**Solution**:
```bash
# Remove unused worktrees
git worktree list
git worktree remove ../odoo-ce-old-deploy

# Clean up branches
git branch -D old-feature-branch
```

## Next Steps

After setting up git worktrees:

1. Create deployment worktree: `git worktree add ../odoo-ce-deploy feature/deployment`
2. Test OCA installation in deployment worktree
3. Verify IPAI activation in staging worktree
4. Run parallel verification across all worktrees
5. Merge successful changes back to main
