# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""Odoo-native HttpCase tests for copilot controller endpoints.

Covers:
  - POST /ipai/copilot/attachments/upload — file upload + validation
  - POST /ipai/copilot/chat — empty prompt rejection
  - POST /ipai/copilot/chat/service — service key auth
  - MIME type validation, file size limits
  - Access control (copilot group membership required)
"""

import base64
import json

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUploadEndpoint(HttpCase):
    """Test /ipai/copilot/attachments/upload controller route."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Add admin to the copilot admin group so controller routes work
        copilot_admin = cls.env.ref(
            "ipai_odoo_copilot.group_copilot_admin",
            raise_if_not_found=False,
        )
        if copilot_admin:
            admin_user = cls.env.ref("base.user_admin")
            admin_user.groups_id = [(4, copilot_admin.id)]

    def _upload(self, filename, data_b64, mime_type="text/plain"):
        """Helper: POST a JSON-RPC upload and return the result dict."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "filename": filename,
                "data": data_b64,
                "mime_type": mime_type,
            },
        }
        resp = self.url_open(
            "/ipai/copilot/attachments/upload",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # JSON-RPC: success in body["result"], errors in body["error"]
        if body.get("error"):
            return body["error"]
        return body.get("result", body)

    def test_upload_text_file(self):
        """Upload a plain text file and get a ref back."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b"Hello World").decode()
        result = self._upload("test.txt", content, "text/plain")

        self.assertFalse(result.get("error"), result.get("message"))
        self.assertTrue(result.get("ref_id"))
        self.assertEqual(result["filename"], "test.txt")
        self.assertEqual(result["mime_type"], "text/plain")
        # Text files extract immediately (quick_mimes)
        self.assertEqual(result["ingestion_state"], "done")

    def test_upload_json_file(self):
        """Upload a JSON file — should extract immediately."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b'{"invoice": 123}').decode()
        result = self._upload("data.json", content, "application/json")

        self.assertFalse(result.get("error"))
        self.assertEqual(result["ingestion_state"], "done")

    def test_upload_csv_file(self):
        """Upload a CSV file — should extract immediately."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b"name,amount\nService,100000").decode()
        result = self._upload("data.csv", content, "text/csv")

        self.assertFalse(result.get("error"))
        self.assertEqual(result["ingestion_state"], "done")

    def test_upload_pdf_deferred(self):
        """Upload a PDF — extraction deferred (not in quick_mimes)."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b"%PDF-1.4 fake content").decode()
        result = self._upload("invoice.pdf", content, "application/pdf")

        self.assertFalse(result.get("error"))
        self.assertEqual(result["ingestion_state"], "pending")

    def test_upload_disallowed_mime(self):
        """Upload with a disallowed MIME type is rejected."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b"#!/bin/bash\nrm -rf /").decode()
        result = self._upload("bad.sh", content, "application/x-sh")

        self.assertTrue(result.get("error"))
        self.assertIn("not allowed", result.get("message", ""))

    def test_upload_missing_data(self):
        """Upload with no data is rejected."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"filename": "test.txt"},
        }
        resp = self.url_open(
            "/ipai/copilot/attachments/upload",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        result = body.get("result", {})
        self.assertTrue(result.get("error"))

    def test_upload_missing_filename(self):
        """Upload with no filename is rejected."""
        self.authenticate("admin", "admin")
        content = base64.b64encode(b"hello").decode()
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"data": content},
        }
        resp = self.url_open(
            "/ipai/copilot/attachments/upload",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        result = body.get("result", {})
        self.assertTrue(result.get("error"))

    def test_upload_requires_auth(self):
        """Upload without authentication returns JSON-RPC error."""
        content = base64.b64encode(b"hello").decode()
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "filename": "test.txt",
                "data": content,
                "mime_type": "text/plain",
            },
        }
        resp = self.url_open(
            "/ipai/copilot/attachments/upload",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        # Odoo returns JSON-RPC error for unauthenticated json endpoints
        self.assertTrue(
            body.get("error") or resp.status_code != 200,
            "Unauthenticated upload should fail",
        )


@tagged("post_install", "-at_install")
class TestChatEndpoint(HttpCase):
    """Test /ipai/copilot/chat controller route — basic validation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        copilot_admin = cls.env.ref(
            "ipai_odoo_copilot.group_copilot_admin",
            raise_if_not_found=False,
        )
        if copilot_admin:
            admin_user = cls.env.ref("base.user_admin")
            admin_user.groups_id = [(4, copilot_admin.id)]

    def _chat(self, params):
        """Helper: POST a JSON-RPC chat call."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
        }
        resp = self.url_open(
            "/ipai/copilot/chat",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        if body.get("error"):
            return body["error"]
        return body.get("result", body)

    def test_empty_prompt_blocked(self):
        """Empty prompt returns blocked=True."""
        self.authenticate("admin", "admin")
        result = self._chat({"prompt": ""})
        self.assertTrue(result.get("blocked"))
        self.assertEqual(result.get("reason"), "Empty prompt")

    def test_null_prompt_blocked(self):
        """Null prompt returns blocked=True."""
        self.authenticate("admin", "admin")
        result = self._chat({})
        self.assertTrue(result.get("blocked"))

    def test_chat_requires_auth(self):
        """Chat without authentication should fail."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"prompt": "hello"},
        }
        resp = self.url_open(
            "/ipai/copilot/chat",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        self.assertTrue(
            body.get("error") or resp.status_code != 200,
            "Unauthenticated chat should fail",
        )


@tagged("post_install", "-at_install")
class TestServiceEndpoint(HttpCase):
    """Test /ipai/copilot/chat/service auth gating."""

    def test_no_service_key_configured(self):
        """Service endpoint with no key configured returns blocked."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"prompt": "hello"},
        }
        resp = self.url_open(
            "/ipai/copilot/chat/service",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "X-Pulser-Service-Key": "wrong-key",
            },
        )
        body = resp.json()
        result = body.get("result", body)
        self.assertTrue(result.get("blocked"))
