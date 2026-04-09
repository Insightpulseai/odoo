# UAT Scenario Pack — Odoo on Azure

## 1. Purpose

This is the executable business acceptance pack for the Odoo-on-Azure workload. Every scenario in this file is owned by a named business role, linked to a process tower, and gated by deterministic pass/fail criteria. No scenario may be signed off without evidence.

## 2. Scope and Usage

| Item | Value |
|------|-------|
| Workload | Odoo CE 18.0 on Azure Container Apps |
| Environment | `odoo_staging` (UAT execution) |
| Authority | This file is the single source of truth for UAT scenario definitions |
| Companion docs | `prd.md` (requirements), `plan.md` (execution model), `tasks.md` (checklist) |

## 3. Roles

### Business Roles

| Role | Abbreviation | Description |
|------|-------------|-------------|
| Finance Manager | FM | Owns finance process-tower sign-off |
| Sales Manager | SM | Owns sales process-tower sign-off |
| Procurement Officer | PO | Owns procurement process-tower sign-off |
| Inventory Controller | IC | Owns inventory process-tower sign-off |
| Project Manager | PM | Owns projects process-tower sign-off |
| Platform Admin | PA | Owns admin/security process-tower sign-off |

### Delivery Roles

| Role | Abbreviation | Description |
|------|-------------|-------------|
| UAT Coordinator | UC | Schedules sessions, tracks register, escalates blockers |
| Solution Architect | SA | Resolves design questions during UAT |
| QA Lead | QA | Validates evidence artifacts, confirms defect severity |

## 4. Scenario Status Model

| Status | Meaning |
|--------|---------|
| **Pass** | All steps executed, all expected results confirmed, evidence collected |
| **Pass with Accepted Workaround** | Business result achieved via documented workaround; defect logged, severity agreed |
| **Fail** | One or more expected results not met; defect logged, scenario blocked until resolved |
| **Blocked** | Precondition not met or environment issue prevents execution |
| **Not Run** | Scenario not yet attempted |

## 5. Severity Reference

| Severity | Label | Definition |
|----------|-------|------------|
| 1 | Critical | Business process cannot complete; no workaround |
| 2 | High | Business process completes with significant manual effort |
| 3 | Medium | Business process completes with minor inconvenience |
| 4 | Low | Cosmetic or non-blocking observation |

## 6. Evidence Requirements

Every executed scenario must produce:

- Screenshot or screen recording of the final system state
- Odoo record ID(s) created or modified
- Timestamp (UTC) of execution
- Tester name and role
- Environment identifier (`odoo_staging`)

Evidence is stored in `docs/evidence/<YYYYMMDD-HHMM>/uat/`.

## 7. Entry Preconditions

Before UAT begins:

- [ ] `odoo_staging` environment is provisioned and accessible
- [ ] Demo/seed data is loaded per `scripts/odoo/seed_staging.sh`
- [ ] All process-tower modules are installed and updated
- [ ] User accounts for all business roles are provisioned with correct access
- [ ] Network connectivity from tester machines to staging URL is confirmed
- [ ] Backup of staging database taken immediately before UAT start

## 8. Exit Preconditions

UAT is complete only when:

- [ ] Every required scenario has status Pass or Pass with Accepted Workaround
- [ ] No open Severity 1 or Severity 2 defects remain unresolved
- [ ] Every process-tower sign-off is collected
- [ ] Consolidated UAT Exit Summary is signed by UAT Coordinator and Platform Admin

---

## 9. Scenario Template

### Header

| Field | Value |
|-------|-------|
| **Scenario ID** | `<TOWER>-<NNN>` |
| **Title** | Short descriptive title |
| **Process Tower** | Finance / Sales / Procurement / Inventory / Projects / Admin |
| **Priority** | Critical / High / Medium |
| **Type** | Positive / Negative / Exception |
| **Owner** | Business role abbreviation |
| **Primary Role** | Role executing the scenario |
| **Supporting Roles** | Other roles involved |
| **Preconditions** | What must be true before this scenario starts |

### Execution

| Field | Value |
|-------|-------|
| **Steps** | Numbered list of actions |
| **Expected System Result** | What Odoo must do (deterministic) |
| **Expected Business Result** | What the business outcome must be |
| **Evidence Required** | Specific artifacts to capture |
| **Defect Logging Rule** | When to log a defect vs. accept |
| **Sign-off Rule** | Who signs off and under what condition |

---

## 10. Finance Scenarios

### FIN-001: Create and Validate Customer Invoice

| Field | Value |
|-------|-------|
| **Scenario ID** | FIN-001 |
| **Title** | Create and Validate Customer Invoice |
| **Process Tower** | Finance |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | FM |
| **Primary Role** | Finance Manager |
| **Supporting Roles** | -- |
| **Preconditions** | At least one customer exists; chart of accounts configured; fiscal year open |

**Steps:**

1. Navigate to Accounting > Customers > Invoices
2. Click Create
3. Select an existing customer
4. Add at least two invoice lines with product, quantity, and unit price
5. Verify tax is auto-calculated
6. Click Confirm

