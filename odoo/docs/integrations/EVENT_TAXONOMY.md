# IPAI Event Taxonomy - Expense, Equipment, Finance PPM

**Purpose**: Canonical event definitions for Odoo → Supabase integration bus

---

## Event Structure

All events follow this schema:

```json
{
  "event_type": "expense.submitted",
  "aggregate_type": "expense",
  "aggregate_id": "12345",
  "payload": {
    "amount": 1000.00,
    "currency": "PHP",
    "employee_id": 42,
    "employee_name": "John Doe",
    "description": "Client dinner",
    "date": "2026-01-22",
    "status": "submit",
    "metadata": {}
  }
}
```

---

## 1. Expense Events (hr.expense)

### 1.1 expense.submitted
**Trigger**: Expense moves to `submit` state (employee submits for approval)
**Aggregate**: expense
**Payload**:
```json
{
  "expense_id": 12345,
  "employee_id": 42,
  "employee_name": "John Doe",
  "employee_code": "EMP001",
  "amount": 1000.00,
  "currency": "PHP",
  "description": "Client dinner - Makati",
  "date": "2026-01-22",
  "category": "Meals & Entertainment",
  "receipt_url": "https://...",
  "submitted_at": "2026-01-22T10:30:00Z",
  "status": "submit"
}
```
**n8n Action**: Send Mattermost notification to approver

### 1.2 expense.approved
**Trigger**: Expense approved by manager (state: `approve`)
**Payload**: Same as expense.submitted + approval metadata
```json
{
  ...
  "approved_by": 7,
  "approved_by_name": "Finance Manager",
  "approved_at": "2026-01-22T11:00:00Z",
  "status": "approve"
}
```
**n8n Action**: Queue for payment processing

### 1.3 expense.rejected
**Trigger**: Expense rejected by approver
**Payload**: Same + rejection reason
```json
{
  ...
  "rejected_by": 7,
  "rejected_by_name": "Finance Manager",
  "rejected_at": "2026-01-22T11:05:00Z",
  "rejection_reason": "Missing receipt",
  "status": "cancel"
}
```
**n8n Action**: Notify employee via Mattermost

### 1.4 expense.paid
**Trigger**: Expense marked as paid (payment journal entry posted)
**Payload**: Same + payment details
```json
{
  ...
  "paid_at": "2026-01-25T14:00:00Z",
  "payment_method": "Bank Transfer",
  "payment_reference": "PMT/2026/00123",
  "status": "done"
}
```
**n8n Action**: Send payment confirmation to employee

---

## 2. Equipment/Asset Events (maintenance.equipment)

### 2.1 asset.reserved
**Trigger**: Asset booking created (custom field: `booking_state = 'reserved'`)
**Aggregate**: asset_booking
**Payload**:
```json
{
  "booking_id": 67890,
  "asset_id": 15,
  "asset_name": "MacBook Pro 14\" M3",
  "asset_category": "Laptop",
  "reserved_by": 42,
  "reserved_by_name": "John Doe",
  "reserved_by_email": "john.doe@tbwa.ph",
  "reserved_from": "2026-01-25",
  "reserved_to": "2026-01-27",
  "purpose": "Client presentation - BGC office",
  "booking_state": "reserved"
}
```
**n8n Action**: Send confirmation email + add to shared calendar

### 2.2 asset.checked_out
**Trigger**: Asset physically handed over (`booking_state = 'checked_out'`)
**Payload**: Same + checkout metadata
```json
{
  ...
  "checked_out_at": "2026-01-25T09:00:00Z",
  "checked_out_by": 7,
  "checked_out_by_name": "IT Admin",
  "booking_state": "checked_out"
}
```
**n8n Action**: Update asset status in inventory system

### 2.3 asset.checked_in
**Trigger**: Asset returned (`booking_state = 'returned'`)
**Payload**: Same + return condition
```json
{
  ...
  "checked_in_at": "2026-01-27T17:00:00Z",
  "checked_in_by": 7,
  "condition": "good",
  "condition_notes": "Minor scratches on casing",
  "booking_state": "returned"
}
```
**n8n Action**: Trigger maintenance check if condition != "good"

