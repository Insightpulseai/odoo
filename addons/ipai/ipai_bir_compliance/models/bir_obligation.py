# -*- coding: utf-8 -*-
import logging
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class L10nPhBirObligation(models.Model):
    _name = 'l10n.ph.bir.obligation'
    _description = 'BIR Filing Obligation'
    _order = 'branch_id, form_id'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    branch_id = fields.Many2one('operating.branch', string='Branch', required=True,
                                 ondelete='restrict')
    form_id = fields.Many2one('l10n.ph.bir.form', string='BIR Form', required=True,
                               ondelete='restrict')
    deadline_rule_id = fields.Many2one('l10n.ph.bir.deadline.rule', string='Deadline Rule',
                                        ondelete='set null',
                                        help='Override default deadline rule for this obligation')
    start_date = fields.Date(string='Start Date', required=True,
                              default=fields.Date.context_today)
    end_date = fields.Date(string='End Date',
                            help='Leave empty if obligation is ongoing')
    filing_frequency = fields.Selection(related='form_id.frequency', store=True, readonly=True)
    filing_channel = fields.Selection([
        ('ebirforms', 'eBIRForms'),
        ('efps', 'eFPS'),
        ('eservices', 'eServices'),
        ('manual', 'Manual'),
    ], string='Filing Channel', default='ebirforms')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User')
    is_active = fields.Boolean(string='Active Obligation', default=True)
    notes = fields.Text(string='Notes')
    period_ids = fields.One2many('l10n.ph.bir.period', 'obligation_id', string='Periods')
    period_count = fields.Integer(compute='_compute_period_count')

    @api.depends('form_id.code', 'branch_id.code')
    def _compute_name(self):
        for rec in self:
            form_code = rec.form_id.code or ''
            branch_code = rec.branch_id.code or ''
            rec.name = '%s / %s' % (form_code, branch_code) if form_code else ''

    @api.depends('period_ids')
    def _compute_period_count(self):
        for rec in self:
            rec.period_count = len(rec.period_ids)

    def _get_deadline_rule(self):
        """Return the applicable deadline rule: obligation override or form default."""
        self.ensure_one()
        if self.deadline_rule_id:
            return self.deadline_rule_id
        rule = self.env['l10n.ph.bir.deadline.rule'].search([
            ('form_id', '=', self.form_id.id),
            ('active', '=', True),
            ('is_efps_variant', '=', self.filing_channel == 'efps'),
        ], limit=1)
        if not rule:
            rule = self.env['l10n.ph.bir.deadline.rule'].search([
                ('form_id', '=', self.form_id.id),
                ('active', '=', True),
            ], limit=1)
        return rule

    def action_generate_periods(self):
        """Generate filing periods for the current fiscal year."""
        for rec in self:
            rule = rec._get_deadline_rule()
            if not rule:
                raise UserError(_('No deadline rule found for form %s.') % rec.form_id.code)

            today = fields.Date.context_today(self)
            year = today.year
            periods = []

            if rec.filing_frequency == 'monthly':
                for month in range(1, 13):
                    period_start = date(year, month, 1)
                    if month == 12:
                        period_end = date(year, 12, 31)
                    else:
                        period_end = date(year, month + 1, 1) - timedelta(days=1)
                    due = rule.compute_due_date(period_start, period_end)
                    label = '%s %s-%02d' % (rec.form_id.code, year, month)
                    # Check if period already exists
                    existing = self.env['l10n.ph.bir.period'].search([
                        ('obligation_id', '=', rec.id),
                        ('period_start', '=', period_start),
                        ('period_end', '=', period_end),
                    ], limit=1)
                    if not existing:
                        periods.append({
                            'obligation_id': rec.id,
                            'period_start': period_start,
                            'period_end': period_end,
                            'period_label': label,
                            'due_date': due,
                            'status': 'open',
                        })

            elif rec.filing_frequency == 'quarterly':
                quarter_months = [(1, 3), (4, 6), (7, 9), (10, 12)]
                # For 1701Q: fixed dates Apr 15, Aug 15, Nov 15
                fixed_quarters = {
                    'Q_FIXED_APR_AUG_NOV_15': [
                        (date(year, 4, 15), 1),
                        (date(year, 8, 15), 2),
                        (date(year, 11, 15), 3),
                    ],
                }
                if rule.rule_code in fixed_quarters:
                    for due_dt, q_num in fixed_quarters[rule.rule_code]:
                        q_start_m, q_end_m = quarter_months[q_num - 1]
                        period_start = date(year, q_start_m, 1)
                        if q_end_m < 12:
                            period_end = date(year, q_end_m + 1, 1) - timedelta(days=1)
                        else:
                            period_end = date(year, 12, 31)
                        label = '%s %s-Q%d' % (rec.form_id.code, year, q_num)
                        existing = self.env['l10n.ph.bir.period'].search([
                            ('obligation_id', '=', rec.id),
                            ('period_start', '=', period_start),
                        ], limit=1)
                        if not existing:
                            periods.append({
                                'obligation_id': rec.id,
                                'period_start': period_start,
                                'period_end': period_end,
                                'period_label': label,
                                'due_date': due_dt,
                                'status': 'open',
                            })
                else:
                    for q_num, (q_start_m, q_end_m) in enumerate(quarter_months, 1):
                        period_start = date(year, q_start_m, 1)
                        if q_end_m < 12:
                            period_end = date(year, q_end_m + 1, 1) - timedelta(days=1)
                        else:
                            period_end = date(year, 12, 31)
                        due = rule.compute_due_date(period_start, period_end)
                        label = '%s %s-Q%d' % (rec.form_id.code, year, q_num)
                        existing = self.env['l10n.ph.bir.period'].search([
                            ('obligation_id', '=', rec.id),
                            ('period_start', '=', period_start),
                        ], limit=1)
                        if not existing:
                            periods.append({
                                'obligation_id': rec.id,
                                'period_start': period_start,
                                'period_end': period_end,
                                'period_label': label,
                                'due_date': due,
                                'status': 'open',
                            })

            elif rec.filing_frequency == 'annual':
                period_start = date(year - 1, 1, 1)
                period_end = date(year - 1, 12, 31)
                due = rule.compute_due_date(period_start, period_end)
                label = '%s %s' % (rec.form_id.code, year - 1)
                existing = self.env['l10n.ph.bir.period'].search([
                    ('obligation_id', '=', rec.id),
                    ('period_start', '=', period_start),
                ], limit=1)
                if not existing:
                    periods.append({
                        'obligation_id': rec.id,
                        'period_start': period_start,
                        'period_end': period_end,
                        'period_label': label,
                        'due_date': due,
                        'status': 'open',
                    })

            if periods:
                self.env['l10n.ph.bir.period'].create(periods)
                _logger.info('Generated %d periods for %s', len(periods), rec.name)

    def action_view_periods(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Filing Periods'),
            'res_model': 'l10n.ph.bir.period',
            'view_mode': 'list,form,calendar',
            'domain': [('obligation_id', '=', self.id)],
            'context': {'default_obligation_id': self.id},
        }
