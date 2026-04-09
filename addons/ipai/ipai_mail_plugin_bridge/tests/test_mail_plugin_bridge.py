# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import hashlib
import secrets

from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMailPluginSession(TransactionCase):
    """Test ipai.mail.plugin.session model integrity."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref("base.user_admin")

    def _create_session(self, expires_delta=None, active=True):
        """Helper: create a session with a raw token, return (record, raw_token)."""
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires = fields.Datetime.now() + (
            expires_delta or timedelta(hours=24)
        )
        session = self.env["ipai.mail.plugin.session"].create({
            "user_id": self.user.id,
            "token": token_hash,
            "expires_at": expires,
            "active": active,
        })
        return session, raw_token

    def test_session_creation(self):
        """Session record must be creatable with required fields."""
        session, _ = self._create_session()
        self.assertTrue(session.id)
        self.assertEqual(session.user_id, self.user)
        self.assertTrue(session.active)

    def test_token_stored_as_hash(self):
        """Raw token must never be stored — only SHA-256 hash."""
        session, raw_token = self._create_session()
        expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        self.assertEqual(session.token, expected_hash)
        self.assertNotEqual(
            session.token,
            raw_token,
            "Raw token must not be stored in the database",
        )

    def test_validate_token_success(self):
        """validate_token must return user for valid, non-expired token."""
        session, raw_token = self._create_session()
        result = self.env["ipai.mail.plugin.session"].validate_token(raw_token)
        self.assertEqual(result, self.user)

    def test_validate_token_expired(self):
        """validate_token must reject expired sessions."""
        session, raw_token = self._create_session(
            expires_delta=timedelta(hours=-1),
        )
        result = self.env["ipai.mail.plugin.session"].validate_token(raw_token)
        self.assertFalse(result, "Expired session should not validate")

    def test_validate_token_inactive(self):
        """validate_token must reject inactive (soft-deleted) sessions."""
        session, raw_token = self._create_session(active=False)
        result = self.env["ipai.mail.plugin.session"].validate_token(raw_token)
        self.assertFalse(result, "Inactive session should not validate")

    def test_validate_token_wrong_token(self):
        """validate_token must reject wrong tokens."""
        self._create_session()
        result = self.env["ipai.mail.plugin.session"].validate_token(
            "completely-wrong-token"
        )
        self.assertFalse(result, "Wrong token should not validate")

    def test_gc_expired_sessions(self):
        """_gc_expired_sessions must deactivate expired sessions."""
        expired_session, _ = self._create_session(
            expires_delta=timedelta(hours=-2),
        )
        valid_session, _ = self._create_session(
            expires_delta=timedelta(hours=12),
        )
        self.env["ipai.mail.plugin.session"]._gc_expired_sessions()
        expired_session.invalidate_recordset()
        valid_session.invalidate_recordset()
        # Read with active_test=False to find deactivated record
        expired_fresh = self.env["ipai.mail.plugin.session"].with_context(
            active_test=False
        ).browse(expired_session.id)
        self.assertFalse(
            expired_fresh.active,
            "Expired session should be deactivated by GC",
        )
        self.assertTrue(
            valid_session.active,
            "Valid session should remain active after GC",
        )

    def test_token_uniqueness(self):
        """Duplicate token hashes must be rejected by SQL constraint."""
        session1, raw1 = self._create_session()
        with self.assertRaises(Exception):
            self.env["ipai.mail.plugin.session"].create({
                "user_id": self.user.id,
                "token": session1.token,  # duplicate hash
                "expires_at": fields.Datetime.now() + timedelta(hours=24),
            })


@tagged("post_install", "-at_install")
class TestMailPluginBridgeAccess(TransactionCase):
    """Test security access rules for mail plugin bridge."""

    def test_model_access_exists(self):
        """ACL for ipai.mail.plugin.session must exist."""
        access = self.env["ir.model.access"].search([
            ("model_id.model", "=", "ipai.mail.plugin.session"),
        ])
        self.assertTrue(
            access,
            "No access rules found for ipai.mail.plugin.session",
        )

    def test_session_model_registered(self):
        """ipai.mail.plugin.session must be a registered model."""
        model = self.env["ir.model"].search([
            ("model", "=", "ipai.mail.plugin.session"),
        ])
        self.assertTrue(model, "Model ipai.mail.plugin.session not registered")
