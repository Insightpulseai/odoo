# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase


class TestMailGateway(TransactionCase):
    """Test cases for Mail Gateway module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Gateway = cls.env["ipai.mail.gateway"]
        cls.MailLog = cls.env["ipai.mail.log"]

    def test_gateway_creation(self):
        """Test creating a mail gateway."""
        gateway = self.Gateway.create(
            {
                "name": "Test SMTP",
                "gateway_type": "smtp",
                "smtp_host": "smtp.test.com",
                "smtp_port": 587,
            }
        )
        self.assertEqual(gateway.name, "Test SMTP")
        self.assertEqual(gateway.gateway_type, "smtp")

    def test_get_default_gateway(self):
        """Test getting default gateway."""
        gateway = self.Gateway.create(
            {
                "name": "Default Gateway",
                "gateway_type": "smtp",
                "is_active": True,
                "is_default": True,
            }
        )
        default = self.Gateway.get_default_gateway()
        self.assertEqual(default, gateway)

    def test_mail_log_creation(self):
        """Test creating a mail log entry."""
        log = self.MailLog.create(
            {
                "recipient": "test@example.com",
                "subject": "Test Subject",
                "status": "sent",
            }
        )
        self.assertEqual(log.recipient, "test@example.com")
        self.assertEqual(log.status, "sent")
