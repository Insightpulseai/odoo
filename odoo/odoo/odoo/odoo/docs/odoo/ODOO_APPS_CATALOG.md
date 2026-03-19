# ODOO APPS CATALOG: CE/OCA 18 Substitutes

> **What Gets Shipped at https://erp.insightpulseai.com/odoo/apps**

This document maps which Odoo Enterprise/IAP apps are replaced by CE/OCA equivalents in the InsightPulse implementation.

---

## APPS DASHBOARD SHIPPING LIST

When users navigate to the Odoo Apps dashboard (`/odoo/apps`), they will find these applications available for installation:

---

## CUSTOM INSIGHTPULSE APPS (New - Not in Standard Odoo)

### 1. InsightPulse Expense Management

| Property | Value |
|----------|-------|
| **Module** | `ipai_expense` |
| **Category** | Expenses & Travel |
| **Icon** | Custom InsightPulse branding |
| **Replaces** | SAP Concur (cloud-based) |
| **Status** | Ready to Install |

**Description**: PH-focused expense and travel management system replacing SAP Concur

**Features**:
- Expense request workflows (Draft → Manager Review → Finance → GL Posted)
- Travel request management
- Receipt attachment & OCR (if configured)
- Multi-currency support (PHP, USD, etc.)
- GL account auto-posting to Chart of Accounts
- Project/Job code tracking (for cost allocation)
- Approval hierarchy configuration
- Per Diem calculations (PH-specific rates)
- Travel advance requests
- Reimbursement tracking

**Dependencies**:
- `base`
- `account` (GL posting)
- `mail` (notifications)
- `web`

---

### 2. InsightPulse Equipment Management

| Property | Value |
|----------|-------|
| **Module** | `ipai_equipment` |
| **Category** | Equipment & Assets |
| **Icon** | Custom InsightPulse branding |
| **Replaces** | Cheqroom (SaaS) |
| **Status** | Ready to Install |

**Description**: Equipment booking and asset management system replacing Cheqroom

**Features**:
- Equipment/asset catalog with categorization
- Serial number tracking with QR codes
- Equipment condition tracking (New, Good, Fair, Poor, Damaged)
- Booking system with calendar view
- Automatic conflict detection (double-booking prevention)
- Check-out workflow (sign document, take photo)
- Check-in workflow (inspect condition, update logs)
- Incident reporting (damage, loss, maintenance needed)
- Maintenance scheduling
- Utilization analytics
- Equipment depreciation tracking
- Multi-location support

**Dependencies**:
- `base`
- `account` (depreciation)
- `mail` (notifications)
- `web`

---

### 3. InsightPulse CE Cleaner

| Property | Value |
|----------|-------|
| **Module** | `ipai_ce_cleaner` |
| **Category** | Customization & Configuration |
| **Icon** | Wrench icon (hidden in production) |
| **Status** | Auto-installed (hidden) |

**Description**: Removes Enterprise/IAP upsells and redirects to CE/OCA alternatives

**Features**:
- Hides "Upgrade to Enterprise" banners
- Removes IAP credit/SMS/email service menus
- Removes Documents Scanner (IAP)
- Removes Sign feature (IAP)
- Removes WhatsApp integration (IAP)
- Removes Studio (Enterprise feature)
- Redirects Help menu to InsightPulse docs
- Redirects to OCA modules for missing features

**Dependencies**:
- `base`

---

## STANDARD ODOO CE APPS (Included in Base Install)

These are included by default when Odoo 18 CE is installed:

### Core Business Management

