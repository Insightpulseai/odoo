# -*- coding: utf-8 -*-
import json
import logging

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class IpaiSmsController(http.Controller):
    """Controller for SMS webhook callbacks and health checks."""

    @http.route(
        "/ipai/sms/health", type="http", auth="none", methods=["GET"], csrf=False
    )
    def sms_health(self):
        """Health check endpoint for SMS gateway."""
        try:
            status = request.env["ipai.sms.message"].sudo().get_health_status()
            return request.make_response(
                json.dumps(status),
                headers=[("Content-Type", "application/json")],
            )
        except Exception as e:
            _logger.exception("SMS health check failed: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                status=500,
                headers=[("Content-Type", "application/json")],
            )

    @http.route(
        "/ipai/sms/webhook/twilio",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def twilio_webhook(self):
        """
        Twilio delivery receipt webhook.
        https://www.twilio.com/docs/sms/outbound-message-logging
        """
        try:
            message_sid = request.params.get("MessageSid")
            message_status = request.params.get("MessageStatus")
            error_code = request.params.get("ErrorCode")
            error_message = request.params.get("ErrorMessage")

            _logger.info("Twilio webhook: %s -> %s", message_sid, message_status)

            status_map = {
                "delivered": "delivered",
                "sent": "sent",
                "failed": "failed",
                "undelivered": "failed",
            }

            odoo_status = status_map.get(message_status)
            if odoo_status and message_sid:
                request.env["ipai.sms.message"].sudo().update_delivery_status(
                    external_id=message_sid,
                    status=odoo_status,
                    error_code=error_code,
                    error_message=error_message,
                )

            return request.make_response("OK", status=200)

        except Exception as e:
            _logger.exception("Twilio webhook error: %s", str(e))
            return request.make_response("Error", status=500)

    @http.route(
        "/ipai/sms/webhook/infobip",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def infobip_webhook(self):
        """
        Infobip delivery receipt webhook.
        https://www.infobip.com/docs/api/channels/sms/sms-messaging/receive-delivery-reports
        """
        try:
            data = request.jsonrequest
            results = data.get("results", [])

            for result in results:
                message_id = result.get("messageId")
                status = result.get("status", {})
                status_name = status.get("name", "").lower()
                error_code = status.get("groupName")
                error_message = status.get("description")

                _logger.info("Infobip webhook: %s -> %s", message_id, status_name)

                status_map = {
                    "delivered": "delivered",
                    "sent": "sent",
                    "rejected": "failed",
                    "undeliverable": "failed",
                    "expired": "failed",
                }

                odoo_status = status_map.get(status_name)
                if odoo_status and message_id:
                    request.env["ipai.sms.message"].sudo().update_delivery_status(
                        external_id=message_id,
                        status=odoo_status,
                        error_code=error_code,
                        error_message=error_message,
                    )

            return {"status": "ok"}

        except Exception as e:
            _logger.exception("Infobip webhook error: %s", str(e))
            return {"status": "error", "message": str(e)}

    @http.route(
        "/ipai/sms/webhook/nexmo",
        type="http",
        auth="none",
        methods=["POST", "GET"],
        csrf=False,
    )
    def nexmo_webhook(self):
        """
        Vonage/Nexmo delivery receipt webhook.
        https://developer.vonage.com/messaging/sms/guides/delivery-receipts
        """
        try:
            message_id = request.params.get("messageId")
            status = request.params.get("status", "").lower()
            err_code = request.params.get("err-code")

            _logger.info("Nexmo webhook: %s -> %s", message_id, status)

            status_map = {
                "delivered": "delivered",
                "accepted": "sent",
                "buffered": "sent",
                "failed": "failed",
                "rejected": "failed",
                "expired": "failed",
            }

            odoo_status = status_map.get(status)
            if odoo_status and message_id:
                request.env["ipai.sms.message"].sudo().update_delivery_status(
                    external_id=message_id,
                    status=odoo_status,
                    error_code=err_code,
                )

            return request.make_response("OK", status=200)

        except Exception as e:
            _logger.exception("Nexmo webhook error: %s", str(e))
            return request.make_response("Error", status=500)