### 2.4 asset.overdue
**Trigger**: Cron job detects `reserved_to < today()` and `booking_state != 'returned'`
**Payload**: Same + overdue days
```json
{
  ...
  "overdue_days": 2,
  "escalation_level": 1,
  "last_reminder_sent": "2026-01-28T08:00:00Z"
}
```
**n8n Action**: Send escalating reminders (employee → manager → IT)

---

## 3. Finance PPM Events (project.task + ipai_finance_ppm)

### 3.1 finance_task.created
**Trigger**: Finance task auto-created from logframe/BIR schedule
**Aggregate**: finance_task
**Payload**:
```json
{
  "task_id": 100,
  "task_code": "BIR-1601C-2026-01-RIM",
  "task_name": "BIR 1601-C Preparation - January 2026",
  "finance_logframe_id": 5,
  "bir_schedule_id": 12,
  "bir_form": "1601-C",
  "period_covered": "2026-01",
  "employee_code": "RIM",
  "responsible_user_id": 42,
  "responsible_user_name": "Finance Supervisor",
  "prep_deadline": "2026-02-06",
  "review_deadline": "2026-02-08",
  "approval_deadline": "2026-02-09",
  "filing_deadline": "2026-02-10",
  "status": "not_started"
}
```
**n8n Action**: Send task assignment notification

### 3.2 finance_task.in_progress
**Trigger**: Task stage changed to `in_progress`
**Payload**: Same + start time
```json
{
  ...
  "started_at": "2026-02-04T09:00:00Z",
  "started_by": 42,
  "status": "in_progress"
}
```
**n8n Action**: Update PPM dashboard (Superset/Tableau)

### 3.3 finance_task.submitted
**Trigger**: Task moved to review stage (custom: `finance_stage = 'review'`)
**Payload**: Same + attachments
```json
{
  ...
  "submitted_at": "2026-02-06T16:00:00Z",
  "submitted_by": 42,
  "attachment_count": 3,
  "attachment_urls": ["https://...", "https://...", "https://..."],
  "status": "review"
}
```
**n8n Action**: Notify reviewer (Senior Finance Manager)

### 3.4 finance_task.approved
**Trigger**: Task approved (`finance_stage = 'approved'`)
**Payload**: Same + approval metadata
```json
{
  ...
  "approved_at": "2026-02-08T14:00:00Z",
  "approved_by": 7,
  "approved_by_name": "Finance Director",
  "status": "approved"
}
```
**n8n Action**: Trigger BIR e-filing workflow (if applicable)

### 3.5 finance_task.filed
**Trigger**: BIR form filed (custom: `bir_filing_status = 'filed'`)
**Payload**: Same + filing proof
```json
{
  ...
  "filed_at": "2026-02-10T10:00:00Z",
  "filed_by": 42,
  "filing_reference": "BIR-2026-1601C-001",
  "filing_receipt_url": "https://...",
  "status": "filed"
}
```
**n8n Action**: Update compliance dashboard + archive filing pack

### 3.6 finance_task.overdue
**Trigger**: Cron job detects deadline breach
**Payload**: Same + escalation details
```json
{
  ...
  "deadline_type": "prep_deadline",
  "deadline_date": "2026-02-06",
  "overdue_days": 1,
  "escalation_level": 2,
  "escalated_to": [7, 9],
  "escalated_to_names": ["Senior Finance Manager", "Finance Director"]
}
```
**n8n Action**: Send escalation alerts via Mattermost + email

---

## Event Emission Points (Odoo Hook Locations)

### Expense Hooks
```python
# addons/hr_expense/models/hr_expense.py
class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def action_submit_expenses(self):
        res = super().action_submit_expenses()
        # Emit expense.submitted event
        return res

    def approve_expense_sheets(self):
        res = super().approve_expense_sheets()
        # Emit expense.approved event
        return res

    def refuse_expense(self, reason):
        res = super().refuse_expense(reason)
        # Emit expense.rejected event
        return res
```

### Equipment Hooks
```python
# addons/ipai/ipai_equipment_booking/models/maintenance_equipment.py
class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    booking_state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned')
    ], default='available')

    def action_reserve(self):
        self.booking_state = 'reserved'
        # Emit asset.reserved event

    def action_checkout(self):
        self.booking_state = 'checked_out'
        # Emit asset.checked_out event

    def action_checkin(self):
        self.booking_state = 'returned'
        # Emit asset.checked_in event
```

