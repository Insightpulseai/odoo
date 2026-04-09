import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GoogleWorkspaceAddonController(http.Controller):
    """Backend API for the W9 Studio Google Workspace Add-on.

    Card JSON endpoints consumed by the add-on framework.
    Auth: Google ID token → session token → Odoo user context.

    Routes:
        POST /ipai/gws/session        — Exchange Google ID token for session
        POST /ipai/gws/gmail/homepage  — Gmail sidebar homepage card
        POST /ipai/gws/gmail/context   — Contextual card for opened email
        POST /ipai/gws/calendar/home   — Calendar sidebar homepage card
        POST /ipai/gws/lead/create     — Create CRM lead from add-on
        GET  /ipai/gws/availability    — Studio availability (public)
    """

    # ── Session Exchange ───────────────────────────────────────────────

    @http.route(
        '/ipai/gws/session',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def exchange_session(self):
        """Exchange a Google ID token for an Odoo session token.

        Expected payload: { "id_token": "<google_jwt>" }
        Returns: { "session_token": "...", "expires_at": "...", "user_name": "..." }
        """
        data = json.loads(request.httprequest.data)
        id_token = data.get('id_token', '')

        if not id_token:
            return {'error': 'id_token required'}

        # Verify Google ID token
        payload = self._verify_google_id_token(id_token)
        if not payload:
            return {'error': 'Invalid Google ID token'}

        google_sub = payload['sub']
        google_email = payload['email']

        session_data = (
            request.env['google.workspace.session']
            .sudo()
            .create_or_refresh_session(google_sub, google_email)
        )
        return session_data

    # ── Gmail Sidebar ──────────────────────────────────────────────────

    @http.route(
        '/ipai/gws/gmail/homepage',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def gmail_homepage(self):
        """Gmail sidebar homepage card — shown when add-on is opened."""
        return {
            'renderActions': {
                'action': {
                    'navigations': [{
                        'pushCard': self._build_homepage_card()
                    }]
                }
            }
        }

    @http.route(
        '/ipai/gws/gmail/context',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def gmail_context(self):
        """Contextual card for opened email — extract sender, suggest lead."""
        data = json.loads(request.httprequest.data)
        gmail_data = data.get('gmail', {})
        message_id = gmail_data.get('messageId', '')
        sender_email = gmail_data.get('senderEmail', '')
        subject = gmail_data.get('subject', '')

        # Check if lead already exists for this sender
        lead = None
        if sender_email:
            lead = request.env['crm.lead'].sudo().search([
                ('email_from', '=', sender_email),
            ], limit=1)

        return {
            'renderActions': {
                'action': {
                    'navigations': [{
                        'pushCard': self._build_context_card(
                            sender_email, subject, lead
                        )
                    }]
                }
            }
        }

    # ── Calendar Sidebar ───────────────────────────────────────────────

    @http.route(
        '/ipai/gws/calendar/home',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def calendar_homepage(self):
        """Calendar sidebar — show W9 Studio availability."""
        return {
            'renderActions': {
                'action': {
                    'navigations': [{
                        'pushCard': self._build_calendar_card()
                    }]
                }
            }
        }

    # ── Lead Creation ──────────────────────────────────────────────────

    @http.route(
        '/ipai/gws/lead/create',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def create_lead(self):
        """Create a CRM lead from the Gmail add-on context."""
        data = json.loads(request.httprequest.data)
        session_token = data.get('session_token', '')

        user = (
            request.env['google.workspace.session']
            .sudo()
            .validate_session(session_token)
        )

        lead_vals = {
            'name': data.get('name', 'W9 Studio Inquiry'),
            'contact_name': data.get('contact_name', ''),
            'email_from': data.get('email', ''),
            'phone': data.get('phone', ''),
            'description': data.get('description', ''),
            'type': 'lead',
            'tag_ids': [],
        }

        lead = (
            request.env['crm.lead']
            .with_user(user)
            .create(lead_vals)
        )

        return {
            'status': 'ok',
            'lead_id': lead.id,
            'lead_name': lead.name,
        }

    # ── Public Availability ────────────────────────────────────────────

    @http.route(
        '/ipai/gws/availability',
        type='json',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
    )
    def get_availability(self):
        """Return studio availability for the next 30 days.

        Public endpoint — no auth required. Used by both the
        landing page calendar widget and the Workspace add-on.
        """
        from datetime import datetime, timedelta

        start = datetime.utcnow()
        end = start + timedelta(days=30)

        # Check Odoo calendar for W9 Studio bookings
        events = request.env['calendar.event'].sudo().search([
            ('start', '>=', start),
            ('start', '<=', end),
            ('name', 'ilike', 'W9 Studio'),
        ])

        booked_dates = []
        for event in events:
            booked_dates.append({
                'date': event.start.strftime('%Y-%m-%d'),
                'start_time': event.start.strftime('%H:%M'),
                'end_time': event.stop.strftime('%H:%M'),
                'type': 'booked',
            })

        return {
            'studio': 'W9 Studio',
            'period': {
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d'),
            },
            'booked': booked_dates,
        }

    # ── Copilot Bridge (GWS → Pulser) ──────────────────────────────────

    @http.route(
        '/ipai/gws/copilot/chat',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def copilot_chat(self):
        """Bridge Google Workspace users to the Odoo copilot.

        Authenticates via GWS session token, then dispatches to the
        copilot gateway using the resolved Odoo user context.

        Expected payload:
            {
                "session_token": "...",
                "message": "...",
                "context": {"surface": "gmail"|"calendar"}
            }
        """
        data = json.loads(request.httprequest.data)
        session_token = data.get('session_token', '')
        message = data.get('message', '').strip()

        if not session_token:
            return {'error': True, 'message': 'session_token required'}
        if not message:
            return {'error': True, 'message': 'message required'}

        # Validate GWS session → Odoo user
        user = (
            request.env['google.workspace.session']
            .sudo()
            .validate_session(session_token)
        )
        if not user:
            return {'error': True, 'message': 'Invalid or expired session'}

        # Dispatch to copilot gateway as the resolved Odoo user
        context = data.get('context', {})
        surface = context.get('surface', 'gmail')

        try:
            from odoo.addons.ipai_odoo_copilot.controllers.copilot_gateway import (
                CopilotGatewayController,
            )
            gateway = CopilotGatewayController()

            # Build minimal context for the copilot
            copilot_context = {
                'context_model': '',
                'context_res_id': 0,
                'surface': surface,
            }

            # Use the copilot's OpenAI dispatch directly
            import uuid
            correlation_id = str(uuid.uuid4())
            system_prompt = (
                'You are Pulser, the W9 Studio assistant. '
                'The user is accessing you from Google Workspace (%s sidebar). '
                'Help with studio bookings, rates, availability, and general questions. '
                'Be concise. Use markdown.' % surface
            )
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message},
            ]

            resp_data, latency_ms = gateway._call_openai(messages, correlation_id)

            _logger.info(
                'GWS copilot chat: user=%s surface=%s latency=%dms',
                user.login, surface, latency_ms,
            )

            return {
                'content': resp_data.get('content', ''),
                'request_id': correlation_id,
                'latency_ms': latency_ms,
                'user_name': user.name,
            }

        except Exception as e:
            _logger.warning('GWS copilot error: %s', e)
            return {'error': True, 'message': 'Copilot unavailable: %s' % str(e)}

    # ── Card Builders (private) ────────────────────────────────────────

    def _build_homepage_card(self):
        """Build the Gmail sidebar homepage card JSON."""
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'header': {
                'title': 'Studio W9',
                'subtitle': 'Commercial Production Studio',
                'imageUrl': f'{base_url}/web/image/website/1/logo',
                'imageType': 'CIRCLE',
            },
            'sections': [
                {
                    'header': 'Quick Actions',
                    'widgets': [
                        {
                            'decoratedText': {
                                'topLabel': 'Book Studio',
                                'text': 'Create a new booking inquiry',
                                'button': {
                                    'text': 'Book Now',
                                    'onClick': {
                                        'action': {
                                            'function': 'openBookingForm',
                                        }
                                    }
                                }
                            }
                        },
                        {
                            'decoratedText': {
                                'topLabel': 'Check Availability',
                                'text': 'View studio calendar',
                                'button': {
                                    'text': 'View',
                                    'onClick': {
                                        'openLink': {
                                            'url': 'https://insightpulseai.com/w9studio#book',
                                        }
                                    }
                                }
                            }
                        },
                    ],
                },
                {
                    'header': 'Studio Details',
                    'widgets': [
                        {
                            'decoratedText': {
                                'topLabel': 'Location',
                                'text': 'Warehouse 9, La Fuerza Plaza II\n2241 Chino Roces Ave, Bangkal\nMakati City 1233',
                            }
                        },
                        {
                            'decoratedText': {
                                'topLabel': 'Rates',
                                'text': 'From PHP 2,500/hr\nHalf-day & full-day packages available',
                            }
                        },
                    ],
                },
                {
                    'header': 'AI Assistant',
                    'widgets': [
                        {
                            'decoratedText': {
                                'topLabel': 'Pulser',
                                'text': 'Ask about rates, availability, equipment, or bookings',
                                'button': {
                                    'text': 'Ask Pulser',
                                    'onClick': {
                                        'action': {
                                            'function': 'openPulserChat',
                                        }
                                    }
                                }
                            }
                        },
                    ],
                },
                {
                    'header': 'Payment Methods',
                    'widgets': [
                        {
                            'decoratedText': {
                                'topLabel': 'Accepted',
                                'text': 'GCash  •  Maya  •  PayPal  •  Bank Transfer  •  Credit Card',
                            }
                        },
                    ],
                },
            ],
        }

    def _build_context_card(self, sender_email, subject, lead=None):
        """Build contextual card for an opened email."""
        widgets = []

        if lead:
            widgets.append({
                'decoratedText': {
                    'topLabel': 'Existing Lead',
                    'text': lead.name,
                    'button': {
                        'text': 'Open in Odoo',
                        'onClick': {
                            'openLink': {
                                'url': f'/web#id={lead.id}&model=crm.lead',
                            }
                        }
                    }
                }
            })
        else:
            widgets.append({
                'decoratedText': {
                    'topLabel': 'No existing lead',
                    'text': f'Create lead for {sender_email}?',
                    'button': {
                        'text': 'Create Lead',
                        'onClick': {
                            'action': {
                                'function': 'createLeadFromEmail',
                                'parameters': [{
                                    'key': 'email',
                                    'value': sender_email,
                                }, {
                                    'key': 'subject',
                                    'value': subject,
                                }],
                            }
                        }
                    }
                }
            })

        return {
            'header': {
                'title': 'W9 Studio CRM',
                'subtitle': sender_email,
            },
            'sections': [{
                'widgets': widgets,
            }],
        }

    def _build_calendar_card(self):
        """Build calendar sidebar card with availability."""
        from datetime import datetime, timedelta

        start = datetime.utcnow()
        end = start + timedelta(days=7)

        events = request.env['calendar.event'].sudo().search([
            ('start', '>=', start),
            ('start', '<=', end),
            ('name', 'ilike', 'W9 Studio'),
        ], order='start asc', limit=10)

        widgets = []
        if events:
            for event in events:
                widgets.append({
                    'decoratedText': {
                        'topLabel': event.start.strftime('%a %b %d'),
                        'text': f'{event.start.strftime("%H:%M")} – {event.stop.strftime("%H:%M")}',
                        'bottomLabel': 'Booked',
                    }
                })
        else:
            widgets.append({
                'decoratedText': {
                    'text': 'All slots available this week',
                    'topLabel': 'Availability',
                }
            })

        return {
            'header': {
                'title': 'W9 Studio Calendar',
                'subtitle': 'Next 7 days',
            },
            'sections': [{
                'header': 'Upcoming Bookings',
                'widgets': widgets,
            }],
        }

    # ── Google ID Token Verification ───────────────────────────────────

    def _verify_google_id_token(self, id_token):
        """Verify Google ID token using Google's tokeninfo endpoint.

        Production should use google-auth library with cached certs.
        This is a minimal implementation for the add-on backend.
        """
        import requests

        try:
            resp = requests.get(
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': id_token},
                timeout=10,
            )
            if resp.status_code != 200:
                _logger.warning('Google ID token verification failed: %s', resp.text)
                return None

            payload = resp.json()

            # Validate claims
            if payload.get('email_verified') != 'true':
                return None

            return payload

        except Exception as e:
            _logger.error('Google ID token verification error: %s', e)
            return None
