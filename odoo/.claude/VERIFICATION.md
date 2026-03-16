# Agent Teams Verification Checklist

> **Purpose**: Deterministic verification that agent teams are configured correctly and operating as intended.
> **Run This**: After enabling teams, after each team execution, before merging team-generated PRs.
> **Last Updated**: 2026-02-20

---

## Pre-Flight Checks (Before Spawning Team)

### Configuration Verification

```bash
# 1. Agent teams enabled
grep -q '"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"' .claude/settings.json && echo "✅ Teams enabled" || echo "❌ Teams not enabled"

# 2. Teammate mode set
grep -q '"teammateMode": "in-process"' .claude/settings.json && echo "✅ In-process mode" || echo "❌ Mode not set"

# 3. Team topology documented
test -f .claude/AGENT_TEAMS.md && echo "✅ Team topology exists" || echo "❌ Missing team topology"

# 4. Risky operations defined
test -f .claude/RISKY_OPERATIONS.md && echo "✅ Risk catalog exists" || echo "❌ Missing risk catalog"
```

**Expected Output**:
```
✅ Teams enabled
✅ In-process mode
✅ Team topology exists
✅ Risk catalog exists
```

---

## Plan Approval Verification (During Team Execution)

When teammate requests plan approval, verify:

### 1. Plan Completeness

```bash
# Check plan has all required sections
grep -q "Files to Change" plan.md && echo "✅ Files listed"
grep -q "Exact Diffs" plan.md && echo "✅ Diffs provided"
grep -q "Verification Checklist" plan.md && echo "✅ Checklist exists"
grep -q "Rollback Strategy" plan.md && echo "✅ Rollback documented"
```

### 2. Risk Category Correct

For each operation in plan, check against `.claude/RISKY_OPERATIONS.md`:

| Operation Type | Risk Category | Approval Required |
|----------------|---------------|-------------------|
| Schema/Migration | 🔴 Critical | YES |
| RLS Policy | 🔴 Critical | YES |
| CI Gate Logic | 🔴 Critical | YES |
| Prod Config | 🔴 Critical | YES |
| Multi-Module Port | 🔴 Critical | YES |
| Edge Function | 🟡 Moderate | Recommended |
| Pre-commit Hook | 🟡 Moderate | Recommended |
| Docker/DevContainer | 🟡 Moderate | Recommended |
| Documentation | 🟢 Low | Optional |
| Single Manifest | 🟢 Low | Optional |
| Tests Only | 🟢 Low | Optional |

### 3. Scope Discipline

```bash
# Verify no unrelated files in plan
git diff --name-only | while read file; do
  grep -q "$file" plan.md || echo "⚠️  Unrelated file: $file"
done
```

**Expected**: No output (all changed files documented in plan).

### 4. Diff Precision

For each file in plan:
- ✅ Diff shows ONLY necessary changes
- ❌ Diff includes formatting changes
- ❌ Diff includes commented-out code
- ❌ Diff includes debug statements

---

## Implementation Verification (After Teammate Executes)

### 1. Teammate Stayed in Scope

```bash
# Compare actual changes to approved plan
git diff --name-only > actual_files.txt
grep "Files to Change" plan.md | tail -n +2 > planned_files.txt
diff actual_files.txt planned_files.txt && echo "✅ Scope matched" || echo "❌ Scope drift"
```

### 2. Verification Checklist Passed

For each item in teammate's verification checklist, run command and confirm:

**Example** (OCA Porter):
```bash
# Python syntax check
python3 -m py_compile addons/oca/connector/component/__init__.py && echo "✅ Syntax OK"

# Manifest version check
grep version addons/oca/connector/component/__manifest__.py | grep -q "19.0" && echo "✅ Version correct"

# No unrelated files
test $(git diff --name-only | wc -l) -eq 1 && echo "✅ Single file only"
```

### 3. Rollback Readiness

If operation was risky (🔴 Critical):
```bash
# Verify rollback documented
grep -q "Rollback:" plan.md && echo "✅ Rollback exists"

# Test rollback command (dry-run if possible)
# Example: git revert --no-commit <hash> && git reset --hard HEAD
```

---

## Synthesis Verification (Lead Pre-Merge)

### 1. All Teammates Completed

```bash
# Check teammate status
echo "Team Completion Status:"
for teammate in "OCA Porter" "CI Gatekeeper" "Platform SSOT" "Runtime Engineer"; do
  # (Manual check in team log/task list)
  echo "  $teammate: [COMPLETE | IN_PROGRESS | BLOCKED]"
done
```

### 2. No Scope Creep

```bash
# Git diff scope check
echo "Changed files by domain:"
git diff --name-only main...HEAD | sort | while read file; do
  case "$file" in
    addons/oca/*) echo "  OCA: $file" ;;
    .github/workflows/*) echo "  CI: $file" ;;
    supabase/*) echo "  SSOT: $file" ;;
    .devcontainer/*|docker-compose*) echo "  Runtime: $file" ;;
    *) echo "  ⚠️  OTHER: $file" ;;
  esac
done
```

**Expected**: All files match assigned teammate domains.

### 3. Commit Message Quality