| App | Category | Status | CE Version | OCA Enhancement |
|-----|----------|--------|------------|-----------------|
| Contacts | CRM | ✅ Installed | Base | Enhanced by partner-contact OCA modules |
| Calendar | Productivity | ✅ Installed | Base | Uses native implementation |
| Accounting | Finance | ✅ Installed | Base | Enhanced by account-financial-tools |
| Invoicing | Finance | ✅ Installed | Base | Enhanced by account-invoicing OCA |
| Bills | Finance | ✅ Installed | Base | Part of Account module |
| Expenses | Finance | ✅ Installed | Base | Replaced by ipai_expense custom |
| Inventory | Inventory | ✅ Installed | Base | Enhanced by stock-logistics OCA |
| Barcode | Inventory | ✅ Installed | Base | Standard CE feature |
| Sales | Sales | ✅ Installed | Base | Enhanced by sale-workflow OCA |
| Quotations | Sales | ✅ Installed | Base | Part of Sales module |
| Purchase | Purchasing | ✅ Installed | Base | Enhanced by purchase-workflow OCA |
| Point of Sale | POS | ✅ Installed | Base | Optional (may not use) |
| Website | Website | ✅ Installed | Base | Enhanced by website OCA modules |
| Documentation | Tools | ✅ Installed | Base | Read-only in CE |

---

## OCA MODULES TO BE INSTALLED (30+ Additional Apps)

Upon go-live, these OCA modules will be available for installation:

### Accounting & Finance (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| General Ledger Report | account-reporting | Advanced GL reporting | 🟢 Ready |
| Account Invoice Refund | account-invoicing | Invoice refund workflows | 🟢 Ready |
| Multi-Company Accounting | account-financial-tools | Multi-entity consolidation | 🟢 Ready |
| Account Reconciliation | account-financial-tools | Bank reconciliation tools | 🟢 Ready |
| Analytic Accounting | account | Cost center allocation | 🟢 Ready |
| Commission Management | commission | Sales commission tracking | 🟢 Ready |
| Invoice State Cloud | account-invoicing | Invoice status tracking | 🟢 Ready |
| Budget Management | account-financial-tools | Budget vs actual | 🟢 Ready |

### Sales & CRM (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| Sale Order Template | sale-workflow | Quote templates | 🟢 Ready |
| Sale Double Validation | sale-workflow | Two-person approval | 🟢 Ready |
| Partner Contact Manager | partner-contact | Contact enhancements | 🟢 Ready |
| CRM Business Development | crm-workflows | Sales pipeline tools | 🟢 Ready |

### Inventory & Procurement (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| Stock Batch Transfer | stock-logistics | Batch move operations | 🟢 Ready |
| Stock Intrastat | stock-logistics | EU compliance reporting | 🟢 Ready |
| Stock Picking Batch | stock-logistics | Pick batch optimization | 🟢 Ready |
| Advanced Inventory Analysis | stock-logistics | Inventory analytics | 🟢 Ready |

### Website & E-Commerce (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| Website Maintenance | website | Site maintenance mode | 🟢 Ready |
| Website Backend Theme | website | Custom themes | 🟢 Ready |
| Web Responsive Design | web | Mobile optimization | 🟢 Ready |

### Tools & Utilities (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| Server Tools | server-tools | Backend utilities | 🟢 Ready |
| Document Management | knowledge | Wiki/knowledge base | 🟢 Ready |
| Mail System Enhancement | server-tools | Email routing | 🟢 Ready |
| Report XML Improvements | reporting-tools | Better reports | 🟢 Ready |

### Integration & Automation (OCA)

| App | Module | Purpose | Status |
|-----|--------|---------|--------|
| Integration with n8n | base + n8n | Workflow automation | 🟢 Ready |
| Notion Sync | external | Notion integration | 🟢 Ready |
| REST API Enhancement | web | Extended API | 🟢 Ready |

---

## APPS NOT SHIPPED (Enterprise/IAP Only)

These require Odoo Enterprise or IAP subscriptions and are intentionally excluded:

