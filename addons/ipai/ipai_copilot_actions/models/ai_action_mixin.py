# -*- coding: utf-8 -*-
import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class AiActionMixin(models.AbstractModel):
    """Mixin for models that support Copilot and OCR actions.

    Inherit this mixin on any business model to get standardized
    action methods for triggering AI jobs.
    """

    _name = 'ipai.ai.action.mixin'
    _description = 'AI Action Mixin'

    def action_ask_copilot(self):
        """Open Copilot chat with current record context."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'ipai_copilot_open',
            'params': {
                'model': self._name,
                'res_id': self.id,
                'action': 'ask',
            },
        }

    def action_copilot_summarize(self):
        """Create a Copilot summary job for this record."""
        self.ensure_one()
        return self._create_ai_job('copilot_summary')

    def action_copilot_suggest_next(self):
        """Ask Copilot to suggest the next workflow step."""
        self.ensure_one()
        return self._create_ai_job('copilot_suggest')

    def action_run_ocr(self):
        """Run OCR on the first attachment of this record."""
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('mimetype', 'in', ['application/pdf', 'image/png', 'image/jpeg', 'image/tiff']),
        ], limit=1, order='create_date desc')
        if not attachment:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Attachment'),
                    'message': _('No suitable attachment found for OCR.'),
                    'type': 'warning',
                },
            }
        return self._create_ai_job('ocr_extract', attachment_id=attachment.id)

    def _create_ai_job(self, job_type, trigger='manual', attachment_id=None):
        """Create an AI job record and return a notification action."""
        job = self.env['ipai.ai.job'].create({
            'source_model': self._name,
            'source_record_id': self.id,
            'source_record_name': getattr(self, 'display_name', str(self.id)),
            'job_type': job_type,
            'trigger': trigger,
            'attachment_id': attachment_id,
        })
        _logger.info(
            'AI job created: %s [%s] on %s/%s by %s',
            job.job_type, job.correlation_id,
            self._name, self.id, self.env.user.login,
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Job Created'),
                'message': _('Job %s queued.', job.correlation_id[:8]),
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'ipai.ai.job',
                    'res_id': job.id,
                    'view_mode': 'form',
                },
            },
        }
