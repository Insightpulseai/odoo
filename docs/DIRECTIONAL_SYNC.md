# Directional Sync System

**Purpose**: Automated, idempotent synchronization system for managing data flows between repositories, remote services, and local artifacts.

**Version**: 1.0.0
**Last Updated**: 2025-01-04

---

## Overview

The directional sync system provides **deterministic, idempotent synchronization** between multiple data sources with three distinct operational modes:

- **PULL** (remote → repo): Clone/update data from external sources into repository
- **PUSH** (repo → remote): Publish repository artifacts to external services
- **BIDIRECTIONAL** (↔): Two-way synchronization maintaining consistency in both directions

### Key Features

- ✅ **Idempotent Operations**: Safe to run multiple times without side effects
- ✅ **Deterministic**: Same input always produces same output
- ✅ **Git-Aware**: Automatic commit for PULL operations (configurable)
- ✅ **Safety Gates**: Pre/post-sync validation checks
- ✅ **Verification**: Optional output verification with thresholds
- ✅ **Dry-Run Mode**: Preview changes without executing
- ✅ **CI Integration**: Full GitHub Actions workflow support
- ✅ **Drift Detection**: Identifies configuration mismatches

---

## Architecture

### Configuration File

**Location**: `.insightpulse/sync.yaml`

**Structure**:
```yaml
version: "1.0"

defaults:
  direction: bidirectional  # pull | push | bidirectional
  dry_run: false
  fail_on_diff: false
  idempotent: true
  git_commit: true  # PULL only

targets:
  <target_name>:
    direction: <pull|push|bidirectional>
    description: "Human-readable description"
    entrypoint: "path/to/script.sh"
    schedule: "cron expression"
    config:
      # Target-specific configuration
    inputs:
      - "glob/pattern/**"  # PUSH only
    outputs:
      - "glob/pattern/**"  # PULL only
    verification:
      command: "validation command"
      expected_min: 100  # Minimum expected count
      expected_exit_code: 0

safety:
  secret_patterns: [...]
  pre_sync_checks: [...]
  post_sync_checks: [...]
  drift_gates: [...]
```

### Sync Targets

#### 1. OCA Repos (PULL)
**Direction**: Remote → Repo
**Purpose**: Clone/update 30+ OCA community module repositories

```yaml
oca_repos:
  direction: pull
  entrypoint: "scripts/sync-oca-repos.sh"
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  outputs:
    - "insightpulse_odoo/addons/oca/**"
  verification:
    command: "find insightpulse_odoo/addons/oca -name '__manifest__.py' | wc -l"
    expected_min: 100
```

**Workflow**:
1. Check if repository exists locally
2. Update existing (git fetch + reset) OR clone fresh (--depth 1)
3. Count modules (__manifest__.py files)
4. Commit changes to main branch

#### 2. Claude Config (BIDIRECTIONAL)
**Direction**: ↔ claude.md ↔ MCP configs/agents/skills
**Purpose**: Synchronize claude.md with external configurations

```yaml
claude_config:
  direction: bidirectional
  entrypoint: "scripts/sync-claude-configs.sh"
  schedule: "0 4 * * *"  # Daily at 4 AM UTC
  config:
    claude_md: "claude.md"
    mcp_config: "$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    agent_dir: "$HOME/.claude/superclaude/agents"
    skills_dir: "docs/claude-code-skills"
  outputs:
    - "docs/claude-config-drift.md"
```

**Workflow**:
1. Validate claude.md structure (sections 0-23)
2. Extract MCP servers, agents, skills from claude.md
3. Compare with actual configs in filesystem
4. Generate drift report
5. Update configs if needed (bidirectional)

#### 3. Apps Truth (PULL)
**Direction**: Remote → Repo
**Purpose**: Pull live app deployment truth from DigitalOcean

```yaml
apps_truth:
  direction: pull
  entrypoint: "scripts/apps-truth-sync.sh"
  schedule: "0 */6 * * *"  # Every 6 hours
  outputs:
    - "docs/runtime/apps_truth.json"
  verification:
    command: "test -f docs/runtime/apps_truth.json && jq -e '.apps | length > 0' docs/runtime/apps_truth.json"
    expected_exit_code: 0
```

**Workflow**:
1. Query DigitalOcean App Platform API
2. Fetch active deployments and metadata
3. Write JSON to docs/runtime/apps_truth.json
4. Verify JSON is valid and non-empty

#### 4. Live to Docs (PULL)
**Direction**: Remote → Repo
**Purpose**: Pull live production configuration to documentation

```yaml
live_to_docs:
  direction: pull
  entrypoint: "scripts/sync-live-to-docs.sh"
  schedule: "0 */12 * * *"  # Every 12 hours
  outputs:
    - "docs/runtime/ADDONS_PATH.prod.txt"
    - "docs/runtime/DB_CONFIG.prod.txt"
    - "docs/runtime/ENV_VARS.prod.txt"
```