**Expected System Result:**

- Invoice moves to Posted status
- Journal entry is created with correct debit/credit lines
- Tax lines match configured tax rates
- Invoice number is auto-assigned from the sequence

**Expected Business Result:**

- Finance Manager can produce a valid, numbered customer invoice ready for delivery

**Evidence Required:**

- Screenshot of posted invoice with invoice number visible
- Screenshot of journal entry (debit/credit lines)
- Invoice record ID

**Defect Logging Rule:**

- Log Severity 1 if invoice cannot be confirmed or journal entry is missing
- Log Severity 2 if tax calculation is incorrect
- Log Severity 3 if cosmetic issues on invoice PDF

**Sign-off Rule:**

- FM signs off when at least 3 invoices have been created and validated without Severity 1/2 defects

---

### FIN-002: Process Supplier Bill

| Field | Value |
|-------|-------|
| **Scenario ID** | FIN-002 |
| **Title** | Process Supplier Bill |
| **Process Tower** | Finance |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | FM |
| **Primary Role** | Finance Manager |
| **Supporting Roles** | PO |
| **Preconditions** | At least one vendor exists; expense accounts configured |

**Steps:**

1. Navigate to Accounting > Vendors > Bills
2. Click Create
3. Select an existing vendor
4. Add bill lines matching a known purchase order or manual entry
5. Verify tax and account mapping
6. Click Confirm
7. Register payment against the bill

**Expected System Result:**

- Bill moves to Posted status
- Payment is registered and reconciled
- Outstanding balance on the vendor record is updated
- Journal entries for bill and payment are created

**Expected Business Result:**

- Finance Manager can record and pay a supplier bill end-to-end

**Evidence Required:**

- Screenshot of posted bill
- Screenshot of payment registration
- Screenshot of vendor balance (before and after)
- Bill and payment record IDs

**Defect Logging Rule:**

- Log Severity 1 if bill cannot be posted or payment fails
- Log Severity 2 if reconciliation does not update vendor balance

**Sign-off Rule:**

- FM signs off when at least 2 bills have been processed and paid without Severity 1/2 defects

---

### FIN-003: Approval-Controlled Journal Entry

| Field | Value |
|-------|-------|
| **Scenario ID** | FIN-003 |
| **Title** | Approval-Controlled Journal Entry |
| **Process Tower** | Finance |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | FM |
| **Primary Role** | Finance Manager |
| **Supporting Roles** | PA |
| **Preconditions** | Journal entry approval workflow is configured; approver user exists |

**Steps:**

1. Navigate to Accounting > Miscellaneous > Journal Entries
2. Create a manual journal entry with balanced debit/credit lines
3. Submit for approval
4. Log in as approver and approve the entry
5. Verify the entry moves to Posted status

**Expected System Result:**

- Journal entry is created in Draft
- Submission triggers approval workflow
- Approved entry moves to Posted
- Rejected entry stays in Draft with rejection reason

**Expected Business Result:**

- Manual journal entries require approval before posting, enforcing segregation of duties

**Evidence Required:**

- Screenshot of draft entry pending approval
- Screenshot of approved/posted entry
- Approver username and timestamp

**Defect Logging Rule:**

- Log Severity 1 if entry can be posted without approval
- Log Severity 2 if approval notification is not sent

**Sign-off Rule:**

- FM signs off when approval workflow is demonstrated for both approve and reject paths

---

### FIN-004: Finance Access Restriction (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | FIN-004 |
| **Title** | Finance Access Restriction |
| **Process Tower** | Finance |
| **Priority** | Critical |
| **Type** | Negative |
| **Owner** | FM |
| **Primary Role** | Sales Manager (acting as unauthorized user) |
| **Supporting Roles** | PA |
| **Preconditions** | Sales Manager user exists with Sales group only; no Finance group assigned |

**Steps:**

1. Log in as Sales Manager
2. Attempt to navigate to Accounting > Customers > Invoices
3. Attempt to create a journal entry via URL manipulation
4. Attempt to access bank reconciliation

**Expected System Result:**

- Access denied for all finance menu items
- URL manipulation returns AccessError or redirect
- No finance data is visible or modifiable

**Expected Business Result:**

- Users without finance permissions cannot view or modify financial records

**Evidence Required:**

- Screenshot of access denied message for each attempt
- Username used for the test

**Defect Logging Rule:**

- Log Severity 1 if any finance data is visible or modifiable
- Log Severity 2 if access is denied but error message is misleading

**Sign-off Rule:**

- FM and PA jointly sign off

---

## 11. Sales Scenarios

### SAL-001: Lead to Quotation

| Field | Value |
|-------|-------|
| **Scenario ID** | SAL-001 |
| **Title** | Lead to Quotation |
| **Process Tower** | Sales |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | SM |
| **Primary Role** | Sales Manager |
| **Supporting Roles** | -- |
| **Preconditions** | CRM module installed; at least one salesperson configured; pipeline stages exist |

**Steps:**

