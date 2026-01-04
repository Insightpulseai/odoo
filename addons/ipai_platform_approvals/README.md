# IPAI Platform - Approvals

## 1. Overview
Role-based approval chains for IPAI modules

**Technical Name**: `ipai_platform_approvals`
**Category**: Technical
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

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
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `ipai_platform_workflow`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.approval.mixin`
- `my.model`

## 6. User Interface
- **Views**: 1 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_platform_approvals --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_platform_approvals --stop-after-init
```