### Finance PPM Hooks
```python
# addons/ipai/ipai_finance_ppm/models/project_task.py
class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        res = super().write(vals)
        if 'stage_id' in vals and self.is_finance_ppm:
            # Emit finance_task.* event based on stage
            self._emit_finance_task_event()
        return res

    def _emit_finance_task_event(self):
        stage_map = {
            'not_started': 'finance_task.created',
            'in_progress': 'finance_task.in_progress',
            'review': 'finance_task.submitted',
            'approved': 'finance_task.approved',
            'filed': 'finance_task.filed',
        }
        event_type = stage_map.get(self.stage_id.name)
        if event_type:
            # Emit event via ipai_webhook.send_ipai_event()
            pass
```

---

## n8n Workflow Routing

### Event Router (Main Workflow)
```
Trigger: Supabase Polling (integration.claim_outbox)
  ↓
Switch Node (event_type):
  ├─ expense.* → Expense Handler Workflow
  ├─ asset.* → Asset Handler Workflow
  ├─ finance_task.* → Finance PPM Handler Workflow
  └─ default → Log + Ack
```

### Expense Handler Workflow
```
expense.submitted:
  1. Fetch approver from Odoo (employee's manager)
  2. Send Mattermost notification with approval buttons
  3. Ack outbox job

expense.approved:
  1. Update payment queue (Supabase table)
  2. Send notification to Finance team
  3. Ack outbox job

expense.rejected:
  1. Send Mattermost notification to employee
  2. Update expense analytics (Superset)
  3. Ack outbox job
```

### Asset Handler Workflow
```
asset.reserved:
  1. Send confirmation email to employee
  2. Create Google Calendar event
  3. Update asset availability dashboard
  4. Ack outbox job

asset.overdue:
  1. Lookup escalation level
  2. Send reminder to employee (level 1)
  3. CC manager (level 2)
  4. CC IT Admin (level 3+)
  5. Fail outbox if escalation fails
```

### Finance PPM Handler Workflow
```
finance_task.submitted:
  1. Fetch reviewer from task metadata
  2. Send Mattermost notification with review link
  3. Update PPM dashboard (Superset)
  4. Ack outbox job

finance_task.overdue:
  1. Lookup escalation rules from BIR schedule
  2. Send alerts to responsible users
  3. Escalate to Finance Director if >3 days overdue
  4. Log escalation in event_log
  5. Ack outbox job
```

---

## MCP Tool Surface (Read-Only)

### Exposed Endpoints (via Supabase RLS)
```
GET /integration/event_log?event_type=eq.expense.submitted&order=created_at.desc&limit=100
GET /integration/event_log?aggregate_type=eq.finance_task&payload->>'bir_form'=eq.1601-C
GET /integration/outbox?status=eq.dead  # Show failed jobs for troubleshooting
```

### MCP Tools (Claude Desktop / VS Code)
```typescript
// mcp/servers/odoo-erp-server/tools/integration.ts
{
  name: "query_expense_events",
  description: "Query expense submission events from integration bus",
  inputSchema: {
    type: "object",
    properties: {
      employee_code: { type: "string" },
      status: { type: "string", enum: ["submit", "approve", "cancel", "done"] },
      date_from: { type: "string", format: "date" },
      date_to: { type: "string", format: "date" },
      limit: { type: "number", default: 50 }
    }
  }
}
```

---

## Deployment Checklist

- [ ] Deploy Supabase migration: `supabase db push`
- [ ] Deploy Edge Function: `supabase functions deploy odoo-webhook`
- [ ] Set secret: `supabase secrets set ODOO_WEBHOOK_SECRET='CHANGE_ME'`
- [ ] Add Odoo system parameter: `ipai.webhook.url`, `ipai.webhook.secret`
- [ ] Install `ipai_equipment_booking` module (if not exists)
- [ ] Add event emission hooks to expense/equipment/finance models
- [ ] Import n8n workflows from `n8n/workflows/integration/*.json`
- [ ] Activate n8n workflows
- [ ] Test end-to-end: Submit expense → Verify Mattermost notification
- [ ] Monitor `integration.outbox` for stuck jobs: `status='dead'`

---

**Last Updated**: 2026-01-22
**Version**: 1.0.0
