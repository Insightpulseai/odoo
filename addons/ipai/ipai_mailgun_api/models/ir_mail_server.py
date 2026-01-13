import logging
import requests
from email.utils import formataddr
from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def _send_email_mailgun_api(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                                  smtp_user=None, smtp_password=None, smtp_encryption=None,
                                  smtp_ssl_certificate=None, smtp_ssl_private_key=None):
        """
        Send email via Mailgun HTTP API instead of SMTP.

        This method bypasses SMTP port blocking (25/587/465) by using
        Mailgun's HTTP API which operates over HTTPS (port 443).

        :param message: email.message.Message object
        :return: Message ID from Mailgun API
        """
        # Get configuration from system parameters
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        api_key = IrConfigParam.get_param('mailgun.api_key')
        domain = IrConfigParam.get_param('mailgun.domain', 'mg.insightpulseai.net')
        use_api = IrConfigParam.get_param('mailgun.use_api', 'True') == 'True'

        # Fallback to standard SMTP if API not configured
        if not use_api or not api_key:
            _logger.info('Mailgun API not configured, falling back to SMTP')
            return super()._send_email_mailgun_api(
                message, mail_server_id, smtp_server, smtp_port, smtp_user,
                smtp_password, smtp_encryption, smtp_ssl_certificate, smtp_ssl_private_key
            )

        # Extract email components
        try:
            from_addr = message.get('From', '')
            to_addrs = message.get('To', '')
            cc_addrs = message.get('Cc', '')
            bcc_addrs = message.get('Bcc', '')
            subject = message.get('Subject', '')

            # Handle multipart messages
            if message.is_multipart():
                text_body = None
                html_body = None
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain' and not text_body:
                        text_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html' and not html_body:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                content_type = message.get_content_type()
                payload = message.get_payload(decode=True)
                if isinstance(payload, bytes):
                    payload = payload.decode('utf-8', errors='ignore')

                if content_type == 'text/html':
                    html_body = payload
                    text_body = None
                else:
                    text_body = payload
                    html_body = None

            # Prepare Mailgun API request
            url = f"https://api.mailgun.net/v3/{domain}/messages"

            data = {
                "from": from_addr,
                "to": to_addrs,
                "subject": subject,
            }

            if text_body:
                data["text"] = text_body
            if html_body:
                data["html"] = html_body
            if cc_addrs:
                data["cc"] = cc_addrs
            if bcc_addrs:
                data["bcc"] = bcc_addrs

            # Send via Mailgun API
            response = requests.post(
                url,
                auth=("api", api_key),
                data=data,
                timeout=30
            )

            # Handle response
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('id', '')
                _logger.info(f"✅ Email sent via Mailgun API: {message_id}")
                return message_id
            else:
                error_msg = f"Mailgun API error: HTTP {response.status_code} - {response.text}"
                _logger.error(error_msg)
                raise UserError(error_msg)

        except Exception as e:
            error_msg = f"Failed to send email via Mailgun API: {str(e)}"
            _logger.error(error_msg, exc_info=True)
            raise UserError(error_msg)

    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   smtp_ssl_certificate=None, smtp_ssl_private_key=None):
        """
        Override send_email to route through Mailgun API if configured.
        """
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        use_mailgun_api = IrConfigParam.get_param('mailgun.use_api', 'True') == 'True'

        if use_mailgun_api:
            return self._send_email_mailgun_api(
                message, mail_server_id, smtp_server, smtp_port, smtp_user,
                smtp_password, smtp_encryption, smtp_ssl_certificate, smtp_ssl_private_key
            )
        else:
            return super().send_email(
                message, mail_server_id, smtp_server, smtp_port, smtp_user,
                smtp_password, smtp_encryption, smtp_debug, smtp_ssl_certificate,
                smtp_ssl_private_key
            )
