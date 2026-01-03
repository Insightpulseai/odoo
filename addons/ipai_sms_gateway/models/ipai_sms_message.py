# -*- coding: utf-8 -*-
import json
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiSmsMessage(models.Model):
    """SMS Message log with delivery status tracking."""

    _name = "ipai.sms.message"
    _description = "SMS Message"
    _order = "create_date desc"
    _inherit = ["mail.thread"]

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.sms.message") or "SMS-NEW",
        copy=False,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("queued", "Queued"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ], string="Status", default="draft", tracking=True)

    # Message content
    to_number = fields.Char(string="To Number", required=True)
    from_number = fields.Char(string="From Number")
    body = fields.Text(string="Message Body", required=True)

    provider_id = fields.Many2one(
        "ipai.sms.provider",
        string="Provider",
        domain="[('active', '=', True)]",
    )

    # External tracking
    external_id = fields.Char(
        string="External Message ID",
        help="Message ID from the SMS provider",
    )

    # Source context
    res_model = fields.Char(string="Related Model")
    res_id = fields.Integer(string="Related Record ID")
    partner_id = fields.Many2one("res.partner", string="Related Partner")

    # Execution tracking
    sent_at = fields.Datetime(string="Sent At")
    delivered_at = fields.Datetime(string="Delivered At")

    retry_count = fields.Integer(string="Retry Count", default=0)
    error_code = fields.Char(string="Error Code")
    error_message = fields.Text(string="Error Message")

    # Provider response
    raw_response = fields.Text(string="Raw Response")

    # Cost tracking
    segments = fields.Integer(string="Message Segments", default=1)
    cost = fields.Float(string="Cost")

    @api.model
    def send_sms(self, to, body, context=None):
        """
        Main entry point for sending SMS.

        Args:
            to: Recipient phone number (E.164 format preferred)
            body: Message content
            context: Optional dict with:
                - res_model: Related model
                - res_id: Related record ID
                - partner_id: Related partner ID
                - provider_id: Specific provider to use
                - async: If True, queue instead of send immediately

        Returns:
            ipai.sms.message record
        """
        context = context or {}

        provider = None
        if context.get("provider_id"):
            provider = self.env["ipai.sms.provider"].browse(context["provider_id"])
        else:
            provider = self.env["ipai.sms.provider"].get_default_provider()

        if not provider:
            raise UserError("No SMS provider configured")

        # Create message record
        message = self.create({
            "to_number": to,
            "from_number": provider.sender_id,
            "body": body,
            "provider_id": provider.id,
            "res_model": context.get("res_model"),
            "res_id": context.get("res_id"),
            "partner_id": context.get("partner_id"),
            "segments": self._calculate_segments(body),
        })

        if context.get("async"):
            message.action_queue()
        else:
            message.action_send()

        return message

    def _calculate_segments(self, body):
        """Calculate SMS segments based on message length."""
        if not body:
            return 0
        # GSM-7: 160 chars (single) or 153 chars per segment (multi)
        # UCS-2: 70 chars (single) or 67 chars per segment (multi)
        length = len(body)
        if length <= 160:
            return 1
        return (length + 152) // 153

    def action_queue(self):
        """Queue message for async sending."""
        for rec in self.filtered(lambda r: r.state == "draft"):
            rec.state = "queued"
        return True

    def action_send(self):
        """Send message immediately."""
        for rec in self.filtered(lambda r: r.state in ("draft", "queued", "failed")):
            rec._send_sms()
        return True

    def action_reset(self):
        """Reset failed message to draft."""
        for rec in self.filtered(lambda r: r.state == "failed"):
            rec.write({
                "state": "draft",
                "error_code": False,
                "error_message": False,
                "retry_count": 0,
            })
        return True

    def _send_sms(self):
        """Execute SMS sending."""
        self.ensure_one()

        self.write({
            "state": "sending",
            "error_code": False,
            "error_message": False,
        })

        try:
            provider = self.provider_id
            if not provider:
                raise UserError("No provider configured")

            result = self._call_sms_provider()

            self.write({
                "state": "sent",
                "sent_at": fields.Datetime.now(),
                "external_id": result.get("message_id"),
                "raw_response": json.dumps(result.get("raw", {})),
                "cost": result.get("cost", 0.0),
            })

            _logger.info("SMS %s sent successfully: %s", self.name, result.get("message_id"))

        except Exception as e:
            _logger.exception("SMS %s failed: %s", self.name, str(e))
            self.write({
                "state": "failed",
                "error_message": str(e),
                "retry_count": self.retry_count + 1,
            })

    def _call_sms_provider(self):
        """Call the configured SMS provider."""
        self.ensure_one()

        provider = self.provider_id
        provider_type = provider.provider_type

        if provider_type == "twilio":
            return self._send_twilio()
        elif provider_type == "infobip":
            return self._send_infobip()
        elif provider_type == "nexmo":
            return self._send_nexmo()
        elif provider_type == "custom":
            return self._send_custom()
        else:
            raise UserError(f"Unsupported provider type: {provider_type}")

    def _send_twilio(self):
        """Send via Twilio."""
        import requests
        from requests.auth import HTTPBasicAuth

        provider = self.provider_id
        auth_token = provider.get_auth_token()

        if not provider.account_sid or not auth_token:
            raise UserError("Twilio credentials not configured")

        url = f"https://api.twilio.com/2010-04-01/Accounts/{provider.account_sid}/Messages.json"

        data = {
            "To": self.to_number,
            "From": self.from_number,
            "Body": self.body,
        }

        response = requests.post(
            url,
            data=data,
            auth=HTTPBasicAuth(provider.account_sid, auth_token),
            timeout=provider.timeout,
        )

        result = response.json()

        if response.status_code >= 400:
            raise UserError(f"Twilio error: {result.get('message', 'Unknown error')}")

        return {
            "message_id": result.get("sid"),
            "raw": result,
            "cost": float(result.get("price", 0) or 0),
        }

    def _send_infobip(self):
        """Send via Infobip."""
        import requests

        provider = self.provider_id
        api_key = provider.get_auth_token()

        if not api_key:
            raise UserError("Infobip API key not configured")

        base_url = provider.base_url or "https://api.infobip.com"
        url = f"{base_url}/sms/2/text/advanced"

        headers = {
            "Authorization": f"App {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [{
                "destinations": [{"to": self.to_number}],
                "from": self.from_number,
                "text": self.body,
            }]
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=provider.timeout,
        )

        result = response.json()

        if response.status_code >= 400:
            raise UserError(f"Infobip error: {result.get('requestError', {}).get('serviceException', {}).get('text', 'Unknown error')}")

        messages = result.get("messages", [{}])
        message_id = messages[0].get("messageId") if messages else None

        return {
            "message_id": message_id,
            "raw": result,
        }

    def _send_nexmo(self):
        """Send via Vonage/Nexmo."""
        import requests

        provider = self.provider_id
        api_secret = provider.get_auth_token()

        if not provider.account_sid or not api_secret:
            raise UserError("Nexmo credentials not configured")

        url = "https://rest.nexmo.com/sms/json"

        params = {
            "api_key": provider.account_sid,
            "api_secret": api_secret,
            "to": self.to_number,
            "from": self.from_number,
            "text": self.body,
        }

        response = requests.post(url, data=params, timeout=provider.timeout)
        result = response.json()

        messages = result.get("messages", [{}])
        if messages and messages[0].get("status") != "0":
            raise UserError(f"Nexmo error: {messages[0].get('error-text', 'Unknown error')}")

        return {
            "message_id": messages[0].get("message-id") if messages else None,
            "raw": result,
            "cost": float(messages[0].get("message-price", 0) or 0) if messages else 0,
        }

    def _send_custom(self):
        """Send via custom HTTP API."""
        import requests

        provider = self.provider_id

        if not provider.base_url:
            raise UserError("Custom API URL not configured")

        headers = {}
        auth_token = provider.get_auth_token()
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        payload = {
            "to": self.to_number,
            "from": self.from_number,
            "body": self.body,
        }

        response = requests.post(
            provider.base_url,
            headers=headers,
            json=payload,
            timeout=provider.timeout,
        )
        response.raise_for_status()

        result = response.json()

        return {
            "message_id": result.get("message_id") or result.get("id"),
            "raw": result,
        }

    def update_delivery_status(self, external_id, status, error_code=None, error_message=None):
        """
        Update message status from delivery receipt webhook.

        Args:
            external_id: Provider message ID
            status: New status (delivered, failed)
            error_code: Optional error code
            error_message: Optional error message
        """
        message = self.search([("external_id", "=", external_id)], limit=1)
        if not message:
            _logger.warning("SMS delivery receipt for unknown message: %s", external_id)
            return False

        vals = {"state": status}
        if status == "delivered":
            vals["delivered_at"] = fields.Datetime.now()
        elif status == "failed":
            vals["error_code"] = error_code
            vals["error_message"] = error_message

        message.write(vals)
        _logger.info("SMS %s status updated to %s", message.name, status)
        return True

    @api.model
    def _cron_process_queued_messages(self):
        """Cron job to send queued messages."""
        queued = self.search([
            ("state", "=", "queued"),
        ], limit=50, order="create_date asc")

        for msg in queued:
            try:
                msg._send_sms()
                self.env.cr.commit()
            except Exception as e:
                _logger.exception("Cron SMS %s failed: %s", msg.name, str(e))
                self.env.cr.rollback()

        _logger.info("Cron processed %d SMS messages", len(queued))
        return True

    @api.model
    def _cron_retry_failed_messages(self):
        """Cron job to retry failed messages."""
        # Retry messages that failed less than max_retries ago
        failed = self.search([
            ("state", "=", "failed"),
            ("retry_count", "<", 3),
        ], limit=20, order="create_date asc")

        for msg in failed:
            try:
                msg._send_sms()
                self.env.cr.commit()
            except Exception as e:
                _logger.exception("Retry SMS %s failed: %s", msg.name, str(e))
                self.env.cr.rollback()

        return True

    @api.model
    def get_health_status(self):
        """Return health status for monitoring."""
        queued_count = self.search_count([("state", "=", "queued")])
        sending_count = self.search_count([("state", "=", "sending")])
        failed_count = self.search_count([("state", "=", "failed")])

        last_sent = self.search([
            ("state", "in", ("sent", "delivered")),
        ], limit=1, order="sent_at desc")

        return {
            "status": "healthy" if failed_count < 20 else "degraded",
            "queued_messages": queued_count,
            "sending_messages": sending_count,
            "failed_messages": failed_count,
            "last_sent": last_sent.sent_at.isoformat() if last_sent.sent_at else None,
            "provider_count": self.env["ipai.sms.provider"].search_count([("active", "=", True)]),
        }