1. Navigate to CRM > My Pipeline
2. Create a new lead with customer name, expected revenue, and source
3. Qualify the lead (move to qualified stage)
4. Click "New Quotation" from the lead
5. Verify customer and opportunity data carry forward

**Expected System Result:**

- Lead is created and visible in pipeline
- Stage transition is recorded
- Quotation is created with pre-filled customer and opportunity link
- Lead status updates to reflect quotation creation

**Expected Business Result:**

- Sales Manager can convert a lead into a quotation without re-entering data

**Evidence Required:**

- Screenshot of lead in pipeline
- Screenshot of quotation with linked opportunity
- Lead and quotation record IDs

**Defect Logging Rule:**

- Log Severity 2 if data does not carry forward
- Log Severity 3 if pipeline view has rendering issues

**Sign-off Rule:**

- SM signs off when at least 2 leads have been converted to quotations

---

### SAL-002: Quotation to Sales Order

| Field | Value |
|-------|-------|
| **Scenario ID** | SAL-002 |
| **Title** | Quotation to Sales Order |
| **Process Tower** | Sales |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | SM |
| **Primary Role** | Sales Manager |
| **Supporting Roles** | FM |
| **Preconditions** | At least one draft quotation exists; products with prices configured |

**Steps:**

1. Open an existing draft quotation
2. Add or verify product lines, quantities, and prices
3. Send quotation to customer (or simulate send)
4. Confirm the quotation (convert to Sales Order)
5. Verify delivery order and/or invoice are generated as configured

**Expected System Result:**

- Quotation moves to Sales Order status
- Sales Order number is assigned
- Downstream documents (delivery order, invoice) are created per workflow configuration
- Inventory reservation occurs if applicable

**Expected Business Result:**

- Sales Manager can confirm a sale and trigger fulfillment and billing workflows

**Evidence Required:**

- Screenshot of confirmed Sales Order
- Screenshot of linked delivery order or invoice
- Sales Order record ID

**Defect Logging Rule:**

- Log Severity 1 if quotation cannot be confirmed
- Log Severity 1 if downstream documents are not created
- Log Severity 2 if inventory reservation fails

**Sign-off Rule:**

- SM signs off when at least 2 quotations have been confirmed end-to-end

---

### SAL-003: Sales Amendment and Cancellation (Exception)

| Field | Value |
|-------|-------|
| **Scenario ID** | SAL-003 |
| **Title** | Sales Amendment and Cancellation |
| **Process Tower** | Sales |
| **Priority** | High |
| **Type** | Exception |
| **Owner** | SM |
| **Primary Role** | Sales Manager |
| **Supporting Roles** | FM |
| **Preconditions** | At least one confirmed Sales Order exists |

**Steps:**

1. Open a confirmed Sales Order
2. Attempt to modify a line (add, remove, change quantity)
3. If locked, cancel the order and recreate
4. Verify downstream documents are updated or cancelled accordingly
5. Verify accounting entries are reversed if invoice was generated

**Expected System Result:**

- Amendment follows configured lock/unlock rules
- Cancellation reverses or cancels downstream documents
- Accounting entries are reversed if applicable
- Audit trail records the change

**Expected Business Result:**

- Sales Manager can handle order changes and cancellations with proper financial impact

**Evidence Required:**

- Screenshot of amended or cancelled order
- Screenshot of reversed/cancelled downstream documents
- Audit trail screenshot

**Defect Logging Rule:**

- Log Severity 1 if cancellation leaves orphaned documents
- Log Severity 2 if accounting reversal is missing

**Sign-off Rule:**

- SM and FM jointly sign off

---

### SAL-004: Sales Permission Boundary (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | SAL-004 |
| **Title** | Sales Permission Boundary |
| **Process Tower** | Sales |
| **Priority** | High |
| **Type** | Negative |
| **Owner** | SM |
| **Primary Role** | Inventory Controller (acting as unauthorized user) |
| **Supporting Roles** | PA |
| **Preconditions** | Inventory Controller user exists with Inventory group only |

**Steps:**

1. Log in as Inventory Controller
2. Attempt to access CRM > My Pipeline
3. Attempt to create a quotation via URL
4. Attempt to confirm a Sales Order via URL

**Expected System Result:**

- Access denied for all sales/CRM actions
- No sales data is visible or modifiable

**Expected Business Result:**

- Users without sales permissions cannot view or modify sales records

**Evidence Required:**

- Screenshot of access denied for each attempt
- Username used

**Defect Logging Rule:**

- Log Severity 1 if any sales data is accessible

**Sign-off Rule:**

- SM and PA jointly sign off

---

## 12. Procurement Scenarios

### PROC-001: Create Purchase Order

| Field | Value |
|-------|-------|
| **Scenario ID** | PROC-001 |
| **Title** | Create Purchase Order |
| **Process Tower** | Procurement |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | PO |
| **Primary Role** | Procurement Officer |
| **Supporting Roles** | -- |
| **Preconditions** | At least one vendor and product exist; purchase module installed |

**Steps:**

