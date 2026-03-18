# Refactor Automation — Implementation Plan

> 5-phase implementation for AI-driven refactor automation with triage and CI integration

## Context

**Why**: Manual code quality management doesn't scale. Refactor opportunities get lost, technical debt accumulates, and quality gates are inconsistent.

**Problem**:
- No automated detection of refactor opportunities
- Manual triage is slow and inconsistent
- Refactor findings scattered across reviews
- No systematic tracking of technical debt
- Quality gates are manual and error-prone

**Intended Outcome**:
- Automated refactor detection on every PR
- AI-driven triage with auto-issue creation
- CI-integrated quality gates
- Evidence-based refactor tracking
- Zero manual UI operations

---

## Phase 1: Analysis Engine

**Goal**: Build refactor detection and scoring system

### Components

**1.1 Static Analyzers**
- Install analysis tools: `radon`, `pylint`, `mypy`, `coverage`
- Create analyzer wrapper scripts in `scripts/refactor/`
- Define scoring algorithms for each analyzer
- Output JSON reports with standardized schema

**1.2 AST-Based Detection**
- Build custom AST walker for Python
- Detect Odoo-specific anti-patterns
- Identify code duplication via syntax tree comparison
- Find dead code and unused imports

**1.3 Complexity Scoring**
- McCabe complexity per function
- Cognitive complexity for nested logic
- Module-level complexity aggregation
- Trend analysis (getting better/worse)

**Files to Create**:
- `scripts/refactor/analyze.py` - Main analysis orchestrator
- `scripts/refactor/analyzers/complexity.py` - Complexity metrics
- `scripts/refactor/analyzers/duplication.py` - Code duplication
- `scripts/refactor/analyzers/types.py` - Type coverage
- `scripts/refactor/analyzers/coverage.py` - Test coverage
- `scripts/refactor/analyzers/oca.py` - OCA compliance
- `scripts/refactor/scoring.py` - Priority scoring logic

**Validation**:
```bash
# Test analysis on sample module
python scripts/refactor/analyze.py addons/ipai_custom/ --output findings.json

# Verify JSON schema
cat findings.json | jq '.findings[] | {type, priority, file, line}'
```

---

## Phase 2: Triage Automation

**Goal**: Intelligent categorization and GitHub issue creation

### Components

**2.1 Triage Engine**
- Categorize findings by type and impact
- Calculate priority scores (critical → low)
- Estimate effort and risk levels
- Group related findings for batch fixing

**2.2 GitHub Issue Templates**
- Define issue template structure
- Generate code snippets with context
- Attach evidence (metrics, diffs)
- Auto-link related issues

**2.3 Issue Creation**
- GitHub API integration for issue creation
- Auto-assign based on CODEOWNERS
- Add labels (refactor, priority, type)
- Link to evidence artifacts

**Files to Create**:
- `scripts/refactor/triage.py` - Triage orchestrator
- `scripts/refactor/github_client.py` - GitHub API wrapper
- `scripts/refactor/templates/issue.md.j2` - Jinja2 issue template
- `.refactor/codeowners.yaml` - Module ownership mapping
- `.refactor/config.yaml` - Triage policies

**Validation**:
```bash
# Test triage without creating issues
python scripts/refactor/triage.py findings.json --dry-run

# Create issues for critical findings only
python scripts/refactor/triage.py findings.json --priority critical --auto-issue

# Verify issue created
gh issue list --label refactor
```

---

## Phase 3: CI Integration

**Goal**: Automated refactor analysis in GitHub Actions

### Components

**3.1 Pre-Commit Hook**
- Install pre-commit framework
- Configure refactor analysis hook
- Fail on critical findings
- Show inline suggestions

**3.2 GitHub Actions Workflow**
- Trigger on PR submission
- Run full analysis on changed files
- Auto-create issues for findings
- Comment on PR with summary
- Block merge on critical findings

**3.3 Quality Gates**
- Define merge criteria
- Require approval for high-risk refactors
- Validate test coverage increase
- Ensure OCA compliance

**Files to Create**:
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.github/workflows/refactor-analysis.yml` - PR analysis workflow
- `.github/workflows/refactor-scheduled.yml` - Daily full scan
- `scripts/refactor/pr_comment.py` - PR comment generator
- `.refactor/gates.yaml` - Quality gate policies

**Validation**:
```bash
# Test pre-commit hook locally
pre-commit run --all-files

# Test workflow locally with act
act pull_request -W .github/workflows/refactor-analysis.yml

# Verify PR comment
gh pr view 123 --comments
```

---

## Phase 4: Evidence Generation

**Goal**: Automated before/after metrics and visual evidence

### Components

**4.1 Metrics Collection**
- Capture baseline metrics before refactor
- Run analysis after refactor
- Calculate deltas (complexity, coverage, etc.)
- Store in time-series format

**4.2 Visual Evidence**
- Generate code diffs with syntax highlighting
- Create complexity heatmaps
- Plot coverage comparison charts
- Export dependency graph changes

**4.3 Evidence Storage**
- Store in `docs/evidence/<YYYYMMDD-HHMM>/refactor/`
- Link to GitHub issues
- Sync to Supabase for dashboard
- Generate summary reports

**Files to Create**:
- `scripts/refactor/evidence.py` - Evidence generator
- `scripts/refactor/visualize.py` - Chart generation
- `scripts/refactor/storage.py` - Evidence storage
- `supabase/migrations/20260214_000007_refactor_tracking.sql` - Refactor history tables

**Validation**:
```bash
# Generate evidence for refactor
python scripts/refactor/evidence.py --before before.json --after after.json

