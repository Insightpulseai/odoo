# Enterprise Parity PRD

**Product Requirements Document**
**Version:** 1.0
**Date:** 2026-01-22

---

## 1. Overview

### 1.1 Purpose

Deliver enterprise-grade capabilities equivalent to SAP Concur, SAP Ariba SRM, Cheqroom, Microsoft Planner, SAP Joule, and Superset using a unified Odoo CE + OCA + IPAI stack with Supabase, n8n, and MCP integration.

### 1.2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Feature parity | 90%+ of core features | Feature checklist completion |
| User satisfaction | 4.0/5.0 | User surveys |
| Processing time | ≤ 2x commercial product | Performance benchmarks |
| Uptime | 99.5% | Monitoring |
| Audit compliance | 100% | BIR audit pass |

---

## 2. Capabilities

### 2.1 Expense & Travel (Concur Parity)

**User Stories:**

1. As an employee, I can capture expenses via mobile with receipt photo
2. As an employee, I can create travel requests with estimated costs
3. As a manager, I can approve/reject expense reports with comments
4. As finance, I can batch reimbursements and post to GL
5. As compliance, I can generate BIR-compliant reports

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| EXP-001 | Expense line item capture with category, amount, date, receipt | P0 | `hr_expense` |
| EXP-002 | Receipt OCR to auto-populate expense fields | P1 | `ipai_expense_ocr` |
| EXP-003 | Policy rules: limits by category, per diem rates | P0 | `ipai_expense_policy` |
| EXP-004 | Multi-level approval workflow | P0 | `hr_expense` + OCA |
| EXP-005 | Travel request with itinerary and budget | P1 | `ipai_travel_request` |
| EXP-006 | Reimbursement batch processing | P0 | `account_payment_group` |
| EXP-007 | Mobile app for expense capture | P1 | PWA + Supabase |
| EXP-008 | BIR reporting extracts | P0 | `ipai_finance_bir_compliance` |

### 2.2 Procurement (Ariba SRM Parity)

**User Stories:**

1. As a requester, I can create purchase requisitions
2. As a buyer, I can convert requisitions to RFQs and POs
3. As a vendor, I can view POs and submit invoices via portal
4. As AP, I can match invoices to POs and receipts (3-way match)
5. As compliance, I can audit all procurement activities

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| PRC-001 | Supplier master with KYC documents | P0 | `res.partner` + docs |
| PRC-002 | Purchase requisition workflow | P1 | `purchase_requisition` |
| PRC-003 | RFQ to PO conversion | P0 | `purchase` |
| PRC-004 | Approval matrix by amount/category | P0 | `ipai_approval_matrix` |
| PRC-005 | Goods receipt against PO | P0 | `stock` |
| PRC-006 | 3-way match (bill/receipt/PO) | P0 | `purchase_stock_picking_invoice_link` |
| PRC-007 | Vendor self-service portal | P1 | Supabase + Next.js |
| PRC-008 | Complete audit trail | P0 | `auditlog` |

### 2.3 Equipment Booking (Cheqroom Parity)

**User Stories:**

1. As an employee, I can browse available equipment and make reservations
2. As a studio tech, I can check out equipment to borrowers
3. As a studio tech, I can log equipment condition on return
4. As a manager, I can view equipment utilization reports
5. As maintenance, I can schedule and track equipment maintenance

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| EQP-001 | Equipment catalog with categories and attributes | P0 | `product.product` |
| EQP-002 | Availability calendar view | P0 | `ipai_equipment_booking` |
| EQP-003 | Reservation with conflict detection | P0 | `ipai_equipment_booking` |
| EQP-004 | Check-out/check-in workflow | P0 | `stock` internal moves |
| EQP-005 | Condition logging on return | P0 | `ipai_equipment_condition` |
| EQP-006 | QR/barcode scanning | P1 | `stock_barcodes` |
| EQP-007 | Maintenance scheduling | P1 | `maintenance` |
| EQP-008 | Custody chain audit trail | P0 | `ipai_custody_log` |

