# IPAI Platform - Audit Trail

## 1. Overview
Field-level audit trail for IPAI modules

**Technical Name**: `ipai_platform_audit`
**Category**: Technical
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

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
- `displayfields.Char(`
- `_recdisplay_name`
- `fieldfields.Char(`
- `ipai.audit.mixin`
- `ipai.audit.log`
- `resfields.Char(`
- `log.display(`

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
odoo-bin -d <db> -i ipai_platform_audit --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_platform_audit --stop-after-init
```