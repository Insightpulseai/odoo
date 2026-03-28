# Gmail Add-on Capability Model

> Taxonomy of actions the add-on can perform, organized by Gmail surface and Odoo operation type.

---

## Capability Classes

### Class 1: Read Actions (No Odoo Mutation)

These actions retrieve data from Odoo and display it in Gmail cards. They require only read access to the mapped Odoo user's permitted records.

| Capability | Gmail Surface | Odoo Model(s) | Description |
|-----------|---------------|----------------|-------------|
| **Contact lookup** | Contextual message | `res.partner` | Match email sender to Odoo partner. Display name, company, phone, tags, and internal notes summary. |
| **Company info** | Contextual message | `res.partner` (company type) | Show parent company details when sender is a contact under a company. |
| **Related leads** | Contextual message | `crm.lead` | List open leads/opportunities associated with the matched partner. |
| **Related invoices** | Contextual message | `account.move` | Show recent invoice summary (number, amount, status) for the matched partner. |
| **Related tasks** | Contextual message | `project.task` | Show active tasks assigned to or involving the matched partner. |
| **Session status** | Homepage | `res.users` | Display current Odoo connection status, authenticated user, and session health. |

### Class 2: Create/Link Actions (Odoo Write)

These actions create new records or link existing records in Odoo. They require write access and are classified as sensitive operations with audit requirements.

| Capability | Gmail Surface | Odoo Model | Description |
|-----------|---------------|------------|-------------|
| **Create lead** | Contextual message | `crm.lead` | Create a new CRM lead pre-populated with sender email, subject line, and email body excerpt. |
| **Create ticket** | Contextual message | `project.task` | Create a task/ticket in a configured project, linked to the sender's partner record. |
| **Create expense** | Contextual message | `hr.expense` | Create an expense entry from a receipt email. Subject becomes description, optional OCR on attachments. |
| **Link email to record** | Contextual message | `mail.message` | Log the email thread as a note/message on an existing Odoo record selected by the user. |
| **Create contact** | Contextual message | `res.partner` | Create a new partner record from the sender's email address when no match exists. |

### Class 3: Log Actions (Odoo Write, Append-Only)

These actions append information to existing Odoo records. They are lower-risk than create actions but still require audit logging.

| Capability | Gmail Surface | Odoo Model | Description |
|-----------|---------------|------------|-------------|
| **Log email as note** | Contextual message | `mail.message` | Append the email subject and body excerpt as a note on a partner, lead, or task. |
| **Log activity** | Contextual message | `mail.activity` | Schedule a follow-up activity on an Odoo record from the email context. |

---

## Non-Goals

The following are explicitly out of scope for this add-on:

- **Full ERP UI**: The add-on does not replicate Odoo forms, list views, or dashboards. Users are directed to the Odoo web UI for complex operations.
- **Bulk operations**: No batch create, batch update, or import/export workflows.
- **Email sending from Odoo**: The add-on does not send email on behalf of Odoo. Odoo's own mail server handles outbound.
- **Attachment storage in Odoo**: Email attachments are not automatically uploaded to Odoo. Receipt OCR is opt-in and processes only the image/PDF, not the full attachment lifecycle.
- **Calendar sync**: Calendar integration is handled separately (Google Calendar add-on scope, not this add-on).
- **Chat/messaging**: No real-time messaging or Discuss integration through the Gmail add-on.

---

## Host-Safe vs. Escalation-to-Web Flows

Google Workspace add-ons render cards inside Gmail. Complex workflows that exceed card UI capabilities must escalate to the Odoo web application.

### Host-Safe (Completable Inside Gmail)

- Contact lookup and display
- Create lead with pre-filled fields (subject, sender, excerpt)
- Log email as note (single button action)
- Create expense from receipt (simple form)
- View related record summaries

### Escalation to Odoo Web

These actions open `erp.insightpulseai.com` in a new browser tab:

- Edit a lead's full details after creation
- View complete invoice or payment history
- Navigate the Odoo pipeline/kanban
- Manage partner record fields beyond what the card shows
- Any operation requiring multi-step form submission

The escalation pattern uses `OpenLink` card actions pointed at the specific Odoo record URL:
`https://erp.insightpulseai.com/web#id={record_id}&model={model}&view_type=form`

---

## Capability-to-Surface Matrix

| Capability | Homepage | Contextual Message | Compose Action |
|-----------|----------|-------------------|----------------|
| Contact lookup | -- | Primary | -- |
| Company info | -- | Primary | -- |
| Related leads | -- | Primary | -- |
| Related invoices | -- | Primary | -- |
| Related tasks | -- | Primary | -- |
| Session status | Primary | -- | -- |
| Create lead | -- | Primary | Secondary |
| Create ticket | -- | Primary | -- |
| Create expense | -- | Primary | -- |
| Link email to record | -- | Primary | -- |
| Create contact | -- | Primary | -- |
| Log email as note | -- | Primary | -- |
| Log activity | -- | Primary | -- |
