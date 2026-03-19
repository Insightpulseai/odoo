# Tests for ipai_expense_ocr
#
# Two test layers:
#
# 1) Pure-Python (pytest) — no Odoo needed:
#    - test_ocr_extract.py  : parse_text() + normalize_amount() fixtures (8 cases)
#    - test_ocr_client.py   : fetch_image_text() network error paths (9 cases)
#
# 2) Odoo TransactionCase — requires Odoo test runner:
#    - test_hr_expense_digitize.py : action_digitize_receipt() end-to-end (T1–T6)
#
# Run pytest layer (no Odoo):
#   pytest addons/ipai/ipai_expense_ocr/tests/ -v --ignore=tests/test_hr_expense_digitize.py
#
# Run Odoo layer:
#   python odoo-bin --test-enable --test-tags ipai_expense_ocr -d odoo_dev

from . import test_hr_expense_digitize