### 2.4 Work Management (Planner Parity)

**User Stories:**

1. As a project manager, I can create projects with task boards
2. As a team lead, I can create plan templates for recurring workflows
3. As a team member, I can view my tasks and update status
4. As a manager, I can see team workload and deadlines
5. As an admin, I can set up recurring task generation

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| WRK-001 | Kanban board with customizable stages | P0 | `project` |
| WRK-002 | Task dependencies | P1 | `project_task_dependency` |
| WRK-003 | Plan templates with task checklists | P0 | `ipai_plan_template` |
| WRK-004 | Recurring task generation | P1 | `project_task_recurrent` |
| WRK-005 | Resource allocation view | P2 | `project_resource_calendar` |
| WRK-006 | Due date reminders | P0 | n8n workflow |
| WRK-007 | Workload dashboard | P1 | Superset |
| WRK-008 | Schedule/timeline view | P2 | `project_timeline` |

### 2.5 Embedded Copilot (Joule Parity)

**User Stories:**

1. As a user, I can ask questions about my data in natural language
2. As a user, I can request the copilot to perform actions
3. As a manager, I can see what actions the copilot performed
4. As an admin, I can configure which tools agents can access
5. As compliance, I can audit all agent activities

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| COP-001 | Natural language query interface | P0 | MCP + RAG |
| COP-002 | Action execution via Odoo RPC | P0 | MCP tools |
| COP-003 | Explanation of recommendations | P1 | Agent reasoning |
| COP-004 | Full audit logging | P0 | `ops.agent_audit_log` |
| COP-005 | Role-based tool permissions | P0 | `ops.tool_permissions` |
| COP-006 | Approval gating for sensitive actions | P0 | `ops.pending_approvals` |
| COP-007 | Context-aware suggestions | P2 | RAG + embeddings |
| COP-008 | Multi-turn conversation | P2 | Session state |

### 2.6 BI & Analytics (Superset Parity)

**User Stories:**

1. As an analyst, I can explore data and create charts
2. As a manager, I can view dashboards relevant to my role
3. As an executive, I can see KPI summaries
4. As a data steward, I can certify datasets
5. As an admin, I can configure row-level security

**Requirements:**

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| BIA-001 | Certified datasets for key domains | P0 | Superset datasets |
| BIA-002 | Pre-built dashboards | P0 | Superset dashboards |
| BIA-003 | Self-service exploration | P1 | Superset SQL Lab |
| BIA-004 | Row-level security | P0 | Superset RLS |
| BIA-005 | Embedded dashboards in Odoo | P2 | Superset embed |
| BIA-006 | Scheduled reports | P1 | Superset alerts |
| BIA-007 | Metric definitions (semantic layer) | P1 | `ipai_metric_definition` |
| BIA-008 | Analytics schema (not direct Odoo) | P0 | `analytics.*` schema |

---

## 3. Integration Requirements

### 3.1 Odoo ↔ Supabase

- Event-driven sync via n8n webhooks
- Supabase Edge Functions for portal API
- Shared auth via JWT tokens

### 3.2 Odoo ↔ n8n

- Odoo webhooks trigger n8n workflows
- n8n calls Odoo XML-RPC for actions
- Credential management via n8n secrets

### 3.3 Odoo ↔ Superset

- Analytics schema populated by ETL/CDC
- No direct Odoo table access from Superset
- RLS aligned to Odoo permission groups

### 3.4 MCP Layer

- Tools registered in `mcp/servers/`
- Each tool has permission requirements
- All tool calls logged to Supabase

---

## 4. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | API < 500ms read, < 2000ms write |
| Availability | 99.5% uptime |
| Security | OWASP Top 10 compliance |
| Scalability | Support 500 concurrent users |
| Backup | Daily backups, 30-day retention |
| Compliance | BIR, PEZA, data privacy |

---

## 5. Acceptance Criteria

1. All P0 requirements implemented and tested
2. CI gates pass for all capabilities
3. User acceptance testing complete
4. Documentation published
5. Training materials delivered
6. Production deployment verified
