#!/bin/bash
set -euo pipefail

# Finance PPM Git Worktree Setup Script
# Automates creation of parallel deployment testing worktrees

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_BASE="$(dirname "$REPO_ROOT")"

echo "=== Finance PPM: Git Worktree Setup ==="
echo "Repository: $REPO_ROOT"
echo "Worktree Base: $WORKTREE_BASE"
echo ""

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ Error: Not a git repository"
  exit 1
fi

# Function to create worktree
create_worktree() {
  local name=$1
  local branch=$2
  local path="$WORKTREE_BASE/$name"

  echo ">>> Creating worktree: $name (branch: $branch)"

  # Check if worktree already exists
  if [ -d "$path" ]; then
    echo "⚠️  Worktree already exists: $path"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      git worktree remove --force "$path" 2>/dev/null || true
    else
      echo "⏭️  Skipping $name"
      return 0
    fi
  fi

  # Check if branch exists
  if git show-ref --verify --quiet refs/heads/"$branch"; then
    echo "ℹ️  Branch $branch already exists, checking out existing branch"
    git worktree add "$path" "$branch"
  else
    echo "ℹ️  Creating new branch: $branch"
    git worktree add "$path" -b "$branch"
  fi

  if [ $? -eq 0 ]; then
    echo "✅ Worktree created: $path"
  else
    echo "❌ Failed to create worktree: $name"
    return 1
  fi
}

# Create deployment worktree
create_worktree "odoo-ce-deploy" "feature/deployment"

# Create staging worktree
create_worktree "odoo-ce-staging" "feature/staging"

# Create CI/CD testing worktree
create_worktree "odoo-ce-cicd" "feature/cicd-test"

# Create verification worktree
create_worktree "odoo-ce-verify" "feature/verification"

# List all worktrees
echo ""
echo "=== Worktree Setup Complete ==="
git worktree list

# Create README in each worktree
echo ""
echo ">>> Creating worktree documentation..."

# Deployment worktree README
cat > "$WORKTREE_BASE/odoo-ce-deploy/README_WORKTREE.md" << 'EOF'
# Deployment Testing Worktree

**Purpose**: Test CI/CD deployment scripts before production rollout

**Branch**: feature/deployment

**Scope**:
- Test OCA module installation
- Test IPAI module activation
- Test n8n workflow import
- Test deployment verification

**Usage**:
```bash
# Test OCA installation
ssh root@159.223.75.148 'bash -s' < scripts/ci/install-oca-modules.sh

# Test IPAI deployment
ssh root@159.223.75.148 "ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD bash -s" < scripts/ci/deploy-ipai-modules.sh

# Test n8n import
ssh root@159.223.75.148 "N8N_API_KEY=$N8N_API_KEY bash -s" < scripts/ci/import-n8n-workflows.sh
```

**Merge Policy**: Only merge after all deployment tests pass
EOF

# Staging worktree README
cat > "$WORKTREE_BASE/odoo-ce-staging/README_WORKTREE.md" << 'EOF'
# Staging Testing Worktree

**Purpose**: Pre-production validation of Finance PPM modules

**Branch**: feature/staging

**Scope**:
- Test module upgrades
- Validate data migrations
- Test A1 workstream configuration
- Validate BIR schedule automation

**Usage**:
```bash
# Test module upgrade
docker exec odoo-accounting odoo-bin -d odoo_accounting -u ipai_finance_ppm --stop-after-init

# Validate logframe data
docker exec odoo-accounting odoo-bin shell -d odoo_accounting
>>> env['ipai.finance.logframe'].search([]).mapped('name')

# Test BIR schedule sync
docker exec odoo-accounting odoo-bin shell -d odoo_accounting
>>> env['ipai.finance.bir_schedule']._cron_sync_bir_tasks()
```

**Merge Policy**: Merge after UAT validation from Finance Supervisor
EOF

# CI/CD worktree README
cat > "$WORKTREE_BASE/odoo-ce-cicd/README_WORKTREE.md" << 'EOF'
# CI/CD Testing Worktree

**Purpose**: Test GitHub Actions workflow changes in isolation

**Branch**: feature/cicd-test

**Scope**:
- GitHub Actions workflow development
- CI/CD pipeline testing
- GitHub secrets validation
- Automated deployment testing