| App | Reason Excluded | CE/OCA Substitute |
|-----|-----------------|-------------------|
| Studio | Enterprise-only | N/A (use JSON forms instead) |
| Documents | IAP service required | Use native documents module |
| Sign | IAP service required | Use signature field in forms |
| WhatsApp | IAP service required | Use email/SMS instead |
| SMS Marketing | IAP service required | Use email marketing (Mailchimp) |
| Social Media | Enterprise-only | Manual posting |
| Knowledge (Premium) | Enterprise features | Use knowledge OCA module |
| Surveys (Premium) | Enterprise features | Use survey CE module |
| Appointments | Enterprise-only | Use calendar + base_calendar |
| Email Marketing (Premium) | Enterprise features | Use Mailchimp integration |
| Website Builder (Advanced) | Enterprise features | Use standard website module |
| PLM | Enterprise-only | Use manufacturing modules |
| Field Service | Enterprise-only | N/A (not in scope) |
| IoT | Enterprise-only | N/A (not in scope) |
| IoT Monitoring | Enterprise-only | N/A (not in scope) |
| OCR Documents | IAP service required | Manual upload instead |

---

## APPS AVAILABLE IN DASHBOARD

When user navigates to `https://erp.insightpulseai.com/web/apps`:

### Installation Status (Day 1 of Go-Live)

```
INSTALLED APPS (Automatically Active):
├── Contacts (CRM)
├── Calendar (Productivity)
├── Accounting (Finance)
├── Invoicing (Finance)
├── Bills (Finance)
├── Sales (Sales)
├── Purchase (Purchasing)
├── Inventory (Inventory)
├── Barcode (Inventory)
├── Website (Website)
├── InsightPulse Expense Management ⭐ CUSTOM
├── InsightPulse Equipment Management ⭐ CUSTOM
└── CE Cleaner (hidden)

AVAILABLE TO INSTALL (User Can Click "Install"):
├── Point of Sale (POS) - Optional
├── Manufacturing - Optional
├── Project Management - Optional
├── Helpdesk - Optional
├── HR Management - Optional
├── Payroll - Optional (CE version)
├── Employees - Optional
├── Appraisals - Optional
├── Recruitment - Optional
├── Timesheets - Optional
├── Fleet Management - Optional
├── Quality Management - Optional
├── Maintenance - Optional
├── Repair - Optional
├── IoT - NOT AVAILABLE (Enterprise)
├── Documents Scanner - NOT AVAILABLE (IAP)
├── Sign - NOT AVAILABLE (IAP)
├── Studio - NOT AVAILABLE (Enterprise)
└── [30+ OCA modules] - AVAILABLE

NOT AVAILABLE (Filtered Out):
├── All IAP-only apps (WhatsApp, SMS, etc.)
├── All Enterprise-only apps (Field Service, etc.)
└── [Filtered by ipai_ce_cleaner]
```

---

## CUSTOM MODULE CONFIGURATION

### ipai_expense Module Details

**When Installed, Users See:**

```
Expenses Menu Structure:
├── Expense Requests
│   ├── My Expenses (all submitted by user)
│   ├── Team Expenses (approval queue for managers)
│   ├── Finance Expenses (all expenses for posting)
│   └── Expense Reports (analytics)
├── Travel Requests
│   ├── My Travel (user submissions)
│   ├── Travel Approvals (manager queue)
│   └── Travel Reports
├── Configuration
│   ├── Expense Categories (meals, transport, accommodation, etc.)
│   ├── GL Accounts Mapping (expense category → GL account)
│   ├── Approval Rules (who approves what)
│   ├── Per Diem Rates (PH rates by location/meal)
│   └── Travel Advance Settings
├── Reports
│   ├── Expense Summary (by user, period, category)
│   ├── GL Posting Report (what was posted to accounting)
│   ├── Travel Analysis (by project, employee, location)
│   └── Budget vs Actual (department budgets)
└── Settings
    ├── Default GL Accounts
    ├── Receipt Requirements (mandatory field)
    ├── Approval Hierarchy
    └── GL Auto-post Settings
```

**Workflows Enabled:**

