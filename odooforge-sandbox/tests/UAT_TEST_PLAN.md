# OdooForge Sandbox - UAT Test Plan

## Overview

This document defines the User Acceptance Testing (UAT) plan for the OdooForge Sandbox environment. The sandbox provides a containerized development environment for creating, validating, and deploying IPAI Odoo modules.

**Version**: 1.0.0
**Last Updated**: 2024-01-10

---

## Test Categories

### 1. Installation Tests (6 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| I-01 | Docker available | Check docker command | Docker CLI available |
| I-02 | Docker Compose available | Check docker compose | Compose available |
| I-03 | Port 8069 available | Check lsof/ss | Port not in use |
| I-04 | Port 5432 available | Check lsof/ss | Port not in use |
| I-05 | Directory creation | Run install script | Directories created |
| I-06 | Container build | Run install script | All containers built |

### 2. Container Health Tests (6 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| C-01 | DB container running | docker compose ps | Status: running |
| C-02 | Odoo container running | docker compose ps | Status: running |
| C-03 | Kit container running | docker compose ps | Status: running |
| C-04 | DB healthcheck | pg_isready | Ready |
| C-05 | Odoo healthcheck | curl /web/health | HTTP 200 |
| C-06 | Kit bash available | exec kit bash | Shell prompt |

### 3. CLI Init Tests (11 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| K-01 | kit version | kit version | Shows version |
| K-02 | kit init basic | kit init ipai_test | Module created |
| K-03 | Invalid name rejected | kit init invalid_name | Error message |
| K-04 | Duplicate rejected | kit init ipai_test (2x) | Error on second |
| K-05 | __manifest__.py created | ls module | File exists |
| K-06 | __init__.py created | ls module | File exists |
| K-07 | models/ created | ls module | Directory exists |
| K-08 | views/ created | ls module | Directory exists |
| K-09 | security/ created | ls module | Directory exists |
| K-10 | tests/ created | ls module | Directory exists |
| K-11 | README.md created | ls module | File exists |

### 4. CLI Validate Tests (5 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| V-01 | Valid module passes | kit validate ipai_test | All rules pass |
| V-02 | Missing manifest fails | Remove __manifest__.py | Error |
| V-03 | Invalid name fails | kit validate bad_name | Error |
| V-04 | Syntax error fails | Add invalid Python | Error |
| V-05 | Strict mode | kit validate --strict | Warnings shown |

### 5. CLI Build/Deploy Tests (4 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| B-01 | kit build | kit build ipai_test | Zip created |
| B-02 | Build with output | kit build -o /tmp | Zip in /tmp |
| B-03 | kit deploy | kit deploy ipai_test | Connection OK |
| B-04 | kit list | kit list | Modules listed |

### 6. Module Structure Tests (6 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| M-01 | Manifest has name | Check manifest | name field exists |
| M-02 | Manifest has version | Check manifest | OCA format |
| M-03 | Manifest has depends | Check manifest | base included |
| M-04 | Manifest has license | Check manifest | LGPL-3 |
| M-05 | Security CSV format | Check security file | Valid CSV header |
| M-06 | Test file present | Check tests/ | test_main.py exists |

### 7. Performance Tests (2 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| P-01 | Init time | Time kit init | < 5 seconds |
| P-02 | Validate time | Time kit validate | < 3 seconds |

### 8. Error Handling Tests (2 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| E-01 | Module not found | kit validate missing | Clear error |
| E-02 | Invalid command | kit invalid | Help shown |

### 9. End-to-End Tests (2 tests)

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| E2E-01 | Full workflow | init → validate → build | Success |
| E2E-02 | Module in Odoo | Install module | Visible in Apps |

---

## Test Execution Summary

| Category | Test Count | Priority |
|----------|------------|----------|
| Installation | 6 | Critical |
| Container Health | 6 | Critical |
| CLI Init | 11 | High |
| CLI Validate | 5 | High |
| CLI Build/Deploy | 4 | Medium |
| Module Structure | 6 | Medium |
| Performance | 2 | Low |
| Error Handling | 2 | Medium |
| End-to-End | 2 | High |
| **Total** | **38** | |

---

## Automated Test Execution

```bash
# Run all UAT tests
docker compose exec kit pytest tests/test_uat.py -v

# Run specific category
docker compose exec kit pytest tests/test_uat.py -v -k "installation"

# Generate HTML report
docker compose exec kit pytest tests/test_uat.py --html=reports/uat.html

# Quick smoke test
./tests/run-uat.sh
```

---

## Pass/Fail Criteria

- **Critical tests**: Must all pass (Installation, Container Health)
- **High priority tests**: 90% pass rate required
- **Medium/Low priority**: 80% pass rate required
- **Overall**: Minimum 85% pass rate for UAT approval

---

## Test Environment

| Component | Version | Notes |
|-----------|---------|-------|
| Docker | 24.0+ | Required |
| Docker Compose | 2.0+ | V2 syntax |
| Odoo | 18.0 | CE Edition |
| PostgreSQL | 15 | Alpine |
| Python | 3.11 | In kit container |
| pytest | 7.0+ | Test runner |

---

## Known Limitations

1. Odoo health check may take 1-2 minutes on first start
2. Port conflicts require manual resolution
3. Some tests require Odoo database initialization
4. E2E-02 (module installation) requires manual verification

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | | | |
| Dev Lead | | | |
| Product Owner | | | |
