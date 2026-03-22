# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class L10nPhBirPeriod(models.Model):
    _name = 'l10n.ph.bir.period'
    _description = 'BIR Filing Period'
    _inherit = ['mail.thread']
    _order = 'due_date desc'

    name = fields.Char(string='Period', compute='_compute_name', store=True)
    obligation_id = fields.Many2one('l10n.ph.bir.obligation', string='Obligation',
                                     required=True, ondelete='cascade', index=True)
    branch_id = fields.Many2one(related='obligation_id.branch_id', store=True, readonly=True)
    form_code = fields.Char(related='obligation_id.form_id.code', store=True, readonly=True)
    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)
    period_label = fields.Char(string='Label')
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    status = fields.Selection([
        ('open', 'Open'),
        ('prepared', 'Prepared'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], string='Status', default='open', required=True, tracking=True)
    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event',
                                         ondelete='set null')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(related='obligation_id.company_id', store=True)
    notes = fields.Text(string='Notes')
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue', store=True)
    filing_ids = fields.One2many('l10n.ph.bir.filing', 'period_id', string='Filings')

    @api.depends('period_label', 'obligation_id.form_id.code')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.period_label or rec.obligation_id.form_id.code or ''

    @api.depends('due_date', 'status')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = (
                rec.due_date and rec.due_date < today
                and rec.status in ('open', 'prepared')
            )

    def action_mark_prepared(self):
        self.ensure_one()
        self.status = 'prepared'
        self.message_post(body=_('Period marked as prepared.'))

    def action_mark_filed(self):
        self.ensure_one()
        self.status = 'filed'
        self.message_post(body=_('Period marked as filed.'))

    def action_mark_paid(self):
        self.ensure_one()
        self.status = 'paid'
        self.message_post(body=_('Period marked as paid.'))

    def action_create_calendar_event(self):
        """Create a calendar event for the due date with a 3-day advance reminder."""
        self.ensure_one()
        if self.calendar_event_id:
            return
        event = self.env['calendar.event'].create({
            'name': _('BIR Filing: %s') % self.period_label,
            'start': self.due_date,
            'stop': self.due_date,
            'allday': True,
            'description': _('Filing deadline for %s\nBranch: %s\nForm: %s') % (
                self.period_label,
                self.obligation_id.branch_id.name,
                self.obligation_id.form_id.code,
            ),
        })
        self.calendar_event_id = event

    @api.model
    def _cron_check_overdue_filings(self):
        """Scheduled action: mark open/prepared periods as overdue if past due date."""
        today = fields.Date.context_today(self)
        overdue = self.search([
            ('due_date', '<', today),
            ('status', 'in', ('open', 'prepared')),
        ])
        for rec in overdue:
            rec.status = 'overdue'
            rec.message_post(body=_(
                'Filing period %s is overdue (due: %s).', rec.period_label, rec.due_date
            ))
            _logger.warning('BIR period %s overdue (due %s)', rec.period_label, rec.due_date)
