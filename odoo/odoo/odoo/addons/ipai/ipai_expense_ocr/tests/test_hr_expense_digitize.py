"""
Odoo TransactionCase tests for ipai_expense_ocr.models.hr_expense_mixin.

Runs via Odoo's test runner (not plain pytest):
    python odoo-bin --test-enable --test-tags ipai_expense_ocr -d odoo_dev

Test coverage targets
---------------------
T1  no attachment attached         → UserError (no image found)
T2  endpoint not configured        → UserError (missing config param)
T3  OCR service error              → UserError + error audit run (status='error')
T4  success — blank fields filled  → unit_amount written, ok audit run created
T5  idempotent — all fields filled → "No Changes" notification, no audit run
T6  low-confidence                 → warning notification (sticky=True)
"""

import base64
from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

# ---------------------------------------------------------------------------
# Minimal 1×1 JPEG (valid image bytes so mimetype filter matches)
# ---------------------------------------------------------------------------
_MINIMAL_JPEG_B64 = base64.b64encode(
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n"
    b"\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d"
    b"\x1a\x1c\x1c $.' \",#\x1c\x1c(7),\x1c\x1c=82<.342\x1e\x1f22\x1f+?"
    b"?\x1c\x1c22222222222222222222222222222222222222222222222222\xff\xc0\x00"
    b"\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01"
    b"\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02"
    b"\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00"
    b"\xfb\xd2\x8a(\xff\xd9"
).decode()

_OCR_ENDPOINT = "http://fake-ocr.test"
_PATCH_FETCH = "odoo.addons.ipai_expense_ocr.utils.ocr_client.fetch_image_text"

# Receipt text that produces: merchant=ACME STORE, date=2026-01-25, total=123.45
_GOOD_RECEIPT = "ACME STORE\n2026-01-25\nTotal PHP 123.45\n"

# Receipt text that produces low confidence (currency fallback, no keyword):
# confidence = 0.2 (merchant) + 0.3 (CURRENCY_RE) = 0.5 > 0.4 — not low enough.
# Use bare merchant only to get 0.2 < 0.4, but then no total → vals empty.
# Patch parse_text directly for the low-confidence test case.
_PATCH_PARSE = "odoo.addons.ipai_expense_ocr.utils.ocr_client.parse_text"


