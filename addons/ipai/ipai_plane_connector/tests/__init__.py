# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
# Tests for ipai_plane_connector
#
# Layer 1 (pure-Python) + Layer 2 (Odoo TransactionCase) tests.
#
# Run via Odoo test runner:
#   python odoo-bin --test-enable --test-tags ipai_plane_connector -d odoo_dev
#
# Test cases:
#   test_plane_client.py    — PlaneClient unit tests (auth, URL, rate limits,
#                             pagination, error mapping)
#   test_plane_webhook.py   — Webhook HMAC verification + dedup behaviour

from . import test_plane_client
from . import test_plane_webhook