**Workflow**:
1. Connect to production Odoo instance
2. Extract configuration files
3. Sanitize secrets (replace with placeholders)
4. Write to docs/runtime/

#### 5. Skillsmith Catalog (PULL)
**Direction**: Remote → Repo
**Purpose**: Pull generated skills from Skillsmith error mining

```yaml
skillsmith_catalog:
  direction: pull
  entrypoint: "scripts/skillsmith_sync.py"
  schedule: "0 5 * * 0"  # Weekly on Sunday at 5 AM
  outputs:
    - "docs/claude-code-skills/**"
  verification:
    command: "python scripts/skillsmith_sync.py --check"
    expected_exit_code: 0
```

**Workflow**:
1. Query Skillsmith service for new skills
2. Download skill templates and metadata
3. Validate skill structure (SKILL.md frontmatter)
4. Install to docs/claude-code-skills/

---

## Usage

### CLI Commands

**List all targets**:
```bash
python scripts/sync_directional.py --list
```

**Dry-run mode (preview changes)**:
```bash
python scripts/sync_directional.py --dry-run
python scripts/sync_directional.py --target oca_repos --dry-run
```

**Sync single target**:
```bash
python scripts/sync_directional.py --target oca_repos
python scripts/sync_directional.py --target oca_repos --verify
```

**Sync by direction**:
```bash
python scripts/sync_directional.py --direction pull
python scripts/sync_directional.py --direction push --dry-run
```

**Sync with pattern matching**:
```bash
python scripts/sync_directional.py --target "oca_*"
python scripts/sync_directional.py --target "notion_*" --direction push
```

**CI mode (no interactive prompts)**:
```bash
python scripts/sync_directional.py --ci
```

### GitHub Actions Workflow

**Manual Trigger** (via workflow_dispatch):

1. Go to Actions → Directional Sync Automation
2. Click "Run workflow"
3. Select options:
   - **Direction**: pull, push, bidirectional, or empty (all)
   - **Target**: Pattern like "oca_*" or empty (all)
   - **Dry Run**: Preview changes without executing
   - **Verify**: Enable verification checks

**Scheduled Runs**:

The workflow automatically runs on schedules matching each target's `schedule` field:

- **2 AM UTC**: OCA repos (daily)
- **3 AM UTC**: Notion field docs (daily)
- **4 AM UTC**: Claude config (daily)
- **Every 6 hours**: Apps truth
- **Every 12 hours**: Live to docs
- **Sunday 5 AM UTC**: Skillsmith catalog
- **1st of month 1 AM UTC**: Notion month-end
- **1st of month 2 AM UTC**: Notion BIR

---

## Safety & Guardrails

### Pre-Sync Checks

**Git Clean Check**:
```yaml
- name: "Git clean"
  command: "git diff --quiet && git diff --staged --quiet"
  skip_on_pull: false
```

**Secret Scanning**:
```yaml
- name: "No secrets in repo"
  command: "git grep -i -E '(password|secret|token).*=' | grep -v '.insightpulse/sync.yaml' | grep -v 'env.example'"
  expected_exit_code: 1  # Expect no matches
```

### Post-Sync Checks

**JSON/YAML Validation**:
```yaml
- name: "Valid JSON/YAML outputs"
  command: "find docs/runtime -name '*.json' -exec jq empty {} \\;"
  skip_on_push: true
```

**Python Syntax Check**:
```yaml
- name: "Python compileall"
  command: "python -m compileall scripts/"
  skip_on_push: false
```

### Drift Gates

**Claude Config Drift**:
```yaml
- name: "Claude config drift"
  command: "scripts/sync-claude-configs.sh"
  max_drift_score: 0
```

**OCA Module Count**:
```yaml
- name: "OCA module count"
  command: "find insightpulse_odoo/addons/oca -name '__manifest__.py' | wc -l"
  min_value: 100
```

### Secret Protection

**Protected Patterns**:
- `NOTION_API_TOKEN`
- `NOTION_.*_DB_ID`
- `GITHUB_TOKEN`
- `SUPABASE_.*KEY`
- `password`
- `secret`

---

## Verification

### Output Verification

Each target can specify verification commands to validate outputs:

**Example: Module Count Verification**
```yaml
verification:
  command: "find insightpulse_odoo/addons/oca -name '__manifest__.py' | wc -l"
  expected_min: 100
```

**Example: JSON Structure Verification**
```yaml
verification:
  command: "test -f docs/runtime/apps_truth.json && jq -e '.apps | length > 0' docs/runtime/apps_truth.json"
  expected_exit_code: 0
```

### Verification Report

After sync, a summary JSON is generated:

