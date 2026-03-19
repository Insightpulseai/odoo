# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Card builder for Google Workspace Add-on responses.

AbstractModel that generates Card Service v1 JSON for each trigger type.
Other ipai_* modules can inherit this to extend card content.
"""

import logging

from odoo import api, models

from ..utils.cards import (
    card,
    card_header,
    card_section,
    decorated_text,
    divider,
    text_button,
    text_paragraph,
)

_logger = logging.getLogger(__name__)

# Base URL for action callbacks
_ACTION_URL = "/ipai/gws/action"


class GWSCardBuilder(models.AbstractModel):
    _name = "ipai.gws.card.builder"
    _description = "Google Workspace Add-on Card Builder"

    # ------------------------------------------------------------------
    # Homepage
    # ------------------------------------------------------------------

    @api.model
    def _build_home_card(self, event_data):
        """Build the homepage card shown when the add-on icon is clicked."""
        home = card(
            header=card_header(
                "InsightPulse AI",
                subtitle="Odoo ERP Integration",
            ),
            sections=[
                card_section(widgets=[
                    text_paragraph(
                        "Access your Odoo data directly from Google Workspace."
                    ),
                    decorated_text("CRM", "Contacts & Leads", icon="PERSON"),
                    decorated_text("Projects", "Tasks & Timesheets", icon="CLOCK"),
                    decorated_text("Accounting", "Invoices & Payments", icon="DOLLAR"),
                ]),
            ],
        )
        return {"action": {"navigations": [{"pushCard": home}]}}

    # ------------------------------------------------------------------
    # Gmail
    # ------------------------------------------------------------------

    @api.model
    def _build_gmail_card(self, event_data):
        """Build contextual card for Gmail — sender lookup + recent activity."""
        # Extract sender email from Gmail event
        gmail_data = (
            event_data.get("gmail", {})
            if isinstance(event_data, dict)
            else {}
        )
        message_id = gmail_data.get("messageId", "")
        sender_email = self._extract_sender_email(event_data)

        widgets = []
        partner = None

        if sender_email:
            partner = (
                self.env["res.partner"]
                .sudo()
                .search([("email", "=ilike", sender_email)], limit=1)
            )

        if partner:
            widgets.append(
                decorated_text("Contact", partner.name, icon="PERSON")
            )
            if partner.phone:
                widgets.append(
                    decorated_text("Phone", partner.phone, icon="PHONE")
                )
            if partner.company_id:
                widgets.append(
                    decorated_text(
                        "Company", partner.company_id.name, icon="HOTEL_ROOM_TYPE"
                    )
                )
            widgets.append(divider())
            widgets.append(
                text_button(
                    "Open in Odoo",
                    _ACTION_URL,
                    parameters={"action": "open_partner", "id": str(partner.id)},
                )
            )
        else:
            widgets.append(
                text_paragraph(
                    f"No Odoo contact found for <b>{sender_email or 'unknown'}</b>"
                )
            )
            widgets.append(
                text_button(
                    "Create Contact",
                    _ACTION_URL,
                    parameters={"action": "create_partner", "email": sender_email or ""},
                )
            )

        # Quick actions
        widgets.append(divider())
        widgets.append(
            text_button(
                "Create Lead",
                _ACTION_URL,
                parameters={"action": "create_lead", "email": sender_email or ""},
            )
        )
        widgets.append(
            text_button(
                "Log Note",
                _ACTION_URL,
                parameters={
                    "action": "log_note",
                    "partner_id": str(partner.id) if partner else "",
                },
            )
        )

        gmail_card = card(
            header=card_header("Gmail", subtitle=sender_email or "Unknown sender"),
            sections=[card_section(header="Contact Info", widgets=widgets)],
        )
        return {"action": {"navigations": [{"pushCard": gmail_card}]}}

    @api.model
    def _extract_sender_email(self, event_data):
        """Extract sender email from Gmail event data."""
        try:
            # Google sends accessToken + messageMetadata in gmail trigger
            gmail = event_data.get("gmail", {})
            # The sender comes from messageMetadata headers
            headers = gmail.get("messageMetadata", {}).get("headers", [])
            for h in headers:
                if h.get("name", "").lower() == "from":
                    value = h.get("value", "")
                    # Parse "Name <email>" format
                    if "<" in value and ">" in value:
                        return value.split("<")[1].split(">")[0].strip()
                    return value.strip()
        except (AttributeError, TypeError, IndexError):
            pass
        return ""

    # ------------------------------------------------------------------
    # Calendar
    # ------------------------------------------------------------------

    @api.model
    def _build_calendar_card(self, event_data):
        """Build card for Calendar event open — attendee info + related records."""
        cal_data = (
            event_data.get("calendar", {})
            if isinstance(event_data, dict)
            else {}
        )
        event_id = cal_data.get("id", "")
        attendees = cal_data.get("attendees", [])
        summary = cal_data.get("summary", "Calendar Event")

        widgets = []

        # Look up attendees in Odoo
        attendee_emails = [
            a.get("email", "") for a in attendees if a.get("email")
        ]
        if attendee_emails:
            partners = (
                self.env["res.partner"]
                .sudo()
                .search([("email", "in", attendee_emails)])
            )
            for p in partners[:5]:
                widgets.append(
                    decorated_text(p.name, p.email or "", icon="PERSON")
                )
        else:
            widgets.append(text_paragraph("No attendees found in event data."))

        widgets.append(divider())
        widgets.append(
            text_button(
                "Create Meeting Minutes",
                _ACTION_URL,
                parameters={"action": "create_note", "subject": summary},
            )
        )

        cal_card = card(
            header=card_header("Calendar", subtitle=summary),
            sections=[card_section(header="Attendees", widgets=widgets)],
        )
        return {"action": {"navigations": [{"pushCard": cal_card}]}}

    # ------------------------------------------------------------------
    # Drive
    # ------------------------------------------------------------------

    @api.model
    def _build_drive_card(self, event_data):
        """Build card for Drive items selected — file actions."""
        drive_data = (
            event_data.get("drive", {})
            if isinstance(event_data, dict)
            else {}
        )
        selected_items = drive_data.get("selectedItems", [])

        widgets = []

        if selected_items:
            for item in selected_items[:5]:
                title = item.get("title", "Untitled")
                mime = item.get("mimeType", "")
                widgets.append(
                    decorated_text(title, mime, icon="DESCRIPTION")
                )
        else:
            widgets.append(text_paragraph("No files selected."))

        widgets.append(divider())
        widgets.append(
            text_button(
                "Attach to Odoo Record",
                _ACTION_URL,
                parameters={"action": "attach_files"},
            )
        )

        drive_card = card(
            header=card_header(
                "Drive",
                subtitle=f"{len(selected_items)} file(s) selected",
            ),
            sections=[card_section(header="Selected Files", widgets=widgets)],
        )
        return {"action": {"navigations": [{"pushCard": drive_card}]}}

    # ------------------------------------------------------------------
    # Sheets
    # ------------------------------------------------------------------

    @api.model
    def _build_sheets_card(self, event_data):
        """Build card for Sheets file scope — import/export actions."""
        widgets = [
            text_paragraph("Sync data between this spreadsheet and Odoo."),
            divider(),
            text_button(
                "Import Contacts to Odoo",
                _ACTION_URL,
                parameters={"action": "import_contacts"},
            ),
            text_button(
                "Export Odoo Data to Sheet",
                _ACTION_URL,
                parameters={"action": "export_data"},
            ),
        ]

        sheets_card = card(
            header=card_header("Sheets", subtitle="Data Sync"),
            sections=[card_section(header="Actions", widgets=widgets)],
        )
        return {"action": {"navigations": [{"pushCard": sheets_card}]}}

    # ------------------------------------------------------------------
    # Action Handler
    # ------------------------------------------------------------------

    @api.model
    def _handle_action(self, event_data):
        """Handle button clicks and form submissions from cards.

        The action name and parameters come from the card button definition.
        This is a dispatcher that routes to specific action methods.
        """
        common_event = event_data.get("commonEventObject", {})
        parameters = common_event.get("parameters", {})
        action_name = parameters.get("action", "")

        _logger.info("GWS action: %s, params: %s", action_name, parameters)

        handler = {
            "open_partner": self._action_open_partner,
            "create_partner": self._action_create_partner,
            "create_lead": self._action_create_lead,
            "log_note": self._action_log_note,
            "create_note": self._action_create_note,
            "attach_files": self._action_attach_files,
            "import_contacts": self._action_import_contacts,
            "export_data": self._action_export_data,
        }.get(action_name)

        if handler:
            return handler(parameters)

        return self._notification_card(f"Unknown action: {action_name}")

    # ------------------------------------------------------------------
    # Action implementations (stubs — extend in submodules)
    # ------------------------------------------------------------------

    @api.model
    def _action_open_partner(self, params):
        """Open partner in Odoo — returns a link card."""
        partner_id = params.get("id", "")
        base_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url", "")
        )
        url = f"{base_url}/web#id={partner_id}&model=res.partner&view_type=form"
        return self._notification_card(f"Open in Odoo: {url}")

    @api.model
    def _action_create_partner(self, params):
        """Create a new partner from email."""
        email = params.get("email", "")
        if email:
            partner = self.env["res.partner"].sudo().create({"email": email, "name": email.split("@")[0]})
            return self._notification_card(f"Contact created: {partner.name}")
        return self._notification_card("No email provided.")

    @api.model
    def _action_create_lead(self, params):
        """Create a CRM lead (if crm module is installed)."""
        email = params.get("email", "")
        if "crm.lead" in self.env:
            lead = self.env["crm.lead"].sudo().create({
                "name": f"Lead from {email}",
                "email_from": email,
            })
            return self._notification_card(f"Lead created: {lead.name}")
        return self._notification_card("CRM module not installed.")

    @api.model
    def _action_log_note(self, params):
        """Log a note on a partner."""
        return self._notification_card("Note logging — extend in submodule.")

    @api.model
    def _action_create_note(self, params):
        """Create meeting minutes."""
        return self._notification_card("Meeting minutes — extend in submodule.")

    @api.model
    def _action_attach_files(self, params):
        """Attach Drive files to an Odoo record."""
        return self._notification_card("File attachment — extend in submodule.")

    @api.model
    def _action_import_contacts(self, params):
        """Import contacts from Sheets."""
        return self._notification_card("Contact import — extend in submodule.")

    @api.model
    def _action_export_data(self, params):
        """Export Odoo data to Sheets."""
        return self._notification_card("Data export — extend in submodule.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @api.model
    def _notification_card(self, message):
        """Return a simple notification card."""
        notify_card = card(
            header=card_header("InsightPulse AI"),
            sections=[card_section(widgets=[text_paragraph(message)])],
        )
        return {"action": {"navigations": [{"pushCard": notify_card}]}}