1. Navigate to Purchase > Orders
2. Click Create
3. Select vendor
4. Add product lines with quantities and agreed prices
5. Confirm the Purchase Order

**Expected System Result:**

- Purchase Order is created and confirmed
- PO number is auto-assigned
- Receipt (incoming shipment) is created in Inventory
- Vendor is notified (if email configured)

**Expected Business Result:**

- Procurement Officer can issue a formal purchase order to a supplier

**Evidence Required:**

- Screenshot of confirmed PO
- Screenshot of linked receipt in Inventory
- PO record ID

**Defect Logging Rule:**

- Log Severity 1 if PO cannot be confirmed or receipt is not created

**Sign-off Rule:**

- PO signs off when at least 2 purchase orders have been created and confirmed

---

### PROC-002: Purchase Approval and Receipt

| Field | Value |
|-------|-------|
| **Scenario ID** | PROC-002 |
| **Title** | Purchase Approval and Receipt |
| **Process Tower** | Procurement |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | PO |
| **Primary Role** | Procurement Officer |
| **Supporting Roles** | IC, FM |
| **Preconditions** | Purchase approval workflow configured; confirmed PO exists with pending receipt |

**Steps:**

1. If approval workflow is active, submit PO for approval
2. Log in as approver and approve the PO
3. Navigate to Inventory > Receipts
4. Open the receipt linked to the PO
5. Validate the receipt (receive goods)
6. Verify vendor bill can be created from the PO

**Expected System Result:**

- Approval workflow executes correctly
- Receipt is validated and stock is updated
- Vendor bill draft is created or can be created from PO
- Three-way match (PO, receipt, bill) is possible

**Expected Business Result:**

- Procurement Officer can manage the full procure-to-pay cycle with proper controls

**Evidence Required:**

- Screenshot of approval workflow execution
- Screenshot of validated receipt
- Screenshot of vendor bill linked to PO
- PO, receipt, and bill record IDs

**Defect Logging Rule:**

- Log Severity 1 if approval can be bypassed
- Log Severity 1 if receipt does not update stock
- Log Severity 2 if bill creation fails from PO

**Sign-off Rule:**

- PO and FM jointly sign off

---

### PROC-003: Supplier Validation Failure (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | PROC-003 |
| **Title** | Supplier Validation Failure |
| **Process Tower** | Procurement |
| **Priority** | Medium |
| **Type** | Negative |
| **Owner** | PO |
| **Primary Role** | Procurement Officer |
| **Supporting Roles** | -- |
| **Preconditions** | Vendor validation rules configured (e.g., required tax ID, address) |

**Steps:**

1. Attempt to create a Purchase Order for a vendor missing required fields (no tax ID)
2. Attempt to confirm the PO
3. Verify the system prevents confirmation with a clear error

**Expected System Result:**

- System blocks PO confirmation
- Error message clearly states which validation failed
- No PO is confirmed for an incomplete vendor

**Expected Business Result:**

- Procurement cannot issue orders to non-compliant vendors

**Evidence Required:**

- Screenshot of validation error
- Vendor record showing missing field

**Defect Logging Rule:**

- Log Severity 2 if PO can be confirmed despite validation failure
- Log Severity 3 if error message is unclear

**Sign-off Rule:**

- PO signs off

---

## 13. Inventory Scenarios

### INV-001: Receive Goods

| Field | Value |
|-------|-------|
| **Scenario ID** | INV-001 |
| **Title** | Receive Goods |
| **Process Tower** | Inventory |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | IC |
| **Primary Role** | Inventory Controller |
| **Supporting Roles** | PO |
| **Preconditions** | Confirmed PO exists with pending receipt; warehouse configured |

**Steps:**

1. Navigate to Inventory > Receipts
2. Open the pending receipt linked to a PO
3. Enter received quantities (may differ from ordered)
4. Validate the receipt
5. Verify stock levels are updated

**Expected System Result:**

- Receipt is validated
- Stock quantities increase by received amount
- Backorder is created if partial receipt
- Stock valuation is updated

**Expected Business Result:**

- Inventory Controller can receive goods and the system reflects accurate stock levels

**Evidence Required:**

- Screenshot of validated receipt
- Screenshot of updated stock level for the received product
- Receipt record ID

**Defect Logging Rule:**

- Log Severity 1 if stock is not updated after receipt
- Log Severity 2 if backorder is not created for partial receipt

**Sign-off Rule:**

- IC signs off when at least 2 receipts (one full, one partial) are validated

---

### INV-002: Internal Transfer

| Field | Value |
|-------|-------|
| **Scenario ID** | INV-002 |
| **Title** | Internal Transfer |
| **Process Tower** | Inventory |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | IC |
| **Primary Role** | Inventory Controller |
| **Supporting Roles** | -- |
| **Preconditions** | At least two warehouse locations exist; stock available in source location |

**Steps:**

1. Navigate to Inventory > Operations > Transfers
2. Create a new internal transfer
3. Set source and destination locations
4. Add product lines with quantities
5. Validate the transfer
6. Verify stock levels in both locations

**Expected System Result:**