```
Expense Request Workflow:
1. Employee submits expense (Draft)
2. System validates receipt, GL account
3. Manager reviews & approves/rejects
4. Finance reviews before posting
5. System auto-posts to GL (creates journal entry)
6. Employee receives reimbursement notification
7. Finance marks as Paid

Travel Request Workflow:
1. Employee requests travel approval (amount)
2. Manager approves/rejects
3. Finance allocates advance (if approved)
4. Employee receives payment (cash, check, or transfer)
5. After travel: Employee submits expense report
6. Expense matched against advance
7. Final settlement calculated
```

---

### ipai_equipment Module Details

**When Installed, Users See:**

```
Equipment Menu Structure:
├── Equipment Catalog
│   ├── Equipment Categories (laptops, projectors, chairs, etc.)
│   ├── Equipment List (all equipment with status)
│   ├── Equipment Dashboard (availability heatmap)
│   └── Condition Status (view by condition level)
├── Bookings
│   ├── My Bookings (what I've booked)
│   ├── Calendar View (what's available when)
│   ├── Create New Booking (search & book)
│   ├── Booking Approvals (admin approval queue)
│   └── Booking History (past bookings)
├── Check-out/Check-in
│   ├── Check-out Equipment (QR scan, sign)
│   ├── Check-in Equipment (condition check, upload photos)
│   ├── Sign Document (digital signature)
│   └── Photo Upload (condition documentation)
├── Incidents
│   ├── Report Incident (damage, loss, maintenance)
│   ├── Incident List (all reported incidents)
│   ├── Incident Resolution (maintenance team)
│   └── Incident Analytics
├── Analytics
│   ├── Equipment Utilization (which equipment used most)
│   ├── Booking Trends (peak times, popular equipment)
│   ├── Incident Analysis (problems by equipment/user)
│   ├── Availability Forecast
│   └── Equipment ROI (cost vs usage)
├── Maintenance
│   ├── Maintenance Schedule (preventive maintenance)
│   ├── Maintenance Records (history)
│   ├── Service Requests
│   └── Depreciation Tracking
└── Configuration
    ├── Equipment Categories
    ├── Condition Levels
    ├── Booking Rules (who can book what)
    ├── Check-in Checklist
    └── Incident Categories
```

**Workflows Enabled:**

```
Equipment Booking Workflow:
1. User searches available equipment (date/time range)
2. System checks for conflicts (prevents double-booking)
3. User selects equipment & submits booking
4. Admin approves booking (if required)
5. User receives confirmation

Check-out Workflow:
1. User scans QR code or selects equipment
2. System loads equipment details
3. User signs digital document (responsibility)
4. System records check-out timestamp
5. User receives check-out confirmation

Check-in Workflow:
1. User scans QR code
2. System loads booking details
3. User inspects condition & selects from checklist
4. User uploads before/after photos (if damaged)
5. User confirms check-in
6. System calculates booking duration
7. If incident reported → creates incident ticket

Incident Workflow:
1. User/checker reports incident (damage/loss/maintenance)
2. Incident type selected (damage, loss, wear, malfunction)
3. Description & photos attached
4. Severity assessed (low/medium/high)
5. Maintenance team notified
6. Team schedules repair/replacement
7. Status tracked until resolved
```

---

## MODULE INSTALLATION STATISTICS

### By the Numbers

| Category | Count | Status |
|----------|-------|--------|
| Installed on Day 1 | 14 apps | ✅ Active |
| Custom InsightPulse Apps | 3 apps | ⭐ Unique |
| Available OCA Modules | 30+ apps | 🟢 Ready to install |
| Intentionally Disabled | 12 apps | 🚫 IAP/Enterprise only |
| **Total Ecosystem** | **59 apps** | Full suite available |

---

## KEY DIFFERENTIATORS: CE/OCA vs Enterprise

### What Remains the Same (Works Identically)

- ✅ Standard Accounting (Invoices, Bills, GL, Reports)
- ✅ Sales Management (Quotations, Sales Orders)
- ✅ Purchase Management (Purchase Orders, Receipts)
- ✅ Inventory Management (Stock, Warehouse)
- ✅ Contacts & CRM
- ✅ Calendar & Communication
- ✅ Reports & Analytics (standard ones)
- ✅ User Management & Permissions
- ✅ Customization (XML views, Python models)
- ✅ API (REST & RPC)
- ✅ Database & Backup

