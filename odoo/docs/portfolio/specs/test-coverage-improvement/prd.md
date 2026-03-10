# Test Coverage Improvement — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-04

---

## 1. Executive Summary

This initiative aims to improve test coverage from the current **21.6%** (8 of 37 IPAI submodules) to **80%** coverage of critical modules. The focus is on financial modules, workflow systems, and platform infrastructure.

---

## 2. Problem Statement

### Current State
- Only 8 of 37 IPAI submodules have tests (21.6% coverage)
- 0 of 30 top-level IPAI modules have tests
- No shared test fixtures library exists
- Critical financial modules (`ipai_finance_ppm`, `ipai_close_orchestration`) lack tests
- E2E coverage limited to 1 Playwright spec file

### Impact
- Regressions discovered in production instead of CI
- Refactoring is risky without test safety net
- New developers lack confidence in making changes
- Compliance requirements for audit trails not verifiable

### Desired State
- 80% test coverage for financial modules
- 70% coverage for workflow modules
- Shared fixtures reduce test setup duplication
- CI enforces coverage thresholds
- E2E tests cover critical user journeys

---

## 3. Prioritized Module List

### Phase 1: Critical Financial Modules (P1)

| Module | Models to Test | Priority |
|--------|----------------|----------|
| `ipai_finance_ppm` | FinanceLogframe, FinanceBIRSchedule, cron sync | P1 |
| `ipai_master_control` | MasterControlMixin, webhook emission | P1 |
| `ipai_close_orchestration` | Close orchestration workflow | P1 |
| `ipai_finance_close_automation` | Automation rules, triggers | P1 |

### Phase 2: Platform Modules (P2)

| Module | Models to Test | Priority |
|--------|----------------|----------|
| `ipai_platform_workflow` | Workflow engine, state transitions | P2 |
| `ipai_platform_approvals` | Approval chains, escalation | P2 |
| `ipai_platform_permissions` | Access control, role boundaries | P2 |
| `ipai_ppm` | Core PPM models | P2 |

### Phase 3: AI & Integration Modules (P3)

| Module | Models to Test | Priority |
|--------|----------------|----------|
| `ipai_agent_core` | Agent registration, dispatch | P3 |
| `ipai_advisor` | AI advisor logic (with mocks) | P3 |
| `ipai_ask_ai` | Query processing | P3 |

---

## 4. Functional Requirements

### 4.1 Shared Test Fixtures Library

| ID | Requirement | Priority |
|----|-------------|----------|
| FIX-001 | Create `ipai_test_fixtures` module | P1 |
| FIX-002 | Provide factory methods for common models | P1 |
| FIX-003 | Support parameterized test data generation | P2 |
| FIX-004 | Include demo data reset utilities | P3 |

### 4.2 Test Infrastructure

| ID | Requirement | Priority |
|----|-------------|----------|
| INF-001 | Enforce coverage thresholds in CI | P1 |
| INF-002 | Generate HTML coverage reports | P2 |
| INF-003 | Support parallel test execution | P2 |
| INF-004 | Add test result badges to README | P3 |

### 4.3 Module-Specific Tests

| ID | Requirement | Priority |
|----|-------------|----------|
| TST-001 | Finance PPM: BIR schedule lifecycle tests | P1 |
| TST-002 | Finance PPM: Cron job task sync tests | P1 |
| TST-003 | Master Control: Webhook emission tests (mocked) | P1 |
| TST-004 | Master Control: Event enablement tests | P1 |
| TST-005 | Close Orchestration: Full workflow tests | P1 |

---

## 5. Test Categories

### Unit Tests (Fast)
- Business logic calculations
- Field validations
- State machine transitions
- Computed field correctness

### Integration Tests (Medium)
- Multi-model workflows
- Cron job execution
- Cross-module dependencies

### E2E Tests (Slow)
- User login and navigation
- Critical form submissions
- Report generation
- Print functionality

---

## 6. Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Module coverage | 21.6% | 80% | - |
| Lines of test code | 4,510 | 15,000+ | - |
| Test execution time | ~3 min | < 5 min | - |
| E2E specs | 1 | 5+ | - |

---

## 7. Non-Goals

- 100% line coverage (not practical)
- Testing private/internal methods directly
- Testing Odoo core functionality
- Testing third-party module internals