- Transfer is created and validated
- Source location stock decreases
- Destination location stock increases
- Total company stock remains unchanged

**Expected Business Result:**

- Inventory Controller can move stock between locations with full traceability

**Evidence Required:**

- Screenshot of validated transfer
- Screenshots of stock levels at source and destination (before and after)
- Transfer record ID

**Defect Logging Rule:**

- Log Severity 1 if stock levels are incorrect after transfer
- Log Severity 2 if transfer is validated but stock does not move

**Sign-off Rule:**

- IC signs off when at least 1 internal transfer is validated

---

### INV-003: Stock Adjustment (Exception)

| Field | Value |
|-------|-------|
| **Scenario ID** | INV-003 |
| **Title** | Stock Adjustment |
| **Process Tower** | Inventory |
| **Priority** | High |
| **Type** | Exception |
| **Owner** | IC |
| **Primary Role** | Inventory Controller |
| **Supporting Roles** | FM |
| **Preconditions** | Stock exists for at least one product; inventory adjustment feature enabled |

**Steps:**

1. Navigate to Inventory > Operations > Physical Inventory
2. Select a product and location
3. Enter the counted quantity (different from system quantity)
4. Apply the adjustment
5. Verify stock level is updated and adjustment journal entry is created

**Expected System Result:**

- Inventory adjustment is applied
- Stock level matches the counted quantity
- Accounting journal entry for inventory gain/loss is created
- Adjustment is traceable with date, user, and reason

**Expected Business Result:**

- Inventory Controller can correct stock discrepancies with proper financial impact recorded

**Evidence Required:**

- Screenshot of adjustment applied
- Screenshot of updated stock level
- Screenshot of inventory adjustment journal entry
- Adjustment record ID

**Defect Logging Rule:**

- Log Severity 1 if adjustment does not update stock
- Log Severity 2 if journal entry is not created

**Sign-off Rule:**

- IC and FM jointly sign off

---

### INV-004: Restricted Inventory Action (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | INV-004 |
| **Title** | Restricted Inventory Action |
| **Process Tower** | Inventory |
| **Priority** | High |
| **Type** | Negative |
| **Owner** | IC |
| **Primary Role** | Sales Manager (acting as unauthorized user) |
| **Supporting Roles** | PA |
| **Preconditions** | Sales Manager user has no inventory permissions |

**Steps:**

1. Log in as Sales Manager
2. Attempt to access Inventory > Operations
3. Attempt to validate a receipt via URL
4. Attempt to perform a stock adjustment via URL

**Expected System Result:**

- Access denied for all inventory operations
- No inventory data is modifiable

**Expected Business Result:**

- Users without inventory permissions cannot alter stock records

**Evidence Required:**

- Screenshot of access denied for each attempt
- Username used

**Defect Logging Rule:**

- Log Severity 1 if any inventory action succeeds

**Sign-off Rule:**

- IC and PA jointly sign off

---

## 14. Projects Scenarios

### PROJ-001: Create Project and Task

| Field | Value |
|-------|-------|
| **Scenario ID** | PROJ-001 |
| **Title** | Create Project and Task |
| **Process Tower** | Projects |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | PM |
| **Primary Role** | Project Manager |
| **Supporting Roles** | -- |
| **Preconditions** | Project module installed; at least one team member exists |

**Steps:**

1. Navigate to Project > Projects
2. Create a new project with name, description, and assigned manager
3. Create at least two tasks under the project
4. Assign tasks to team members
5. Set deadlines and priorities
6. Verify Kanban view displays correctly

**Expected System Result:**

- Project is created with unique identifier
- Tasks are linked to the project
- Assignments and deadlines are recorded
- Kanban stages reflect task status

**Expected Business Result:**

- Project Manager can set up and organize a project with tasks and assignments

**Evidence Required:**

- Screenshot of project with tasks in Kanban view
- Project and task record IDs

**Defect Logging Rule:**

- Log Severity 2 if tasks cannot be assigned or deadlines fail to save
- Log Severity 3 if Kanban rendering has issues

**Sign-off Rule:**

- PM signs off when at least 1 project with 2+ tasks is created

---

### PROJ-002: Time and Cost Capture

| Field | Value |
|-------|-------|
| **Scenario ID** | PROJ-002 |
| **Title** | Time and Cost Capture |
| **Process Tower** | Projects |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | PM |
| **Primary Role** | Project Manager |
| **Supporting Roles** | FM |
| **Preconditions** | Timesheet module installed; project with tasks exists; team member assigned |

**Steps:**

1. Log in as assigned team member
2. Navigate to a task and log timesheet hours
3. Log in as Project Manager
4. Review timesheet entries for the project
5. Verify cost calculation based on employee rate
6. Verify project profitability view (if configured)

**Expected System Result:**

- Timesheet entries are recorded against the task
- Cost is calculated using the employee's hourly rate
- Project overview shows total hours and cost
- Profitability metrics update (if module configured)

**Expected Business Result:**

- Project Manager can track time and cost against projects for billing and reporting

**Evidence Required:**

