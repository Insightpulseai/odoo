# -*- coding: utf-8 -*-

import json
import logging
import requests
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError

_logger = logging.getLogger(__name__)


class AskAIController(http.Controller):
    """Controller for AI Copilot API endpoints"""

    @http.route('/ask_ai/config', type='json', auth='user')
    def get_config(self):
        """Get AI configuration for frontend"""
        return request.env['res.config.settings'].get_ask_ai_config()

    @http.route('/ask_ai/conversations', type='json', auth='user')
    def get_conversations(self, limit=10, offset=0):
        """Get user's conversations"""
        Conversation = request.env['ask.ai.conversation']
        domain = [
            ('user_id', '=', request.env.uid),
            ('state', '=', 'active'),
        ]
        total = Conversation.search_count(domain)
        conversations = Conversation.search(
            domain, limit=limit, offset=offset, order='last_message_date desc'
        )
        return {
            'total': total,
            'conversations': [{
                'id': c.id,
                'title': c.title,
                'message_count': c.message_count,
                'last_message_date': c.last_message_date.isoformat() if c.last_message_date else None,
                'mode': c.mode,
                'context_model': c.context_model,
            } for c in conversations]
        }

    @http.route('/ask_ai/conversation/<int:conversation_id>', type='json', auth='user')
    def get_conversation(self, conversation_id):
        """Get a specific conversation with messages"""
        conv = request.env['ask.ai.conversation'].browse(conversation_id)
        if not conv.exists() or conv.user_id.id != request.env.uid:
            return {'error': 'Conversation not found'}

        return {
            'id': conv.id,
            'title': conv.title,
            'mode': conv.mode,
            'context_model': conv.context_model,
            'context_res_id': conv.context_res_id,
            'messages': [{
                'id': m.id,
                'role': m.role,
                'content': m.content,
                'citations': m.get_citations(),
                'actions': m.get_actions(),
                'action_executed': m.action_executed,
                'create_date': m.create_date.isoformat(),
            } for m in conv.message_ids.sorted('create_date')]
        }

    @http.route('/ask_ai/conversation/create', type='json', auth='user')
    def create_conversation(self, context_data=None):
        """Create a new conversation"""
        conv = request.env['ask.ai.conversation'].get_or_create_conversation(
            context_data or {}
        )
        return {'id': conv.id, 'title': conv.title}

    @http.route('/ask_ai/execute', type='json', auth='user')
    def execute_prompt(self, conversation_id=None, prompt=None, context=None, mode='ask'):
        """
        Execute an AI prompt and return the response.

        This is the main endpoint that:
        1. Receives user prompt + context
        2. Calls external AI backend
        3. Parses structured response
        4. Stores messages
        5. Returns response with citations/actions

        Expected AI response schema:
        {
            "message": "string - the main response text",
            "citations": [
                {"model": "res.partner", "res_id": 123, "label": "Partner Name", "field": "name"}
            ],
            "actions": [
                {
                    "type": "create|update|navigate|search",
                    "label": "Create Invoice",
                    "payload": {...},
                    "preview_diff": {...}
                }
            ],
            "tokens": {"prompt": 100, "completion": 50}
        }
        """
        if not prompt:
            return {'error': 'No prompt provided'}

        # Get or create conversation
        Conversation = request.env['ask.ai.conversation']
        if conversation_id:
            conv = Conversation.browse(conversation_id)
            if not conv.exists() or conv.user_id.id != request.env.uid:
                return {'error': 'Conversation not found'}
        else:
            conv = Conversation.get_or_create_conversation(context)

        # Add user message
        user_msg = conv.add_message('user', prompt)

        # Build AI request payload
        ai_payload = self._build_ai_payload(conv, prompt, context, mode)

        # Call AI backend
        try:
            ai_response = self._call_ai_backend(ai_payload)
        except Exception as e:
            _logger.exception('AI backend error')
            return {
                'error': str(e),
                'conversation_id': conv.id,
                'user_message_id': user_msg.id,
            }

        # Parse and store assistant response
        assistant_msg = conv.add_message(
            'assistant',
            ai_response.get('message', ''),
            metadata={
                'citations': ai_response.get('citations', []),
                'actions': ai_response.get('actions', []),
            }
        )

        # Update token usage if provided
        tokens = ai_response.get('tokens', {})
        if tokens:
            assistant_msg.write({
                'tokens_prompt': tokens.get('prompt', 0),
                'tokens_completion': tokens.get('completion', 0),
            })

        return {
            'conversation_id': conv.id,
            'message': {
                'id': assistant_msg.id,
                'role': 'assistant',
                'content': assistant_msg.content,
                'citations': ai_response.get('citations', []),
                'actions': ai_response.get('actions', []),
                'create_date': assistant_msg.create_date.isoformat(),
            }
        }

    @http.route('/ask_ai/execute_action', type='json', auth='user')
    def execute_action(self, message_id, action_index):
        """Execute a specific action from an AI response"""
        Message = request.env['ask.ai.message']
        msg = Message.browse(message_id)

        if not msg.exists():
            return {'error': 'Message not found'}

        # Verify user has access
        if msg.conversation_id.user_id.id != request.env.uid:
            return {'error': 'Access denied'}

        # Check if confirmation is required
        ICP = request.env['ir.config_parameter'].sudo()
        require_confirmation = ICP.get_param('ask_ai.require_confirmation', 'True') == 'True'

        actions = msg.get_actions()
        if action_index >= len(actions):
            return {'error': 'Invalid action index'}

        action = actions[action_index]

        # Validate action is allowed
        validation = self._validate_action(action)
        if not validation['allowed']:
            return {'error': validation['reason']}

        # Execute the action
        result = msg.execute_action(action_index)
        return result

    @http.route('/ask_ai/context', type='json', auth='user')
    def get_record_context(self, model, res_id, fields=None):
        """Get context data for a specific record"""
        try:
            Model = request.env[model]
            record = Model.browse(res_id)

            if not record.exists():
                return {'error': 'Record not found'}

            # Get basic record info
            context = {
                'model': model,
                'res_id': res_id,
                'display_name': record.display_name,
            }

            # Get field values if specified
            if fields:
                field_values = {}
                for field in fields:
                    if hasattr(record, field):
                        value = getattr(record, field)
                        # Handle relational fields
                        if hasattr(value, 'display_name'):
                            field_values[field] = {
                                'id': value.id,
                                'display_name': value.display_name
                            }
                        elif hasattr(value, 'ids'):
                            field_values[field] = [
                                {'id': r.id, 'display_name': r.display_name}
                                for r in value
                            ]
                        else:
                            field_values[field] = value
                context['fields'] = field_values

            # Get model description
            model_desc = request.env['ir.model'].search([
                ('model', '=', model)
            ], limit=1)
            if model_desc:
                context['model_name'] = model_desc.name

            return context

        except Exception as e:
            _logger.exception('Error getting record context')
            return {'error': str(e)}

    def _build_ai_payload(self, conversation, prompt, context, mode):
        """Build the payload for the AI backend"""
        # Get conversation history
        history = conversation.get_messages_for_api(limit=10)

        # Build context description
        context_desc = self._build_context_description(context)

        # Build system prompt based on mode
        system_prompt = self._get_system_prompt(mode, context_desc)

        return {
            'messages': [
                {'role': 'system', 'content': system_prompt},
                *history,
                {'role': 'user', 'content': prompt},
            ],
            'context': context or {},
            'mode': mode,
            'user_id': request.env.uid,
            'company_id': request.env.company.id,
        }

    def _build_context_description(self, context):
        """Build a text description of the current context"""
        if not context:
            return ''

        parts = []
        if context.get('model'):
            model_name = context.get('model_name') or context['model']
            parts.append(f"Current model: {model_name}")

        if context.get('res_id'):
            parts.append(f"Current record ID: {context['res_id']}")
            if context.get('display_name'):
                parts.append(f"Record name: {context['display_name']}")

        if context.get('view_type'):
            parts.append(f"View type: {context['view_type']}")

        if context.get('selected_ids'):
            parts.append(f"Selected records: {len(context['selected_ids'])} items")

        return '\n'.join(parts)

    def _get_system_prompt(self, mode, context_desc):
        """Get the system prompt based on mode"""
        base = """You are an AI assistant integrated into Odoo ERP.
You help users with their business operations by answering questions,
explaining data, and suggesting or executing actions.

Always respond with structured JSON in this format:
{
    "message": "Your response text here (supports markdown)",
    "citations": [
        {"model": "model.name", "res_id": 123, "label": "Display Name", "field": "field_name"}
    ],
    "actions": [
        {
            "type": "create|update|navigate|search",
            "label": "Action button label",
            "description": "What this action does",
            "payload": {},
            "preview_diff": {"field": {"old": "value", "new": "value"}}
        }
    ]
}

"""
        if context_desc:
            base += f"\nCurrent context:\n{context_desc}\n"

        if mode == 'ask':
            base += "\nMode: ASK - Answer questions and explain. Do not propose write actions."
        elif mode == 'do':
            base += "\nMode: DO - You can propose actions. Always include preview_diff for write operations."
        elif mode == 'explain':
            base += "\nMode: EXPLAIN - Provide detailed explanations with citations to relevant records."

        return base

    def _call_ai_backend(self, payload):
        """Call the external AI backend"""
        ICP = request.env['ir.config_parameter'].sudo()
        endpoint = ICP.get_param('ask_ai.endpoint')
        api_key = ICP.get_param('ask_ai.api_key')

        if not endpoint:
            # Return mock response for development
            return self._mock_ai_response(payload)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else '',
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise UserError('AI service timeout. Please try again.')
        except requests.exceptions.RequestException as e:
            raise UserError(f'AI service error: {str(e)}')

    def _mock_ai_response(self, payload):
        """Mock response for development without AI backend"""
        user_msg = payload['messages'][-1]['content'] if payload['messages'] else ''
        return {
            'message': f"This is a **mock response** to your query:\n\n> {user_msg}\n\nConfigure an AI endpoint in Settings → AI Copilot to enable real AI responses.",
            'citations': [],
            'actions': [],
            'tokens': {'prompt': 100, 'completion': 50},
        }

    def _validate_action(self, action):
        """Validate if an action is allowed to be executed"""
        ICP = request.env['ir.config_parameter'].sudo()

        # Get blocked models
        blocked = ICP.get_param('ask_ai.blocked_models', '')
        blocked_models = [m.strip() for m in blocked.split(',') if m.strip()]

        # Get allowed models (empty = all allowed)
        allowed = ICP.get_param('ask_ai.allowed_models', '')
        allowed_models = [m.strip() for m in allowed.split(',') if m.strip()]

        action_type = action.get('type')
        payload = action.get('payload', {})
        model = payload.get('model')

        if not model:
            return {'allowed': True}

        # Check blocked list
        if model in blocked_models:
            return {
                'allowed': False,
                'reason': f'Actions on {model} are not allowed'
            }

        # Check allowed list (if specified)
        if allowed_models and model not in allowed_models:
            return {
                'allowed': False,
                'reason': f'{model} is not in the allowed models list'
            }

        # Additional security checks for write operations
        if action_type in ['create', 'update']:
            # Check user has write access to the model
            try:
                Model = request.env[model]
                if action_type == 'create':
                    Model.check_access_rights('create')
                else:
                    Model.check_access_rights('write')
            except AccessDenied:
                return {
                    'allowed': False,
                    'reason': f'You do not have permission to {action_type} {model} records'
                }

        return {'allowed': True}
