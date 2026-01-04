# IPAI CRM - Pipeline Clone

## 1. Overview
Salesforce-like CRM pipeline experience

**Technical Name**: `ipai_crm_pipeline`
**Category**: Sales/CRM
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

IPAI CRM Pipeline Clone
=======================

Delivers a Salesforce-like CRM pipeline experience on Odoo CRM.

Capability ID: crm.pipeline.board (P0)

Features:
- Enhanced kanban board with stage rules
- Quick action buttons (log call, schedule meeting, send email)
- Activity timeline improvements
- Stage validation rules
- Role-based dashboards

This module targets feature parity with Salesforce Sales Cloud
pipeline functionality while leveraging the IPAI design system.
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `crm`
- `mail`
- `ipai_platform_workflow`
- `ipai_platform_theme`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- No explicit new models detected (may inherit existing).

## 6. User Interface
- **Views**: 3 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_crm_pipeline --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_crm_pipeline --stop-after-init
```