- Screenshot of timesheet entries on the task
- Screenshot of project cost/profitability summary
- Timesheet record IDs

**Defect Logging Rule:**

- Log Severity 2 if cost calculation is incorrect
- Log Severity 2 if timesheet entries do not appear on project summary

**Sign-off Rule:**

- PM signs off when timesheet logging and cost calculation are verified for at least 1 project

---

### PROJ-003: Invalid State Transition (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | PROJ-003 |
| **Title** | Invalid State Transition |
| **Process Tower** | Projects |
| **Priority** | Medium |
| **Type** | Negative |
| **Owner** | PM |
| **Primary Role** | Project Manager |
| **Supporting Roles** | -- |
| **Preconditions** | Project with stage restrictions configured (if applicable) |

**Steps:**

1. Attempt to move a task from Done back to New (if restricted)
2. Attempt to delete a project with active tasks
3. Attempt to close a project with incomplete mandatory tasks

**Expected System Result:**

- Restricted state transitions are blocked with clear messages
- Deletion of projects with active tasks is prevented or requires confirmation
- Business rules enforce valid workflow progression

**Expected Business Result:**

- Project data integrity is maintained; invalid operations are blocked

**Evidence Required:**

- Screenshot of blocked action with error message
- Task/project record IDs

**Defect Logging Rule:**

- Log Severity 2 if invalid transitions are allowed without warning
- Log Severity 3 if error messages are unclear

**Sign-off Rule:**

- PM signs off

---

## 15. Admin Scenarios

### ADM-001: Create and Provision User

| Field | Value |
|-------|-------|
| **Scenario ID** | ADM-001 |
| **Title** | Create and Provision User |
| **Process Tower** | Admin |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | PA |
| **Primary Role** | Platform Admin |
| **Supporting Roles** | -- |
| **Preconditions** | Admin access to Settings > Users |

**Steps:**

1. Navigate to Settings > Users & Companies > Users
2. Create a new user with name, email, and login
3. Assign appropriate access groups (e.g., Sales / User)
4. Save and send invitation (or set password)
5. Log in as the new user
6. Verify access matches assigned groups

**Expected System Result:**

- User is created with correct group memberships
- Login works with assigned credentials
- Menu items and data access match the assigned groups
- User appears in the user list

**Expected Business Result:**

- Platform Admin can onboard a new team member with correct permissions in one step

**Evidence Required:**

- Screenshot of user creation form with groups assigned
- Screenshot of successful login as new user
- Screenshot showing accessible menu items match group assignment
- User record ID

**Defect Logging Rule:**

- Log Severity 1 if user cannot log in
- Log Severity 1 if access does not match assigned groups
- Log Severity 2 if invitation email fails

**Sign-off Rule:**

- PA signs off when at least 2 users are created with different group combinations and verified

---

### ADM-002: Modify and Remove Access

| Field | Value |
|-------|-------|
| **Scenario ID** | ADM-002 |
| **Title** | Modify and Remove Access |
| **Process Tower** | Admin |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | PA |
| **Primary Role** | Platform Admin |
| **Supporting Roles** | -- |
| **Preconditions** | At least one active user with assigned groups |

**Steps:**

1. Open an existing user
2. Change their group assignment (e.g., add Finance, remove Sales)
3. Save
4. Log in as the modified user
5. Verify new access is granted and old access is revoked
6. Archive (deactivate) the user
7. Attempt to log in as the archived user

**Expected System Result:**

- Group changes take effect immediately (or after re-login)
- New menus/data access reflect updated groups
- Previous group access is revoked
- Archived user cannot log in

**Expected Business Result:**

- Platform Admin can modify permissions and offboard users with immediate effect

**Evidence Required:**

- Screenshot of updated user groups
- Screenshot showing new access after modification
- Screenshot of login failure after archival
- User record ID

**Defect Logging Rule:**

- Log Severity 1 if archived user can still log in
- Log Severity 1 if old access is not revoked after group removal
- Log Severity 2 if group change requires system restart

**Sign-off Rule:**

- PA signs off when both modification and archival are demonstrated

---

### ADM-003: Unauthorized Admin Attempt (Negative)

| Field | Value |
|-------|-------|
| **Scenario ID** | ADM-003 |
| **Title** | Unauthorized Admin Attempt |
| **Process Tower** | Admin |
| **Priority** | Critical |
| **Type** | Negative |
| **Owner** | PA |
| **Primary Role** | Sales Manager (acting as unauthorized user) |
| **Supporting Roles** | -- |
| **Preconditions** | Sales Manager has no admin/settings access |

**Steps:**

1. Log in as Sales Manager
2. Attempt to access Settings > Users
3. Attempt to create a user via URL manipulation
4. Attempt to modify another user's groups via URL
5. Attempt to access Settings > Technical menu

**Expected System Result:**

- Access denied for all admin operations
- URL manipulation returns AccessError
- No user data is modifiable by non-admin

**Expected Business Result:**

- Only Platform Admins can manage users and system settings

**Evidence Required:**

