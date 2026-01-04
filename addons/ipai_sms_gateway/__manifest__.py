# -*- coding: utf-8 -*-
{
    "name": "IPAI SMS Gateway",
    "version": "18.0.1.0.0",
    "category": "Marketing/SMS",
    "summary": "SMS gateway for sending messages via HTTP providers",
    "description": """
IPAI SMS Gateway
================

Production-ready SMS gateway module that:
- Sends SMS via HTTP API providers (Twilio, Infobip, custom)
- Logs all messages with delivery status
- Handles delivery receipts via webhook
- Provides health check endpoints

Models:
- ipai.sms.provider: Provider configuration (Twilio, Infobip, custom)
- ipai.sms.message: SMS message log with status tracking

Service Methods:
- send_sms(to, body, context={...}): Main entry point for sending SMS

Integration:
- Async queue via ir.cron for bulk sends
- Webhook endpoint for delivery receipts
- Health endpoint at /ipai/sms/health
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "icon": "fa-sms",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/ipai_sms_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
