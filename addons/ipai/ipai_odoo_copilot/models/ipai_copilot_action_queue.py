# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CopilotActionQueue(models.Model):
    """Queue for agent-proposed actions awaiting human approval.

    Agents never write directly to Odoo business records. They propose
    actions that land here. A human reviews and approves/rejects.
    Approved actions are executed by the queue processor.
    """

    _name = 'ipai.copilot.action.queue'
    _description = 'Copilot Action Queue'
    _order = 'create_date desc'
    _rec_name = 'summary'

    summary = fields.Char(required=True, help="One-line description of proposed action")
    workflow_id = fields.Char(required=True, help="Diva workflow that proposed this action")
    agent_run_id = fields.Char(help="Foundry agent run ID for traceability")
    target_model = fields.Char(required=True, help="Odoo model to act on")
    target_res_id = fields.Integer(help="Record ID (0 for create)")
    action_type = fields.Selection([
        ('create', 'Create Record'),
        ('write', 'Update Record'),
        ('action', 'Execute Action Method'),
    ], required=True)
    action_payload = fields.Text(
        required=True,
        help="JSON payload for the action (vals dict or method args)",
    )
    state = fields.Selection([
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
        ('failed', 'Failed'),
    ], default='pending', required=True)
    reviewed_by = fields.Many2one('res.users', readonly=True)
    reviewed_at = fields.Datetime(readonly=True)
    rejection_reason = fields.Text()
    execution_log = fields.Text(readonly=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True,
    )

    def action_approve(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_("Only pending actions can be approved."))
        self.write({
            'state': 'approved',
            'reviewed_by': self.env.uid,
            'reviewed_at': fields.Datetime.now(),
        })

    def action_reject(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_("Only pending actions can be rejected."))
        self.write({
            'state': 'rejected',
            'reviewed_by': self.env.uid,
            'reviewed_at': fields.Datetime.now(),
        })

    def action_execute(self):
        """Execute an approved action against the target model."""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Only approved actions can be executed."))

        try:
            payload = json.loads(self.action_payload)
            Model = self.env[self.target_model]

            if self.action_type == 'create':
                record = Model.create(payload)
                log = _("Created %s (ID: %s)", self.target_model, record.id)
            elif self.action_type == 'write':
                record = Model.browse(self.target_res_id)
                if not record.exists():
                    raise UserError(
                        _("Target record %s/%s not found", self.target_model, self.target_res_id)
                    )
                record.write(payload)
                log = _("Updated %s (ID: %s)", self.target_model, self.target_res_id)
            elif self.action_type == 'action':
                record = Model.browse(self.target_res_id)
                if not record.exists():
                    raise UserError(
                        _("Target record %s/%s not found", self.target_model, self.target_res_id)
                    )
                method_name = payload.get('method')
                if not method_name or not method_name.startswith('action_'):
                    raise UserError(_("Only action_* methods are allowed"))
                getattr(record, method_name)()
                log = _("Executed %s.%s (ID: %s)", self.target_model, method_name, self.target_res_id)
            else:
                raise UserError(_("Unknown action type: %s", self.action_type))

            self.write({'state': 'executed', 'execution_log': log})
            _logger.info("Copilot action executed: %s", log)

        except (UserError, KeyError, json.JSONDecodeError) as e:
            self.write({'state': 'failed', 'execution_log': str(e)})
            _logger.error("Copilot action failed: %s", e)
            raise
