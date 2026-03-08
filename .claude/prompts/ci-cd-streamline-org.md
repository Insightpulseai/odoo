# CI/CD Streamline — Org-Wide Green Build + Unified Image Update

## Objective

Make ALL CI/CD workflows green across the entire InsightPulseAI GitHub organization (9 active repos, 358+ workflows in `odoo` alone). Streamline, deduplicate, fix failures, update the unified Docker image with all accumulated changes, and push.

## Context

### Organization repos (active)
- `Insightpulseai/odoo` — PRIMARY (358 workflows, 73 ipai_* modules, 84 Edge Functions)
- `Insightpulseai/agents` — AI agent framework, MCP servers
- `Insightpulseai/.github` — Org-wide reusable workflows, templates
- `Insightpulseai/ops-platform` — Supabase control plane
- `Insightpulseai/lakehouse` — Databricks medallion pipelines
- `Insightpulseai/web` — Product web surfaces
- `Insightpulseai/infra` — IaC (Azure, DO, Cloudflare, Terraform)
- `Insightpulseai/design-system` — Design tokens, components
- `Insightpulseai/templates` — Repo/starter templates

### Stack
- Odoo CE 19.0 + OCA + PostgreSQL 16
- Node >= 18.0.0 (pnpm workspaces, Turborepo)
- Python 3.12+
- Docker (unified image: `ghcr.io/insightpulseai/ipai-odoo-runtime`)
- Supabase (`spdtwktxdalcfigzeqrz`) — Edge Functions, Vault, Auth
- GitHub Actions (358+ workflows, target: self-hosted runner on DO)

### Key files
- `docker/Dockerfile.unified` — canonical production image
- `.github/workflows/` — 358 workflow files
- `addons/ipai/` — 73 custom modules
- `addons/oca/` — OCA submodules (currently `.gitkeep` only)
- `docs/org/` — NEW governance docs (ORG_TARGET_STATE, ROADMAP, INVENTORY)
- `marketplace/` — NEW Microsoft Marketplace control plane
- `scripts/repo_health.sh` — repo structure validator
- `scripts/spec_validate.sh` — spec bundle validator
- `scripts/ci_local.sh` — local CI runner

---

## Execution Plan

### Phase 1: Audit — Understand current CI/CD state

```bash
# 1.1 Get all workflow run statuses across the org
gh api orgs/Insightpulseai/repos --paginate --jq '.[].name' | while read repo; do
  echo "=== $repo ==="
  gh run list --repo "Insightpulseai/$repo" --limit 5 --json name,status,conclusion,headBranch \
    --jq '.[] | "\(.conclusion)\t\(.name)\t\(.headBranch)"' 2>/dev/null || echo "  (no runs)"
done

# 1.2 List all workflows in odoo repo with their status
gh workflow list --repo Insightpulseai/odoo --all --json name,state \
  --jq '.[] | "\(.state)\t\(.name)"' | sort

# 1.3 Find disabled workflows
gh workflow list --repo Insightpulseai/odoo --all --json name,state \
  --jq '.[] | select(.state == "disabled_manually") | .name'

# 1.4 Get recent failures (last 20 runs)
gh run list --repo Insightpulseai/odoo --status failure --limit 20 \
  --json name,conclusion,headBranch,createdAt \
  --jq '.[] | "\(.createdAt)\t\(.name)\t\(.headBranch)"'

# 1.5 Identify duplicate/overlapping workflows
ls .github/workflows/*.yml | wc -l
# Group by trigger event
grep -l "on:.*push" .github/workflows/*.yml | wc -l
grep -l "on:.*pull_request" .github/workflows/*.yml | wc -l
grep -l "on:.*schedule" .github/workflows/*.yml | wc -l
grep -l "on:.*workflow_dispatch" .github/workflows/*.yml | wc -l
```

### Phase 2: Fix — Make failing workflows green

For each failing workflow, diagnose and fix:

```bash
# 2.1 Get failure details
gh run view <RUN_ID> --repo Insightpulseai/odoo --log-failed

# 2.2 Common failure patterns to fix:

# A) Missing secrets — add to org-level secrets
gh secret list --repo Insightpulseai/odoo
# If missing: gh secret set SECRET_NAME --org Insightpulseai --visibility all

# B) Outdated action versions — update to latest
# Find: actions/checkout@v3 → actions/checkout@v4
# Find: actions/setup-node@v3 → actions/setup-node@v4
# Find: actions/setup-python@v4 → actions/setup-python@v5

# C) Node/Python version mismatches
# Ensure: node-version: '18' or '20'
# Ensure: python-version: '3.12'

# D) Missing dependencies or broken imports
# Run locally first: ./scripts/ci_local.sh

# E) Docker build failures
docker build -f docker/Dockerfile.unified -t test-build .
```