# Verify evidence created
ls docs/evidence/20260214-1500/refactor/
# → metrics.json, diff.html, complexity_heatmap.png, summary.md

# Upload to Supabase
python scripts/refactor/storage.py --upload docs/evidence/20260214-1500/refactor/
```

---

## Phase 5: CLI & Dashboard

**Goal**: Developer-friendly CLI and metrics dashboard

### Components

**5.1 CLI Tool**
- `refactor scan` - Analyze code
- `refactor triage` - Auto-create issues
- `refactor apply` - Execute suggested refactor
- `refactor metrics` - View dashboard
- `refactor validate` - Check quality gates

**5.2 Metrics Dashboard**
- Refactor trends over time
- Technical debt reduction
- Automation accuracy
- Developer productivity

**5.3 Configuration**
- YAML-based config
- Per-module policies
- Team-specific thresholds
- Custom analyzer plugins

**Files to Create**:
- `scripts/refactor/cli.py` - CLI entry point
- `scripts/refactor/commands/` - Command implementations
- `scripts/refactor/dashboard.py` - Metrics dashboard
- `.refactor/config.yaml` - Default configuration
- `README-refactor.md` - Usage documentation

**Validation**:
```bash
# Test CLI commands
refactor scan --help
refactor scan addons/ipai_custom/ --priority high

# View metrics dashboard
refactor metrics --dashboard
# → Opens browser with metrics charts

# Apply refactor suggestion
refactor apply --issue 123 --validate
```

---

## Critical Files to Create/Modify

### New Files
1. `scripts/refactor/analyze.py` - Main analysis engine
2. `scripts/refactor/triage.py` - Triage orchestrator
3. `scripts/refactor/github_client.py` - GitHub API integration
4. `scripts/refactor/evidence.py` - Evidence generation
5. `scripts/refactor/cli.py` - CLI tool
6. `.github/workflows/refactor-analysis.yml` - PR workflow
7. `.github/workflows/refactor-scheduled.yml` - Daily scan
8. `.pre-commit-config.yaml` - Pre-commit hooks
9. `.refactor/config.yaml` - Configuration
10. `supabase/migrations/20260214_000007_refactor_tracking.sql` - DB schema

### Modified Files
1. `scripts/repo_health.sh` - Add refactor checks
2. `scripts/ci_local.sh` - Integrate refactor validation
3. `CLAUDE.md` - Document refactor workflows
4. `docs/ai/REFACTOR.md` - Refactor system docs

---

## Verification Plan

### Phase 1 Verification (Analysis)
```bash
# Run analysis on test module
python scripts/refactor/analyze.py addons/ipai_test/ --output test_findings.json

# Verify findings schema
cat test_findings.json | jq '.findings | length'
# → Should show count of findings

# Check priority distribution
cat test_findings.json | jq '.findings | group_by(.priority) | map({priority: .[0].priority, count: length})'
```

### Phase 2 Verification (Triage)
```bash
# Dry-run triage
python scripts/refactor/triage.py test_findings.json --dry-run

# Create test issue
python scripts/refactor/triage.py test_findings.json --priority critical --limit 1 --auto-issue

# Verify issue
gh issue view --repo Insightpulseai/odoo $(gh issue list --label refactor --limit 1 --json number -q '.[0].number')
```

### Phase 3 Verification (CI)
```bash
# Test pre-commit locally
pre-commit run refactor-scan --all-files

# Simulate PR workflow
act pull_request -W .github/workflows/refactor-analysis.yml -e test/pr-event.json

# Verify quality gates
refactor validate --pr 123
```

### Phase 4 Verification (Evidence)
```bash
# Generate evidence
refactor evidence --before baseline.json --after current.json

# Verify artifacts
ls docs/evidence/latest/refactor/
# → metrics.json, diff.html, charts/

# Check Supabase upload
psql $SUPABASE_URL -c "SELECT * FROM refactor.findings ORDER BY created_at DESC LIMIT 5;"
```

### Phase 5 Verification (CLI)
```bash
# Test all CLI commands
refactor scan addons/ipai_custom/
refactor triage --auto-issue --priority high
refactor metrics --dashboard
refactor validate --strict
```

---

## Success Metrics

- ✅ 100% PRs analyzed automatically
- ✅ >95% issue creation accuracy (no false positives)
- ✅ <5 min detection to GitHub issue
- ✅ Zero manual triage operations
- ✅ All refactors have evidence attached
- ✅ Average McCabe complexity <8
- ✅ Test coverage >80% for refactored modules

---

## Risks & Mitigations

**Risk 1: False positive rate too high**
- **Mitigation**: Tune scoring thresholds per module, allow custom overrides

**Risk 2: Analysis too slow for CI**
- **Mitigation**: Incremental analysis on changed files only, parallel analyzer execution

**Risk 3: GitHub API rate limits**
- **Mitigation**: Batch issue creation, use GitHub App tokens (higher limits)

**Risk 4: Evidence storage costs**
- **Mitigation**: Lifecycle policies, compress artifacts, store only deltas

**Risk 5: Developer resistance to automation**
- **Mitigation**: Clear value proposition, easy opt-out for specific cases, gradual rollout
