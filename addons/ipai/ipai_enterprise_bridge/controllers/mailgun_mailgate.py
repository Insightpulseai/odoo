# -*- coding: utf-8 -*-
"""
Mailgun Mailgate Controller for Odoo 18 CE

This controller implements the /mailgate/mailgun endpoint to receive
inbound emails from Mailgun webhooks and create mail.message records.

Architecture:
    Mailgun (mg.insightpulseai.com)
        → Route: match_recipient(".*@insightpulseai.com")
        → Forward to: https://erp.insightpulseai.com/mailgate/mailgun
        → This controller processes and creates mail.message

Expected Mailgun POST payload (application/x-www-form-urlencoded):
    - sender: email address of sender
    - recipient: target recipient address
    - subject: email subject line
    - body-plain: plain text body
    - body-html: HTML body (optional)
    - stripped-text: body without signatures (optional)
    - Message-Id: unique message identifier
    - timestamp: Unix timestamp
    - token: Mailgun verification token
    - signature: HMAC signature for verification
    - attachments: JSON array of attachment info (optional)

Security:
    - CSRF disabled for webhook endpoint
    - Mailgun signature verification recommended in production
    - Rate limiting via Odoo's built-in mechanisms
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Mailgun signature verification tolerance (seconds)
SIGNATURE_TOLERANCE = 300


class MailgunMailgateController(http.Controller):
    """
    HTTP Controller for Mailgun inbound email webhooks.

    This implements Enterprise-equivalent mail gateway functionality
    for Odoo CE, replacing the need for fetchmail or IMAP polling.
    """

    @http.route(
        "/mailgate/mailgun",
        type="http",
        auth="public",
        methods=["POST", "GET"],
        csrf=False,
    )
    def mailgun_mailgate(self, **kwargs):
        """
        Handle inbound email from Mailgun webhook.

        GET: Health check endpoint returns 200 OK
        POST: Process Mailgun webhook payload and create mail.message

        Returns:
            - 200 OK: Message processed successfully
            - 400 Bad Request: Missing required fields
            - 401 Unauthorized: Invalid signature (if verification enabled)
            - 500 Internal Error: Processing failure
        """
        if request.httprequest.method == "GET":
            # Health check endpoint
            return request.make_response(
                "OK - Mailgun Mailgate Active",
                headers=[("Content-Type", "text/plain")],
            )

        try:
            return self._process_mailgun_webhook(kwargs)
        except Exception as e:
            _logger.exception("Mailgun mailgate error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[("Content-Type", "application/json")],
                status=500,
            )

    def _process_mailgun_webhook(self, data):
        """
        Process the Mailgun webhook payload.

        Args:
            data: POST form data from Mailgun

        Returns:
            HTTP Response with processing result
        """
        # Extract fields from Mailgun payload
        sender = data.get("sender", data.get("from", ""))
        recipient = data.get("recipient", data.get("To", ""))
        subject = data.get("subject", "(No Subject)")
        body_plain = data.get("body-plain", data.get("stripped-text", ""))
        body_html = data.get("body-html", "")
        message_id = data.get("Message-Id", "")
        timestamp = data.get("timestamp", "")
        token = data.get("token", "")
        signature = data.get("signature", "")

        _logger.info(
            "Mailgun webhook received: from=%s, to=%s, subject=%s",
            sender,
            recipient,
            subject,
        )

        # Validate required fields
        if not sender:
            return request.make_response(
                json.dumps({"status": "error", "message": "Missing sender"}),
                headers=[("Content-Type", "application/json")],
                status=400,
            )

        # Optional: Verify Mailgun signature
        # Uncomment and configure MAILGUN_API_KEY in res.config.settings
        # if not self._verify_mailgun_signature(timestamp, token, signature):
        #     return request.make_response(
        #         json.dumps({'status': 'error', 'message': 'Invalid signature'}),
        #         headers=[('Content-Type', 'application/json')],
        #         status=401,
        #     )

        # Determine message body (prefer HTML, fallback to plain)
        body = body_html if body_html else f"<pre>{body_plain}</pre>"

        # Generate message_id if not provided
        if not message_id:
            message_id = f"<mailgun-{int(time.time())}-{hash(sender + subject)}@mg.insightpulseai.com>"

        # Create mail.message record
        try:
            message_vals = {
                "message_type": "email",
                "subtype_id": request.env.ref("mail.mt_comment").id,
                "email_from": sender,
                "author_id": self._find_or_create_partner(sender),
                "subject": subject,
                "body": body,
                "message_id": message_id,
                "date": datetime.now(),
            }

            # Try to route to appropriate record
            model, res_id = self._route_message(recipient, subject)
            if model and res_id:
                message_vals["model"] = model
                message_vals["res_id"] = res_id

            message = request.env["mail.message"].sudo().create(message_vals)

            _logger.info(
                "Created mail.message id=%s from %s, subject=%s",
                message.id,
                sender,
                subject,
            )

            return request.make_response(
                json.dumps(
                    {
                        "status": "ok",
                        "message_id": message.id,
                        "message": "Email processed successfully",
                    }
                ),
                headers=[("Content-Type", "application/json")],
                status=200,
            )

        except Exception as e:
            _logger.exception("Failed to create mail.message: %s", str(e))
            raise

    def _find_or_create_partner(self, email):
        """
        Find existing partner by email or return False.

        Does NOT auto-create partners to avoid polluting the database.
        Returns partner_id if found, False otherwise.
        """
        if not email:
            return False

        Partner = request.env["res.partner"].sudo()

        # Extract email if it contains name <email> format
        if "<" in email and ">" in email:
            email = email.split("<")[1].split(">")[0]

        partner = Partner.search([("email", "=ilike", email)], limit=1)
        return partner.id if partner else False

    def _route_message(self, recipient, subject):
        """
        Route incoming message to appropriate Odoo record.

        Routing rules:
        - invoices@*: route to account.move (invoices)
        - support@*: route to helpdesk.ticket (if installed)
        - sales@*: route to crm.lead (if installed)
        - Otherwise: unrouted (general inbox)

        Returns:
            tuple(model, res_id) or (None, None) if no routing match
        """
        if not recipient:
            return None, None

        recipient_lower = recipient.lower()

        # Invoice routing: try to find invoice by reference in subject
        if "invoice" in recipient_lower or "invoices" in recipient_lower:
            return self._route_to_invoice(subject)

        # Add more routing rules as needed
        # if 'support' in recipient_lower:
        #     return self._route_to_helpdesk(subject)

        return None, None

    def _route_to_invoice(self, subject):
        """
        Try to route to an existing invoice based on subject line.

        Searches for invoice references like INV/2026/0001 in subject.
        """
        if not subject:
            return None, None

        Move = request.env["account.move"].sudo()

        # Try to find invoice by name/reference in subject
        # Common patterns: INV/2026/0001, BILL/2026/0001, etc.
        invoice = Move.search(
            [
                ("name", "ilike", subject),
                ("move_type", "in", ["out_invoice", "in_invoice"]),
            ],
            limit=1,
        )

        if invoice:
            return "account.move", invoice.id

        return None, None

    def _verify_mailgun_signature(self, timestamp, token, signature):
        """
        Verify Mailgun webhook signature using HMAC-SHA256.

        Requires MAILGUN_API_KEY to be configured in system parameters.

        Args:
            timestamp: Unix timestamp from Mailgun
            token: Random token from Mailgun
            signature: HMAC signature from Mailgun

        Returns:
            True if signature is valid, False otherwise
        """
        if not all([timestamp, token, signature]):
            _logger.warning("Mailgun signature verification failed: missing parameters")
            return False

        # Check timestamp is within tolerance
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > SIGNATURE_TOLERANCE:
                _logger.warning(
                    "Mailgun signature verification failed: timestamp expired"
                )
                return False
        except (ValueError, TypeError):
            return False

        # Get API key from config
        api_key = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_enterprise_bridge.mailgun_api_key", "")
        )

        if not api_key:
            _logger.warning(
                "Mailgun API key not configured, skipping signature verification"
            )
            return True  # Allow without verification if not configured

        # Compute expected signature
        data = f"{timestamp}{token}".encode("utf-8")
        expected = hmac.new(api_key.encode("utf-8"), data, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected, signature)
