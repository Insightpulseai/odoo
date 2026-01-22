# Enterprise Parity Task Checklist

**Legend:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Blocked

---

## Phase 1: Foundation

### Supabase Schema
- ⬜ Create `ops` schema
- ⬜ Create `agent_runs` table with indexes
- ⬜ Create `agent_audit_log` table
- ⬜ Create `tool_permissions` table
- ⬜ Create `portal_sessions` table
- ⬜ Configure RLS policies
- ⬜ Create Edge Functions for portal API
- ⬜ Test schema with sample data

### n8n Infrastructure
- ⬜ Deploy n8n instance (compose)
- ⬜ Configure Odoo XML-RPC credentials
- ⬜ Configure Supabase credentials
- ⬜ Create webhook receiver templates
- ⬜ Create base error handling workflow
- ⬜ Document workflow patterns

### Design System
- ⬜ Create `ipai_design_system` module scaffold
- ⬜ Extract Odoo SCSS variables
- ⬜ Create CSS custom properties export
- ⬜ Create JSON token export
- ⬜ Apply tokens to Odoo theme
- ⬜ Document token usage

### MCP Layer
- ⬜ Register `odoo_search` tool
- ⬜ Register `odoo_create` tool
- ⬜ Register `odoo_update` tool
- ⬜ Register `supabase_query` tool
- ⬜ Implement permission checking
- ⬜ Implement audit logging
- ⬜ Write tool tests

### CI/CD
- ⬜ Create `check_expense_parity.sh`
- ⬜ Create `check_procurement_parity.sh`
- ⬜ Create `check_equipment_parity.sh`
- ⬜ Create `check_project_parity.sh`
- ⬜ Create `check_copilot_parity.sh`
- ⬜ Create `check_bi_parity.sh`
- ⬜ Add parity gate to CI workflow

---

## Phase 2: Expense & Travel (Concur Parity)

### Core Expense
- ✅ Verify `hr_expense` installed
- ⬜ Configure expense categories (PH-specific)
- ⬜ Create `ipai.expense.policy` model
- ⬜ Implement policy rule engine
- ⬜ Create policy violation alerts
- ⬜ Configure multi-level approval
- ⬜ Test approval delegation

### Travel Request
- ⬜ Create `ipai.travel.request` model
- ⬜ Create travel request form view
- ⬜ Link travel to expense reports
- ⬜ Implement travel approval workflow
- ⬜ Test budget tracking

### OCR Integration
- ⬜ Select OCR provider (Google/AWS/Azure)
- ⬜ Create `ipai_expense_ocr` module
- ⬜ Build OCR API integration
- ⬜ Create n8n `expense_ocr_ingest` workflow
- ⬜ Map OCR fields to expense lines
- ⬜ Test accuracy

### Reimbursement
- ⬜ Install `account_payment_group`
- ⬜ Configure payment methods
- ⬜ Create batch grouping logic
- ⬜ Create n8n `reimbursement_batch` workflow
- ⬜ Test GL posting
- ⬜ Create reimbursement reports

### Mobile App
- ⬜ Create PWA project structure
- ⬜ Implement expense capture form
- ⬜ Implement camera capture
- ⬜ Implement offline storage
- ⬜ Create sync mechanism
- ⬜ Test offline/online scenarios

### BIR Compliance
- ✅ `ipai_finance_bir_compliance` module exists
- ⬜ Configure 2307 withholding tax
- ⬜ Create SAWT generation
- ⬜ Create QAP generation
- ⬜ Test against BIR formats
- ⬜ Document compliance procedures

---

## Phase 3: Procurement (Ariba SRM Parity)

### Supplier Management
- ⬜ Add KYC document fields to partner
- ⬜ Create supplier status workflow
- ⬜ Implement supplier scoring
- ⬜ Create supplier dashboard
- ⬜ Test KYC document tracking

### Purchase Workflow
- ⬜ Install `purchase_requisition`
- ⬜ Configure requisition categories
- ⬜ Create RFQ template
- ⬜ Implement vendor selection
- ⬜ Test requisition to PO flow

### Approval Matrix
- ⬜ Create `ipai.approval.matrix` model
- ⬜ Implement amount thresholds
- ⬜ Implement category rules
- ⬜ Implement cost center rules
- ⬜ Create n8n `po_approval` workflow
- ⬜ Test escalation

### Receiving & Matching
- ⬜ Configure goods receipt
- ⬜ Install `purchase_stock_picking_invoice_link`
- ⬜ Implement 3-way match logic
- ⬜ Create n8n `invoice_match` workflow
- ⬜ Handle match exceptions
- ⬜ Test matching scenarios

### Vendor Portal
- ⬜ Create Next.js portal project
- ⬜ Implement Supabase auth
- ⬜ Create PO list view
- ⬜ Create PO detail view
- ⬜ Create invoice submission form
- ⬜ Test portal workflow

### Audit Trail
- ⬜ Install `auditlog` OCA module
- ⬜ Configure audited models
- ⬜ Create audit reports
- ⬜ Test audit completeness
- ⬜ Document retention policy

---

## Phase 4: Equipment (Cheqroom Parity)

### Equipment Catalog
- ⬜ Create equipment product category
- ⬜ Configure equipment attributes
- ⬜ Create equipment locations
- ⬜ Import equipment master data
- ⬜ Test search and filtering

### Booking System
- ⬜ Create `ipai.equipment.booking` model
- ⬜ Create calendar view
- ⬜ Implement conflict detection
- ⬜ Create booking form
- ⬜ Create n8n `booking_confirm` workflow
- ⬜ Test booking scenarios