### Phase 3: Streamline — Deduplicate and consolidate

```bash
# 3.1 Identify workflow categories and consolidation targets
# TARGET: Reduce 358 workflows to ~50-80 well-organized workflows

# Categories to consolidate:
# - CI gates (lint, test, type-check) → 1 unified ci.yml with matrix
# - Security scans (secret, SAST, deps) → 1 security.yml
# - Parity gates → 1 parity.yml with matrix
# - Deploy workflows → 1 per environment (dev, staging, prod)
# - Spec/doc gates → 1 governance.yml
# - Health checks → 1 health.yml with matrix

# 3.2 Use reusable workflows from .github repo
# Move shared workflow logic to Insightpulseai/.github/.github/workflows/
# Reference with: uses: Insightpulseai/.github/.github/workflows/ci.yml@main

# 3.3 Consolidation map:
# BEFORE (358 workflows) → AFTER (~60 workflows)
#
# CI:
#   ci.yml                    — lint + typecheck + test (matrix: node, python)
#   ci-odoo.yml               — Odoo module tests
#   ci-docker.yml             — Docker build validation
#
# Security:
#   security.yml              — secret scan + SAST + dependency audit
#
# Gates:
#   governance-gate.yml       — spec validate + repo health + naming
#   parity-gate.yml           — EE parity checks
#   taxonomy-gate.yml         — org taxonomy validation
#
# Deploy:
#   deploy-dev.yml            — Deploy to dev environment
#   deploy-staging.yml        — Deploy to staging
#   deploy-prod.yml           — Deploy to production
#   deploy-supabase.yml       — Supabase migrations + functions
#   deploy-vercel.yml         — Vercel deployments
#
# Build:
#   build-unified-image.yml   — Build + push unified Docker image
#   build-seeded-image.yml    — Build pre-seeded image
#
# Health:
#   health-check.yml          — All health checks (scheduled)
#
# Release:
#   release.yml               — Tag + release + changelog
#
# Marketplace:
#   marketplace-validate.yml  — Validate offer schemas
#   marketplace-publish.yml   — Publish to Partner Center
```

### Phase 4: Update unified Docker image

```bash
# 4.1 Update Dockerfile.unified to include ALL accumulated changes

# The unified image must include:
# - Odoo CE 19.0 base
# - All 73 ipai_* modules from addons/ipai/
# - OCA modules from addons/oca/ (flattened)
# - New docs/org/ governance documents
# - New marketplace/ control plane
# - Updated Python dependencies
# - Updated Node.js dependencies

# 4.2 Build and test locally
cd /path/to/odoo
docker build -f docker/Dockerfile.unified \
  --tag ghcr.io/insightpulseai/ipai-odoo-runtime:$(date +%Y%m%d) \
  --tag ghcr.io/insightpulseai/ipai-odoo-runtime:latest \
  .

# 4.3 Test the image
docker run -d --name test-odoo \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=odoo_dev \
  -p 8069:8069 \
  ghcr.io/insightpulseai/ipai-odoo-runtime:latest

# 4.4 Verify Odoo starts cleanly
docker logs test-odoo 2>&1 | tail -20
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health

# 4.5 Verify all ipai_* modules are discoverable
docker exec test-odoo odoo --addons-path=/opt/odoo/addons/ipai,/opt/odoo/addons/oca \
  -d odoo_dev --stop-after-init -i base 2>&1 | grep -i error

# 4.6 Push to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker push ghcr.io/insightpulseai/ipai-odoo-runtime:$(date +%Y%m%d)
docker push ghcr.io/insightpulseai/ipai-odoo-runtime:latest

# 4.7 Clean up test container
docker stop test-odoo && docker rm test-odoo
```

### Phase 5: Bulk update across all repos