- Screenshot of access denied for each attempt
- Username used

**Defect Logging Rule:**

- Log Severity 1 if any admin action succeeds for non-admin user

**Sign-off Rule:**

- PA signs off

---

## 16. Cross-Tower Exception Scenarios

### X-001: Order-to-Cash Full Cycle

| Field | Value |
|-------|-------|
| **Scenario ID** | X-001 |
| **Title** | Order-to-Cash Full Cycle |
| **Process Tower** | Cross-Tower (Sales + Inventory + Finance) |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | SM |
| **Primary Role** | Sales Manager |
| **Supporting Roles** | IC, FM |
| **Preconditions** | Product with stock exists; customer exists; all modules installed |

**Steps:**

1. Create and confirm a Sales Order (SM)
2. Process the delivery order — pick, pack, ship (IC)
3. Create and validate the customer invoice (FM)
4. Register customer payment (FM)
5. Verify all documents are linked and reconciled

**Expected System Result:**

- Sales Order, Delivery, Invoice, and Payment are all linked
- Stock is decremented
- Revenue is recognized
- Customer balance is zero after payment

**Expected Business Result:**

- Complete order-to-cash cycle works end-to-end across towers

**Evidence Required:**

- Screenshots of each document in the chain
- Record IDs for SO, DO, INV, PMT
- Customer balance screenshot

**Defect Logging Rule:**

- Log Severity 1 if any link in the chain breaks
- Log Severity 2 if reconciliation fails

**Sign-off Rule:**

- SM, IC, and FM jointly sign off

---

### X-002: Procure-to-Pay Full Cycle

| Field | Value |
|-------|-------|
| **Scenario ID** | X-002 |
| **Title** | Procure-to-Pay Full Cycle |
| **Process Tower** | Cross-Tower (Procurement + Inventory + Finance) |
| **Priority** | Critical |
| **Type** | Positive |
| **Owner** | PO |
| **Primary Role** | Procurement Officer |
| **Supporting Roles** | IC, FM |
| **Preconditions** | Vendor exists; product exists; all modules installed |

**Steps:**

1. Create and confirm a Purchase Order (PO)
2. Receive goods against the PO (IC)
3. Create vendor bill from PO (FM)
4. Register payment on the vendor bill (FM)
5. Verify three-way match and vendor balance

**Expected System Result:**

- PO, Receipt, Bill, and Payment are all linked
- Stock is incremented
- Expense is recognized
- Vendor balance is zero after payment

**Expected Business Result:**

- Complete procure-to-pay cycle works end-to-end across towers

**Evidence Required:**

- Screenshots of each document in the chain
- Record IDs for PO, RCV, BILL, PMT
- Vendor balance screenshot

**Defect Logging Rule:**

- Log Severity 1 if any link in the chain breaks

**Sign-off Rule:**

- PO, IC, and FM jointly sign off

---

### X-003: Project Cost Allocation to Finance

| Field | Value |
|-------|-------|
| **Scenario ID** | X-003 |
| **Title** | Project Cost Allocation to Finance |
| **Process Tower** | Cross-Tower (Projects + Finance) |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | PM |
| **Primary Role** | Project Manager |
| **Supporting Roles** | FM |
| **Preconditions** | Project with analytic account exists; timesheet entries logged; analytic accounting enabled |

**Steps:**

1. Verify timesheet entries exist for a project (PM)
2. Navigate to Accounting > Reporting > Analytic (FM)
3. Verify project costs appear under the correct analytic account
4. Verify cost totals match timesheet hours multiplied by rate

**Expected System Result:**

- Analytic account reflects project costs
- Cost amounts match timesheet calculations
- Report is filterable by project/analytic account

**Expected Business Result:**

- Finance can report on project costs using analytic accounting

**Evidence Required:**

- Screenshot of analytic report filtered by project
- Screenshot of timesheet total vs. analytic cost comparison

**Defect Logging Rule:**

- Log Severity 2 if analytic costs do not match timesheets
- Log Severity 3 if report filtering is limited

**Sign-off Rule:**

- PM and FM jointly sign off

---

### X-004: User Offboarding Cascade

| Field | Value |
|-------|-------|
| **Scenario ID** | X-004 |
| **Title** | User Offboarding Cascade |
| **Process Tower** | Cross-Tower (Admin + all towers) |
| **Priority** | High |
| **Type** | Exception |
| **Owner** | PA |
| **Primary Role** | Platform Admin |
| **Supporting Roles** | SM, FM |
| **Preconditions** | User to be offboarded has active records (sales orders, tasks, etc.) |

**Steps:**

1. Archive the user (PA)
2. Verify user cannot log in
3. Verify records owned by the user are still accessible to other authorized users
4. Verify assigned tasks/orders can be reassigned
5. Verify no data is lost or orphaned

**Expected System Result:**

- User is archived and cannot authenticate
- All records remain accessible
- Records can be reassigned to other users
- No cascade deletion of business data

**Expected Business Result:**

- Offboarding a user does not disrupt business operations or lose data

**Evidence Required:**