### Check-out/in
- ⬜ Configure internal transfer route
- ⬜ Create check-out wizard
- ⬜ Create check-in wizard
- ⬜ Create `ipai.equipment.condition` model
- ⬜ Create `ipai.custody.log` model
- ⬜ Create n8n `checkout_notify` workflow

### QR Integration
- ⬜ Install `stock_barcodes`
- ⬜ Generate QR codes for equipment
- ⬜ Create mobile scanning view
- ⬜ Test QR workflows

### Maintenance
- ⬜ Install `maintenance` module
- ⬜ Link to equipment products
- ⬜ Create maintenance schedules
- ⬜ Create n8n `maintenance_schedule` workflow
- ⬜ Test maintenance workflow

---

## Phase 5: Work Management (Planner Parity)

### Project Configuration
- ⬜ Configure project stages
- ⬜ Install `project_task_dependency`
- ⬜ Install `project_task_checklist`
- ⬜ Configure task templates
- ⬜ Test Kanban board

### Plan Templates
- ⬜ Create `ipai.plan.template` model
- ⬜ Create template items model
- ⬜ Implement template instantiation
- ⬜ Create n8n `plan_instantiate` workflow
- ⬜ Test template scenarios

### Recurring Tasks
- ⬜ Install `project_task_recurrent`
- ⬜ Configure recurrence patterns
- ⬜ Create n8n `task_generate` workflow
- ⬜ Test recurrence generation

### Notifications
- ⬜ Create n8n `task_assign` workflow
- ⬜ Create n8n `due_reminder` workflow
- ⬜ Configure email templates
- ⬜ Configure Mattermost integration
- ⬜ Test notification delivery

---

## Phase 6: Copilot (Joule Parity)

### RAG Setup
- ⬜ Select embedding model
- ⬜ Create document ingestion pipeline
- ⬜ Index Odoo records
- ⬜ Index documentation
- ⬜ Test retrieval accuracy

### Query Interface
- ⬜ Create chat UI component
- ⬜ Implement conversation state
- ⬜ Create prompt templates
- ⬜ Implement response streaming
- ⬜ Test query scenarios

### MCP Tools (Extended)
- ⬜ Register `odoo_action` tool
- ⬜ Register `docs_search` tool
- ⬜ Register `send_notification` tool
- ⬜ Register `request_approval` tool
- ⬜ Implement error recovery
- ⬜ Test tool execution

### Action Execution
- ⬜ Implement write confirmation flow
- ⬜ Implement approval gating
- ⬜ Create pending approvals view
- ⬜ Create approval workflow
- ⬜ Test sensitive actions

### Audit & Explanation
- ⬜ Log all tool calls to Supabase
- ⬜ Generate explanations
- ⬜ Create audit dashboard
- ⬜ Create explanation view
- ⬜ Test audit completeness

### Role-Based Access
- ⬜ Configure tool permissions per role
- ⬜ Implement permission checking
- ⬜ Test role scenarios
- ⬜ Document role capabilities

---

## Phase 7: BI & Analytics (Superset Parity)

### Analytics Schema
- ⬜ Create `analytics` schema
- ⬜ Design expense facts/dimensions
- ⬜ Design procurement facts/dimensions
- ⬜ Design equipment facts/dimensions
- ⬜ Design project facts/dimensions
- ⬜ Create ETL jobs
- ⬜ Test data freshness

### Superset Configuration
- ⬜ Create database connection
- ⬜ Import datasets
- ⬜ Configure RLS rules
- ⬜ Certify datasets
- ⬜ Test permissions

### Dashboards
- ⬜ Create expense analytics dashboard
- ⬜ Create procurement analytics dashboard
- ⬜ Create equipment utilization dashboard
- ⬜ Create project workload dashboard
- ⬜ Create executive summary dashboard
- ⬜ Test all dashboards

### Embedding
- ⬜ Configure guest tokens
- ⬜ Create Odoo embed action
- ⬜ Test embedded dashboards
- ⬜ Document embedding

---

## Phase 8: Integration & Polish

### Integration Testing
- ⬜ Expense end-to-end test
- ⬜ Procurement end-to-end test
- ⬜ Equipment end-to-end test
- ⬜ Project end-to-end test
- ⬜ Copilot end-to-end test
- ⬜ Cross-capability test
- ⬜ Error recovery test

### Performance
- ⬜ Load test Odoo
- ⬜ Load test Superset
- ⬜ Load test n8n
- ⬜ Optimize slow queries
- ⬜ Implement caching
- ⬜ Document benchmarks

### UX Polish
- ⬜ Apply design tokens consistently
- ⬜ Verify mobile responsiveness
- ⬜ Accessibility audit
- ⬜ Fix UX issues
- ⬜ User testing

### Documentation
- ⬜ Create user guide - Expense
- ⬜ Create user guide - Procurement
- ⬜ Create user guide - Equipment
- ⬜ Create user guide - Projects
- ⬜ Create user guide - Copilot
- ⬜ Create admin guide
- ⬜ Create API documentation

### Training
- ⬜ Create training slides
- ⬜ Record demo videos
- ⬜ Create FAQ
- ⬜ Conduct training sessions
- ⬜ Gather feedback

---

## Summary

| Phase | Total Tasks | Complete | In Progress | Blocked |
|-------|-------------|----------|-------------|---------|
| Foundation | 32 | 0 | 0 | 0 |
| Expense | 36 | 2 | 0 | 0 |
| Procurement | 30 | 0 | 0 | 0 |
| Equipment | 25 | 0 | 0 | 0 |
| Work Mgmt | 18 | 0 | 0 | 0 |
| Copilot | 30 | 0 | 0 | 0 |
| BI | 20 | 0 | 0 | 0 |
| Polish | 25 | 0 | 0 | 0 |
| **Total** | **216** | **2** | **0** | **0** |

---

*Last Updated: 2026-01-22*
