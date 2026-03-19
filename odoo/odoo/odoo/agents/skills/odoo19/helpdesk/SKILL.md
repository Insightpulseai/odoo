---
name: helpdesk
description: Ticket-based customer support with SLA policies, multi-channel intake, and after-sales services
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# helpdesk -- Odoo 19.0 Skill Reference

## Overview

Odoo Helpdesk is a ticket-based customer support application. Multiple teams can be managed from one dashboard, each with its own pipeline, SLA policies, and assignment rules. Tickets are received via email, live chat, website forms, or manual creation. The module integrates with Sales (time billing), Timesheets (time tracking), Project (task tracking), Inventory (returns), Accounting (refunds), Field Service (on-site interventions), and CRM (opportunity conversion). Used by support teams, customer service managers, and after-sales staff.

## Key Concepts

- **Helpdesk Team**: A support team with its own pipeline, SLA policies, channels, and assignment rules.
- **Ticket**: A customer support request with a priority, assignee, stage, and optional SLA deadline.
- **SLA Policy (Service Level Agreement)**: A rule defining time-based targets for ticket resolution (e.g., "reach Solved stage within 8 working hours").
- **Stage**: A pipeline column for ticket progression (e.g., New, In Progress, Customer Feedback, Solved).
- **Priority**: 0-3 star rating on tickets (Low, Medium, High, Urgent).
- **Automatic Assignment**: Round-robin assignment to team members based on equal ticket count, equal open tickets, or tag-based expertise.
- **After-Sales Services**: Integrated actions from tickets: Refunds (credit notes), Coupons, Returns (reverse transfers), Repairs, Field Service.
- **Ticket Channel**: How tickets are received -- Email Alias, Live Chat, Website Form.
- **Customer Rating**: 1-5 satisfaction rating collected after ticket resolution.

## Core Workflows

### 1. Create a Helpdesk Team

1. Navigate to **Helpdesk > Configuration > Helpdesk Teams**, click **New**.
2. Enter team **Name** and description.
3. Configure **Visibility**: Private, Company, or Public (portal users).
4. Enable **Automatic Assignment** and select the method: equal ticket count, equal open tickets, or tag-based dispatch.
5. Add **Team Members**.
6. Under **Channels**, enable Email Alias, Live Chat, and/or Website Form.
7. Under **Performance**, enable **SLA Policies**.
8. Under **After-Sales**, enable Refunds, Coupons, Returns, Repairs, and/or Field Service as needed.

### 2. Receive and Manage Tickets

1. Tickets arrive via configured channels (email, live chat `/ticket` command, website form, manual creation).
2. Tickets appear in the team's Kanban pipeline.
3. Assignees work the ticket and move it through stages.
4. Set priority (0-3 stars) to influence SLA deadlines and pipeline ordering.
5. Close tickets by moving them to a **folded** stage (marks as closed).

### 3. Apply SLA Policies

1. Navigate to **Helpdesk > Configuration > SLA Policies**, click **New**.
2. Define **Criteria**: Helpdesk Team (required), Priority, Tags, Customers, Services.
3. Set **Target**: **Reach Stage** (e.g., Solved) within a specified time.
4. Optionally define **Excluding Stages** (time in these stages is not counted).
5. When a ticket matches SLA criteria, a deadline is calculated and shown on the ticket.
6. SLA tags turn green (satisfied) or red (failed) based on deadline compliance.

### 4. Track and Bill Time

1. Enable **Timesheets** and **Time Billing** on the team settings.
2. Select or create a **Project** for timesheet entries.
3. On the ticket, use the **Timesheets** tab to log time.
4. Link tickets to a Sales Order Item (prepaid or post-paid service).
5. Invoice via the linked Sales Order once work is completed.

### 5. Process After-Sales Actions

