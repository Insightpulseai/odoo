# Odoo Apps Inventory — Product Requirements Document

## Executive Summary

Achieve 100% feature parity with Odoo Enterprise's 55-app catalog using only open-source components: Odoo CE 18.0, OCA modules, and custom Control Room builds.

## Problem Statement

Odoo Enterprise costs $24-72/user/month and locks organizations into proprietary features. 10 critical apps (Accounting, Helpdesk, Knowledge, etc.) are Enterprise-only, creating vendor lock-in.

## Solution

Three-tier replacement strategy:
1. **Tier 1**: Install 38 CE-native apps (zero effort)
2. **Tier 2**: Deploy 9 OCA replacement modules (configuration)
3. **Tier 3**: Build 7 Control Room custom modules (development)

## Detailed Requirements

### Tier 1: CE-Native Apps (38)

| Category | Apps | Status |
|----------|------|--------|
| Core Transactional | Sales, CRM, Invoicing, Purchase, Inventory, Contacts | Install |
| Manufacturing | MRP, Maintenance | Install |
| HR | Employees, Time Off, Attendances, Recruitment, Contracts, Skills | Install |
| Finance | Expenses | Install |
| Web & Commerce | Website, eCommerce, Events, eLearning, Live Chat | Install |
| Marketing | Email Marketing, SMS Marketing, Marketing Card | Install |
| Productivity | Discuss (installed), Calendar (installed), Surveys, To-Do, Lunch | Install |
| Project | Project, POS, Restaurant POS, Repairs | Install |
| Admin | Data Recycle, Fleet | Install |

**Requirement**: Single script to install all 38 apps in correct dependency order.

### Tier 2: OCA Replacements (9)

| Enterprise App | OCA Replacement | Repo |
|----------------|-----------------|------|
| Accounting | `account-financial-tools`, `mis-builder` | OCA/account-financial-tools |
| MRP II | `mrp-multi-level`, `manufacture` | OCA/manufacture |
| Appraisal | `hr-attendance`, `hr` | OCA/hr |
| Timesheets | `project-timesheet`, `timesheet-grid` | OCA/timesheet |
| Subscriptions | `sale-subscription` | OCA/sale-workflow |
| Social Marketing | n8n social connectors | n8n-io/n8n |
| Helpdesk | `helpdesk` | OCA/helpdesk |
| Planning | `project-timeline`, `project-stage` | OCA/project |
| Quality Control | Control Room metrics + Supabase | Custom |

**Requirement**: OCA manifest with pinned versions and dependency resolution.

### Tier 3: Control Room Custom Modules (7)

#### 3.1 Knowledge Base (`control_room.kb`)

**Replaces**: Odoo Knowledge (Enterprise)

**Features**:
- Spaces and artifacts (process, data_model, business_rule)
- Persona-ranked search
- Lineage tracking (docs → code → jobs → data)
- Version history with diff view

**Schema**:
```sql
kb_spaces, kb_artifacts, kb_catalog, kb_audit
```

**API**:
```
POST/GET/PATCH/DELETE /api/v1/kb/artifacts
GET /api/v1/kb/artifacts/{id}/lineage
```

#### 3.2 Form Builder (`control_room.studio`)

**Replaces**: Odoo Studio (Enterprise)

**Features**:
- Drag-and-drop form designer
- Field types: text, number, date, select, relation, computed
- Auto-generate Odoo XML views
- Live preview

**Schema**:
```sql
studio_forms, studio_fields, studio_views, studio_audit
```

#### 3.3 E-Signature (`control_room.sign`)

**Replaces**: Odoo Sign (Enterprise)

**Features**:
- Document upload (PDF, DOCX)
- Signature placement UI
- Email workflow (send → sign → complete)
- Integration: DocuSign, SigDash, or native canvas

**Schema**:
```sql
sign_documents, sign_requests, sign_signatures, sign_audit
```

#### 3.4 Appointments (`control_room.booking`)

**Replaces**: Odoo Appointments (Enterprise)

**Features**:
- Calendar availability management
- Booking links with configurable durations
- Email/SMS notifications
- Timezone handling

**Schema**:
```sql
booking_calendars, booking_slots, booking_appointments, booking_audit
```

#### 3.5 Field Service (`control_room.fsm`)

**Replaces**: Odoo Field Service (Enterprise)

**Features**:
- Job dispatch control panel
- Technician assignment with skills matching
- Route optimization (via n8n + Google Maps)
- Mobile check-in/out

**Schema**:
```sql
fsm_jobs, fsm_technicians, fsm_skills, fsm_routes, fsm_audit
```

#### 3.6 Barcode Scanner (`control_room.barcode`)

**Replaces**: Odoo Barcode (Enterprise)

**Features**:
- Mobile camera barcode scanning
- Inventory operations: receive, pick, transfer
- Batch scanning mode
- Offline queue with sync

**Schema**:
```sql
barcode_scans, barcode_operations, barcode_queue, barcode_audit
```

#### 3.7 Mobile API (`control_room.mobile`)

**Replaces**: Odoo Android & iPhone (Enterprise)

**Features**:
- REST API for all Control Room modules
- JWT authentication with refresh tokens
- Push notification support (FCM/APNS)
- Offline-first data sync

**API**:
```
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET /api/v1/sync/delta?since={timestamp}
POST /api/v1/sync/push
```

## Non-Functional Requirements

### Performance
- API response time: < 200ms (p95)
- Dashboard load: < 2s
- Barcode scan to confirm: < 500ms

### Security
- All endpoints require JWT authentication
- Row-level security in Supabase
- Audit logging for all mutations
- GDPR-compliant data handling

### Scalability
- Support 1000 concurrent users
- Handle 10M records per table
- Horizontal scaling via Supabase Edge Functions

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | Days 1-3 | 38 CE apps installed |
| Phase 2 | Days 4-7 | 9 OCA modules deployed |
| Phase 3 | Days 8-21 | 7 Control Room modules built |
| Phase 4 | Days 22-30 | Testing, documentation, cutover |

## Success Metrics

| Metric | Target |
|--------|--------|
| Feature parity score | 100% |
| User adoption (30-day) | 80% |
| Support tickets (vs Enterprise) | -20% |
| TCO savings | 90% |
