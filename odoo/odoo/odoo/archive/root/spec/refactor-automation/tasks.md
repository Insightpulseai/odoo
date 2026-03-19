# TASKS — Refactor Automation

## T0 — Spec-kit compliance
- [x] Ensure `spec/refactor-automation/{constitution,prd,plan,tasks}.md` exist
- [ ] Add CI check enforcing presence for platform specs

## T1 — Analysis Engine
- [ ] Install analysis dependencies:
  - [ ] `pip install radon pylint mypy coverage`
  - [ ] Add to `requirements.txt`
  - [ ] Update DevContainer with tools
- [ ] Create analyzer scripts:
  - [ ] `scripts/refactor/analyze.py` - Main orchestrator
  - [ ] `scripts/refactor/analyzers/complexity.py` - McCabe complexity
  - [ ] `scripts/refactor/analyzers/duplication.py` - Code duplication via AST
  - [ ] `scripts/refactor/analyzers/types.py` - Type coverage with mypy
  - [ ] `scripts/refactor/analyzers/coverage.py` - Test coverage analysis
  - [ ] `scripts/refactor/analyzers/oca.py` - OCA compliance validation
  - [ ] `scripts/refactor/scoring.py` - Priority scoring algorithm
- [ ] Define JSON output schema:
  - [ ] `findings` array with type, priority, file, line, suggestion
  - [ ] `metrics` object with before/after scores
  - [ ] `evidence` paths to artifacts
- [ ] Add unit tests:
  - [ ] Test each analyzer independently
  - [ ] Validate JSON schema compliance
  - [ ] Test scoring algorithm edge cases

## T2 — Triage Automation
- [ ] Create triage engine:
  - [ ] `scripts/refactor/triage.py` - Main triage orchestrator
  - [ ] Categorization logic (type + impact → priority)
  - [ ] Effort estimation based on lines changed
  - [ ] Risk scoring based on file criticality
- [ ] GitHub integration:
  - [ ] `scripts/refactor/github_client.py` - GitHub API wrapper
  - [ ] Issue creation with template rendering
  - [ ] Auto-assignment via CODEOWNERS
  - [ ] Label management (refactor, priority levels)
  - [ ] Auto-linking related issues
- [ ] Configuration:
  - [ ] `.refactor/config.yaml` - Triage policies
  - [ ] `.refactor/codeowners.yaml` - Module ownership
  - [ ] `.refactor/templates/issue.md.j2` - Jinja2 issue template
- [ ] Add tests:
  - [ ] Mock GitHub API responses
  - [ ] Validate issue template rendering
  - [ ] Test auto-assignment logic

## T3 — CI Integration
- [ ] Pre-commit hooks:
  - [ ] `.pre-commit-config.yaml` - Hook configuration
  - [ ] `scripts/refactor/pre_commit.py` - Pre-commit script
  - [ ] Fail on critical findings
  - [ ] Show inline suggestions
- [ ] GitHub Actions workflows:
  - [ ] `.github/workflows/refactor-analysis.yml` - PR analysis
    - [ ] Trigger on `pull_request` event
    - [ ] Run analysis on changed files only
    - [ ] Auto-create issues for findings
    - [ ] Comment on PR with summary
    - [ ] Block merge on critical findings
  - [ ] `.github/workflows/refactor-scheduled.yml` - Daily full scan
    - [ ] Schedule: `cron: '0 2 * * *'` (2 AM daily)
    - [ ] Analyze entire codebase
    - [ ] Track metrics over time
    - [ ] Report to Slack/dashboard
- [ ] Quality gates:
  - [ ] `.refactor/gates.yaml` - Merge criteria
  - [ ] `scripts/refactor/gates.py` - Gate validator
  - [ ] Define blocking criteria (critical findings, coverage drop, etc.)
- [ ] PR comment generator:
  - [ ] `scripts/refactor/pr_comment.py` - Markdown comment generator
  - [ ] Summary table with findings count
  - [ ] Link to auto-created issues
  - [ ] Diff preview for suggested refactors
- [ ] Add workflow tests:
  - [ ] Test with `act` (local GitHub Actions)
  - [ ] Verify comment generation
  - [ ] Test quality gate blocking

