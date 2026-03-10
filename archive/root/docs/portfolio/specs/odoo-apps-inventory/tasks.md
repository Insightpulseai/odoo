# Odoo Apps Inventory — Task Checklist

## Phase 1: CE-Native Apps (Days 1-3)

### Day 1: Core Business Apps
- [ ] Install `contacts` module
- [ ] Install `account` module (Invoicing)
- [ ] Install `sale_management` module (Sales)
- [ ] Install `crm` module (CRM)
- [ ] Install `purchase` module (Purchase)
- [ ] Install `stock` module (Inventory)
- [ ] Install `mrp` module (Manufacturing)
- [ ] Install `maintenance` module
- [ ] Verify all 8 apps functional

### Day 2: HR & Finance Apps
- [ ] Install `hr` module (Employees base)
- [ ] Install `hr_contract` module
- [ ] Install `hr_skills` module
- [ ] Install `hr_recruitment` module
- [ ] Install `hr_holidays` module (Time Off)
- [ ] Install `hr_attendance` module
- [ ] Install `hr_expense` module
- [ ] Install `fleet` module
- [ ] Verify all 8 apps functional

### Day 3: Web, Marketing, Productivity
- [ ] Install `website` module
- [ ] Install `website_sale` module (eCommerce)
- [ ] Install `website_event` module
- [ ] Install `website_slides` module (eLearning)
- [ ] Install `im_livechat` module
- [ ] Install `mass_mailing` module
- [ ] Install `mass_mailing_sms` module
- [ ] Install `marketing_card` module
- [ ] Install `project` module
- [ ] Install `project_todo` module
- [ ] Install `survey` module
- [ ] Install `lunch` module
- [ ] Install `point_of_sale` module
- [ ] Install `pos_restaurant` module
- [ ] Install `repair` module
- [ ] Install `data_recycle` module
- [ ] Run `./scripts/odoo/verify-ce-apps.sh`
- [ ] Document any installation issues

## Phase 2: OCA Modules (Days 4-7)

### Day 4: Finance & Accounting
- [ ] Add OCA account-financial-tools repo
- [ ] Install `account_financial_report` module
- [ ] Install `mis_builder` module
- [ ] Install `account_asset_management` module
- [ ] Configure chart of accounts
- [ ] Verify financial reports generate correctly

### Day 5: Manufacturing & HR
- [ ] Install `mrp_multi_level` module (MRP II replacement)
- [ ] Install `mrp_production_request` module
- [ ] Install `hr_appraisal_goal` module
- [ ] Install `hr_appraisal_self` module
- [ ] Install `hr_timesheet_sheet` module
- [ ] Install `project_timesheet_time_control` module
- [ ] Verify appraisal workflow functional
- [ ] Verify timesheet grid view works

### Day 6: Sales & Project
- [ ] Install `sale_subscription` module
- [ ] Configure subscription templates
- [ ] Install `project_timeline` module
- [ ] Install `project_stage_closed` module
- [ ] Install `helpdesk_mgmt` module
- [ ] Install `helpdesk_mgmt_timesheet` module
- [ ] Verify helpdesk ticket workflow

### Day 7: Integration Testing
- [ ] Run `./scripts/odoo/verify-oca-modules.sh`
- [ ] Test cross-module workflows
- [ ] Document OCA configuration
- [ ] Create user acceptance test cases

## Phase 3: Control Room Modules (Days 8-21)

### Days 8-10: Knowledge Base
- [ ] Create Supabase migration for `kb_*` tables
- [ ] Create API routes: `/api/kb/spaces`, `/api/kb/artifacts`
- [ ] Implement artifact CRUD operations
- [ ] Implement lineage tracking endpoint
- [ ] Create KB spaces page UI
- [ ] Create artifact editor with markdown
- [ ] Create artifact search with persona filtering
- [ ] Implement version history view
- [ ] Write unit tests for KB API
- [ ] Document KB module

