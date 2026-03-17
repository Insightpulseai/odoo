# Test Coverage Improvement — Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-04

---

## Phase 1: Foundation

### Step 1.1: Create Shared Test Fixtures Module

**Location**: `addons/ipai/ipai_test_fixtures/`

```
ipai_test_fixtures/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── test_factories.py
└── tests/
    ├── __init__.py
    └── test_fixtures.py
```

**Factory Methods**:
- `create_test_user(role='user'|'manager'|'admin')`
- `create_test_employee(user=None)`
- `create_test_project(name=None)`
- `create_test_task(project=None, user=None)`
- `create_test_expense(employee=None, amount=100.0)`
- `create_test_bir_schedule(period=None)`

### Step 1.2: Implement ipai_finance_ppm Tests

**File**: `addons/ipai/ipai_finance_ppm/tests/test_finance_ppm.py`

**Test Classes**:
1. `TestFinanceLogframe`
   - `test_logframe_creation`
   - `test_logframe_levels`
   - `test_task_count_computed`

2. `TestFinanceBIRSchedule`
   - `test_schedule_creation`
   - `test_schedule_status_transitions`
   - `test_completion_percentage_calculation`
   - `test_late_status_detection`

3. `TestBIRCronSync`
   - `test_cron_creates_tasks`
   - `test_cron_updates_existing_tasks`
   - `test_cron_skips_filed_schedules`

### Step 1.3: Implement ipai_master_control Tests

**File**: `addons/ipai/ipai_master_control/tests/test_master_control.py`

**Test Classes**:
1. `TestMasterControlConfig`
   - `test_default_config_values`
   - `test_config_from_parameters`
   - `test_event_enablement`

2. `TestMasterControlMixin`
   - `test_emit_disabled_when_not_configured`
   - `test_emit_builds_correct_payload`
   - `test_emit_handles_network_errors` (mocked)

---

## Phase 2: Workflow & Platform

### Step 2.1: Implement ipai_close_orchestration Tests

**Test Classes**:
1. `TestCloseOrchestration`
   - `test_close_workflow_initiation`
   - `test_step_progression`
   - `test_rollback_on_failure`

### Step 2.2: Implement ipai_platform_approvals Tests

**Test Classes**:
1. `TestApprovalChain`
   - `test_approval_chain_creation`
   - `test_approval_routing`
   - `test_escalation_triggers`

---

## Phase 3: E2E Expansion

### Step 3.1: Add Critical E2E Specs

**New Playwright Specs**:
1. `tests/playwright/login_flow.spec.js`
2. `tests/playwright/expense_submission.spec.js`
3. `tests/playwright/month_end_close.spec.js`
4. `tests/playwright/equipment_booking.spec.js`

---

## Implementation Guidelines

### Test File Template

```python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024 InsightPulseAI
"""
Test cases for [Module Name].

Tests cover:
- [List key areas]
"""
from datetime import date, timedelta

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "module_name")
class TestModelName(TransactionCase):
    """Test [model description]."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        # Create shared test data here

    def test_01_creation(self):
        """Test that records are created with correct defaults."""
        # Test implementation
        pass
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_webhook_call(self):
    """Test webhook is called correctly."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {'work_item_id': 'test-123'}
        )

        result = self.env['master.control.mixin']._emit_work_item(
            source='test',
            source_ref='test:1',
            title='Test Item',
            lane='HR'
        )

        self.assertTrue(result)
        mock_post.assert_called_once()
```

---

## Verification Commands

```bash
# Run all tests
./scripts/ci/run_odoo_tests.sh

# Run specific module
ODOO_MODULES=ipai_finance_ppm ./scripts/ci/run_odoo_tests.sh

# Run with coverage
WITH_COVERAGE=true ./scripts/ci/run_odoo_tests.sh

# Run by tag
TEST_TAGS="/ipai_finance_ppm" ./scripts/ci/run_odoo_tests.sh
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Tests slow down CI | Use test tags to run subsets; parallelize |
| Flaky tests | Avoid time-sensitive assertions; use relative dates |
| Test data pollution | Use TransactionCase for automatic rollback |
| External service dependencies | Mock all HTTP calls |
