# ipai_approvals (Enterprise Parity)

Generic approval workflow system that mirrors Odoo Enterprise's Approvals module functionality for Odoo CE 18.

## Features

- **Approval Types**: Define approval workflows for any model
  - User-based approvers
  - Group-based approvers
  - Manager chain approvers
  - Custom approval matrices

- **Approval Requests**: Full lifecycle management
  - Draft → Pending → Approved/Rejected
  - Multi-level approvals
  - Minimum approver requirements
  - Amount-based auto-approval thresholds

- **Delegation**: Approvers can delegate to others

- **Notifications**: Email notifications for pending/approved/rejected

- **Activity Integration**: Creates activities for pending approvals

- **Audit Trail**: Full history via mail.thread

## Supported Models (out of box)

- Purchase Orders
- Sale Orders
- Account Moves (Invoices/Bills)
- Expense Reports
- Custom (any res_model)

## Configuration

### Creating an Approval Type

1. Go to **Approvals → Configuration → Approval Types**
2. Click **Create**
3. Fill in:
   - **Name**: Descriptive name
   - **Model**: The Odoo model requiring approval
   - **Approval Type**: User, Group, or Manager
   - **Minimum Approvers**: How many approvals needed
   - **Auto-approve Amount**: Skip approval for small amounts

### Approval Type Options

| Type | Description |
|------|-------------|
| User | Specific users are approvers |
| Group | All users in a security group |
| Manager | Employee's management chain |
| Custom | Use approval matrix (future) |

### Amount-based Auto-approval

Set `auto_approve_amount` to automatically approve requests below a threshold:
- `auto_approve_amount = 500` → Requests ≤ $500 auto-approve
- `amount_field = amount_total` → Which field contains the amount

## Usage

### Creating a Request

1. Go to **Approvals → My Requests**
2. Click **Create**
3. Select the **Approval Type**
4. Fill in details and **Submit**

### Approving a Request

1. Go to **Approvals → To Approve**
2. Open a pending request
3. Click **Approve** or **Reject**

### Delegating

1. Open a request where you're an approver
2. Click **Delegate**
3. Select the user to delegate to

## Security Groups

- **Approvals / User**: Create requests, see own requests, approve assigned
- **Approvals / Manager**: Full access to all requests in company

## Integration

### Adding Approval to Your Workflow

```python
# In your model
def action_confirm(self):
    # Check if approval required
    approval_type = self.env['ipai.approval.type'].search([
        ('res_model', '=', self._name),
        ('company_id', '=', self.company_id.id),
    ], limit=1)

    if approval_type:
        # Create approval request
        request = self.env['ipai.approval.request'].create({
            'type_id': approval_type.id,
            'res_model': self._name,
            'res_id': self.id,
            'amount': self.amount_total,
        })
        request.action_submit()
        return {'type': 'ir.actions.act_window_close'}

    # No approval needed
    return super().action_confirm()
```

## Dependencies

- `base`
- `mail`
- `hr` (for manager chain)

## Related Modules

- `ipai_ai_agents` - AI-powered approval assistance
- `ipai_finance_close_automation` - Finance close approvals
