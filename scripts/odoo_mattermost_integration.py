# Odoo Mattermost Integration Script
# Python code for Odoo Automated Actions

import requests
import json
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class PurchaseOrderMattermostIntegration(models.Model):
    _inherit = 'purchase.order'

    def send_mattermost_approval_notification(self):
        """
        Send approval notification to Mattermost when PO state changes to 'to approve'
        """
        webhook_url = "https://chat.insightpulseai.net/hooks/YOUR_WEBHOOK_ID"

        # Logic to determine approver based on amount
        if self.amount_total > 50000:
            approver = "@khalil"
        elif self.amount_total > 10000:
            approver = "@rey"
        else:
            approver = "@finance-team"

        message = {
            "text": f"""🚨 **Approval Needed**

**PO:** {self.name}
**Amount:** {self.amount_total:,.2f} PHP
**Vendor:** {self.partner_id.name}
**Requested By:** {self.user_id.name}

{approver}, please check Odoo to approve this purchase order.

[View in Odoo](https://erp.insightpulseai.net/web#id={self.id}&model=purchase.order&view_type=form)"""
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                _logger.info(f"✅ Mattermost notification sent for PO {self.name}")
            else:
                _logger.warning(f"⚠️ Mattermost webhook returned {response.status_code}")
        except Exception as e:
            _logger.error(f"❌ Failed to send Mattermost notification: {str(e)}")

class ExpenseMattermostIntegration(models.Model):
    _inherit = 'hr.expense'

    def send_mattermost_expense_notification(self):
        """
        Send expense approval notification to Mattermost
        """
        webhook_url = "https://chat.insightpulseai.net/hooks/YOUR_WEBHOOK_ID"

        message = {
            "text": f"""💰 **Expense Approval Needed**

**Employee:** {self.employee_id.name}
**Amount:** {self.total_amount:,.2f} PHP
**Description:** {self.name}
**Category:** {self.product_id.name}

@finance-team, please review this expense in Odoo.

[View in Odoo](https://erp.insightpulseai.net/web#id={self.id}&model=hr.expense&view_type=form)"""
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                _logger.info(f"✅ Mattermost expense notification sent for {self.name}")
        except Exception as e:
            _logger.error(f"❌ Failed to send Mattermost expense notification: {str(e)}")

# Automated Action Configuration Instructions:
"""
To set up Mattermost integration in Odoo:

1. Go to Settings > Technical > Automation > Automated Actions
2. Create new automated action:

Action 1: Purchase Order Approval
- Model: Purchase Order
- Trigger: On Update
- Domain: [('state', '=', 'to approve')]
- Action: Execute Python Code
- Code: record.send_mattermost_approval_notification()

Action 2: Expense Approval
- Model: Expense
- Trigger: On Creation
- Domain: [('state', '=', 'reported')]
- Action: Execute Python Code
- Code: record.send_mattermost_expense_notification()

3. Replace YOUR_WEBHOOK_ID with actual Mattermost webhook URL
4. Install requests library in Odoo environment if not present
"""
