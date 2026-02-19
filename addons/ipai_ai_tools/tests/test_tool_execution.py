# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestToolExecution(TransactionCase):
    """Test cases for tool execution."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tool = cls.env["ipai.ai.tool"]

        # Create a test partner
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Customer",
            "email": "test@example.com",
        })

        # Create a test product
        cls.product = cls.env["product.product"].create({
            "name": "Test Product",
            "type": "consu",
            "list_price": 100.0,
        })

    def test_crm_create_lead_dry_run(self):
        """Test CRM lead creation in dry-run mode."""
        from odoo.addons.ipai_ai_tools.tools.crm_tools import create_lead

        result = create_lead(
            self.env,
            {
                "name": "Test Lead",
                "contact_name": "John Doe",
                "email": "john@example.com",
            },
            dry_run=True,
        )

        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result["would_create"]["name"], "Test Lead")

    def test_crm_create_lead(self):
        """Test CRM lead creation."""
        from odoo.addons.ipai_ai_tools.tools.crm_tools import create_lead

        result = create_lead(
            self.env,
            {
                "name": "Real Lead",
                "contact_name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1234567890",
            },
            dry_run=False,
        )

        self.assertTrue(result.get("lead_id"))
        lead = self.env["crm.lead"].browse(result["lead_id"])
        self.assertEqual(lead.name, "Real Lead")
        self.assertEqual(lead.contact_name, "Jane Doe")
        self.assertEqual(lead.email_from, "jane@example.com")

    def test_crm_create_lead_missing_name(self):
        """Test CRM lead creation fails without name."""
        from odoo.addons.ipai_ai_tools.tools.crm_tools import create_lead

        with self.assertRaises(ValidationError):
            create_lead(self.env, {}, dry_run=False)

    def test_calendar_create_event_dry_run(self):
        """Test calendar event creation in dry-run mode."""
        from odoo.addons.ipai_ai_tools.tools.calendar_tools import create_event

        result = create_event(
            self.env,
            {
                "name": "Test Meeting",
                "start": "2026-02-01T10:00:00",
                "stop": "2026-02-01T11:00:00",
            },
            dry_run=True,
        )

        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result["would_create"]["name"], "Test Meeting")

    def test_calendar_create_event(self):
        """Test calendar event creation."""
        from odoo.addons.ipai_ai_tools.tools.calendar_tools import create_event

        result = create_event(
            self.env,
            {
                "name": "Real Meeting",
                "start": "2026-02-01T14:00:00",
                "stop": "2026-02-01T15:00:00",
                "description": "A test meeting",
            },
            dry_run=False,
        )

        self.assertTrue(result.get("event_id"))
        event = self.env["calendar.event"].browse(result["event_id"])
        self.assertEqual(event.name, "Real Meeting")

    def test_calendar_create_event_invalid_time(self):
        """Test calendar event fails with invalid times."""
        from odoo.addons.ipai_ai_tools.tools.calendar_tools import create_event

        with self.assertRaises(ValidationError):
            create_event(
                self.env,
                {
                    "name": "Invalid Meeting",
                    "start": "2026-02-01T15:00:00",
                    "stop": "2026-02-01T14:00:00",  # End before start
                },
                dry_run=False,
            )

    def test_sale_create_order_dry_run(self):
        """Test sale order creation in dry-run mode."""
        from odoo.addons.ipai_ai_tools.tools.sale_tools import create_order

        result = create_order(
            self.env,
            {
                "partner_id": self.partner.id,
                "lines": [
                    {"product_id": self.product.id, "quantity": 2},
                ],
            },
            dry_run=True,
        )

        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result["would_create"]["partner"], self.partner.name)

    def test_sale_create_order(self):
        """Test sale order creation."""
        from odoo.addons.ipai_ai_tools.tools.sale_tools import create_order

        result = create_order(
            self.env,
            {
                "partner_id": self.partner.id,
                "lines": [
                    {"product_id": self.product.id, "quantity": 3},
                ],
            },
            dry_run=False,
        )

        self.assertTrue(result.get("order_id"))
        order = self.env["sale.order"].browse(result["order_id"])
        self.assertEqual(order.partner_id.id, self.partner.id)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_uom_qty, 3)

    def test_sale_create_order_missing_lines(self):
        """Test sale order fails without lines."""
        from odoo.addons.ipai_ai_tools.tools.sale_tools import create_order

        with self.assertRaises(ValidationError):
            create_order(
                self.env,
                {"partner_id": self.partner.id, "lines": []},
                dry_run=False,
            )

    def test_search_leads(self):
        """Test lead search."""
        from odoo.addons.ipai_ai_tools.tools.crm_tools import search_leads, create_lead

        # Create test lead
        create_lead(self.env, {"name": "Searchable Lead", "email": "search@test.com"})

        result = search_leads(
            self.env,
            {"query": "Searchable", "limit": 5},
        )

        self.assertTrue(result.get("count") >= 1)
        found = any(l["name"] == "Searchable Lead" for l in result["leads"])
        self.assertTrue(found)

    def test_tool_permission_gating(self):
        """Test that tool permissions are checked."""
        tool = self.Tool.search([("key", "=", "crm_create_lead")], limit=1)
        if tool and tool.group_ids:
            # Tool has permission requirements
            self.assertTrue(tool.check_permission())  # Admin should have access
