# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class FinanceBIRDeadline(models.Model):
    _name = 'finance.bir.deadline'
    _description = 'BIR Tax Filing Deadline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline_date asc'
    _rec_name = 'display_name'

    name = fields.Char(string="BIR Form", required=True, tracking=True)
    period_covered = fields.Char(string="Period Covered", tracking=True)
    deadline_date = fields.Date(string="Filing Deadline", required=True, tracking=True)

    # Descriptive info
    description = fields.Text(string="Description")
    form_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('one_time', 'One-Time'),
    ], string="Form Type", default='monthly')

    # Process Targets (computed fields)
    target_prep_date = fields.Date(
        string="Target: Preparation",
        compute="_compute_targets",
        store=True,
        help="4 business days before the BIR deadline"
    )
    target_report_approval_date = fields.Date(
        string="Target: Report Approval",
        compute="_compute_targets",
        store=True,
        help="2 business days before the BIR deadline"
    )
    target_payment_approval_date = fields.Date(
        string="Target: Payment Approval",
        compute="_compute_targets",
        store=True,
        help="1 business day before the BIR deadline"
    )

    # Responsibility assignments
    responsible_prep_id = fields.Many2one('ipai.finance.person', string='Prep By')
    responsible_review_id = fields.Many2one('ipai.finance.person', string='Review By')
    responsible_approval_id = fields.Many2one('ipai.finance.person', string='Approve By')

    # Status tracking
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('filed', 'Filed'),
    ], string="Status", default='pending', tracking=True)

    active = fields.Boolean(default=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('name', 'period_covered')
    def _compute_display_name(self):
        for record in self:
            if record.period_covered:
                record.display_name = f"{record.name} - {record.period_covered}"
            else:
                record.display_name = record.name or ''

    @api.depends('deadline_date')
    def _compute_targets(self):
        """Compute target dates based on the filing deadline.

        - Preparation: 4 days before deadline
        - Report Approval: 2 days before deadline
        - Payment Approval: 1 day before deadline
        """
        for record in self:
            if record.deadline_date:
                record.target_prep_date = record.deadline_date - timedelta(days=4)
                record.target_report_approval_date = record.deadline_date - timedelta(days=2)
                record.target_payment_approval_date = record.deadline_date - timedelta(days=1)
            else:
                record.target_prep_date = False
                record.target_report_approval_date = False
                record.target_payment_approval_date = False

    def action_mark_in_progress(self):
        """Mark the deadline as in progress."""
        self.write({'state': 'in_progress'})

    def action_mark_submitted(self):
        """Mark the deadline as submitted."""
        self.write({'state': 'submitted'})

    def action_mark_filed(self):
        """Mark the deadline as filed."""
        self.write({'state': 'filed'})

    @api.model
    def get_upcoming_deadlines(self, days=14):
        """Get all deadlines due within the specified number of days."""
        today = fields.Date.today()
        end_date = today + timedelta(days=days)
        return self.search([
            ('deadline_date', '>=', today),
            ('deadline_date', '<=', end_date),
            ('state', 'not in', ['filed']),
        ])
