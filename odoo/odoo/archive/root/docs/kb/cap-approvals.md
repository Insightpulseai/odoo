# Approval Workflows

> **Slug**: `approvals`
> **Module**: `ipai_approvals`

## Overview

Generic approval workflow system that mirrors Odoo Enterprise's Approvals module functionality for Odoo CE 18.

## Features

- **Approval Types**: Define approval workflows for any model
  - User-based approvers
  - Group-based approvers
  - Manager chain approvers

- **Approval Requests**: Full lifecycle management
  - Draft → Pending → Approved/Rejected
  - Multi-level approvals
  - Minimum approver requirements
  - Amount-based auto-approval thresholds

- **Delegation**: Approvers can delegate to others

- **Notifications**: Email notifications for pending/approved/rejected

- **Activity Integration**: Creates activities for pending approvals

- **Audit Trail**: Full history via mail.thread

## Models

- `ipai.approval.type` - Approval type definitions
- `ipai.approval.request` - Approval requests with workflow
- `ipai.approval.approver` - Per-approver tracking

## Supported Models

Out of the box:
- Purchase Orders
- Sale Orders
- Account Moves (Invoices/Bills)
- Expense Reports
- Custom (any res_model)

## Usage

### Creating a Request

1. Go to **Approvals → My Requests**
2. Click **Create**
3. Select the **Approval Type**
4. Fill in details and **Submit**

### Approving

1. Go to **Approvals → To Approve**
2. Open a pending request
3. Click **Approve** or **Reject**

### Delegating

1. Open a request where you're an approver
2. Click **Delegate**
3. Select the user to delegate to

## Configuration

See [Configuration → Approvals](Configuration#approvals) for setup instructions.

## Security Groups

- **Approvals / User**: Create requests, see own, approve assigned
- **Approvals / Manager**: Full access within company

## Dependencies

- `base`
- `mail`
- `hr` (for manager chain)

## Related Modules

- `ipai_ai_agents` - AI-powered approval assistance
- `ipai_finance_close_automation` - Finance close approvals
