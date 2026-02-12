# Odoo Apps Inventory — Implementation Plan

## Overview

21-day implementation to achieve 55-app parity using CE + OCA + Control Room.

## Phase 1: CE-Native Apps (Days 1-3)

### Day 1: Core Business Apps

```bash
# Install order (dependency-aware)
1. contacts          # Base for all
2. account           # Invoicing
3. sale_management   # Sales
4. crm               # CRM
5. purchase          # Purchase
6. stock             # Inventory
7. mrp               # Manufacturing
8. maintenance       # Maintenance
```

### Day 2: HR & Finance Apps

```bash
1. hr                # Employees (base)
2. hr_contract       # Contracts
3. hr_skills         # Skills
4. hr_recruitment    # Recruitment
5. hr_holidays       # Time Off
6. hr_attendance     # Attendances
7. hr_expense        # Expenses
8. fleet             # Fleet
```

### Day 3: Web, Marketing, Productivity

```bash
# Web & Commerce
1. website           # Website (base)
2. website_sale      # eCommerce
3. website_event     # Events
4. website_slides    # eLearning
5. im_livechat       # Live Chat

# Marketing
6. mass_mailing      # Email Marketing
7. mass_mailing_sms  # SMS Marketing
8. marketing_card    # Marketing Card

# Productivity & POS
9. project           # Project
10. project_todo     # To-Do
11. survey           # Surveys
12. lunch            # Lunch
13. point_of_sale    # POS
14. pos_restaurant   # Restaurant POS
15. repair           # Repairs
16. data_recycle     # Data Recycle (GDPR)
```

### Verification

```bash
./scripts/odoo/verify-ce-apps.sh
# Expected: 38/38 CE apps installed
```

## Phase 2: OCA Modules (Days 4-7)

### Day 4: Finance & Accounting

```yaml
# addons/oca-requirements.txt
odoo-addon-account-financial-tools==18.0.1.0.0
odoo-addon-mis-builder==18.0.1.0.0
odoo-addon-account-financial-reporting==18.0.1.0.0
```

```bash
pip install -r addons/oca-requirements.txt
./scripts/odoo/install-oca-modules.sh accounting
```

### Day 5: Manufacturing & HR

```yaml
# MRP II replacement
odoo-addon-mrp-multi-level==18.0.1.0.0
odoo-addon-mrp-production-request==18.0.1.0.0

# Appraisal replacement
odoo-addon-hr-appraisal-goal==18.0.1.0.0
odoo-addon-hr-appraisal-self==18.0.1.0.0

# Timesheets replacement
odoo-addon-project-timesheet-time-control==18.0.1.0.0
odoo-addon-hr-timesheet-sheet==18.0.1.0.0
```

### Day 6: Sales & Project

```yaml
# Subscriptions replacement
odoo-addon-sale-subscription==18.0.1.0.0

# Planning replacement
odoo-addon-project-timeline==18.0.1.0.0
odoo-addon-project-stage-closed==18.0.1.0.0

# Helpdesk replacement
odoo-addon-helpdesk-mgmt==18.0.1.0.0
odoo-addon-helpdesk-mgmt-timesheet==18.0.1.0.0
```

### Day 7: Integration Testing

```bash
./scripts/odoo/verify-oca-modules.sh
# Expected: 9/9 OCA replacements functional
```

## Phase 3: Control Room Modules (Days 8-21)

### Days 8-10: Knowledge Base

```
Files to create:
├── apps/control-room/src/app/kb/
│   ├── page.tsx                 # KB home
│   ├── [spaceId]/page.tsx       # Space view
│   └── [spaceId]/[artifactId]/page.tsx
├── apps/control-room/src/app/api/kb/
│   ├── spaces/route.ts
│   ├── artifacts/route.ts
│   └── artifacts/[id]/lineage/route.ts
└── supabase/migrations/
    └── 20240101000001_kb_schema.sql
```

### Days 11-12: Form Builder (Studio)

