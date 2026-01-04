# IPAI Platform - Audit Trail

## Overview

Field-level audit trail for IPAI modules

- **Technical Name:** `ipai_platform_audit`
- **Version:** 18.0.1.0.0
- **Category:** Technical
- **License:** LGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Platform Audit Trail
=========================

Provides comprehensive audit trail functionality for IPAI modules.

Features:
- Field-level change tracking
- Configurable audit policies per model
- Change history viewer
- Retention and archival rules
- Export capabilities

This module enables compliance-grade audit logging for
sensitive data and operations across all IPAI modules.

## Functional Scope

### Data Models

- **ipai.audit.mixin** (AbstractModel)
  - IPAI Audit Mixin
  - Fields: 2 defined
- **ipai.audit.log** (Model)
  - IPAI Audit Log
  - Fields: 9 defined

### Views

- : 1
- Form: 1
- Search: 1

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_platform_audit --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_platform_audit --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*2 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_audit'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_platform_audit")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/audit_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