### Days 11-12: Form Builder (Studio)
- [ ] Create Supabase migration for `studio_*` tables
- [ ] Create API routes: `/api/studio/forms`, `/api/studio/fields`
- [ ] Implement form designer canvas
- [ ] Implement field palette component
- [ ] Implement property panel
- [ ] Create Odoo XML view generator
- [ ] Create form preview mode
- [ ] Write unit tests
- [ ] Document Studio module

### Days 13-14: E-Signature
- [ ] Create Supabase migration for `sign_*` tables
- [ ] Create API routes: `/api/sign/documents`, `/api/sign/requests`
- [ ] Implement document upload (PDF, DOCX)
- [ ] Implement signature placement UI
- [ ] Create DocuSign OAuth integration
- [ ] Implement email notification workflow
- [ ] Create signing completion page
- [ ] Write unit tests
- [ ] Document Sign module

### Days 15-16: Appointments
- [ ] Create Supabase migration for `booking_*` tables
- [ ] Create API routes: `/api/booking/calendars`, `/api/booking/slots`
- [ ] Implement availability grid editor
- [ ] Create public booking page
- [ ] Implement timezone handling
- [ ] Create email confirmation templates
- [ ] Implement SMS notifications (via n8n)
- [ ] Write unit tests
- [ ] Document Booking module

### Days 17-18: Field Service
- [ ] Create Supabase migration for `fsm_*` tables
- [ ] Create API routes: `/api/fsm/jobs`, `/api/fsm/technicians`
- [ ] Implement dispatch board UI
- [ ] Create job assignment workflow
- [ ] Implement skills matching algorithm
- [ ] Create map view with technician locations
- [ ] Implement mobile check-in/out
- [ ] Write unit tests
- [ ] Document FSM module

### Days 19-20: Barcode Scanner
- [ ] Create Supabase migration for `barcode_*` tables
- [ ] Create API routes: `/api/barcode/scans`, `/api/barcode/operations`
- [ ] Implement camera barcode scanner component
- [ ] Create receive goods workflow
- [ ] Create pick orders workflow
- [ ] Create internal transfer workflow
- [ ] Implement offline queue with sync
- [ ] Write unit tests
- [ ] Document Barcode module

### Day 21: Mobile API
- [ ] Create auth endpoints: `/api/mobile/auth/login`, `/api/mobile/auth/refresh`
- [ ] Create sync endpoints: `/api/mobile/sync/delta`, `/api/mobile/sync/push`
- [ ] Implement JWT refresh token flow
- [ ] Set up FCM for push notifications
- [ ] Implement delta sync algorithm
- [ ] Create conflict resolution logic
- [ ] Write API integration tests
- [ ] Generate OpenAPI spec
- [ ] Document Mobile API

## Phase 4: Testing & Cutover (Days 22-30)

### Days 22-25: Integration Testing
- [ ] Run full verification suite
- [ ] Execute load tests (k6)
- [ ] Test all 55 app workflows end-to-end
- [ ] Fix identified bugs
- [ ] Performance optimization
- [ ] Security audit

### Days 26-28: Documentation
- [ ] Write installation guide
- [ ] Write OCA modules guide
- [ ] Write Control Room modules guide
- [ ] Create runbooks for each custom module
- [ ] Update architecture diagrams
- [ ] Create video walkthroughs

### Days 29-30: Cutover
- [ ] Backup production Odoo database
- [ ] Run migration scripts in staging
- [ ] Verify staging environment
- [ ] Execute production migration
- [ ] Update DNS/routing
- [ ] Monitor for 24 hours
- [ ] Sign-off from stakeholders

## Verification Checkpoints

### After Phase 1
- [ ] `./scripts/odoo/verify-ce-apps.sh` passes (38/38)
- [ ] All CE modules show "Installed" in Odoo

### After Phase 2
- [ ] `./scripts/odoo/verify-oca-modules.sh` passes (9/9)
- [ ] OCA modules functional in Odoo

### After Phase 3
- [ ] All Control Room APIs return 200 on health check
- [ ] All Supabase tables created
- [ ] All UI pages render without errors

### After Phase 4
- [ ] Full parity verification passes (55/55)
- [ ] Load test passes (1000 concurrent users)
- [ ] Documentation complete
- [ ] Stakeholder sign-off obtained
