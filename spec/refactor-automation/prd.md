# Refactor Automation — Product Requirements

> AI-driven code quality improvement with automated triage and issue tracking

## User Personas

**Platform Admin**:
- Monitors refactor quality metrics
- Approves high-risk refactors
- Configures automation policies
- Reviews triage accuracy

**Odoo Developer**:
- Receives auto-created issues for refactor work
- Reviews refactor suggestions with evidence
- Executes refactors with CI validation
- Tracks impact on module quality

**QA Engineer**:
- Validates refactor quality gates
- Reviews before/after test coverage
- Verifies no regression introduced
- Monitors automated issue accuracy

**Technical Lead**:
- Prioritizes refactor backlog
- Reviews high-complexity findings
- Approves architectural refactors
- Tracks technical debt reduction

## Core Features

### 1. Automated Refactor Detection

**Triggers**:
- PR submission (check changed files)
- Scheduled daily scan (full codebase)
- Manual trigger via CLI (`refactor scan`)
- Pre-commit hook (local validation)

**Analyzers**:
- **Complexity**: Detect functions >McCabe 10
- **Duplication**: Find repeated code blocks >15 lines
- **Type Safety**: Identify missing type hints
- **Test Coverage**: Flag untested code paths
- **OCA Compliance**: Validate module structure
- **Dead Code**: Detect unused imports/functions
- **Performance**: Identify inefficient queries/loops

**Output**:
- JSON report with findings
- Priority scoring (critical → low)
- Impact analysis (files, risk, effort)
- Suggested fixes with code snippets

### 2. Intelligent Triage

**Auto-Categorization**:
- **Critical**: Security issues, broken imports, syntax errors
- **High**: High complexity, low coverage, major duplication
- **Medium**: Minor duplication, missing types, style violations
- **Low**: Documentation, dead code, minor optimization

**Issue Template**:
```markdown
## Refactor: [Brief description]

**Type**: Complexity | Duplication | Type Safety | Test Coverage | etc.
**Priority**: Critical | High | Medium | Low
**Impact**: [Files affected, risk level, effort estimate]

### Current State
[Code snippet showing issue]

### Suggested Fix
[Code snippet with improvement]

### Evidence
- Complexity: McCabe score [before → after]
- Coverage: [before% → after%]
- Files affected: [list]

### Related
- Related issues: [auto-linked]
- OCA compliance: [pass/fail]
```

**Auto-Assignment**:
- Route by module ownership (CODEOWNERS)
- Balance workload across developers
- Escalate critical to tech leads
- Group related issues for batch fixing

### 3. CI Integration

**Pre-Commit Hook** (local):
```bash
#!/bin/bash
# .git/hooks/pre-commit
refactor scan --staged --fail-on critical
```

**PR Check** (GitHub Actions):
```yaml
name: Refactor Analysis
on: [pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run refactor analysis
        run: refactor scan --pr ${{ github.event.number }}
      - name: Auto-create issues
        run: refactor triage --auto-issue
      - name: Comment on PR
        run: refactor comment --findings
```

**Quality Gates**:
- Block merge if critical findings unresolved
- Require approval for high-risk refactors
- Validate test coverage increase
- Ensure OCA compliance maintained

### 4. Evidence Generation

**Before/After Metrics**:
- Complexity scores (radon)
- Test coverage percentages
- Duplication statistics
- Type coverage percentages
- Performance benchmarks

**Visual Evidence**:
- Code diff with highlights
- Complexity heatmaps
- Coverage comparison charts
- Dependency graph changes

**Storage**:
- `docs/evidence/<YYYYMMDD-HHMM>/refactor/`
- Screenshots in PNG format
- Metrics in JSON format
- Summary in Markdown

## Workflows

### Developer Workflow

1. **Local Development**:
   ```bash
   # Pre-commit hook triggers on git commit
   git add addons/ipai_custom/models/
   git commit -m "feat: add custom model"
   # → Refactor scan runs automatically
   # → Fails if critical findings
   # → Shows suggestions inline
   ```

2. **PR Submission**:
   ```bash
   gh pr create --title "feat: custom model"
   # → CI runs refactor analysis
   # → Auto-creates issues for findings
   # → Comments on PR with summary
   # → Blocks merge if critical
   ```

3. **Issue Resolution**:
   ```bash
   # Developer receives auto-created issue
   gh issue view 123
   # → Sees evidence and suggestions
   # → Applies refactor
   refactor apply --issue 123
   # → Validates with tests
   # → Closes issue automatically
   ```

### Platform Admin Workflow

1. **Monitor Metrics**:
   ```bash
   refactor metrics --dashboard
   # → View refactor trends
   # → Track technical debt reduction
   # → Review automation accuracy
   ```

2. **Configure Policies**:
   ```yaml
   # .refactor/config.yaml
   policies:
     auto_issue_threshold: high
     block_merge_on: critical
     require_evidence: true
     oca_compliance: enforce
   ```

3. **Review Queue**:
   ```bash
   refactor queue --priority critical
   # → Review pending refactors
   # → Approve high-risk changes
   # → Re-prioritize as needed
   ```

## Success Metrics

**Automation Quality**:
- >95% issue creation accuracy (no false positives)
- <5 min detection to GitHub issue
- 100% findings have evidence attached
- Zero manual triage operations

**Code Quality Improvements**:
- Average McCabe complexity <8 (target <10)
- Test coverage >80% for refactored modules
- Duplication <5% (target <10%)
- Type coverage >70% (target >90%)

**Developer Experience**:
- <2 min local refactor scan
- Clear, actionable issue descriptions
- Auto-suggestions reduce manual work by >60%
- No false blocking on valid code

## Technical Requirements

**CLI Tool**:
- `refactor scan` - Analyze code for refactor opportunities
- `refactor triage` - Auto-create GitHub issues
- `refactor apply` - Execute suggested refactor
- `refactor metrics` - View quality dashboard
- `refactor validate` - Check quality gates

**GitHub Integration**:
- Issue creation via GitHub API
- PR comments with findings
- Automated labels (refactor, priority)
- Auto-assignment based on CODEOWNERS

**Supabase Storage**:
- Refactor findings history
- Metrics time series
- Evidence artifacts
- Automation audit trail