## T4 — Evidence Generation
- [ ] Metrics collection:
  - [ ] `scripts/refactor/metrics.py` - Metrics collector
  - [ ] Baseline capture before refactor
  - [ ] Delta calculation (before → after)
  - [ ] Time-series storage format
- [ ] Visual evidence:
  - [ ] `scripts/refactor/visualize.py` - Chart generator
  - [ ] Code diff with syntax highlighting
  - [ ] Complexity heatmaps (matplotlib)
  - [ ] Coverage comparison charts
  - [ ] Dependency graph diffs
- [ ] Evidence storage:
  - [ ] `scripts/refactor/storage.py` - Evidence manager
  - [ ] Local: `docs/evidence/<YYYYMMDD-HHMM>/refactor/`
  - [ ] Supabase: Upload artifacts
  - [ ] Link to GitHub issues
- [ ] Supabase schema:
  - [ ] `supabase/migrations/20260214_000007_refactor_tracking.sql`
  - [ ] `refactor.findings` - Finding history
  - [ ] `refactor.metrics` - Metrics time series
  - [ ] `refactor.evidence` - Artifact metadata
- [ ] Add tests:
  - [ ] Test metrics calculation
  - [ ] Validate chart generation
  - [ ] Test storage upload

## T5 — CLI & Dashboard
- [ ] CLI tool:
  - [ ] `scripts/refactor/cli.py` - CLI entry point with argparse
  - [ ] Commands:
    - [ ] `refactor scan <path>` - Analyze code
    - [ ] `refactor triage <findings.json>` - Auto-create issues
    - [ ] `refactor apply --issue <id>` - Execute suggested refactor
    - [ ] `refactor metrics` - View dashboard
    - [ ] `refactor validate` - Check quality gates
  - [ ] Add to PATH: `ln -s scripts/refactor/cli.py ~/bin/refactor`
- [ ] Metrics dashboard:
  - [ ] `scripts/refactor/dashboard.py` - Flask/Streamlit dashboard
  - [ ] Charts:
    - [ ] Refactor trends over time
    - [ ] Technical debt reduction
    - [ ] Automation accuracy (false positive rate)
    - [ ] Developer productivity
  - [ ] Filters: date range, module, priority
- [ ] Configuration management:
  - [ ] `.refactor/config.yaml` - Default config
  - [ ] Per-module overrides: `addons/<module>/.refactor.yaml`
  - [ ] Config validation schema
- [ ] Documentation:
  - [ ] `README-refactor.md` - Usage guide
  - [ ] `docs/ai/REFACTOR.md` - System architecture
  - [ ] Add to `CLAUDE.md`
- [ ] Add tests:
  - [ ] CLI command integration tests
  - [ ] Dashboard rendering tests
  - [ ] Config validation tests

## T6 — Integration & Testing
- [ ] End-to-end testing:
  - [ ] Test full workflow: PR → analysis → issue → refactor → close
  - [ ] Validate evidence generation
  - [ ] Check quality gate blocking
  - [ ] Verify metrics dashboard
- [ ] Performance testing:
  - [ ] Measure analysis time for large modules
  - [ ] Optimize for CI environment (<5 min)
  - [ ] Test parallel analyzer execution
- [ ] Documentation:
  - [ ] Update `CLAUDE.md` with refactor workflows
  - [ ] Create `docs/ai/REFACTOR.md` with architecture
  - [ ] Add runbook to `docs/runbooks/refactor-automation.md`
- [ ] Rollout:
  - [ ] Deploy to dev environment
  - [ ] Run on `addons/ipai_test/` module
  - [ ] Gather feedback from developers
  - [ ] Tune thresholds and policies
  - [ ] Deploy to production CI

## Acceptance Criteria
- [ ] Analysis runs in <5 min on average PR
- [ ] >95% issue creation accuracy (no false positives)
- [ ] 100% findings have evidence attached
- [ ] Quality gates block merge on critical findings
- [ ] Dashboard shows metrics trends
- [ ] CLI tool works end-to-end
- [ ] All tests pass
- [ ] Documentation complete
