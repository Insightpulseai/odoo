# Target Capability Suite

**Version:** 1.0
**Date:** 2026-01-22
**Status:** Active Development

---

## Overview

This document defines the enterprise capabilities being implemented through the Odoo CE + OCA + IPAI stack, replacing commercial SaaS products with a unified, self-hosted solution.

## Target Products → IPAI Replacements

| Target Product | Capability Domain | IPAI Replacement Pattern |
|----------------|-------------------|--------------------------|
| **SAP Concur** | Expense + Travel | Odoo Expenses + Approvals + IPAI policy/PH compliance |
| **SAP Ariba SRM** | Procurement + Supplier Mgmt | Odoo Purchase + Inventory + IPAI supplier controls |
| **Cheqroom** | Equipment Booking | Odoo Inventory + IPAI reservation model + QR flows |
| **Microsoft Planner** | Work Management | Odoo Project + OCA queue + IPAI plan templates |
| **SAP Joule** | Embedded Copilot | MCP tools + RAG + action execution + audit |
| **Superset** | BI + Analytics | Superset on curated schema + RLS alignment |

## Capability Domains

### 1. Expense & Travel Management (Concur-class)

**Features Required:**
- Policy rules (limits, per diems, category caps)
- Multi-step approvals with delegation + SLA
- Receipt OCR ingestion → expense line suggestions
- Reimbursement batching → accounting entries
- PH-specific required fields + reporting extracts
- Mobile capture + offline sync

**Implementation:**
- `hr_expense` (CE) + OCA enhancements
- `ipai_expense_policy` (custom policy engine)
- `ipai_finance_bir_compliance` (PH tax compliance)
- n8n: approval escalations, reimbursement workflows

### 2. Procurement & Supplier Management (Ariba SRM-class)

**Features Required:**
- Supplier master + KYC docs + status (active/suspended)
- RFQ → PO → receiving → 3-way match (bill/receipt/PO)
- Approval matrices by amount/category/cost center
- Vendor portal for self-service
- Audit trail for every state change

**Implementation:**
- `purchase` + `stock` (CE)
- `ipai_supplier_portal` (vendor self-service)
- `ipai_procurement_controls` (approval matrix)
- Supabase: vendor portal API + document storage
- n8n: vendor onboarding, invoice matching

### 3. Equipment Booking & Inventory (Cheqroom-class)

**Features Required:**
- Asset catalog + location + availability
- Reservations (calendar), checkout/in, condition logs
- Maintenance schedules + incident tickets
- Barcode/QR flows + custody chain
- Mobile app for field operations

**Implementation:**
- `stock` + `maintenance` (CE)
- `ipai_equipment_booking` (reservation model)
- `ipai_asset_tracking` (QR/barcode integration)
- Supabase: mobile API + offline sync

### 4. Work Management (Planner-class)

**Features Required:**
- Plan templates → instantiated checklists
- Board (bucket), grid, schedule views
- Recurrence + automation
- Reporting (burnup, workload, SLA)
- Team assignments + notifications

**Implementation:**
- `project` (CE) + OCA `project_task_dependency`
- `ipai_plan_templates` (template instantiation)
- `ipai_project_automation` (scheduled tasks)
- n8n: SLA alerts, workload notifications

### 5. Embedded Copilot (Joule-class)

**Features Required:**
- "Ask" (RAG over Odoo/Supabase data)
- "Act" (execute actions via RPC)
- "Explain" (why recommendations made)
- "Audit" (full provenance logging)
- Tool permissions, approval gating for writes

**Implementation:**
- MCP layer: tool definitions for Odoo/Supabase/Superset
- `ipai_ai_agents` (agent orchestration)
- `ipai_copilot` (UI integration)
- Supabase: agent_runs table, audit log

### 6. BI & Analytics (Superset-class)

**Features Required:**
- Certified datasets + metric registry
- RLS alignment to Odoo org model
- Self-service exploration
- Scheduled reports + alerts
- Embedded dashboards

**Implementation:**
- Apache Superset on curated analytics schema
- CDC/ETL to analytics warehouse
- `ipai_bi_connector` (metric definitions)
- Row-level security aligned to Odoo permissions

---

## Implementation Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Odoo Web    │   Portals    │   Mobile     │   Superset    │
│  (Backend)   │  (Supabase)  │  (PWA/App)   │   (BI)        │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
┌──────┴──────────────┴──────────────┴───────────────┴───────┐
│                    MCP Tool Layer                           │
│  (Odoo RPC, Supabase RPC, Superset API, Storage, Email)    │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
┌──────┴───────┐ ┌────┴────┐ ┌──────┴──────┐
│   Odoo CE    │ │ Supabase │ │     n8n     │
│  (SoR/Txn)   │ │ (Ops Hub)│ │ (Orchestr.) │
└──────────────┘ └──────────┘ └─────────────┘
```

---

## Parity Gates

Each capability must pass these gates before declaring parity:

1. **Functional Parity**: All core features implemented
2. **UX Parity**: Design system tokens applied consistently
3. **Performance Parity**: Response times within 2x of target
4. **Security Parity**: Same or better access controls
5. **Audit Parity**: Complete trail for compliance
6. **CI Gate**: Automated tests prevent regression

---

See: [IMPLEMENTATION_MAP.md](./IMPLEMENTATION_MAP.md) for detailed mapping.
