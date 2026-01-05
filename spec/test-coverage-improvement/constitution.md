# Test Coverage Improvement — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Created**: 2026-01-04

---

## Core Principles

### 1. Test Coverage is Non-Negotiable for Critical Modules

All modules handling financial data, workflow state transitions, or security boundaries **MUST** have test coverage before production deployment.

### 2. Tests Must Be Independent and Repeatable

- Each test must create its own test data
- Tests must not depend on execution order
- Tests must use `TransactionCase` or `SavepointCase` for automatic rollback

### 3. Follow Existing Patterns

- Use `@tagged('post_install', '-at_install', 'module_name')` for all tests
- Use `setUpClass` for shared test data
- Follow naming convention: `test_XX_description` for ordered execution

### 4. Test the Right Things

| Priority | What to Test |
|----------|--------------|
| P1 | State transitions and workflow logic |
| P1 | Financial calculations and data integrity |
| P1 | Access control and permission boundaries |
| P2 | Computed fields and business logic |
| P2 | Cron jobs and automated processes |
| P3 | UI helpers and display logic |

### 5. Minimum Coverage Requirements

| Module Category | Minimum Coverage |
|-----------------|------------------|
| Finance modules | 80% |
| Workflow modules | 70% |
| Platform modules | 60% |
| Utility modules | 50% |

---

## Constraints

### DO

- Create shared fixtures in `addons/ipai/ipai_test_fixtures/`
- Tag tests appropriately for selective execution
- Document test prerequisites in docstrings
- Use descriptive assertion messages

### DO NOT

- Skip tests for "simple" modules without approval
- Create tests that depend on external services
- Hardcode dates (use `date.today()` or relative dates)
- Create tests that modify production data

---

## Quality Gates

1. All new code must include tests before merge
2. CI must pass with all tests green
3. Coverage reports must not decrease
4. Test execution time must stay under 5 minutes per module
