# Local ↔ Codespaces Synchronization Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-28
**Purpose**: Maintain environment parity between local development and GitHub Codespaces

---

## Quick Reference

### Initial Sync
```bash
# Run before starting work in either environment
./scripts/dev/sync-env.sh
```

### Start Development
```bash
# Works in both local and Codespaces (auto-detects environment)
./scripts/dev/start-dev.sh
```

### Verify Parity
```bash
# Run in both environments to confirm they're synchronized
docker ps --format 'table {{.Names}}\t{{.Status}}'
curl -I http://localhost:8069/web/login
./scripts/verify.sh
git log --oneline -5
```

---

## Architecture

### Single Source of Truth

| Component | Location | Purpose |
|-----------|----------|---------|
| Container Stack | `.devcontainer/docker-compose.yml` | Shared services (Postgres, Odoo, etc.) |
| Environment Config | `.devcontainer/devcontainer.json` | Codespaces settings |
| Code State | `main` branch | Canonical repository state |
| Secrets (Local) | `.env` (git-ignored) | Local environment variables |
| Secrets (Codespaces) | GitHub Codespaces Secrets | Cloud environment variables |

### Environment Detection

The `start-dev.sh` script automatically detects the environment:

```bash
if [[ -n "${CODESPACES:-}" ]]; then
    ENV_TYPE="codespaces"
    # Use Codespaces-specific URLs
else
    ENV_TYPE="local"
    # Use localhost URLs
fi
```

---

## Workflows

### Local → Codespaces Transfer

**Scenario**: You made changes locally and want to test in Codespaces

```bash
# 1. On local machine
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
git add -A
git commit -m "feat: your changes"
git push origin main

# 2. Create or connect to codespace
gh codespace create --repo jgtolentino/odoo-ce --branch main
# OR
gh codespace code --repo jgtolentino/odoo-ce

# 3. Inside codespace terminal
git pull origin main
./scripts/dev/start-dev.sh

# 4. Access Odoo via forwarded port
# URL automatically provided by Codespaces UI
```

### Codespaces → Local Transfer

**Scenario**: You made changes in Codespaces and want to continue locally

```bash
# 1. Inside codespace terminal
git add -A
git commit -m "feat: your changes"
git push origin main

# 2. On local machine
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
git pull origin main
./scripts/dev/start-dev.sh

# 3. Access Odoo
open http://localhost:8069
```

### Daily Sync Routine

**Best Practice**: Start each work session with a sync

```bash
# Morning routine (both environments)
./scripts/dev/sync-env.sh

# This ensures:
# ✅ Latest code from origin/main
# ✅ No unpushed commits lingering
# ✅ Devcontainer config is valid
# ✅ Health checks pass
```

---

## What Gets Synchronized

### Via Git (Automatic)
- ✅ Source code (`addons/`, `scripts/`, etc.)
- ✅ Configuration files (`config/odoo.conf`)
- ✅ Documentation (`docs/`, `*.md`)
- ✅ Devcontainer config (`.devcontainer/`)
- ✅ CI/CD workflows (`.github/workflows/`)

### Via Docker Compose (Consistent)
- ✅ PostgreSQL version and configuration
- ✅ Odoo version and addons path
- ✅ Service dependencies (networks, volumes)
- ✅ Port mappings (adjusted for environment)

### NOT Synchronized (Environment-Specific)
- ❌ Secret values (`.env` vs GitHub Secrets)
- ❌ Local database state (each environment has its own Postgres)
- ❌ Container volumes (recreated per environment)
- ❌ User preferences (IDE settings, shell aliases)

---

## Troubleshooting

### Environments Out of Sync

**Symptom**: Different behavior in local vs Codespaces

**Diagnosis**:
```bash
# Check Git state
git status
git log origin/main..HEAD  # Unpushed commits?
git log HEAD..origin/main  # Unpulled commits?

# Check container state
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'

# Check config hash
sha256sum .devcontainer/docker-compose.yml
```

**Solution**:
```bash
# Force sync
./scripts/dev/sync-env.sh

# If containers differ, rebuild
docker compose -f .devcontainer/docker-compose.yml down
docker compose -f .devcontainer/docker-compose.yml up -d --build
```

### Push Rejected (Diverged Branches)

**Symptom**: `git push` fails with "fetch first" error

**Solution**:
```bash
# Pull with rebase (preserves your commits on top)
git pull --rebase origin main

# Resolve conflicts if any
git status
# ... edit conflicting files ...
git add <resolved-files>
git rebase --continue

# Push again
git push origin main
```

### Codespaces Slow to Start

**Symptom**: Codespace creation takes >5 minutes

**Diagnosis**:
- Heavy Docker image pulls
- Large repository size
- Many devcontainer features

**Optimization**:
```bash
# Pre-build image (run locally, push to GHCR)
docker build -t ghcr.io/jgtolentino/odoo-ce:dev -f .devcontainer/Dockerfile .
docker push ghcr.io/jgtolentino/odoo-ce:dev

# Update devcontainer.json to use pre-built image
# "image": "ghcr.io/jgtolentino/odoo-ce:dev"
```

### Local Docker Not Running

**Symptom**: `sync-env.sh` skips container checks

**Expected Behavior**: This is normal on macOS when Docker Desktop is not running

**Options**:
1. Start Docker Desktop (if you want to test locally)
2. Skip local testing, rely on Codespaces (faster for cloud-first workflow)

---

## Best Practices

### Do's ✅

- ✅ Always run `sync-env.sh` before starting work
- ✅ Commit and push frequently (keeps environments aligned)
- ✅ Use `start-dev.sh` instead of manual docker-compose commands
- ✅ Test in both environments before merging to main
- ✅ Keep `.env.example` updated with new variables

### Don'ts ❌

- ❌ Don't create separate docker-compose files for local vs Codespaces
- ❌ Don't commit secrets to Git (use `.env` locally, GitHub Secrets remotely)
- ❌ Don't modify `.devcontainer/` files without testing in both environments
- ❌ Don't work on multiple branches simultaneously in different environments
- ❌ Don't skip `sync-env.sh` - it catches divergence early

---

## Cost Optimization

### GitHub Codespaces Usage

**Free Tier**:
- 120 core-hours/month
- 15 GB storage

**Recommended Settings** (in `.devcontainer/devcontainer.json`):
```json
{
  "hostRequirements": {
    "cpus": 2,
    "memory": "4gb",
    "storage": "32gb"
  }
}
```

**Usage Strategy**:
- Use Codespaces for: Remote work, testing in cloud environment
- Use local for: Heavy development, long-running tasks
- Stop Codespaces when not in use: `gh codespace stop`

---

## Scripts Reference

| Script | Purpose | Environment |
|--------|---------|-------------|
| `sync-env.sh` | Synchronize Git state and verify config | Both |
| `start-dev.sh` | Start unified dev environment | Both |
| `up.sh` | Start services (legacy, use start-dev.sh) | Local only |
| `down.sh` | Stop services | Both |
| `health.sh` | Run health checks | Both |
| `logs.sh` | View container logs | Both |
| `reset-db.sh` | Reset PostgreSQL database | Both |

---

## Related Documentation

- **Developer Runbook**: `docs/runbooks/DEV_SANDBOX.md` (complete guide)
- **Project Instructions**: `CLAUDE.md` (project-specific context)
- **Verification Script**: `scripts/verify.sh` (automated checks)
- **Global Framework**: `~/.claude/CLAUDE.md` (SuperClaude framework)

---

**Last Synchronized**: 2026-01-28
**Commits Pushed**: 7 (includes environment sync improvements)
**Status**: ✅ Both environments aligned with origin/main
