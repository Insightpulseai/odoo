# Tasks – InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

**Product:** Documentation handbook
**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## Epics

| Epic ID | Title | Description |
|---------|-------|-------------|
| `EPIC-DOC-FIN` | Finance docs – Odoo CE + Supabase | Complete finance workspace documentation |
| `EPIC-DOC-PPM` | PPM docs – Projects + Timesheets | Complete PPM workspace documentation |
| `EPIC-DOC-HR` | HR docs – People Ops | Complete HR workspace documentation |
| `EPIC-DOC-RET` | Retail docs – Scout + SariCoach | Complete retail workspace documentation |
| `EPIC-DOC-EQP` | Equipment docs – Cheqroom Parity | Complete equipment workspace documentation |
| `EPIC-DOC-AI` | AI Workbench docs | Document AI/agent integration |
| `EPIC-SUPA-MAP` | Supabase schema mapping | Document all Supabase schemas |
| `EPIC-N8N-BP` | n8n workflow blueprints | Document all automation workflows |
| `EPIC-RAG` | RAG indexing | Set up handbook as RAG corpus |
| `EPIC-DEV` | Developer Guide | Development standards documentation |
| `EPIC-OPS` | DevOps documentation | Infrastructure and deployment docs |

---

## Task Inventory

### EPIC-DOC-FIN: Finance Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-FIN-01 | Draft Finance Overview page | docs | EPIC-DOC-FIN | Module intro, differentiators table | M | P0 |
| T-FIN-02 | Draft Chart of Accounts page | docs | EPIC-DOC-FIN | PH localization, setup steps | M | P0 |
| T-FIN-03 | Draft Customer Invoicing page | docs | EPIC-DOC-FIN | Workflow, step-by-step, n8n triggers | L | P0 |
| T-FIN-04 | Draft Vendor Bills page | docs | EPIC-DOC-FIN | AP workflow, approval patterns | M | P0 |
| T-FIN-05 | Draft Expense Management page | docs | EPIC-DOC-FIN | TE-Cheq integration, OCR | L | P0 |
| T-FIN-06 | Draft Bank Reconciliation page | docs | EPIC-DOC-FIN | AI-assisted matching | M | P1 |
| T-FIN-07 | Draft Month-End Close page | docs | EPIC-DOC-FIN | Checklist, n8n automation | M | P1 |
| T-FIN-08 | Document finance.* Supabase schema | docs | EPIC-DOC-FIN | ERD, column definitions | M | P0 |
| T-FIN-09 | Document expense.* Supabase schema | docs | EPIC-DOC-FIN | ERD, column definitions | M | P0 |
| T-FIN-10 | Create Finance UAT checklist | docs | EPIC-DOC-FIN | Test scenarios | S | P1 |

### EPIC-DOC-PPM: PPM Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-PPM-01 | Draft PPM Overview page | docs | EPIC-DOC-PPM | Module intro, Clarity PPM comparison | M | P0 |
| T-PPM-02 | Draft Portfolio Hierarchy page | docs | EPIC-DOC-PPM | Portfolio → Program → Project setup | L | P0 |
| T-PPM-03 | Draft WBS Management page | docs | EPIC-DOC-PPM | WBS codes, task hierarchy | M | P0 |
| T-PPM-04 | Draft Timesheet Entry page | docs | EPIC-DOC-PPM | Entry, approval workflow | L | P0 |
| T-PPM-05 | Draft Budget Tracking page | docs | EPIC-DOC-PPM | Budget setup, variance monitoring | M | P1 |
| T-PPM-06 | Draft Rate Cards page | docs | EPIC-DOC-PPM | Rate card config, sync patterns | M | P1 |
| T-PPM-07 | Document projects.* Supabase schema | docs | EPIC-DOC-PPM | ERD, column definitions | M | P0 |
| T-PPM-08 | Document rates.* Supabase schema | docs | EPIC-DOC-PPM | ERD, column definitions | S | P1 |
| T-PPM-09 | Create PPM UAT checklist | docs | EPIC-DOC-PPM | Test scenarios | S | P1 |

### EPIC-DOC-HR: HR Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-HR-01 | Draft HR Overview page | docs | EPIC-DOC-HR | Module intro, OCA modules | M | P1 |
| T-HR-02 | Draft Employee Master page | docs | EPIC-DOC-HR | Employee data management | M | P1 |
| T-HR-03 | Draft Recruitment page | docs | EPIC-DOC-HR | Applicant workflow | M | P2 |
| T-HR-04 | Draft Time Off page | docs | EPIC-DOC-HR | Leave management, approval | M | P1 |
| T-HR-05 | Draft Attendance page | docs | EPIC-DOC-HR | Check-in/out tracking | S | P2 |
| T-HR-06 | Document core.employees Supabase sync | docs | EPIC-DOC-HR | Sync patterns | S | P1 |