- Screenshot of archived user
- Screenshot of login failure
- Screenshot of records still accessible under a different user
- Screenshot of reassigned record

**Defect Logging Rule:**

- Log Severity 1 if records are deleted or inaccessible after archival
- Log Severity 1 if user can still log in

**Sign-off Rule:**

- PA signs off with confirmation from SM and FM that their tower data is intact

---

### X-005: Concurrent Multi-User Operation

| Field | Value |
|-------|-------|
| **Scenario ID** | X-005 |
| **Title** | Concurrent Multi-User Operation |
| **Process Tower** | Cross-Tower (all) |
| **Priority** | High |
| **Type** | Positive |
| **Owner** | UC |
| **Primary Role** | UAT Coordinator |
| **Supporting Roles** | SM, FM, IC, PO |
| **Preconditions** | All business roles logged in simultaneously; staging environment stable |

**Steps:**

1. SM creates a Sales Order while FM posts an invoice simultaneously
2. IC validates a receipt while PO confirms a Purchase Order simultaneously
3. PA modifies user permissions while other users are active
4. Verify no record locking errors, data corruption, or session conflicts

**Expected System Result:**

- All concurrent operations complete without error
- No data corruption or unexpected locking
- Each user's session is independent
- Database integrity constraints are maintained

**Expected Business Result:**

- The system supports normal multi-user business operations without conflict

**Evidence Required:**

- Timestamps of each concurrent action
- Record IDs from each operation
- Confirmation of no error logs in `odoo_staging` server log

**Defect Logging Rule:**

- Log Severity 1 if data corruption occurs
- Log Severity 2 if record locking prevents normal operations

**Sign-off Rule:**

- UC signs off with confirmation from all participating roles

---

## 17. Scenario Execution Register

Use this template to track execution of each scenario during UAT.

| Scenario ID | Title | Tester | Date (UTC) | Status | Defect IDs | Evidence Path | Notes |
|-------------|-------|--------|------------|--------|------------|---------------|-------|
| FIN-001 | Create/Validate Invoice | | | Not Run | | | |
| FIN-002 | Process Supplier Bill | | | Not Run | | | |
| FIN-003 | Approval-Controlled Journal | | | Not Run | | | |
| FIN-004 | Finance Access Restriction | | | Not Run | | | |
| SAL-001 | Lead to Quotation | | | Not Run | | | |
| SAL-002 | Quotation to Sales Order | | | Not Run | | | |
| SAL-003 | Sales Amendment/Cancellation | | | Not Run | | | |
| SAL-004 | Sales Permission Boundary | | | Not Run | | | |
| PROC-001 | Create PO | | | Not Run | | | |
| PROC-002 | Purchase Approval/Receipt | | | Not Run | | | |
| PROC-003 | Supplier Validation Failure | | | Not Run | | | |
| INV-001 | Receive Goods | | | Not Run | | | |
| INV-002 | Internal Transfer | | | Not Run | | | |
| INV-003 | Stock Adjustment | | | Not Run | | | |
| INV-004 | Restricted Inventory Action | | | Not Run | | | |
| PROJ-001 | Create Project/Task | | | Not Run | | | |
| PROJ-002 | Time/Cost Capture | | | Not Run | | | |
| PROJ-003 | Invalid State Transition | | | Not Run | | | |
| ADM-001 | Create/Provision User | | | Not Run | | | |
| ADM-002 | Modify/Remove Access | | | Not Run | | | |
| ADM-003 | Unauthorized Admin Attempt | | | Not Run | | | |
| X-001 | Order-to-Cash Full Cycle | | | Not Run | | | |
| X-002 | Procure-to-Pay Full Cycle | | | Not Run | | | |
| X-003 | Project Cost to Finance | | | Not Run | | | |
| X-004 | User Offboarding Cascade | | | Not Run | | | |
| X-005 | Concurrent Multi-User | | | Not Run | | | |

---

## 18. Process-Tower Sign-off

| Process Tower | Owner Role | Owner Name | Sign-off Date | Status | Conditions / Notes |
|---------------|-----------|------------|---------------|--------|--------------------|
| Finance | FM | | | Pending | |
| Sales | SM | | | Pending | |
| Procurement | PO | | | Pending | |
| Inventory | IC | | | Pending | |
| Projects | PM | | | Pending | |
| Admin | PA | | | Pending | |

---

## 19. Consolidated UAT Exit Summary

| Item | Value |
|------|-------|
| **UAT Start Date** | |
| **UAT End Date** | |
| **Total Scenarios** | 26 |
| **Passed** | |
| **Passed with Accepted Workaround** | |
| **Failed** | |
| **Blocked** | |
| **Not Run** | |
| **Open Sev-1 Defects** | |
| **Open Sev-2 Defects** | |
| **All Process Towers Signed Off** | Yes / No |
| **UAT Coordinator** | |
| **Platform Admin** | |
| **Exit Decision** | Go / No-Go / Conditional Go |
| **Exit Decision Date** | |
| **Conditions (if Conditional)** | |

---

*Last updated: 2026-04-05*
