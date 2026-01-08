# -*- coding: utf-8 -*-
{
    "name": "IPAI Approvals (Enterprise Parity)",
    "summary": "Generic approval workflow system - Enterprise Approvals parity for Odoo CE",
    "description": """
IPAI Approvals - Enterprise Parity Module
==========================================

Provides a generic approval workflow system that mirrors Odoo Enterprise's
Approvals module functionality for Odoo CE 18.

Features:
- Approval Types: Define approval workflows for any model
- Approval Requests: Create requests that follow the defined workflow
- Multi-level Approvers: Configure multiple approval levels
- Minimum Approvers: Require N approvals before proceeding
- Delegation: Approvers can delegate to others
- Email Notifications: Automatic notifications for pending approvals
- Activity Integration: Creates activities for pending approvals
- Audit Trail: Full history via mail.thread

Supported Models (out of box):
- Purchase Orders
- Sale Orders
- Account Moves (Invoices/Bills)
- Expense Reports
- Custom (any res_model)
    """,
    "version": "18.0.1.0.0",
    "category": "Human Resources/Approvals",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["base", "mail", "hr"],
    "data": [
        "security/approvals_security.xml",
        "security/ir.model.access.csv",
        "data/approval_data.xml",
        "data/mail_templates.xml",
        "views/approval_type_views.xml",
        "views/approval_request_views.xml",
        "views/approval_approver_views.xml",
        "views/menu.xml",
        "wizard/approval_delegate_views.xml",
    ],
    "demo": [
        "demo/approval_demo.xml",
    ],
    "application": True,
    "installable": True,
}
