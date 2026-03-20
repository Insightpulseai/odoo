# -*- coding: utf-8 -*-
import logging
import uuid

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiJob(models.Model):
    """Tracks AI/OCR job execution state across Odoo, Foundry, and Document Intelligence."""

    _name = 'ipai.ai.job'
    _description = 'AI/OCR Job'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # --- Identification ---
    correlation_id = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        copy=False,
        index=True,
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    # --- Source context ---
    source_model = fields.Char(required=True, index=True)
    source_record_id = fields.Integer(required=True)
    source_record_name = fields.Char()
    attachment_id = fields.Many2one('ir.attachment')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        required=True,
        string='Triggered By',
    )

    # --- Job type and execution ---
    job_type = fields.Selection(
        [
            ('copilot_chat', 'Copilot Chat'),
            ('copilot_summary', 'Copilot Summary'),
            ('copilot_suggest', 'Copilot Suggestion'),
            ('ocr_read', 'OCR Read'),
            ('ocr_extract', 'OCR Extract Fields'),
            ('ocr_classify', 'OCR Classify'),
            ('finance_draft', 'Finance Draft Proposal'),
            ('finance_review', 'Finance Review'),
        ],
        required=True,
        index=True,
    )
    trigger = fields.Selection(
        [
            ('manual', 'Manual (Button)'),
            ('automation', 'Automation Rule'),
            ('cron', 'Scheduled Job'),
            ('api', 'API Call'),
        ],
        default='manual',
        required=True,
    )

    # --- Status lifecycle ---
    state = fields.Selection(
        [
            ('queued', 'Queued'),
            ('running', 'Running'),
            ('done', 'Done'),
            ('needs_review', 'Needs Review'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='queued',
        required=True,
        tracking=True,
        index=True,
    )

    # --- External service tracking ---
    external_job_id = fields.Char(index=True)
    agent_id = fields.Char()
    agent_version = fields.Char()
    model_name = fields.Char(string='AI Model')
    model_version = fields.Char()

    # --- Result ---
    result_payload = fields.Json()
    confidence = fields.Float(digits=(3, 2))
    needs_human_review = fields.Boolean(default=False)
    review_reason = fields.Char()
    error_message = fields.Text()
    error_class = fields.Selection(
        [
            ('auth', 'Authentication'),
            ('network', 'Network'),
            ('service', 'Service Error'),
            ('model', 'Model Error'),
            ('data', 'Data Error'),
            ('timeout', 'Timeout'),
        ],
    )

    # --- Timing ---
    started_at = fields.Datetime()
    completed_at = fields.Datetime()
    duration_ms = fields.Integer(compute='_compute_duration_ms', store=True)

    # --- Retry ---
    retry_count = fields.Integer(default=0)
    max_retries = fields.Integer(default=3)
    last_retry_at = fields.Datetime()

    # --- Linked proposal ---
    proposal_ids = fields.One2many('ipai.ai.proposal', 'job_id')
    proposal_count = fields.Integer(compute='_compute_proposal_count')

    @api.depends('correlation_id', 'job_type')
    def _compute_display_name(self):
        for rec in self:
            short_id = (rec.correlation_id or '')[:8]
            job_label = dict(rec._fields['job_type'].selection).get(rec.job_type, '')
            rec.display_name = f"{job_label} [{short_id}]"

    @api.depends('started_at', 'completed_at')
    def _compute_duration_ms(self):
        for rec in self:
            if rec.started_at and rec.completed_at:
                delta = rec.completed_at - rec.started_at
                rec.duration_ms = int(delta.total_seconds() * 1000)
            else:
                rec.duration_ms = 0

    def _compute_proposal_count(self):
        for rec in self:
            rec.proposal_count = len(rec.proposal_ids)

    # --- State transitions ---

    def action_start(self):
        self.ensure_one()
        if self.state != 'queued':
            raise UserError(_('Can only start a queued job.'))
        self.write({
            'state': 'running',
            'started_at': fields.Datetime.now(),
        })

    def action_complete(self, result_payload=None, confidence=0.0):
        self.ensure_one()
        vals = {
            'state': 'done',
            'completed_at': fields.Datetime.now(),
            'result_payload': result_payload,
            'confidence': confidence,
        }
        threshold = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'ipai.copilot_actions.review_threshold', '0.7'
            )
        )
        if confidence and confidence < threshold:
            vals['state'] = 'needs_review'
            vals['needs_human_review'] = True
            vals['review_reason'] = _('Confidence %.0f%% below threshold %.0f%%',
                                      confidence * 100, threshold * 100)
        self.write(vals)

    def action_fail(self, error_message, error_class=None):
        self.ensure_one()
        self.write({
            'state': 'failed',
            'completed_at': fields.Datetime.now(),
            'error_message': error_message,
            'error_class': error_class,
        })

    def action_retry(self):
        self.ensure_one()
        if self.retry_count >= self.max_retries:
            raise UserError(_('Maximum retries (%s) reached.', self.max_retries))
        self.write({
            'state': 'queued',
            'retry_count': self.retry_count + 1,
            'last_retry_at': fields.Datetime.now(),
            'error_message': False,
            'error_class': False,
        })

    def action_cancel(self):
        self.filtered(lambda j: j.state in ('queued', 'failed', 'needs_review')).write({
            'state': 'cancelled',
        })

    def action_view_proposals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Proposals'),
            'res_model': 'ipai.ai.proposal',
            'domain': [('job_id', '=', self.id)],
            'view_mode': 'list,form',
        }
