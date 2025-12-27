# -*- coding: utf-8 -*-
"""
IPAI Studio AI - Natural Language Processing Service
=====================================================

Processes natural language commands to create Odoo customizations.
Integrates with the AI Assistant module.

Example commands:
- "Add a phone number field to contacts"
- "Create a status dropdown on sales orders"
- "When an invoice is confirmed, send an email"
- "Add a notes field to the task form"

Author: InsightPulse AI
License: AGPL-3
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Tuple

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# Field type detection patterns
FIELD_TYPE_PATTERNS = {
    'char': [
        r'\b(text|string|name|title|label|code|reference|number)\b',
        r'\b(phone|email|url|website)\b',
    ],
    'text': [
        r'\b(long\s*text|notes|comments|description|memo|remarks)\b',
        r'\b(multi.?line|paragraph)\b',
    ],
    'html': [
        r'\b(rich\s*text|html|formatted|wysiwyg)\b',
    ],
    'integer': [
        r'\b(integer|count|quantity|qty|sequence|number\s+of)\b',
        r'\b(age|year|days?)\b',
    ],
    'float': [
        r'\b(decimal|float|rate|percentage|percent|ratio)\b',
        r'\b(weight|height|length|width|size)\b',
    ],
    'monetary': [
        r'\b(price|cost|amount|money|currency|budget|fee|salary)\b',
        r'\b(total|subtotal|tax|discount)\b',
    ],
    'boolean': [
        r'\b(yes.?no|true.?false|checkbox|flag|toggle|switch)\b',
        r'\b(is_|has_|can_|allow|enable|active)\b',
    ],
    'date': [
        r'\b(date|day|when)\b(?!.*time)',
        r'\b(birthday|deadline|due|start|end|expiry)\b(?!.*time)',
    ],
    'datetime': [
        r'\b(datetime|timestamp|date\s*and\s*time|date.?time)\b',
    ],
    'selection': [
        r'\b(dropdown|select|choice|option|status|state|type|category|priority)\b',
        r'\b(pick\s*list|combo|enum)\b',
    ],
    'many2one': [
        r'\b(link\s*to|related\s*to|belongs\s*to|reference\s*to)\b',
        r'\b(parent|owner|assigned|responsible|manager)\b',
    ],
    'one2many': [
        r'\b(list\s*of|multiple|many|lines|items|children)\b',
    ],
    'many2many': [
        r'\b(tags|categories|multiple\s*select|multi.?select)\b',
    ],
    'binary': [
        r'\b(file|attachment|upload|image|photo|picture|document|pdf)\b',
    ],
}

# Model name patterns
MODEL_PATTERNS = {
    'res.partner': [
        r'\b(contact|customer|vendor|supplier|partner|client|company)\b',
    ],
    'sale.order': [
        r'\b(sale|sales?\s*order|quotation|quote)\b',
    ],
    'purchase.order': [
        r'\b(purchase|purchase\s*order|po|procurement)\b',
    ],
    'account.move': [
        r'\b(invoice|bill|journal\s*entry|accounting\s*entry)\b',
    ],
    'project.project': [
        r'\b(project)\b(?!.*task)',
    ],
    'project.task': [
        r'\b(task|todo|ticket|issue)\b',
    ],
    'hr.employee': [
        r'\b(employee|staff|worker|personnel)\b',
    ],
    'hr.expense': [
        r'\b(expense|reimbursement)\b',
    ],
    'product.product': [
        r'\b(product|item|sku|article)\b',
    ],
    'product.template': [
        r'\b(product\s*template|product\s*category)\b',
    ],
    'stock.picking': [
        r'\b(delivery|shipment|transfer|picking|receipt)\b',
    ],
    'crm.lead': [
        r'\b(lead|opportunity|prospect|crm)\b',
    ],
    'helpdesk.ticket': [
        r'\b(ticket|support|helpdesk|issue)\b',
    ],
    'mail.activity': [
        r'\b(activity|reminder|follow.?up)\b',
    ],
}

# Automation trigger patterns
TRIGGER_PATTERNS = {
    'on_create': [
        r'\b(when|if|after)\b.*\b(create|new|add)\b',
        r'\b(on\s*creation|upon\s*creation|after\s*creating)\b',
    ],
    'on_write': [
        r'\b(when|if|after)\b.*\b(update|change|modify|edit)\b',
        r'\b(on\s*update|upon\s*change|after\s*updating)\b',
    ],
    'on_unlink': [
        r'\b(when|if|after)\b.*\b(delete|remove)\b',
        r'\b(on\s*deletion|upon\s*delete)\b',
    ],
    'on_time': [
        r'\b(every|daily|weekly|monthly|hourly)\b',
        r'\b(at\s*\d+|schedule|cron|time.?based)\b',
        r'\b(before|after)\b.*\b(days?|hours?|minutes?)\b',
    ],
}


class StudioAIService(models.AbstractModel):
    """Service model for processing natural language Studio commands."""

    _name = 'ipai.studio.ai.service'
    _description = 'Studio AI Service'

    @api.model
    def process_command(self, command: str, context: dict = None) -> Dict[str, Any]:
        """
        Process a natural language command and return analysis.

        Args:
            command: Natural language command like "Add a phone field to contacts"
            context: Optional context (current model, view, etc.)

        Returns:
            dict with analysis and suggested action
        """
        command_lower = command.lower().strip()
        context = context or {}

        # Determine command type
        command_type = self._detect_command_type(command_lower)

        result = {
            'command': command,
            'type': command_type,
            'confidence': 0.0,
            'analysis': {},
            'ready': False,
            'message': '',
        }

        if command_type == 'field':
            result.update(self._analyze_field_command(command_lower, context))
        elif command_type == 'view':
            result.update(self._analyze_view_command(command_lower, context))
        elif command_type == 'automation':
            result.update(self._analyze_automation_command(command_lower, context))
        elif command_type == 'report':
            result.update(self._analyze_report_command(command_lower, context))
        else:
            result['message'] = _("I couldn't understand that command. Try:\n"
                                 "- 'Add a [field type] field called [name] to [model]'\n"
                                 "- 'When [event], do [action]'\n"
                                 "- 'Show [field] in the [model] list view'")

        return result

    def _detect_command_type(self, command: str) -> str:
        """Detect the type of command."""
        # Field creation patterns
        field_patterns = [
            r'\b(add|create|new|insert)\b.*\b(field|column)\b',
            r'\b(field|column)\b.*\b(for|to|on|in)\b',
            r'\badd\b.*\b(to|on|in)\b.*\b(model|form|view)\b',
        ]

        # View modification patterns
        view_patterns = [
            r'\b(show|display|add|hide|remove)\b.*\b(view|form|list|tree|kanban)\b',
            r'\b(move|reorder|rearrange)\b.*\bfield\b',
            r'\b(form|list|tree|kanban)\b.*\bview\b',
        ]

        # Automation patterns
        automation_patterns = [
            r'\b(when|if|after|before|every|on)\b.*\b(then|send|create|update|notify)\b',
            r'\b(automate|automation|automated|automatic)\b',
            r'\b(trigger|triggered|workflow)\b',
        ]

        # Report patterns
        report_patterns = [
            r'\b(report|pdf|print|export)\b',
            r'\b(generate|create)\b.*\b(document|report)\b',
        ]

        for pattern in field_patterns:
            if re.search(pattern, command):
                return 'field'

        for pattern in automation_patterns:
            if re.search(pattern, command):
                return 'automation'

        for pattern in view_patterns:
            if re.search(pattern, command):
                return 'view'

        for pattern in report_patterns:
            if re.search(pattern, command):
                return 'report'

        # Default: check if it mentions a field type
        for ftype in FIELD_TYPE_PATTERNS:
            for pattern in FIELD_TYPE_PATTERNS[ftype]:
                if re.search(pattern, command):
                    return 'field'

        return 'unknown'

    def _analyze_field_command(self, command: str, context: dict) -> dict:
        """Analyze a field creation command."""
        result = {
            'analysis': {
                'field_type': 'char',
                'field_name': '',
                'field_label': '',
                'model': '',
                'model_id': False,
                'required': False,
                'selection_options': [],
                'relation_model': '',
            },
            'confidence': 0.5,
            'ready': False,
        }

        analysis = result['analysis']

        # Detect field type
        for ftype, patterns in FIELD_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    analysis['field_type'] = ftype
                    result['confidence'] += 0.1
                    break

        # Extract field name (look for "called X", "named X", '"X"', etc.)
        name_patterns = [
            r'(?:called|named|label(?:ed)?)\s+["\']?([a-zA-Z_][a-zA-Z0-9_\s]*)["\']?',
            r'["\']([a-zA-Z_][a-zA-Z0-9_\s]*)["\'](?:\s+field)?',
            r'(?:add|create)\s+(?:a\s+)?(?:\w+\s+)?([a-zA-Z_][a-zA-Z0-9_\s]+?)\s+(?:field|to|on|for)',
        ]

        for pattern in name_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and name.lower() not in ['field', 'to', 'on', 'for', 'the', 'a', 'an']:
                    analysis['field_label'] = name.title()
                    analysis['field_name'] = 'x_' + re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                    result['confidence'] += 0.2
                    break

        # Detect target model
        for model, patterns in MODEL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    analysis['model'] = model
                    # Look up model ID
                    model_rec = self.env['ir.model'].search([('model', '=', model)], limit=1)
                    if model_rec:
                        analysis['model_id'] = model_rec.id
                        result['confidence'] += 0.2
                    break
            if analysis['model']:
                break

        # Use context model if not detected
        if not analysis['model'] and context.get('model'):
            analysis['model'] = context['model']
            model_rec = self.env['ir.model'].search([('model', '=', context['model'])], limit=1)
            if model_rec:
                analysis['model_id'] = model_rec.id

        # Check for required
        if re.search(r'\b(required|mandatory|must\s+have)\b', command):
            analysis['required'] = True

        # Extract selection options
        if analysis['field_type'] == 'selection':
            # Look for patterns like "options: a, b, c" or "choices are x, y, z"
            options_match = re.search(
                r'(?:options?|choices?|values?)(?:\s+are)?[:\s]+([^.]+)',
                command
            )
            if options_match:
                options_str = options_match.group(1)
                options = [o.strip() for o in re.split(r'[,;/]|\band\b|\bor\b', options_str) if o.strip()]
                analysis['selection_options'] = [
                    (re.sub(r'[^a-z0-9]+', '_', o.lower()), o.title())
                    for o in options
                ]

        # Extract relation model for relational fields
        if analysis['field_type'] in ('many2one', 'one2many', 'many2many'):
            rel_match = re.search(r'(?:link(?:ed)?\s+to|related?\s+to|of)\s+(\w+)', command)
            if rel_match:
                rel_name = rel_match.group(1).lower()
                for model, patterns in MODEL_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, rel_name):
                            analysis['relation_model'] = model
                            break

        # Determine if ready to create
        result['ready'] = (
            analysis['field_name'] and
            analysis['model_id'] and
            result['confidence'] >= 0.5
        )

        # Build message
        if result['ready']:
            result['message'] = _(
                "I'll create a **%s** field called **%s** on **%s**.\n\n"
                "Technical name: `%s`\n"
                "Type: %s%s\n\n"
                "Should I proceed?"
            ) % (
                analysis['field_type'],
                analysis['field_label'],
                analysis['model'],
                analysis['field_name'],
                analysis['field_type'],
                ' (required)' if analysis['required'] else '',
            )
        else:
            missing = []
            if not analysis['field_name']:
                missing.append("field name")
            if not analysis['model']:
                missing.append("target model")
            result['message'] = _(
                "I need more information to create the field. Missing: %s\n\n"
                "Try: 'Add a text field called \"Notes\" to contacts'"
            ) % ', '.join(missing)

        return result

    def _analyze_view_command(self, command: str, context: dict) -> dict:
        """Analyze a view modification command."""
        result = {
            'analysis': {
                'action': 'add',  # add, remove, move, show, hide
                'view_type': 'form',
                'field_name': '',
                'position': 'after',
                'target_field': 'name',
                'model': '',
            },
            'confidence': 0.3,
            'ready': False,
            'message': _("View modification is in beta. For now, please use the Field Creator to add fields to views automatically."),
        }

        # Detect action
        if re.search(r'\b(add|show|display|insert)\b', command):
            result['analysis']['action'] = 'add'
        elif re.search(r'\b(hide|remove|delete)\b', command):
            result['analysis']['action'] = 'hide'
        elif re.search(r'\b(move|reorder)\b', command):
            result['analysis']['action'] = 'move'

        # Detect view type
        if re.search(r'\b(list|tree)\b', command):
            result['analysis']['view_type'] = 'tree'
        elif re.search(r'\b(kanban)\b', command):
            result['analysis']['view_type'] = 'kanban'
        elif re.search(r'\b(search)\b', command):
            result['analysis']['view_type'] = 'search'

        return result

    def _analyze_automation_command(self, command: str, context: dict) -> dict:
        """Analyze an automation command."""
        result = {
            'analysis': {
                'trigger': 'on_create',
                'action_type': 'code',
                'model': '',
                'model_id': False,
                'filter_domain': '[]',
                'description': '',
            },
            'confidence': 0.4,
            'ready': False,
        }

        analysis = result['analysis']

        # Detect trigger
        for trigger, patterns in TRIGGER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    analysis['trigger'] = trigger
                    result['confidence'] += 0.1
                    break

        # Detect model
        for model, patterns in MODEL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    analysis['model'] = model
                    model_rec = self.env['ir.model'].search([('model', '=', model)], limit=1)
                    if model_rec:
                        analysis['model_id'] = model_rec.id
                        result['confidence'] += 0.2
                    break

        # Detect action type
        if re.search(r'\b(email|send\s+email|mail)\b', command):
            analysis['action_type'] = 'email'
        elif re.search(r'\b(sms|text\s+message)\b', command):
            analysis['action_type'] = 'sms'
        elif re.search(r'\b(webhook|api|http|url)\b', command):
            analysis['action_type'] = 'webhook'
        elif re.search(r'\b(activity|reminder|follow.?up)\b', command):
            analysis['action_type'] = 'activity'

        # Extract description/action from command
        analysis['description'] = command[:100]

        result['message'] = _(
            "I'll create an automation:\n\n"
            "• **Trigger:** %s\n"
            "• **Model:** %s\n"
            "• **Action:** %s\n\n"
            "Use the Automation Wizard for full control over the automation settings."
        ) % (
            analysis['trigger'].replace('_', ' ').title(),
            analysis['model'] or 'Not detected',
            analysis['action_type'].replace('_', ' ').title(),
        )

        return result

    def _analyze_report_command(self, command: str, context: dict) -> dict:
        """Analyze a report command."""
        return {
            'analysis': {},
            'confidence': 0.2,
            'ready': False,
            'message': _("Report creation is coming soon. For now, you can:\n"
                        "1. Use Accounting → Reports for financial reports\n"
                        "2. Export data to Excel using the action menu\n"
                        "3. Create a custom report module"),
        }

    @api.model
    def execute_field_creation(self, analysis: dict) -> Dict[str, Any]:
        """Execute field creation from analysis."""
        if not analysis.get('model_id'):
            return {'success': False, 'error': _("No model specified")}

        if not analysis.get('field_name'):
            return {'success': False, 'error': _("No field name specified")}

        field_name = analysis['field_name']
        if not field_name.startswith('x_'):
            field_name = 'x_' + field_name

        # Check if exists
        existing = self.env['ir.model.fields'].search([
            ('model_id', '=', analysis['model_id']),
            ('name', '=', field_name),
        ])
        if existing:
            return {'success': False, 'error': _("Field already exists")}

        # Create field
        vals = {
            'name': field_name,
            'field_description': analysis.get('field_label', field_name.replace('x_', '').replace('_', ' ').title()),
            'model_id': analysis['model_id'],
            'ttype': analysis.get('field_type', 'char'),
            'required': analysis.get('required', False),
            'state': 'manual',
        }

        # Selection options
        if analysis.get('selection_options'):
            vals['selection'] = str(analysis['selection_options'])

        # Relation
        if analysis.get('relation_model'):
            vals['relation'] = analysis['relation_model']

        try:
            field = self.env['ir.model.fields'].create(vals)
            return {
                'success': True,
                'field_id': field.id,
                'field_name': field.name,
                'message': _("Field '%s' created successfully!") % field.field_description,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AIAssistantStudioMixin(models.AbstractModel):
    """Mixin to add Studio capabilities to AI Assistant."""

    _name = 'ipai.ai.studio.mixin'
    _description = 'AI Assistant Studio Mixin'

    @api.model
    def handle_studio_command(self, message: str, context: dict = None) -> Optional[str]:
        """
        Handle a potential Studio command from AI Assistant.

        Returns response string if handled, None if not a studio command.
        """
        studio_keywords = [
            'add field', 'create field', 'new field',
            'automation', 'automate', 'when', 'trigger',
            'modify view', 'add to form', 'add to list',
            'customize', 'studio',
        ]

        message_lower = message.lower()
        if not any(kw in message_lower for kw in studio_keywords):
            return None

        # Process through Studio AI Service
        service = self.env['ipai.studio.ai.service']
        result = service.process_command(message, context)

        return result.get('message', '')
