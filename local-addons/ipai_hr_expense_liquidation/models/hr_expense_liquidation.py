from odoo import models, fields, api, _

class HrExpenseLiquidation(models.Model):
    _name = 'hr.expense.liquidation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Expense Liquidation"

    name = fields.Char(string="Reference", required=True, copy=False, default='New')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_approved', 'Manager Approved'),
        ('finance_approved', 'Finance Approved'),
        ('released', 'Released'),
        ('in_liquidation', 'In Liquidation'),
        ('liquidated', 'Liquidated'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ], string="Status", default='draft', tracking=True)

    # Orthogonal Agent States
    channel_state = fields.Selection([
        ('received', 'Received'),
        ('normalized', 'Normalized'),
        ('failed', 'Failed'),
    ], string="Channel State", default='received')
    
    document_state = fields.Selection([
        ('pending', 'Pending'),
        ('extracted', 'Extracted'),
        ('review_needed', 'Review Needed'),
        ('accepted', 'Accepted'),
    ], string="Document State", default='pending')
    
    policy_state = fields.Selection([
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('waived', 'Waived'),
    ], string="Policy State", default='pending')
    
    settlement_state = fields.Selection([
        ('net_zero', 'Net Zero'),
        ('employee_owes_company', 'Employee Owes Company'),
        ('company_owes_employee', 'Company Owes Employee'),
    ], string="Settlement State")

    # Submission Envelope
    envelope_id = fields.Char(string="Envelope ID", copy=False)
    source_channel = fields.Selection([
        ('telegram', 'Telegram'),
        ('web', 'Web'),
        ('email', 'Email'),
    ], string="Source Channel")
    source_message_id = fields.Char(string="Source Message ID", copy=False)

    def action_ipai_audit_all_lines(self):
        """Autonomous Agent method to audit all lines against policy."""
        self.ensure_one()
        results = []
        for line in self.line_ids:
            res = line.action_ipai_audit_line()
            results.append(res)
        
        if all(r == 'pass' for r in results):
            self.policy_state = 'pass'
            self.message_post(body="IPAI [Agent]: All lines passed policy audit.")
        else:
            self.policy_state = 'fail'
            self.message_post(body="IPAI [Agent]: Policy violations detected. Please review lines.")

class HrExpenseLiquidationLine(models.Model):
    _name = 'hr.expense.liquidation.line'
    _description = "Expense Liquidation Line"

    liquidation_id = fields.Many2one('hr.expense.liquidation', string="Liquidation")
    date = fields.Date(string="Date")
    description = fields.Char(string="Description")
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency")
    attachment_id = fields.Many2one('ir.attachment', string="Receipt")
    audit_result = fields.Selection([
        ('none', 'Not Audited'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string="Audit Result", default='none')

    def action_ipai_ingest_ocr(self):
        """Call Foundry Document Intelligence via the ipai_foundry bridge."""
        self.ensure_one()
        if not self.attachment_id:
            return False
        
        # Call the central bridge
        connector = self.env['ipai.foundry.connector'].sudo()
        ocr_data = connector.action_ocr_process(self.attachment_id)
        
        if ocr_data:
            self.write({
                'date': ocr_data.get('date'),
                'amount': ocr_data.get('amount_total', 0.0),
                'description': f"OCR Extraction: {ocr_data.get('vendor_name', 'Unknown Vendor')}",
                'audit_result': 'none', # Reset audit to re-verify extracted data
            })
            self.liquidation_id.document_state = 'extracted'
            self.message_post(body=f"IPAI [Foundry]: Successfully extracted data from receipt.")
            return True
        return False

    def action_ipai_audit_line(self):
        """Policy enforcement logic (Governess as Code)."""
        self.ensure_one()
        # Simulated Policy Rules:
        # 1. Must have attachment
        if not self.attachment_id:
            self.audit_result = 'fail'
            return 'fail'
        
        # 2. Amount > 500 PHP requires explicit detail (simulated)
        if self.amount > 500 and not self.description:
            self.audit_result = 'fail'
            return 'fail'
            
        self.audit_result = 'pass'
        return 'pass'