### EPIC-DOC-RET: Retail Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-RET-01 | Draft Retail Overview page | docs | EPIC-DOC-RET | POS + Scout intro | M | P1 |
| T-RET-02 | Draft POS Configuration page | docs | EPIC-DOC-RET | Store setup, payment methods | M | P1 |
| T-RET-03 | Draft Scout Pipeline page | docs | EPIC-DOC-RET | Ingestion workflow | L | P0 |
| T-RET-04 | Draft Medallion Architecture page | docs | EPIC-DOC-RET | Bronze/Silver/Gold ETL | L | P0 |
| T-RET-05 | Draft SariCoach page | docs | EPIC-DOC-RET | AI coaching patterns | L | P1 |
| T-RET-06 | Document scout_* Supabase schemas | docs | EPIC-DOC-RET | All medallion schemas | L | P0 |

### EPIC-DOC-EQP: Equipment Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-EQP-01 | Draft Equipment Overview page | docs | EPIC-DOC-EQP | Cheqroom parity intro | M | P2 |
| T-EQP-02 | Draft Asset Registry page | docs | EPIC-DOC-EQP | Asset management | M | P2 |
| T-EQP-03 | Draft Booking Workflow page | docs | EPIC-DOC-EQP | Check-out/in process | M | P2 |
| T-EQP-04 | Draft Maintenance page | docs | EPIC-DOC-EQP | Maintenance scheduling | S | P2 |
| T-EQP-05 | Document equipment.* Supabase schema | docs | EPIC-DOC-EQP | ERD, sync patterns | M | P2 |

### EPIC-DOC-AI: AI Workbench Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-AI-01 | Draft AI Overview page | docs | EPIC-DOC-AI | Engine architecture | M | P1 |
| T-AI-02 | Draft Engine Registry page | docs | EPIC-DOC-AI | Engine specs, YAML format | M | P1 |
| T-AI-03 | Draft MCP Server page | docs | EPIC-DOC-AI | MCP setup, tools | L | P1 |
| T-AI-04 | Draft RAG Pipeline page | docs | EPIC-DOC-AI | Chunking, embeddings | L | P0 |
| T-AI-05 | Draft Domain Agents page | docs | EPIC-DOC-AI | Agent configurations | M | P1 |

### EPIC-SUPA-MAP: Supabase Schema Mapping

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-SUPA-01 | Document core.* schema | docs | EPIC-SUPA-MAP | Platform schemas | M | P0 |
| T-SUPA-02 | Document saas.* schema | docs | EPIC-SUPA-MAP | Tenancy schemas | S | P0 |
| T-SUPA-03 | Document rag.* schema | docs | EPIC-SUPA-MAP | Vector store | M | P1 |
| T-SUPA-04 | Create master ERD | docs | EPIC-SUPA-MAP | Full schema diagram | L | P1 |

### EPIC-N8N-BP: n8n Workflow Blueprints

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-N8N-01 | Document wf_expense_* workflows | docs | EPIC-N8N-BP | Expense automation | M | P0 |
| T-N8N-02 | Document wf_timesheet_* workflows | docs | EPIC-N8N-BP | Timesheet automation | M | P1 |
| T-N8N-03 | Document wf_scout_* workflows | docs | EPIC-N8N-BP | Scout ingestion | M | P0 |
| T-N8N-04 | Document wf_saricoach_* workflows | docs | EPIC-N8N-BP | AI coaching | M | P1 |
| T-N8N-05 | Create workflow naming convention | docs | EPIC-N8N-BP | Standards document | S | P0 |

### EPIC-RAG: RAG Indexing

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-RAG-01 | Define chunking strategy | docs | EPIC-RAG | Token sizes, overlaps | M | P0 |
| T-RAG-02 | Define metadata schema | docs | EPIC-RAG | Tags, domains, layers | M | P0 |
| T-RAG-03 | Create indexing script | code | EPIC-RAG | Python chunker + embedder | L | P1 |
| T-RAG-04 | Create rag.doc_chunks table | code | EPIC-RAG | Supabase migration | S | P1 |
| T-RAG-05 | Test RAG retrieval | test | EPIC-RAG | Accuracy validation | M | P1 |

### EPIC-DEV: Developer Guide

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-DEV-01 | Draft OCA Standards page | docs | EPIC-DEV | Coding standards | M | P1 |
| T-DEV-02 | Draft Module Development page | docs | EPIC-DEV | ipai_* patterns | L | P1 |
| T-DEV-03 | Draft Security Patterns page | docs | EPIC-DEV | RLS, permissions | M | P1 |
| T-DEV-04 | Draft Testing Framework page | docs | EPIC-DEV | Unit/integration tests | M | P2 |
| T-DEV-05 | Draft Migration Procedures page | docs | EPIC-DEV | Schema migrations | M | P2 |

