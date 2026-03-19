# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json
import logging

_logger = logging.getLogger(__name__)


class AskAIMessage(models.Model):
    """Individual message in an AI conversation"""
    _name = 'ask.ai.message'
    _description = 'AI Copilot Message'
    _order = 'create_date asc'

    conversation_id = fields.Many2one(
        'ask.ai.conversation',
        string='Conversation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ], string='Role', required=True, default='user')

    content = fields.Text(
        string='Content',
        required=True,
    )

    # Structured response data (for assistant messages)
    metadata = fields.Text(
        string='Metadata (JSON)',
        help='JSON metadata including citations, actions, etc.',
    )

    # Parsed metadata fields (computed)
    citations_json = fields.Text(
        string='Citations',
        compute='_compute_parsed_metadata',
    )
    actions_json = fields.Text(
        string='Actions',
        compute='_compute_parsed_metadata',
    )
    has_actions = fields.Boolean(
        string='Has Actions',
        compute='_compute_parsed_metadata',
    )
    has_citations = fields.Boolean(
        string='Has Citations',
        compute='_compute_parsed_metadata',
    )

    # Action execution tracking
    action_executed = fields.Boolean(
        string='Actions Executed',
        default=False,
    )
    action_result = fields.Text(
        string='Action Result (JSON)',
    )

    # Token usage (optional)
    tokens_prompt = fields.Integer(string='Prompt Tokens')
    tokens_completion = fields.Integer(string='Completion Tokens')

    @api.depends('metadata')
    def _compute_parsed_metadata(self):
        for msg in self:
            citations = []
            actions = []
            if msg.metadata:
                try:
                    data = json.loads(msg.metadata)
                    citations = data.get('citations', [])
                    actions = data.get('actions', [])
                except json.JSONDecodeError:
                    _logger.warning(f'Invalid JSON metadata for message {msg.id}')

            msg.citations_json = json.dumps(citations)
            msg.actions_json = json.dumps(actions)
            msg.has_citations = bool(citations)
            msg.has_actions = bool(actions)

    def get_citations(self):
        """Get parsed citations list"""
        self.ensure_one()
        if self.metadata:
            try:
                data = json.loads(self.metadata)
                return data.get('citations', [])
            except json.JSONDecodeError:
                pass
        return []

    def get_actions(self):
        """Get parsed actions list"""
        self.ensure_one()
        if self.metadata:
            try:
                data = json.loads(self.metadata)
                return data.get('actions', [])
            except json.JSONDecodeError:
                pass
        return []

    def execute_action(self, action_index):
        """Execute a specific action from the message"""
        self.ensure_one()
        actions = self.get_actions()

        if action_index >= len(actions):
            return {'success': False, 'error': 'Invalid action index'}

        action = actions[action_index]
        action_type = action.get('type')
        payload = action.get('payload', {})

        try:
            result = self._execute_action_by_type(action_type, payload)
            self._record_action_result(action_index, result)
            return result
        except Exception as e:
            _logger.exception(f'Error executing action: {e}')
            result = {'success': False, 'error': str(e)}
            self._record_action_result(action_index, result)
            return result

    def _execute_action_by_type(self, action_type, payload):
        """Execute action based on type"""
        if action_type == 'create':
            return self._action_create(payload)
        elif action_type == 'update':
            return self._action_update(payload)
        elif action_type == 'navigate':
            return self._action_navigate(payload)
        elif action_type == 'search':
            return self._action_search(payload)
        else:
            return {'success': False, 'error': f'Unknown action type: {action_type}'}

    def _action_create(self, payload):
        """Create a new record"""
        model = payload.get('model')
        values = payload.get('values', {})

        if not model:
            return {'success': False, 'error': 'No model specified'}

        try:
            Model = self.env[model]
            record = Model.create(values)
            return {
                'success': True,
                'model': model,
                'res_id': record.id,
                'display_name': record.display_name,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _action_update(self, payload):
        """Update existing record(s)"""
        model = payload.get('model')
        res_id = payload.get('res_id')
        res_ids = payload.get('res_ids', [res_id] if res_id else [])
        values = payload.get('values', {})

        if not model or not res_ids:
            return {'success': False, 'error': 'No model or records specified'}

        try:
            records = self.env[model].browse(res_ids)
            records.write(values)
            return {
                'success': True,
                'model': model,
                'res_ids': res_ids,
                'updated_fields': list(values.keys()),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _action_navigate(self, payload):
        """Navigate to a record or view"""
        return {
            'success': True,
            'action_type': 'navigate',
            'model': payload.get('model'),
            'res_id': payload.get('res_id'),
            'view_type': payload.get('view_type', 'form'),
        }

    def _action_search(self, payload):
        """Perform a search"""
        model = payload.get('model')
        domain = payload.get('domain', [])
        limit = payload.get('limit', 10)

        if not model:
            return {'success': False, 'error': 'No model specified'}

        try:
            records = self.env[model].search(domain, limit=limit)
            return {
                'success': True,
                'model': model,
                'count': len(records),
                'res_ids': records.ids,
                'records': [{'id': r.id, 'display_name': r.display_name} for r in records],
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _record_action_result(self, action_index, result):
        """Record the result of an action execution"""
        try:
            existing = json.loads(self.action_result or '{}')
        except json.JSONDecodeError:
            existing = {}

        existing[str(action_index)] = result
        self.write({
            'action_executed': True,
            'action_result': json.dumps(existing),
        })
