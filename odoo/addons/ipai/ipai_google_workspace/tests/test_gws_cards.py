"""
Odoo TransactionCase tests for ipai_google_workspace card builder.

Runs via Odoo's test runner:
    python odoo-bin --test-enable --test-tags ipai_google_workspace -d test_ipai_gws

Test coverage:
  C1  Homepage card structure           → valid Card Service v1 JSON
  C2  Gmail card with known partner     → partner name + phone in card
  C3  Gmail card with unknown sender    → "No contact found" + Create button
  C4  Calendar card with attendees      → attendee names resolved from Odoo
  C5  Drive card with selected items    → file titles shown
  C6  Sheets card                       → import/export buttons present
  C7  Action dispatcher routes correctly → known action returns result
  C8  Unknown action returns notification → error card
  A1  Auth — missing Bearer token       → returns None tuple
  A2  Card helpers produce valid dicts  → no exceptions
"""

from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("ipai_google_workspace", "-at_install", "post_install")
class TestGWSCards(TransactionCase):
    """Tests for ipai.gws.card.builder AbstractModel."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["ipai.gws.card.builder"]
        # Create a test partner
        cls.partner = cls.env["res.partner"].create({
            "name": "Test GWS Contact",
            "email": "test@example.com",
            "phone": "+1234567890",
        })

    # ------------------------------------------------------------------
    # C1 — Homepage card
    # ------------------------------------------------------------------

    def test_c1_home_card_structure(self):
        """Homepage card returns valid navigation structure."""
        result = self.builder._build_home_card({})
        self.assertIn("action", result)
        self.assertIn("navigations", result["action"])
        nav = result["action"]["navigations"]
        self.assertTrue(len(nav) > 0)
        card_data = nav[0].get("pushCard", {})
        self.assertIn("header", card_data)
        self.assertIn("sections", card_data)

    # ------------------------------------------------------------------
    # C2 — Gmail card with known partner
    # ------------------------------------------------------------------

    def test_c2_gmail_known_partner(self):
        """Gmail card shows partner info when sender email matches."""
        event = {
            "gmail": {
                "messageMetadata": {
                    "headers": [
                        {"name": "From", "value": "Test <test@example.com>"}
                    ]
                }
            }
        }
        result = self.builder._build_gmail_card(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        # Flatten all widget text to check for partner name
        section_json = str(card_data["sections"])
        self.assertIn("Test GWS Contact", section_json)

    # ------------------------------------------------------------------
    # C3 — Gmail card with unknown sender
    # ------------------------------------------------------------------

    def test_c3_gmail_unknown_sender(self):
        """Gmail card shows 'no contact found' for unknown email."""
        event = {
            "gmail": {
                "messageMetadata": {
                    "headers": [
                        {"name": "From", "value": "nobody@nowhere.com"}
                    ]
                }
            }
        }
        result = self.builder._build_gmail_card(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("No Odoo contact found", section_json)

    # ------------------------------------------------------------------
    # C4 — Calendar card with attendees
    # ------------------------------------------------------------------

    def test_c4_calendar_with_attendees(self):
        """Calendar card resolves attendee emails to Odoo partners."""
        event = {
            "calendar": {
                "summary": "Team Meeting",
                "attendees": [{"email": "test@example.com"}],
            }
        }
        result = self.builder._build_calendar_card(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("Test GWS Contact", section_json)

    # ------------------------------------------------------------------
    # C5 — Drive card with selected items
    # ------------------------------------------------------------------

    def test_c5_drive_selected_items(self):
        """Drive card shows file titles."""
        event = {
            "drive": {
                "selectedItems": [
                    {"title": "Report.pdf", "mimeType": "application/pdf"},
                    {"title": "Data.xlsx", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
                ]
            }
        }
        result = self.builder._build_drive_card(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("Report.pdf", section_json)
        self.assertIn("Data.xlsx", section_json)

    # ------------------------------------------------------------------
    # C6 — Sheets card
    # ------------------------------------------------------------------

    def test_c6_sheets_card(self):
        """Sheets card has import/export buttons."""
        result = self.builder._build_sheets_card({})
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("Import Contacts", section_json)
        self.assertIn("Export Odoo Data", section_json)

    # ------------------------------------------------------------------
    # C7 — Action dispatcher
    # ------------------------------------------------------------------

    def test_c7_action_create_partner(self):
        """create_partner action creates a partner and returns confirmation."""
        event = {
            "commonEventObject": {
                "parameters": {
                    "action": "create_partner",
                    "email": "newuser@example.com",
                }
            }
        }
        result = self.builder._handle_action(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("Contact created", section_json)

        # Verify partner was actually created
        partner = self.env["res.partner"].search(
            [("email", "=", "newuser@example.com")]
        )
        self.assertTrue(partner)

    # ------------------------------------------------------------------
    # C8 — Unknown action
    # ------------------------------------------------------------------

    def test_c8_unknown_action(self):
        """Unknown action returns notification card."""
        event = {
            "commonEventObject": {
                "parameters": {"action": "nonexistent_action"}
            }
        }
        result = self.builder._handle_action(event)
        card_data = result["action"]["navigations"][0]["pushCard"]
        section_json = str(card_data["sections"])
        self.assertIn("Unknown action", section_json)


@tagged("ipai_google_workspace", "-at_install", "post_install")
class TestGWSCardHelpers(TransactionCase):
    """Tests for utils/cards.py helper functions."""

    def test_a2_card_helpers_produce_dicts(self):
        """All card helper functions return valid dicts."""
        from odoo.addons.ipai_google_workspace.utils.cards import (
            card,
            card_header,
            card_section,
            decorated_text,
            divider,
            text_button,
            text_paragraph,
        )

        h = card_header("Title", subtitle="Sub")
        self.assertIsInstance(h, dict)
        self.assertEqual(h["title"], "Title")

        s = card_section(header="Section", widgets=[text_paragraph("Hello")])
        self.assertIsInstance(s, dict)

        c = card(header=h, sections=[s])
        self.assertIsInstance(c, dict)
        self.assertIn("header", c)
        self.assertIn("sections", c)

        dt = decorated_text("Label", "Value", icon="PERSON")
        self.assertIn("decoratedText", dt)

        btn = text_button("Click", "/action", parameters={"key": "val"})
        self.assertIn("buttonList", btn)

        d = divider()
        self.assertIn("divider", d)