### What's Enhanced by Custom Modules

- ✅ Expense Management (was generic → now PH-specific with ipai_expense)
- ✅ Equipment Management (was non-existent → now fully featured with ipai_equipment)
- ✅ GL Posting (expense auto-posting → new automation)
- ✅ Travel Management (was generic → now PH travel workflows)
- ✅ Asset Tracking (QR codes, serial numbers → new in ipai_equipment)

### What's Missing (vs Enterprise)

- ❌ Visual Studio IDE (Studio → use Python/XML instead)
- ❌ Document Scanning (IAP → manual upload instead)
- ❌ Digital Signatures (Sign → signature field in forms)
- ❌ WhatsApp Integration (IAP → email/SMS instead)
- ❌ SMS Marketing (IAP → email marketing instead)
- ❌ Advanced Appointments (Enterprise → use calendar)
- ❌ Field Service (Enterprise → not in scope)
- ❌ IoT Monitoring (Enterprise → not in scope)
- ❌ Advanced PLM (Enterprise → manufacturing modules)

### What's Enhanced by OCA

- ⬆️ Accounting (30+ OCA modules for advanced features)
- ⬆️ Inventory (stock-logistics modules)
- ⬆️ Sales (sale-workflow improvements)
- ⬆️ Purchasing (purchase-workflow improvements)
- ⬆️ Reporting (enhanced report generation)
- ⬆️ CRM (partner-contact enhancements)
- ⬆️ Tools (server-tools utilities)
- ⬆️ Website (web customization modules)

---

## APPS VISIBLE TO END USERS

### For Regular Employee

```
Visible Apps:
├── My Expenses (ipai_expense) ⭐
├── Travel Requests (ipai_expense) ⭐
├── Equipment Bookings (ipai_equipment) ⭐
├── Calendar
├── Contacts
├── Documents (shared)
└── Helpdesk (if enabled)

NOT Visible:
├── Accounting (read-only access only)
├── Admin panel
├── Settings
└── Development tools
```

### For Manager/Approver

```
Visible Apps:
├── Approve Expenses (ipai_expense) ⭐
├── Approve Travel (ipai_expense) ⭐
├── My Expenses (ipai_expense) ⭐
├── Approve Equipment Bookings (ipai_equipment) ⭐
├── Team Dashboard
├── Contacts
├── Reports
└── Calendar
```

### For Finance Team

```
Visible Apps:
├── All Expenses (ipai_expense) ⭐
├── GL Posting Report (ipai_expense) ⭐
├── Accounting
├── Invoicing
├── Bills
├── Reports
├── Expense Analytics (ipai_expense) ⭐
└── Equipment Analytics (ipai_equipment) ⭐
```

### For Administrator

```
Visible Apps:
├── ALL APPS
├── Settings & Configuration
├── User Management
├── Access Control
├── System Health
├── Database Management
├── Backup & Restore
└── Development Tools
```

---

## RESPONSIVE DESIGN

All apps are fully responsive and work on:

- ✅ Desktop (1920x1080 and above)
- ✅ Tablet (iPad, Android tablets)
- ✅ Mobile (iPhone, Android phones)
- ✅ Progressive Web App (PWA) capable

---

## ACCESS CONTROL BY APP

### Group-Based Permissions

**Employee Group:**
- Can view own expenses
- Can submit expenses
- Can view own travel requests
- Can submit travel requests
- Can book equipment
- Can check-out/check-in equipment
- Cannot approve or delete

**Manager Group:**
- Can view team expenses
- Can approve/reject expenses
- Can view team travel requests
- Can approve/reject travel
- Can approve equipment bookings
- Can view equipment analytics
- Can view reports

**Finance Group:**
- Can view all expenses
- Can post to GL
- Can modify GL accounts
- Can run financial reports
- Can reconcile
- Can audit trail
- Admin access to all settings

