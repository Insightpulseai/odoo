# IPAI Platform - Approvals

## Overview

Role-based approval chains for IPAI modules

- **Technical Name:** `ipai_platform_approvals`
- **Version:** 18.0.1.0.0
- **Category:** Technical
- **License:** LGPL-3
- **Author:** IPAI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Platform Approvals
=======================

Provides configurable approval chain functionality for IPAI modules.

Features:
- Role-based approver lookup
- Multi-level approval chains
- Delegation configuration
- Escalation timers
- Approval audit trail

This module extends ipai_platform_workflow to add approval-specific
functionality like approver resolution, delegation, and escalation.

## Functional Scope

### Data Models

- **ipai.approval.mixin** (AbstractModel)
  - IPAI Approval Mixin
  - Fields: 5 defined

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `ipai_platform_workflow` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_platform_approvals --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_platform_approvals --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_approvals'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_platform_approvals")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/approval_views.xml`

## Static Validation Status

- Passed: 4
- Warnings: 1
- Failed: 0
