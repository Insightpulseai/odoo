# Vendor Subtree Isolation Strategy

**Version**: 1.0.0
**Date**: 2026-03-05
**Status**: Implemented
**Related Workflow**: `.github/workflows/docs-sync-odoo-official.yml`

---

## Overview

External documentation syncs are isolated to a vendor subtree (`vendor/docs/`) to prevent blast radius issues and maintain clear boundaries between internal and external content.

---

## Directory Structure

### Before (Mixed Namespace)

```
docs/
├── odoo-official/         ← External sync (PROBLEM: mixed with internal)
│   ├── administration/
│   ├── applications/
│   ├── contributing/
│   └── developer/
├── architecture/          ← Internal docs
├── ai/                    ← Internal docs
└── runbooks/              ← Internal docs
```

**Issues**:
- External and internal docs share namespace
- Rsync misconfiguration could affect internal docs
- Unclear ownership boundary
- No version isolation

### After (Isolated Vendor Subtree)

```
vendor/
└── docs/
    └── odoo-official/
        ├── README.md              ← Vendor metadata
        └── 19.0/                  ← Version-specific isolation
            ├── administration/
            ├── applications/
            ├── contributing/
            ├── developer/
            ├── SYNC_METADATA.json
            ├── SYNC_REPORT.md
            └── search-index.json

docs/
├── architecture/          ← Internal only (protected)
├── ai/                    ← Internal only (protected)
└── runbooks/              ← Internal only (protected)
```

**Benefits**:
- Clear boundary: `vendor/` = external, `docs/` = internal
- No namespace collision possible
- Version-specific isolation (supports future 20.0, 21.0)
- Easy to identify sync artifacts
- Blast radius limited to `vendor/docs/odoo-official/19.0/`

---

## Diff Gates

The sync workflow includes three validation gates to prevent catastrophic changes:

### Gate 1: Pre-Sync File Count Validation

**Purpose**: Prevent syncing from empty or incomplete upstream clones

**Thresholds**:
- **Minimum**: 100 files (hard stop if below)
- **Maximum**: 1000 files (warning if above)

**Implementation**:
```bash
UPSTREAM_FILES=$(find official-docs/content -name '*.rst' | wc -l)

if [ "$UPSTREAM_FILES" -lt 100 ]; then
  echo "❌ GATE 1 FAILURE: Upstream incomplete"
  exit 1
fi
```

**Prevents**:
- Syncing from failed/partial git clones
- Network interruption causing empty syncs
- Upstream repository corruption

### Gate 2: Structural Integrity Check

**Purpose**: Ensure all documentation sections present and populated

**Validation**:
- All 4 required directories exist:
  - `administration/`
  - `applications/`
  - `contributing/`
  - `developer/`
- Each directory has ≥5 RST files

**Implementation**:
```bash
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ GATE 2 FAILURE: Missing directory"
    exit 1
  fi

  FILE_COUNT=$(find "$dir" -name '*.rst' | wc -l)
  if [ "$FILE_COUNT" -lt 5 ]; then
    echo "❌ GATE 2 FAILURE: Directory nearly empty"
    exit 1
  fi
done
```

**Prevents**:
- Upstream structural changes breaking builds
- Section deletions going unnoticed
- Incomplete syncs

### Gate 3: Diff Magnitude Validation

**Purpose**: Prevent catastrophically large changes from being committed automatically

**Thresholds**:
- **Max Files Changed**: 50 (hard stop if exceeded)
- **Max Lines Deleted**: 5000 (hard stop if exceeded)
- **Warn Lines Added**: 10000 (warning only)

**Implementation**:
```bash
git diff --numstat vendor/docs/odoo-official/19.0/ > /tmp/diff-stats.txt

ADDED=$(awk '{sum+=$1} END {print sum}' /tmp/diff-stats.txt)
DELETED=$(awk '{sum+=$2} END {print sum}' /tmp/diff-stats.txt)
FILES_CHANGED=$(wc -l < /tmp/diff-stats.txt)

if [ "$FILES_CHANGED" -gt 50 ]; then
  echo "🚨 GATE 3 FAILURE: Too many files changed"
  exit 1
fi

if [ "$DELETED" -gt 5000 ]; then
  echo "🚨 GATE 3 FAILURE: Too many lines deleted"
  exit 1
fi
```

**Prevents**:
- Accidental wide-scope deletions
- Upstream restructures being blindly accepted
- Mass content removal going unnoticed

---

## Rollback Strategy

### Automatic Tagging

Successful syncs are automatically tagged for rollback:

```bash
git tag -a "docs-sync-good-$(date +%Y%m%d-%H%M)" -m "Known good sync"
git push --tags
```

**Tag Format**: `docs-sync-good-YYYYMMDD-HHMM`

**Example**: `docs-sync-good-20260305-0300`

### Rollback Procedure

#### Automatic Rollback Triggers

The workflow will fail (not commit) if:
1. Gate 1 fails (file count too low)
2. Gate 2 fails (missing directories or empty sections)
3. Gate 3 fails (diff magnitude exceeds thresholds)

No rollback needed - bad sync never reaches main branch.

#### Manual Rollback

If a bad sync somehow reaches production:

```bash
# 1. Find last known good tag
git tag -l "docs-sync-good-*" | sort -r | head -5

# 2. Restore from tag
git checkout docs-sync-good-20260304-0300 -- vendor/docs/odoo-official/

# 3. Commit rollback
git commit -m "revert(docs): emergency rollback to 20260304-0300

Reason: [describe issue]

Restoring last known good sync state."

# 4. Push (triggers auto-redeploy via GitHub Pages)
git push origin main
```

### Recovery Time Objective (RTO)

- **Detection**: Immediate (GitHub Actions failure notification)
- **Rollback Execution**: < 5 minutes (manual or automated)
- **Deployment**: ~3-5 minutes (GitHub Pages rebuild)
- **Total RTO**: < 10 minutes from detection to restored service

---

## Workflow Controls

### Workflow Dispatch Inputs

#### `force_rebuild`

**Purpose**: Force complete rebuild even if no changes detected

**Use Cases**:
- Search index corrupted
- Sphinx build artifacts stale
- Manual verification needed

**Usage**:
```yaml
inputs:
  force_rebuild:
    type: boolean
    default: false
```

#### `skip_gates`

**Purpose**: Override diff gates for legitimate large changes

**⚠️ WARNING**: Use with extreme caution. Only skip gates after manual verification.

**Use Cases**:
- Upstream major version upgrade (e.g., 19.0 → 20.0)
- Odoo documentation restructure (verified legitimate)
- Emergency sync with known large changes

**Usage**:
```yaml
inputs:
  skip_gates:
    type: boolean
    default: false
```

**Safety**: Requires manual workflow dispatch - cannot be triggered via cron with gates disabled.

---

## Monitoring & Alerting

### Success Metrics

Track via workflow outputs and Slack notifications:

1. **Sync Duration**: Baseline 2-5 minutes
2. **File Count Deltas**: Baseline ±5 files per sync
3. **Line Count Deltas**: Baseline ±500 lines per sync
4. **Gate Failure Rate**: Target <5% of syncs
5. **Rollback Frequency**: Target <1% of syncs

### Slack Notifications

#### Success Notification

```
📚 **Documentation Platform Updated**

**Site**: https://insightpulseai.github.io/odoo/
**Sync**: Official Odoo 18.0 docs synchronized to vendor subtree
**AI Assistant**: Available via chat widget
**Diff Gates**: All gates passed ✅
```

#### Gate Failure Notification

```
🚨 **Documentation Sync: Diff Gate Failure**

**Workflow**: [Run link]
**Reason**: Diff magnitude exceeded thresholds

**Action Required**: Review changes and re-run with `skip_gates` if legitimate.
```

---

## Migration Notes

### Path Changes

All references to `docs/odoo-official/` must be updated to `vendor/docs/odoo-official/19.0/`:

**Updated Files**:
1. `.github/workflows/docs-sync-odoo-official.yml` - rsync targets
2. `docs/conf.py` - Sphinx source paths
3. `docs/index.rst` - toctree paths
4. AI chat widget - search index path
5. Search index builder - output path

**Search and Replace**:
```bash
# Old path
docs/odoo-official/

# New path
vendor/docs/odoo-official/19.0/
```

### GitHub Pages Configuration

No changes required - GitHub Pages deployment uses build artifact from `docs/_build/html/`, which references vendor subtree via Sphinx configuration.

---

## Security Considerations

### Vendor Content Trust

**Source**: `https://github.com/odoo/documentation` (Odoo SA - official)

**Verification**:
- Syncs only from official Odoo repository
- Uses specific branch (`19.0`) - no arbitrary refs
- Git clone over HTTPS (TLS encrypted)
- No user-supplied content in sync

### Attack Surface

**Minimal Attack Surface**:
- Read-only sync (no write to upstream)
- No secret credentials required
- No external API calls (pure git + rsync)
- No dynamic code execution in synced content (RST files only)

**Blast Radius Containment**:
- Limited to `vendor/docs/odoo-official/19.0/` directory
- Diff gates prevent massive deletions
- Rollback available via git tags
- Internal docs (`docs/`) completely isolated

---

## Future Enhancements

### Multi-Version Support

**Planned**: Support for multiple Odoo versions simultaneously

```
vendor/
└── docs/
    └── odoo-official/
        ├── 19.0/          ← Current
        ├── 20.0/          ← Future
        └── 21.0/          ← Future
```

**Implementation**: Duplicate workflow with version-specific branch and path.

### PR-Based Review

**Consideration**: Replace direct commit with PR creation for human review

**Benefits**:
- Manual review before merge
- CI checks on PR before deploy
- Easier to reject bad syncs

**Tradeoff**: Adds manual step to daily sync process

**Decision**: Keep direct commit for now, add PR mode as optional flag if needed.

---

## References

- **Workflow**: `.github/workflows/docs-sync-odoo-official.yml`
- **Evidence Bundle**: `web/docs/evidence/20260305-0000+0800/docs-sync-sandbox/`
- **Governance Plan**: Governance hardening - Task 3
- **Source Repository**: https://github.com/odoo/documentation

---

**Maintainer**: InsightPulse AI DevOps
**Review Schedule**: Quarterly (or after Odoo version releases)
**Last Updated**: 2026-03-05
