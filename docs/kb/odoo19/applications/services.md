# Odoo 19 Services Applications

## Project

**Model:** `project.project`, `project.task`

- **Structure:** Projects contain Tasks. Tasks can have Sub-tasks and Dependencies.
- **Features:**
  - **Milestones:** Track major progress points (`project.milestone`).
  - **Profitability:** Tracks Costs (Timesheets/Bills) vs Revenues (Sales/Invoices).
  - **Sharing:** Portal access for customers to view tasks/documents.

## Timesheets

**Model:** `account.analytic.line`

- **Integration:** Linked to Projects, Tasks, and Employees.
- **Billing:**
  - **Billable Time:** Invoiced to customers based on SO lines.
  - **Non-billable:** Internal tracking.
- **Validation:** Manager approval workflows.

## Field Service

**Model:** `project.task` (specialized)

- **Workflow:** Plan -> Execute -> Sign -> Invoice.
- **Worksheets:** Custom forms (`x_...` models) for on-site data collection.
- **Inventory:** Track parts used during service (`stock.move`).

## Helpdesk

**Model:** `helpdesk.ticket`

- **Teams:** Organize tickets by functionality/region (e.g., "Support", "Returns").
- **SLA:** Service Level Agreements for "Time to Value" or "Time to Close".
- **Channels:** Email (alias), Website Form, Live Chat.

## Planning

**Model:** `planning.slot`

- **Resource Management:** Shift scheduling for Employees or Material resources.
- **Roles:** Assign shifts based on specific roles (e.g., "Developer", "Driver").
- **Publishing:** Draft shifts are invisible until published to employees.

## Appointments

**Model:** `calendar.appointment.type`

- **Online Booking:** Customers schedule meetings based on availability.
- **Resources:** Book specific resources (rooms, tables) or staff types.
- **Calendar Sync:** Integrates with Google/Outlook/Odoo Calendar.

## Source Links

- [Project](https://www.odoo.com/documentation/19.0/applications/services/project.html)
- [Timesheets](https://www.odoo.com/documentation/19.0/applications/services/timesheets.html)
- [Field Service](https://www.odoo.com/documentation/19.0/applications/services/field_service.html)
- [Helpdesk](https://www.odoo.com/documentation/19.0/applications/services/helpdesk.html)
- [Planning](https://www.odoo.com/documentation/19.0/applications/services/planning.html)
- [Appointments](https://www.odoo.com/documentation/19.0/applications/productivity/appointments.html)