```
Files to create:
├── apps/control-room/src/app/studio/
│   ├── page.tsx                 # Form list
│   ├── [formId]/page.tsx        # Form designer
│   └── [formId]/preview/page.tsx
├── apps/control-room/src/components/studio/
│   ├── FormCanvas.tsx
│   ├── FieldPalette.tsx
│   └── PropertyPanel.tsx
└── supabase/migrations/
    └── 20240101000002_studio_schema.sql
```

### Days 13-14: E-Signature

```
Files to create:
├── apps/control-room/src/app/sign/
│   ├── page.tsx                 # Document list
│   ├── [docId]/page.tsx         # Signing view
│   └── [docId]/complete/page.tsx
├── apps/control-room/src/lib/
│   └── docusign.ts              # DocuSign integration
└── supabase/migrations/
    └── 20240101000003_sign_schema.sql
```

### Days 15-16: Appointments

```
Files to create:
├── apps/control-room/src/app/booking/
│   ├── page.tsx                 # Calendar overview
│   ├── [calendarId]/page.tsx    # Availability editor
│   └── book/[calendarId]/page.tsx  # Public booking
├── apps/control-room/src/components/booking/
│   ├── AvailabilityGrid.tsx
│   └── BookingForm.tsx
└── supabase/migrations/
    └── 20240101000004_booking_schema.sql
```

### Days 17-18: Field Service

```
Files to create:
├── apps/control-room/src/app/fsm/
│   ├── page.tsx                 # Dispatch board
│   ├── jobs/page.tsx            # Job list
│   ├── jobs/[jobId]/page.tsx    # Job detail
│   └── technicians/page.tsx     # Technician roster
├── apps/control-room/src/components/fsm/
│   ├── DispatchMap.tsx
│   └── JobCard.tsx
└── supabase/migrations/
    └── 20240101000005_fsm_schema.sql
```

### Days 19-20: Barcode Scanner

```
Files to create:
├── apps/control-room/src/app/barcode/
│   ├── page.tsx                 # Scan home
│   ├── receive/page.tsx         # Receive goods
│   ├── pick/page.tsx            # Pick orders
│   └── transfer/page.tsx        # Internal transfer
├── apps/control-room/src/components/barcode/
│   ├── BarcodeScanner.tsx       # Camera component
│   └── OperationQueue.tsx
└── supabase/migrations/
    └── 20240101000006_barcode_schema.sql
```

### Day 21: Mobile API & Integration

```
Files to create:
├── apps/control-room/src/app/api/mobile/
│   ├── auth/login/route.ts
│   ├── auth/refresh/route.ts
│   ├── sync/delta/route.ts
│   └── sync/push/route.ts
└── apps/control-room/src/lib/
    └── push-notifications.ts
```

## Phase 4: Testing & Documentation (Days 22-30)

### Days 22-25: Integration Testing

```bash
# Run full test suite
./scripts/ppm/verify-all.sh
./scripts/odoo/verify-full-parity.sh

# Load testing
k6 run scripts/load-tests/control-room-api.js
```

### Days 26-28: Documentation

```
docs/
├── odoo-apps/
│   ├── installation-guide.md
│   ├── oca-modules.md
│   └── control-room-modules.md
└── runbooks/
    ├── kb-operations.md
    ├── sign-operations.md
    └── fsm-operations.md
```

### Days 29-30: Cutover

1. Backup existing Odoo database
2. Run migration scripts
3. Verify all 55 apps functional
4. Update DNS/routing
5. Monitor for 24 hours

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OCA version incompatibility | Pin versions, test in staging |
| Control Room performance | Load testing, caching layer |
| Data migration issues | Incremental migration with rollback |
| User adoption | Training sessions, documentation |

## Deliverables Checklist

- [ ] 38 CE apps installed and configured
- [ ] 9 OCA modules deployed with tests
- [ ] 7 Control Room modules built with APIs
- [ ] Supabase schemas migrated
- [ ] Installation scripts automated
- [ ] Verification scripts passing
- [ ] Documentation complete
- [ ] Load tests passing