```bash
# 5.1 For each active repo, ensure baseline governance
for repo in .github odoo agents ops-platform lakehouse web infra design-system templates; do
  echo "=== Updating $repo ==="

  # Clone if not local
  gh repo clone "Insightpulseai/$repo" "/tmp/ipai-$repo" -- --depth 1 2>/dev/null || true

  cd "/tmp/ipai-$repo"

  # Ensure README exists
  [ ! -f README.md ] && echo "# $repo" > README.md

  # Ensure CODEOWNERS exists
  [ ! -f CODEOWNERS ] && echo "* @jgtolentino" > CODEOWNERS

  # Ensure branch protection (via gh api)
  gh api repos/Insightpulseai/$repo/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":[]}' \
    --field enforce_admins=false \
    --field required_pull_request_reviews='{"required_approving_review_count":0}' \
    --field restrictions=null 2>/dev/null || echo "  (branch protection requires admin)"

  # Enable Dependabot
  if [ ! -f .github/dependabot.yml ]; then
    mkdir -p .github
    cat > .github/dependabot.yml << 'DEPEOF'
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      actions:
        patterns: ["*"]
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
DEPEOF
  fi

  cd /tmp
done

# 5.2 Update GitHub Actions versions across all workflows in odoo repo
cd /path/to/odoo

# Bulk update action versions
find .github/workflows -name '*.yml' -exec sed -i '' \
  -e 's|actions/checkout@v3|actions/checkout@v4|g' \
  -e 's|actions/setup-node@v3|actions/setup-node@v4|g' \
  -e 's|actions/setup-python@v4|actions/setup-python@v5|g' \
  -e 's|actions/upload-artifact@v3|actions/upload-artifact@v4|g' \
  -e 's|actions/download-artifact@v3|actions/download-artifact@v4|g' \
  -e 's|actions/cache@v3|actions/cache@v4|g' \
  {} \;

# 5.3 Fix common YAML issues
# Validate all workflow YAML
for f in .github/workflows/*.yml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>/dev/null || echo "INVALID YAML: $f"
done
```

### Phase 6: Verify — All green

```bash
# 6.1 Run local CI suite
./scripts/repo_health.sh
./scripts/spec_validate.sh
./scripts/ci_local.sh

# 6.2 Trigger CI on all repos
for repo in odoo agents ops-platform; do
  gh workflow run ci.yml --repo "Insightpulseai/$repo" --ref main 2>/dev/null || echo "  $repo: no ci.yml or dispatch not enabled"
done

# 6.3 Wait and check results
sleep 120
for repo in odoo agents ops-platform; do
  echo "=== $repo ==="
  gh run list --repo "Insightpulseai/$repo" --limit 3 \
    --json name,status,conclusion --jq '.[] | "\(.conclusion)\t\(.name)"'
done

# 6.4 Generate evidence
mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/ci-streamline
gh run list --repo Insightpulseai/odoo --limit 20 \
  --json name,status,conclusion,url \
  > docs/evidence/$(date +%Y%m%d-%H%M)/ci-streamline/workflow_runs.json

# 6.5 Count: before vs after
echo "Workflow count: $(ls .github/workflows/*.yml | wc -l)"
echo "Failing: $(gh run list --repo Insightpulseai/odoo --status failure --limit 50 --json conclusion | jq length)"
echo "Passing: $(gh run list --repo Insightpulseai/odoo --status success --limit 50 --json conclusion | jq length)"
```

---

## Commit Convention

```
chore(ci): streamline org-wide CI/CD — deduplicate workflows, fix failures

- Consolidate 358 workflows into ~60 organized workflows
- Update GitHub Actions to v4 across all workflows
- Fix failing workflow root causes
- Enable Dependabot on all active repos
- Add CODEOWNERS to repos missing them
- Update unified Docker image with all accumulated changes
- Add branch protection baseline to active repos
- Generate CI evidence pack

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Success Criteria

- [ ] `gh run list --status failure` returns 0 failures on main branch
- [ ] All active repos have: README, CODEOWNERS, branch protection, dependabot.yml
- [ ] Unified Docker image builds successfully with all 73 ipai_* modules
- [ ] `ghcr.io/insightpulseai/ipai-odoo-runtime:latest` pushed and verified
- [ ] Workflow count reduced from 358 to <80
- [ ] GitHub Actions versions all at v4+
- [ ] All YAML files pass syntax validation
- [ ] `./scripts/repo_health.sh` passes
- [ ] `./scripts/ci_local.sh` passes
- [ ] Evidence pack committed to `docs/evidence/`

---

## References

- GitHub Actions docs: https://docs.github.com/en/actions
- GitHub Reusable workflows: https://docs.github.com/en/actions/sharing-automations/reusing-workflows
- GitHub GHCR: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- Dependabot config: https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
- Odoo 19 testing: https://www.odoo.com/documentation/19.0/developer/reference/testing.html
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