1. **Refund**: Click **Refund** on the ticket, select invoice(s) to reverse, click **Reverse**.
2. **Coupon**: Click **Coupon**, select a coupon program, optionally set expiration, send to customer.
3. **Return**: Click **Return**, select delivery/SO, adjust quantities, click **Return** or **Return for Exchange**.
4. **Repair**: Click **Repair**, fill in product/customer/schedule details, click **Confirm Repair**.
5. **Field Service**: Click **Plan Intervention**, set project and worksheet template, click **Create Task**.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `helpdesk.team` | Helpdesk teams |
| `helpdesk.ticket` | Support tickets |
| `helpdesk.stage` | Pipeline stages |
| `helpdesk.sla` | SLA policies |
| `helpdesk.sla.status` | SLA status per ticket |
| `helpdesk.tag` | Ticket tags |

### Key Fields on `helpdesk.ticket`

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Ticket title |
| `team_id` | Many2one | Helpdesk team |
| `user_id` | Many2one | Assigned user |
| `partner_id` | Many2one | Customer |
| `stage_id` | Many2one | Current stage |
| `priority` | Selection | `0`-`3` (Low to Urgent) |
| `sla_deadline` | Datetime | Earliest SLA deadline |
| `sla_status_ids` | One2many | SLA statuses for this ticket |
| `sale_order_id` | Many2one | Linked sales order |
| `sale_line_id` | Many2one | Linked SO line item |
| `timesheet_ids` | One2many | Timesheet entries |
| `tag_ids` | Many2many | Tags |

### Key Fields on `helpdesk.sla`

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | SLA name |
| `team_id` | Many2one | Helpdesk team |
| `priority` | Selection | Minimum priority for SLA to apply |
| `tag_ids` | Many2many | Tag criteria |
| `partner_ids` | Many2many | Customer criteria |
| `stage_id` | Many2one | Target stage (Reach Stage) |
| `exclude_stage_ids` | Many2many | Stages excluded from time calculation |
| `time` | Float | Time target (hours) |
| `company_id` | Many2one | Company |

### Reports

| Report | Path | Description |
|--------|------|-------------|
| Tickets Analysis | Reporting > Tickets Analysis | Ticket counts, response times, hours open |
| SLA Status Analysis | Reporting > SLA Status Analysis | SLA pass/fail rates by team, pivot/graph/cohort views |
| Customer Ratings | Reporting > Customer Ratings | Satisfaction scores with comments |

### Menu Paths

- Dashboard: `Helpdesk > Dashboard`
- Tickets: `Helpdesk > Tickets > All Tickets / My Tickets`
- Configuration: `Helpdesk > Configuration > Helpdesk Teams / Stages / SLA Policies`
- Reporting: `Helpdesk > Reporting > Tickets Analysis / SLA Status Analysis / Customer Ratings`

## API / RPC Patterns

<!-- TODO: Helpdesk-specific external API examples not found in docs -->

Standard ORM access:

```python
# Search open tickets for a team
env['helpdesk.ticket'].search([('team_id', '=', team_id), ('stage_id.fold', '=', False)])

# Create a ticket
env['helpdesk.ticket'].create({
    'name': 'Cannot connect to WiFi',
    'team_id': team_id,
    'partner_id': customer_id,
    'priority': '2',
})
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- SLA Policies feature is enabled by default on newly created teams.
- Ticket merging requires the **Data Cleaning** app to be installed.
- Converting tickets to CRM opportunities requires the **CRM** app. If Leads are enabled in CRM, the button reads "Convert to Lead".
- After-sales features (Refunds, Returns, Repairs, Field Service) each require their respective apps to be installed.

## Common Pitfalls

- **Folded stage = closed**: Tickets are only considered "closed" when they reach a stage with **Folded in Kanban** enabled. Simply dragging to the last stage does not close the ticket if that stage is not folded.
- **SLA priority matching**: SLA policies with no priority selection only apply to **Low priority** (0 stars) tickets. You must explicitly select higher priority levels for SLAs to match.
- **Automatic assignment with no members**: If the team members field is left empty, all employees with proper access rights are included in assignment. This may assign tickets to unintended users.
- **Tag-based dispatch requires tags on tickets**: If a ticket has no tag and tag-based dispatch is active, the ticket remains unassigned.
- **After-sales module installations**: Enabling after-sales features can trigger installation of additional apps (Accounting, Inventory, Repairs, Field Service), which may affect pricing on One-App-Free databases.