@tagged("ipai_expense_ocr", "-at_install", "post_install")
class TestDigitizeReceipt(TransactionCase):
    """Regression tests for action_digitize_receipt() business logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        # Minimal employee — required by hr.expense
        self.employee = self.env["hr.employee"].create({"name": "OCR Test Employee"})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_expense(self, **kwargs):
        """Create a minimal hr.expense for testing."""
        defaults = {
            "name": "Test Receipt",
            "employee_id": self.employee.id,
        }
        defaults.update(kwargs)
        return self.env["hr.expense"].create(defaults)

    def _attach_image(self, expense):
        """Attach a minimal JPEG to the given expense."""
        return self.env["ir.attachment"].create(
            {
                "name": "receipt.jpg",
                "datas": _MINIMAL_JPEG_B64,
                "res_model": "hr.expense",
                "res_id": expense.id,
                "mimetype": "image/jpeg",
            }
        )

    def _set_endpoint(self):
        """Write OCR endpoint config param."""
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.ocr.endpoint_url", _OCR_ENDPOINT
        )

    # ------------------------------------------------------------------
    # T1 — no image attachment
    # ------------------------------------------------------------------

    def test_t1_no_attachment_raises_user_error(self):
        """No image attachment → UserError with actionable message."""
        expense = self._make_expense()
        with self.assertRaises(UserError) as ctx:
            expense.action_digitize_receipt()
        self.assertIn("No image attachment", str(ctx.exception))

    # ------------------------------------------------------------------
    # T2 — endpoint not configured
    # ------------------------------------------------------------------

    def test_t2_no_endpoint_raises_user_error(self):
        """Endpoint not configured → UserError pointing to config script."""
        expense = self._make_expense()
        self._attach_image(expense)
        # Ensure param is absent
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.ocr.endpoint_url", ""
        )
        with self.assertRaises(UserError) as ctx:
            expense.action_digitize_receipt()
        self.assertIn("OCR endpoint not configured", str(ctx.exception))

    # ------------------------------------------------------------------
    # T3 — OCR service error → error audit run
    # ------------------------------------------------------------------

    def test_t3_service_error_creates_error_run(self):
        """OCR service error → UserError raised + error audit run persisted."""
        import requests  # noqa: PLC0415

        expense = self._make_expense()
        self._attach_image(expense)
        self._set_endpoint()

        with patch(_PATCH_FETCH, side_effect=requests.ConnectionError("refused")):
            with self.assertRaises(UserError) as ctx:
                expense.action_digitize_receipt()

        self.assertIn("OCR service error", str(ctx.exception))

        runs = expense.ocr_run_ids
        self.assertEqual(len(runs), 1, "One audit run should be created on error")
        self.assertEqual(runs[0].status, "error")
        self.assertIn("refused", runs[0].error)

    # ------------------------------------------------------------------
    # T4 — success: blank fields written, ok audit run created
    # ------------------------------------------------------------------

    def test_t4_success_writes_blank_unit_amount(self):
        """Success: unit_amount (blank) is written from OCR; ok audit run created."""
        expense = self._make_expense(unit_amount=0.0, date=False)
        self._attach_image(expense)
        self._set_endpoint()

        with patch(_PATCH_FETCH, return_value=_GOOD_RECEIPT):
            expense.action_digitize_receipt()

        self.assertAlmostEqual(expense.unit_amount, 123.45)
        # name was pre-set to 'Test Receipt' — must NOT be overwritten
        self.assertEqual(expense.name, "Test Receipt")

        runs = expense.ocr_run_ids
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0].status, "ok")
        self.assertAlmostEqual(runs[0].total, 123.45)
        self.assertEqual(runs[0].merchant, "ACME STORE")

    # ------------------------------------------------------------------
    # T5 — idempotency: all fields pre-filled → no overwrite, no audit run
    # ------------------------------------------------------------------

    def test_t5_idempotent_no_overwrite_returns_no_changes(self):
        """All target fields already filled → 'No Changes' notification, no audit run."""
        expense = self._make_expense(
            unit_amount=999.0,
            date="2026-01-01",
        )
        self._attach_image(expense)
        self._set_endpoint()

        with patch(_PATCH_FETCH, return_value=_GOOD_RECEIPT):
            result = expense.action_digitize_receipt()

        # name, unit_amount, date all pre-filled → OCR data is newer but MUST NOT overwrite
        self.assertEqual(expense.unit_amount, 999.0)
        self.assertEqual(str(expense.date), "2026-01-01")
        # The method returns the "No Changes" notification early (no audit run)
        self.assertEqual(result["params"]["title"], "No Changes")
        self.assertEqual(len(expense.ocr_run_ids), 0, "No audit run on no-op digitize")

    # ------------------------------------------------------------------
    # T6 — low confidence → warning notification (sticky)
    # ------------------------------------------------------------------

    def test_t6_low_confidence_warning_notification(self):
        """OCR confidence < 0.4 → warning-type notification with sticky=True."""
        from odoo.addons.ipai_expense_ocr.utils.ocr_client import OCRResult  # noqa: PLC0415

        low_conf_result = OCRResult(
            merchant=None,
            receipt_date=None,
            total=55.0,
            confidence=0.3,  # below LOW_CONFIDENCE_THRESHOLD (0.4)
            raw={"text": "PHP 55.00"},
        )

        expense = self._make_expense(unit_amount=0.0, date=False)
        self._attach_image(expense)
        self._set_endpoint()

        with patch(_PATCH_FETCH, return_value="PHP 55.00"), patch(
            _PATCH_PARSE, return_value=low_conf_result
        ):
            result = expense.action_digitize_receipt()

        self.assertEqual(result["params"]["type"], "warning")
        self.assertTrue(result["params"]["sticky"])
        self.assertAlmostEqual(expense.unit_amount, 55.0)