**Usage**:
```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Test workflow locally
act workflow_dispatch -s DROPLET_SSH_KEY="$(cat ~/.ssh/finance_ppm_deploy)"

# Test specific job
act -j deploy-oca

# Debug workflow
act workflow_dispatch --verbose
```

**Merge Policy**: Only merge after successful local act testing
EOF

# Verification worktree README
cat > "$WORKTREE_BASE/odoo-ce-verify/README_WORKTREE.md" << 'EOF'
# Verification Testing Worktree

**Purpose**: Run deployment verification checks in parallel

**Branch**: feature/verification

**Scope**:
- Odoo UI accessibility checks
- Module installation verification
- n8n workflow validation
- Supabase schema validation
- Mattermost notification testing

**Usage**:
```bash
# Run full verification
ssh root@159.223.75.148 \
  "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY MATTERMOST_WEBHOOK_URL=$MATTERMOST_WEBHOOK_URL bash -s" \
  < scripts/ci/verify-deployment.sh

# Run individual checks
# Check 1: Odoo UI
curl -sf http://159.223.75.148:8071/web/login

# Check 2: Modules
ssh root@159.223.75.148 'docker exec odoo-accounting odoo-bin shell -d odoo_accounting'

# Check 3: n8n workflows
curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://ipa.insightpulseai.com/api/v1/workflows" | jq '.data | length'
```

**Merge Policy**: Merge after all 5 verification checks pass
EOF

echo "✅ Worktree documentation created"

# Create worktree management helper scripts
echo ""
echo ">>> Creating worktree management scripts..."

# Cleanup script
cat > "$REPO_ROOT/scripts/worktree-cleanup.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

# Finance PPM Git Worktree Cleanup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_BASE="$(dirname "$REPO_ROOT")"

echo "=== Finance PPM: Git Worktree Cleanup ==="

cd "$REPO_ROOT"

# List worktrees
echo "Current worktrees:"
git worktree list
echo ""

# Confirm cleanup
read -p "Remove all worktrees except main? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cleanup cancelled"
  exit 0
fi

# Remove each worktree
for worktree in odoo-ce-deploy odoo-ce-staging odoo-ce-cicd odoo-ce-verify; do
  path="$WORKTREE_BASE/$worktree"
  if [ -d "$path" ]; then
    echo ">>> Removing worktree: $worktree"
    git worktree remove --force "$path" 2>/dev/null || true
    echo "✅ Removed: $path"
  else
    echo "⏭️  Worktree not found: $worktree"
  fi
done

# Prune worktree metadata
echo ""
echo ">>> Pruning worktree metadata..."
git worktree prune

# List remaining worktrees
echo ""
echo "=== Cleanup Complete ==="
git worktree list
EOF

chmod +x "$REPO_ROOT/scripts/worktree-cleanup.sh"

# Parallel testing script
cat > "$REPO_ROOT/scripts/worktree-parallel-test.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

# Finance PPM Parallel Deployment Testing Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_BASE="$(dirname "$REPO_ROOT")"

echo "=== Finance PPM: Parallel Deployment Testing ==="

# Export secrets (required for deployment scripts)
if [ -z "${ODOO_ADMIN_PASSWORD:-}" ]; then
  echo "❌ Error: ODOO_ADMIN_PASSWORD not set"
  exit 1
fi

if [ -z "${N8N_API_KEY:-}" ]; then
  echo "❌ Error: N8N_API_KEY not set"
  exit 1
fi

