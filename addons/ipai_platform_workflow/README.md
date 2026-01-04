# IPAI Platform - Workflow Engine

## 1. Overview
Generic workflow state machine for IPAI modules

**Technical Name**: `ipai_platform_workflow`
**Category**: Technical
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

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
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `my.model`
- `ipai.workflow.mixin`

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
odoo-bin -d <db> -i ipai_platform_workflow --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_platform_workflow --stop-after-init
```