### EPIC-OPS: DevOps Documentation

| ID | Title | Type | Epic | Scope Notes | Effort | Priority |
|----|-------|------|------|-------------|--------|----------|
| T-OPS-01 | Draft DevOps Overview page | docs | EPIC-OPS | Infrastructure intro | M | P1 |
| T-OPS-02 | Draft DigitalOcean Setup page | docs | EPIC-OPS | Droplet provisioning | M | P1 |
| T-OPS-03 | Draft Docker Compose page | docs | EPIC-OPS | Container configuration | L | P1 |
| T-OPS-04 | Draft CI/CD Pipeline page | docs | EPIC-OPS | GitHub Actions | M | P1 |
| T-OPS-05 | Draft Backup/Restore page | docs | EPIC-OPS | Database backup | M | P0 |
| T-OPS-06 | Draft Security Hardening page | docs | EPIC-OPS | SSL, firewall | M | P1 |
| T-OPS-07 | Draft Monitoring page | docs | EPIC-OPS | Observability | M | P2 |

---

## Task Status Legend

| Status | Description |
|--------|-------------|
| `backlog` | Not started |
| `in_progress` | Currently being worked on |
| `review` | Pending SME review |
| `done` | Completed and approved |
| `blocked` | Waiting on dependency |

---

## Effort Estimates

| Size | Description | Hours |
|------|-------------|-------|
| S | Small - simple page or update | 2-4 |
| M | Medium - standard page with examples | 4-8 |
| L | Large - complex page with diagrams/code | 8-16 |
| XL | Extra Large - major section rewrite | 16+ |

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| P0 | Critical - blocks release |
| P1 | High - important for release |
| P2 | Medium - nice to have |
| P3 | Low - future enhancement |

---

## Sprint Assignments

### Sprint 1 (v0.1 Finance)

| Task ID | Assignee | Status |
|---------|----------|--------|
| T-FIN-01 | Doc Lead | done |
| T-FIN-02 | Doc Lead | backlog |
| T-FIN-03 | Doc Lead | backlog |
| T-FIN-04 | Doc Lead | backlog |
| T-FIN-05 | Finance SME | backlog |
| T-FIN-08 | Platform Dev | backlog |
| T-FIN-09 | Platform Dev | backlog |
| T-N8N-01 | Platform Dev | backlog |
| T-RAG-01 | AI Dev | backlog |
| T-RAG-02 | AI Dev | backlog |

### Sprint 2 (v0.1 Finance cont.)

| Task ID | Assignee | Status |
|---------|----------|--------|
| T-FIN-06 | Doc Lead | backlog |
| T-FIN-07 | Doc Lead | backlog |
| T-FIN-10 | Finance SME | backlog |
| T-RAG-03 | AI Dev | backlog |
| T-RAG-04 | Platform Dev | backlog |
| T-N8N-05 | Platform Dev | backlog |

### Sprint 3 (v0.2 PPM)

| Task ID | Assignee | Status |
|---------|----------|--------|
| T-PPM-01 | Doc Lead | backlog |
| T-PPM-02 | Doc Lead | backlog |
| T-PPM-03 | PPM SME | backlog |
| T-PPM-04 | PPM SME | backlog |
| T-PPM-07 | Platform Dev | backlog |
| T-N8N-02 | Platform Dev | backlog |

### Sprint 4 (v0.2 PPM + HR)

| Task ID | Assignee | Status |
|---------|----------|--------|
| T-PPM-05 | Doc Lead | backlog |
| T-PPM-06 | Doc Lead | backlog |
| T-PPM-08 | Platform Dev | backlog |
| T-HR-01 | Doc Lead | backlog |
| T-HR-02 | HR SME | backlog |
| T-HR-04 | HR SME | backlog |

---

## Dependencies Matrix

| Task | Depends On |
|------|------------|
| T-FIN-03 | T-FIN-08 (schema must be documented first) |
| T-FIN-05 | T-FIN-09, T-N8N-01 |
| T-PPM-04 | T-N8N-02 |
| T-RET-04 | T-RET-06 |
| T-RAG-03 | T-RAG-01, T-RAG-02 |
| T-RAG-05 | T-RAG-03, T-RAG-04 |
| T-AI-04 | T-RAG-05 |

---

## Acceptance Criteria Template

Each documentation task must meet:

1. **Content Complete**: All sections per page template filled
2. **Schema Verified**: Supabase references match actual schemas
3. **Workflow Verified**: n8n workflow IDs match actual workflows
4. **Code Tested**: Examples run on Odoo 18 CE
5. **Delta Notes**: Enterprise differences clearly marked
6. **Integration Callout**: InsightPulseAI box included
7. **RAG Metadata**: Tags applied for indexing
8. **SME Approved**: Domain expert review completed