For each commit by teammates:
```bash
git log --oneline main..HEAD | while read line; do
  hash=$(echo "$line" | awk '{print $1}')
  msg=$(echo "$line" | cut -d' ' -f2-)

  # Check conventional commit format
  echo "$msg" | grep -qE '^(feat|fix|chore|docs|refactor|test)\([a-z-]+\):' && \
    echo "✅ $hash: $msg" || \
    echo "❌ $hash: Bad format: $msg"
done
```

### 4. No Accidental Commits

```bash
# Check for common accidentals
git diff --name-only main...HEAD | grep -E '\.(log|tmp|cache|pyc|swp)$' && \
  echo "❌ Temp files committed" || echo "✅ No temp files"

git diff main...HEAD | grep -qE '(console\.log|debugger|binding\.pry|import pdb)' && \
  echo "❌ Debug statements found" || echo "✅ No debug code"
```

---

## Post-Merge Verification

### 1. CI Passes

```bash
# Check GitHub Actions status
gh pr checks $(gh pr view --json number -q .number) && \
  echo "✅ All checks passed" || echo "❌ CI failures"
```

### 2. No Regressions

For risky operations, run smoke tests:

**Schema changes**:
```bash
# Verify migration applied
psql $DATABASE_URL -c "\d+ table_name" | grep new_column && echo "✅ Migration OK"
```

**OCA ports**:
```bash
# Verify module installs
# (Would run in DevContainer or CI)
odoo -i ported_module_name --stop-after-init && echo "✅ Module installs"
```

**CI gates**:
```bash
# Trigger workflow manually
gh workflow run workflow_name.yml && echo "✅ Workflow triggered"
```

---

## Team Cleanup Verification

### 1. Teammates Shut Down

```bash
# Check for orphaned processes (manual check in terminal/tmux)
ps aux | grep -i claude | grep -v grep && echo "⚠️  Orphaned processes" || echo "✅ Clean shutdown"
```

### 2. Task List Clean

```bash
# Verify shared task list cleared (if using task persistence)
# (Manual check in .claude/tasks/ or task list file)
echo "Open tasks remaining: $(ls .claude/tasks/*.json 2>/dev/null | wc -l)"
```

**Expected**: `0` open tasks.

### 3. Artifacts Cleaned

```bash
# Remove temporary plan files
rm -f plan.md teammate_*.log actual_files.txt planned_files.txt
echo "✅ Temp files cleaned"
```

---

## Emergency Abort Procedure

If team execution goes wrong (scope explosion, conflicts, etc.):

```bash
# 1. Stop all teammates (manual intervention)
# 2. Reset working tree
git reset --hard HEAD
git clean -fd

# 3. Check clean state
git status | grep -q "nothing to commit" && echo "✅ Clean reset"

# 4. Document incident
mkdir -p docs/incidents
cat > docs/incidents/$(date +%Y%m%d)-team-abort.md <<EOF
# Team Execution Abort - $(date)

**Reason**: [Why abort was necessary]
**State**: [What was in progress]
**Recovery**: [How state was cleaned]
**Prevention**: [What to change to avoid repeat]
EOF

echo "✅ Abort complete, incident documented"
```

---

## Verification Summary Template

After team execution, fill this out:

```markdown
## Agent Team Verification - [DATE]

**Team**: [OCA Porter | CI Gatekeeper | Platform SSOT | Runtime Engineer]
**Task**: [Brief description]

### Pre-Flight
- [x] Teams enabled in settings.json
- [x] Teammate mode: in-process
- [x] Team topology documented
- [x] Risk catalog up to date

### Plan Approval
- [x] All risky operations had plans
- [x] Plans were complete (files, diffs, checklist, rollback)
- [x] Risk categories correctly identified
- [x] Lead approved before implementation

### Implementation
- [x] Teammates stayed in scope
- [x] Verification checklists all passed
- [x] Rollback tested (if critical)

### Synthesis
- [x] All teammates completed
- [x] No scope creep (git diff matches domains)
- [x] Commit messages follow convention
- [x] No accidental files committed

### Post-Merge
- [x] CI passes
- [x] No regressions (smoke tests passed)
- [x] Team cleaned up

**Status**: ✅ SUCCESS | ⚠️  WITH_ISSUES | ❌ FAILED

**Issues**: [List any problems encountered]
**Lessons**: [What to improve next time]
```

---

## Quick Reference Commands

```bash
# Enable teams
echo '{"env":{"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"},"teammateMode":"in-process"}' > .claude/settings.json

# Verify configuration
grep -E '(AGENT_TEAMS|teammateMode)' .claude/settings.json

# Check scope discipline
git diff --name-only | wc -l  # Should match plan

# Verify commit quality
git log --oneline main..HEAD | grep -vE '^[a-f0-9]+ (feat|fix|chore|docs|refactor|test)\([a-z-]+\):'

# Emergency abort
git reset --hard HEAD && git clean -fd
```

---

## References

- `.claude/AGENT_TEAMS.md` - Team topology
- `.claude/RISKY_OPERATIONS.md` - Risk categories
- [Claude Code Docs - Agent Teams](https://code.claude.com/docs/en/agent-teams)
