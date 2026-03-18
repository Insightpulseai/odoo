# COE generation

A certificate of employment (COE) confirms an individual's employment history with the company. Philippine labor law (Labor Code Article 285) requires employers to issue a COE within 3 calendar days of an employee's request. InsightPulse AI targets 1 business day.

## COE types

| Type | Content | Use case |
|------|---------|----------|
| **Basic** | Name, position, employment dates | General purpose (bank, visa, rental) |
| **With compensation** | Basic + last salary, allowances | Loan applications, new employer verification |
| **Detailed (separation)** | Basic + compensation + separation reason + clearance status | Government submissions, legal proceedings |

!!! note
    The **detailed** type includes separation reason and is only issued after clearance completion. The **basic** and **with compensation** types can be issued to current or former employees at any time.

## Statutory SLA

| Requirement | Deadline | Legal basis |
|-------------|----------|-------------|
| COE issuance | 3 calendar days from request | Labor Code Article 285 |
| Internal SLA | 1 business day from request | Company policy |

!!! warning
    Refusal or delay in issuing a COE is a labor law violation. The COE must be issued regardless of whether clearance is complete, except for the **detailed** type which requires clearance sign-off.

## Generation process

| Step | Action | Actor | System |
|------|--------|-------|--------|
| 1 | Employee or former employee requests COE | Requestor | `hr.coe.request` form or Odoo portal |
| 2 | HR receives and validates request | HR Operations | Odoo notification |
| 3 | System auto-populates COE from employee record | System | `ipai_hr_coe` |
| 4 | HR reviews and approves | HR Operations | Approval workflow |
| 5 | COE generated as PDF and released via selected channel | System | Report engine |

### Request model

```python
class HrCoeRequest(models.Model):
    _name = 'hr.coe.request'
    _description = 'Certificate of Employment Request'

    employee_id = fields.Many2one('hr.employee', required=True)
    coe_type = fields.Selection([
        ('basic', 'Basic'),
        ('with_compensation', 'With Compensation'),
        ('detailed', 'Detailed (Separation)'),
    ], required=True, default='basic')
    request_date = fields.Date(default=fields.Date.today)
    purpose = fields.Char()
    release_channel = fields.Selection([
        ('email', 'Email'),
        ('portal', 'Odoo Portal'),
        ('physical', 'Physical Copy'),
    ], default='email')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('released', 'Released'),
        ('rejected', 'Rejected'),
    ], default='draft')
    sla_deadline = fields.Date(compute='_compute_sla_deadline')
    coe_pdf = fields.Binary('COE Document')
```

## COE content by type

### Basic COE

| Field | Source |
|-------|--------|
| Employee full name | `hr.employee.name` |
| Position / job title | `hr.employee.job_id` |
| Department | `hr.employee.department_id` |
| Employment start date | `hr.contract.date_start` |
| Employment end date (if separated) | `hr.contract.date_end` |
| Employment status | Active / Separated |

### With compensation (adds)

| Field | Source |
|-------|--------|
| Last monthly salary | `hr.contract.wage` |
| Allowances | `hr.contract` allowance fields |
| Total monthly compensation | Computed |

### Detailed / separation (adds)

| Field | Source |
|-------|--------|
| Separation reason | `hr.employee.departure_reason_id` |
| Last working day | `hr.clearance.last_working_day` |
| Clearance status | `hr.clearance.state` |

## Release channels

| Channel | Format | Delivery | Tracking |
|---------|--------|----------|----------|
| **Email** | PDF attachment | Sent to employee's personal email | Mail delivery confirmation |
| **Odoo Portal** | PDF download | Available in employee self-service portal | Download timestamp |
| **Physical copy** | Printed, signed, sealed | Picked up or mailed to forwarding address | Acknowledgment receipt |

!!! tip
    For physical copies, use the forwarding address from the Admin clearance checklist. Send via registered mail if the employee cannot pick up in person.

## COE numbering

Each COE receives a unique reference number for tracking and verification.

```
Format: COE-{YYYY}-{sequence_number}
Example: COE-2026-00142
```

The sequence auto-increments per calendar year via `ir.sequence` configured for the `hr.coe.request` model.

## Verification by third parties

Third parties (banks, prospective employers) can verify COE authenticity by contacting HR with the COE reference number. The `hr.coe.request` record serves as the verification source.