**Equipment Admin Group:**
- Can manage equipment catalog
- Can approve/modify bookings
- Can manage incidents
- Can schedule maintenance
- Can view utilization analytics
- Can generate equipment reports

**System Admin Group:**
- All permissions
- Can modify all apps
- Can change configurations
- Can manage users
- Can access debug mode
- Can perform backups

---

## QUICK REFERENCE TABLE: All Apps at Go-Live

| App Name | Status | Category | Custom | OCA | Enterprise Only |
|----------|--------|----------|--------|-----|-----------------|
| InsightPulse Expense | ✅ | Finance | ⭐ | | |
| InsightPulse Equipment | ✅ | Assets | ⭐ | | |
| Accounting | ✅ | Finance | | ✓ | |
| Invoicing | ✅ | Finance | | ✓ | |
| Bills | ✅ | Finance | | ✓ | |
| Sales | ✅ | Sales | | ✓ | |
| Purchase | ✅ | Purchasing | | ✓ | |
| Inventory | ✅ | Inventory | | ✓ | |
| Barcode | ✅ | Inventory | | ✓ | |
| Contacts | ✅ | CRM | | ✓ | |
| Calendar | ✅ | Productivity | | ✓ | |
| Website | ✅ | Marketing | | ✓ | |
| Point of Sale | 🟡 | Retail | | ✓ | |
| Manufacturing | 🟡 | Operations | | ✓ | |
| Projects | 🟡 | Operations | | ✓ | |
| Helpdesk | 🟡 | Support | | ✓ | |
| HR | 🟡 | HR | | ✓ | |
| Payroll | 🟡 | Payroll | | ✓ | |
| Employees | 🟡 | HR | | ✓ | |
| Appraisals | 🟡 | HR | | ✓ | |
| Recruitment | 🟡 | HR | | ✓ | |
| Timesheets | 🟡 | HR | | ✓ | |
| Fleet | 🟡 | Logistics | | ✓ | |
| Quality | 🟡 | Operations | | ✓ | |
| Maintenance | 🟡 | Operations | | ✓ | |
| Repair | 🟡 | Operations | | ✓ | |
| Documents | 🟡 | Knowledge | | ✓ | |
| Survey | 🟡 | Marketing | | ✓ | |
| Knowledge | 🟡 | Documentation | | ✓ | |
| Studio | ❌ | Dev Tools | | | ✓ |
| IoT | ❌ | IoT | | | ✓ |
| Field Service | ❌ | Services | | | ✓ |
| Documents Scanner | ❌ | IAP | | | ✓ |
| Sign | ❌ | IAP | | | ✓ |
| WhatsApp | ❌ | IAP | | | ✓ |
| SMS | ❌ | IAP | | | ✓ |

**Legend:** ✅ Installed | 🟡 Available but not installed | ❌ Not available | ⭐ Custom | ✓ Standard

---

## SUMMARY: WHAT SHIPS IN THE APP STORE

### At Launch (Installed)

- **3 Custom Apps** (Expense, Equipment, CE Cleaner)
- **11 Standard Odoo CE Apps** (Accounting, Sales, Inventory, etc.)

### Available to Install (One-Click)

- **30+ OCA Modules** (enhancements & add-ons)
- **15 Optional CE Apps** (Manufacturing, HR, Projects, etc.)

### Intentionally Excluded

- **12 Enterprise/IAP Apps** (Studio, Sign, WhatsApp, Field Service, etc.)

### Total Ecosystem

| Metric | Count |
|--------|-------|
| Total Apps available in the marketplace | 59 |
| Apps installed & active on Day 1 | 14 |
| Apps available for optional installation | 45 |
| Apps are InsightPulse custom modules (never available elsewhere) | 3 |

---

> **The InsightPulse Odoo CE deployment provides a comprehensive, production-ready ERP with 100% open-source stack, zero vendor lock-in, and total cost of ownership savings vs Odoo Enterprise.**