```json
{
  "timestamp": "2025-01-04T10:30:00Z",
  "total_targets": 8,
  "successful": 7,
  "failed": 1,
  "total_duration": 45.2,
  "results": [
    {
      "target": "oca_repos",
      "direction": "pull",
      "success": true,
      "message": "Synced successfully: 30 repos updated",
      "duration": 12.5,
      "outputs_created": [
        "insightpulse_odoo/addons/oca/account-financial-tools",
        "insightpulse_odoo/addons/oca/sale-workflow"
      ],
      "verification_passed": true
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. Sync Fails with "Directory not found"
**Cause**: Output directory doesn't exist
**Solution**: Script should create directories automatically, but verify:
```bash
mkdir -p insightpulse_odoo/addons/oca
mkdir -p docs/runtime
```

#### 2. Verification Fails
**Cause**: Output doesn't meet expected thresholds
**Solution**: Check verification command manually:
```bash
find insightpulse_odoo/addons/oca -name '__manifest__.py' | wc -l
```

#### 3. Git Commit Fails
**Cause**: Git not configured or untracked files
**Solution**: Configure git and stage files:
```bash
git config user.name "CI Bot"
git config user.email "ci@example.com"
git add -A
```

#### 4. Environment Variables Not Found
**Cause**: Required env vars missing
**Solution**: Set in CI secrets or .env:
```bash
export NOTION_API_TOKEN=secret_...
export GITHUB_TOKEN=ghp_...
```

### Debug Mode

Run with verbose logging:
```bash
python scripts/sync_directional.py --target oca_repos --dry-run 2>&1 | tee sync.log
```

---

## Development

### Adding New Sync Targets

1. **Define in `.insightpulse/sync.yaml`**:
```yaml
my_new_target:
  direction: pull
  description: "My new sync target"
  entrypoint: "scripts/my-sync.sh"
  schedule: "0 3 * * *"
  outputs:
    - "path/to/output/**"
  verification:
    command: "test -f path/to/output/file.json"
    expected_exit_code: 0
```

2. **Create entrypoint script**:
```bash
#!/usr/bin/env bash
# scripts/my-sync.sh
set -euo pipefail

echo "Starting my sync..."
# Your sync logic here
echo "Sync complete"
```

3. **Test locally**:
```bash
python scripts/sync_directional.py --target my_new_target --dry-run
python scripts/sync_directional.py --target my_new_target --verify
```

4. **Update CI workflow** (if needed):
Add to `.github/workflows/directional-sync.yml` if scheduling required.

### Testing

**Unit Tests** (to be implemented):
```bash
pytest tests/test_directional_sync.py -v
```

**Smoke Tests**:
```bash
# Test dry-run mode
python scripts/sync_directional.py --dry-run

# Test single target
python scripts/sync_directional.py --target oca_repos --dry-run

# Test verification
python scripts/sync_directional.py --target oca_repos --verify --dry-run
```

**Integration Tests**:
```bash
# Test full sync cycle
python scripts/sync_directional.py --direction pull --dry-run
```

---

## Acceptance Criteria

All of the following must pass for the sync system to be considered operational:

1. ✅ **Config Valid**: `.insightpulse/sync.yaml` validates against schema
2. ✅ **Runner Executable**: `python scripts/sync_directional.py --list` succeeds
3. ✅ **Dry-Run Works**: All targets complete in dry-run mode
4. ✅ **Pre-Sync Gates Pass**: Git clean, no secrets in repo
5. ✅ **Post-Sync Gates Pass**: JSON/YAML valid, Python compileall succeeds
6. ✅ **Drift Gates Green**: Claude config drift = 0, OCA modules ≥ 100
7. ✅ **CI Workflow Valid**: GitHub Actions workflow syntax correct
8. ✅ **Verification Reports Generated**: JSON summary created after sync
9. ✅ **Git Commits Work**: PULL operations commit successfully
10. ✅ **Scheduled Runs Execute**: CI triggers match sync.yaml schedules

---

## Roadmap

**Phase 1** (Current):
- Core sync runner implementation
- 8 initial sync targets
- Basic CI integration
- Drift detection

**Phase 2** (Future):
- Web dashboard for sync status
- Slack/Mattermost notifications
- Advanced conflict resolution
- Sync history and rollback
- Performance metrics (P95/P99 sync times)

**Phase 3** (Future):
- Multi-repository sync support
- Custom sync plugins
- Advanced scheduling (dependencies, priorities)
- Real-time sync monitoring

---

## References

- **Configuration**: `.insightpulse/sync.yaml`
- **Main Runner**: `scripts/sync_directional.py`
- **CI Workflow**: `.github/workflows/directional-sync.yml`
- **Existing Syncs**: `scripts/sync-oca-repos.sh`, `scripts/sync-claude-configs.sh`

---

**Maintainer**: InsightPulse AI Team
**Repository**: https://github.com/jgtolentino/odoo-ce
**Last Updated**: 2025-01-04
