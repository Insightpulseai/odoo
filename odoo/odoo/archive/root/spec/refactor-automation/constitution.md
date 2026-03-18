# Refactor Automation — Constitution

> Non-negotiable principles for automated code quality improvement and triage

## 1) Scope

Automated refactoring intelligence system for Odoo CE+OCA+ipai with:
- Multi-file refactor detection and execution
- Quality triage with auto-issue creation
- CI-integrated refactor validation
- Zero manual UI steps for refactor operations

## 2) Non-negotiables

1. **Automated Issue Creation**: All refactor findings auto-create GitHub issues with context
2. **Quality Gates**: Refactors must pass lint, typecheck, tests before merge
3. **Evidence Required**: Every refactor produces before/after metrics and screenshots
4. **OCA Compliance**: Refactors follow OCA module structure and conventions
5. **Reversible Changes**: All refactors tracked in git with atomic commits
6. **Triage Intelligence**: AI-driven priority and impact scoring for findings
7. **No Manual UI**: All operations via CLI, API, or CI workflows

## 3) Quality Standards

**Refactor Quality**:
- Complexity reduction (McCabe < 10 per function)
- Duplication elimination (DRY principle)
- Type safety improvements (Python type hints)
- Test coverage increase (≥80% for refactored modules)

**Issue Quality**:
- Clear title with refactor scope
- Automated priority (critical, high, medium, low)
- Impact analysis (files affected, risk level)
- Suggested fix with code snippets

**CI Integration**:
- Pre-commit hooks for local validation
- PR checks for refactor impact
- Automated comments on findings
- Quality metrics reporting

## 4) Tech Stack

**Analysis Tools**:
- `radon` - Complexity metrics
- `pylint` - Code quality
- `mypy` - Type checking
- `coverage` - Test coverage
- Custom AST analyzers for Odoo patterns

**Automation**:
- GitHub Actions for CI
- GitHub API for issue creation
- Supabase for refactor tracking
- Odoo module scaffolding templates

**Storage**:
- `docs/refactor/` - Refactor reports
- `docs/evidence/` - Before/after evidence
- GitHub Issues - Triage queue
- Supabase - Refactor history and metrics

## 5) Success Metrics

- >90% automated issue creation from findings
- <5 min from detection to GitHub issue
- 100% refactors pass quality gates
- Zero manual triage operations
- Refactor impact visible in metrics dashboard

## 6) Constraints

- No breaking changes without explicit approval
- Refactors scoped to single module per PR
- All changes reversible via git
- Quality metrics must improve or stay same
- OCA compliance validated before merge
