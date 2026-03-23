# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class L10nPhBirFiling(models.Model):
    _name = 'l10n.ph.bir.filing'
    _description = 'BIR Filing Record'
    _inherit = ['mail.thread']
    _order = 'filing_datetime desc'

    name = fields.Char(string='Filing Reference', compute='_compute_name', store=True)
    period_id = fields.Many2one('l10n.ph.bir.period', string='Filing Period',
                                 required=True, ondelete='cascade', index=True)
    branch_id = fields.Many2one(related='period_id.branch_id', store=True, readonly=True)
    form_code = fields.Char(related='period_id.form_code', store=True, readonly=True)
    filing_reference = fields.Char(string='Confirmation Number', tracking=True)
    filing_datetime = fields.Datetime(string='Filing Date/Time', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    payment_datetime = fields.Datetime(string='Payment Date/Time')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount_due = fields.Monetary(string='Tax Due', currency_field='currency_id')
    amount_paid = fields.Monetary(string='Tax Paid', currency_field='currency_id')
    return_attachment_id = fields.Many2one('ir.attachment', string='Filed Return',
                                            help='eBIRForms XML/PDF or scanned filed return')
    payment_proof_attachment_id = fields.Many2one('ir.attachment', string='Payment Proof',
                                                    help='ePay confirmation or bank debit memo')
    alphalist_attachment_id = fields.Many2one('ir.attachment', string='Alphalist / SAWT / QAP',
                                               help='SAWT, QAP, SLSP, or alphalist DAT file')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('filed', 'Filed'),
        ('paid', 'Filed & Paid'),
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one(related='period_id.company_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('filing_reference', 'period_id.period_label')
    def _compute_name(self):
        for rec in self:
            if rec.filing_reference:
                rec.name = rec.filing_reference
            elif rec.period_id:
                rec.name = _('Filing: %s') % rec.period_id.period_label
            else:
                rec.name = _('New Filing')

    def action_mark_filed(self):
        self.ensure_one()
        self.status = 'filed'
        if self.period_id.status in ('open', 'prepared', 'overdue'):
            self.period_id.status = 'filed'
        self.message_post(body=_('Filing recorded with reference: %s') % (self.filing_reference or 'N/A'))

    def action_mark_paid(self):
        self.ensure_one()
        self.status = 'paid'
        if self.period_id.status != 'paid':
            self.period_id.status = 'paid'
        self.message_post(body=_('Payment recorded: %s') % (self.payment_reference or 'N/A'))
