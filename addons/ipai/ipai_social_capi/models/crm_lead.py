"""CRM Lead extension — relay lifecycle events to Meta CAPI bridge."""

import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    capi_event_ids = fields.One2many(
        "ipai.capi.event.log",
        "res_id",
        string="CAPI Events",
        domain=[("res_model", "=", "crm.lead")],
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Fire lead_created CAPI event on new lead/opportunity creation."""
        records = super().create(vals_list)
        for lead in records:
            self._fire_capi_lead_created(lead)
        return records

    def write(self, vals):
        """Detect stage changes that indicate qualification or win."""
        # Capture pre-write stage for comparison
        old_stages = {lead.id: lead.stage_id for lead in self}
        result = super().write(vals)

        if "stage_id" in vals:
            for lead in self:
                old_stage = old_stages.get(lead.id)
                self._check_stage_transition(lead, old_stage)

        return result

    def _fire_capi_lead_created(self, lead):
        """Send lead_created event to CAPI bridge."""
        user_data = self._extract_user_data(lead)
        if not user_data:
            return

        custom_data = {}
        if lead.expected_revenue:
            custom_data["value"] = lead.expected_revenue
            custom_data["currency"] = (
                lead.company_currency.name
                if lead.company_currency
                else "PHP"
            )
        if lead.name:
            custom_data["content_name"] = lead.name

        self.env["ipai.capi.event.log"].send_event(
            event_type="lead_created",
            record=lead,
            user_data=user_data,
            custom_data=custom_data or None,
        )

    def _check_stage_transition(self, lead, old_stage):
        """Detect qualification or win from stage changes."""
        if not lead.stage_id or not old_stage:
            return

        new_stage = lead.stage_id

        # Won stage → opportunity_won event
        if new_stage.is_won and not old_stage.is_won:
            self._fire_capi_opportunity_won(lead)
            return

        # Qualified stage detection: second stage or beyond, not won
        # Heuristic: any forward movement past first stage = qualified
        if (
            new_stage.sequence > old_stage.sequence
            and not new_stage.is_won
            and old_stage.sequence == 1
        ):
            self._fire_capi_lead_qualified(lead)

    def _fire_capi_lead_qualified(self, lead):
        """Send lead_qualified event to CAPI bridge."""
        user_data = self._extract_user_data(lead)
        if not user_data:
            return

        custom_data = {"content_name": lead.name or ""}
        if lead.expected_revenue:
            custom_data["value"] = lead.expected_revenue
            custom_data["currency"] = (
                lead.company_currency.name
                if lead.company_currency
                else "PHP"
            )

        self.env["ipai.capi.event.log"].send_event(
            event_type="lead_qualified",
            record=lead,
            user_data=user_data,
            custom_data=custom_data,
        )

    def _fire_capi_opportunity_won(self, lead):
        """Send opportunity_won event to CAPI bridge."""
        user_data = self._extract_user_data(lead)
        if not user_data:
            return

        custom_data = {}
        if lead.expected_revenue:
            custom_data["value"] = lead.expected_revenue
        elif lead.prorated_revenue:
            custom_data["value"] = lead.prorated_revenue
        custom_data["currency"] = (
            lead.company_currency.name
            if lead.company_currency
            else "PHP"
        )
        if lead.name:
            custom_data["content_name"] = lead.name

        self.env["ipai.capi.event.log"].send_event(
            event_type="opportunity_won",
            record=lead,
            user_data=user_data,
            custom_data=custom_data,
        )

    @api.model
    def _extract_user_data(self, lead):
        """Extract PII from lead's partner for CAPI user_data.

        Returns empty dict if no usable identity data exists.
        Bridge handles SHA-256 hashing — we send plaintext here.
        """
        data = {}
        partner = lead.partner_id

        # Email — prefer partner, fall back to lead
        email = (partner.email if partner else None) or lead.email_from
        if email:
            data["email"] = email

        # Phone — prefer partner, fall back to lead
        phone = (partner.phone if partner else None) or lead.phone
        if phone:
            data["phone"] = phone

        # Name
        if partner:
            # partner_firstname OCA module adds firstname/lastname fields;
            # fall back to splitting name if not installed.
            if hasattr(partner, "firstname") and partner.firstname:
                data["first_name"] = partner.firstname
            if hasattr(partner, "lastname") and partner.lastname:
                data["last_name"] = partner.lastname
            elif partner.name:
                parts = partner.name.split(" ", 1)
                data["first_name"] = parts[0]
                if len(parts) > 1:
                    data["last_name"] = parts[1]
        elif lead.contact_name:
            parts = lead.contact_name.split(" ", 1)
            data["first_name"] = parts[0]
            if len(parts) > 1:
                data["last_name"] = parts[1]

        # Location
        country = partner.country_id if partner else lead.country_id
        if country:
            data["country_code"] = country.code

        city = (partner.city if partner else None) or lead.city
        if city:
            data["city"] = city

        # Must have at least email or phone for Meta to match
        if not data.get("email") and not data.get("phone"):
            return {}

        return data