if [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "❌ Error: SUPABASE_SERVICE_ROLE_KEY not set"
  exit 1
fi

if [ -z "${MATTERMOST_WEBHOOK_URL:-}" ]; then
  echo "❌ Error: MATTERMOST_WEBHOOK_URL not set"
  exit 1
fi

# Function to run deployment phase
run_phase() {
  local phase=$1
  local worktree=$2
  local script=$3

  echo ">>> Starting phase: $phase (worktree: $worktree)"

  cd "$WORKTREE_BASE/$worktree"

  # Run deployment script
  ssh root@159.223.75.148 'bash -s' < "$script" 2>&1 | tee "deployment-$phase.log"

  if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Phase complete: $phase"
    return 0
  else
    echo "❌ Phase failed: $phase"
    return 1
  fi
}

# Create results directory
mkdir -p "$REPO_ROOT/deployment-results"
RESULTS_DIR="$REPO_ROOT/deployment-results"

# Phase 1: OCA Installation (Deployment Worktree)
echo ""
echo "=== Phase 1: OCA Module Installation ==="
run_phase "oca-install" "odoo-ce-deploy" "scripts/ci/install-oca-modules.sh" &
PID_OCA=$!

# Wait for OCA installation to complete before starting IPAI
wait $PID_OCA
if [ $? -ne 0 ]; then
  echo "❌ OCA installation failed, aborting deployment"
  exit 1
fi

# Phase 2: IPAI Deployment (Staging Worktree)
echo ""
echo "=== Phase 2: IPAI Module Deployment ==="
cd "$WORKTREE_BASE/odoo-ce-staging"
ssh root@159.223.75.148 \
  "ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD bash -s" \
  < scripts/ci/deploy-ipai-modules.sh 2>&1 | tee "$RESULTS_DIR/deployment-ipai.log" &
PID_IPAI=$!

# Phase 3: n8n Import (Parallel with IPAI)
echo ""
echo "=== Phase 3: n8n Workflow Import ==="
cd "$WORKTREE_BASE/odoo-ce-deploy"
ssh root@159.223.75.148 \
  "N8N_API_KEY=$N8N_API_KEY bash -s" \
  < scripts/ci/import-n8n-workflows.sh 2>&1 | tee "$RESULTS_DIR/deployment-n8n.log" &
PID_N8N=$!

# Wait for IPAI and n8n to complete
wait $PID_IPAI
IPAI_RESULT=$?

wait $PID_N8N
N8N_RESULT=$?

if [ $IPAI_RESULT -ne 0 ] || [ $N8N_RESULT -ne 0 ]; then
  echo "❌ Deployment failed (IPAI: $IPAI_RESULT, n8n: $N8N_RESULT)"
  exit 1
fi

# Phase 4: Verification (Verification Worktree)
echo ""
echo "=== Phase 4: Deployment Verification ==="
cd "$WORKTREE_BASE/odoo-ce-verify"
ssh root@159.223.75.148 \
  "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY MATTERMOST_WEBHOOK_URL=$MATTERMOST_WEBHOOK_URL bash -s" \
  < scripts/ci/verify-deployment.sh 2>&1 | tee "$RESULTS_DIR/deployment-verify.log"

if [ $? -eq 0 ]; then
  echo ""
  echo "=== Parallel Deployment Testing Complete ==="
  echo "✅ ALL PHASES PASSED"
  echo ""
  echo "Results:"
  echo "  - OCA Installation: ✅ PASSED"
  echo "  - IPAI Deployment: ✅ PASSED"
  echo "  - n8n Import: ✅ PASSED"
  echo "  - Verification: ✅ PASSED"
  echo ""
  echo "Logs saved to: $RESULTS_DIR"
  exit 0
else
  echo ""
  echo "=== Parallel Deployment Testing Failed ==="
  echo "❌ VERIFICATION FAILED"
  echo ""
  echo "Check logs in: $RESULTS_DIR"
  exit 1
fi
EOF

chmod +x "$REPO_ROOT/scripts/worktree-parallel-test.sh"

echo "✅ Worktree management scripts created"

# Final instructions
echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Navigate to worktrees:"
echo "   cd $WORKTREE_BASE/odoo-ce-deploy"
echo "   cd $WORKTREE_BASE/odoo-ce-staging"
echo "   cd $WORKTREE_BASE/odoo-ce-cicd"
echo "   cd $WORKTREE_BASE/odoo-ce-verify"
echo ""
echo "2. Export deployment secrets:"
echo "   export ODOO_ADMIN_PASSWORD='your_password'"
echo "   export N8N_API_KEY='your_api_key'"
echo "   export SUPABASE_SERVICE_ROLE_KEY='your_service_role_key'"
echo "   export MATTERMOST_WEBHOOK_URL='your_webhook_url'"
echo ""
echo "3. Run parallel deployment testing:"
echo "   ./scripts/worktree-parallel-test.sh"
echo ""
echo "4. Cleanup worktrees when done:"
echo "   ./scripts/worktree-cleanup.sh"
echo ""
echo "Documentation:"
echo "  - GitHub Secrets: docs/GITHUB_SECRETS_SETUP.md"
echo "  - Git Worktrees: docs/GIT_WORKTREE_STRATEGY.md"
echo "  - Worktree READMEs: */README_WORKTREE.md"
