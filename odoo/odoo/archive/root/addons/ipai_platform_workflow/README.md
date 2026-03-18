# IPAI Platform - Workflow Engine

## Overview

Generic workflow state machine for IPAI modules

- **Technical Name:** `ipai_platform_workflow`
- **Version:** 18.0.1.0.0
- **Category:** Technical
- **License:** LGPL-3
- **Author:** IPAI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Platform Workflow Engine
=============================

Provides a generic, reusable workflow state machine for IPAI modules.

Features:
- Configurable state definitions
- Transition rules with conditions
- Notification hooks (email, Mattermost)
- Audit trail integration

This module serves as the foundation for approval workflows,
status tracking, and process automation across all IPAI modules.

## Functional Scope

### Data Models

- **ipai.workflow.mixin** (AbstractModel)
  - IPAI Workflow Mixin
  - Fields: 3 defined

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_platform_workflow --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_platform_workflow --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

*No specific security configuration.*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_workflow'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_platform_workflow")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/workflow_views.xml`

## Static Validation Status

- Passed: 4
- Warnings: 1
- Failed: 0
