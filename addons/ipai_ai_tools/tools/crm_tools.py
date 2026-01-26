# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

"""CRM tools for AI agents.

These functions are called by the AI Agent tool executor.
Each function receives:
- env: Odoo environment
- input_data: dict with input parameters
- dry_run: bool indicating if this is a dry run

Returns:
- dict with operation results
"""

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def create_lead(env, input_data, dry_run=False):
    """Create a new CRM lead.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - name (required): Lead name/opportunity title
            - contact_name: Contact person name
            - email: Email address
            - phone: Phone number
            - description: Notes or description
            - partner_id: Existing partner ID
            - team_id: Sales team ID
        dry_run: If True, validate but don't create

    Returns:
        dict with lead_id, name, and message
    """
    Lead = env["crm.lead"]

    # Validate required fields
    if not input_data.get("name"):
        raise ValidationError("Lead name is required.")

    # Prepare values
    values = {
        "name": input_data["name"],
        "type": "lead",  # Can be 'lead' or 'opportunity'
    }

    # Optional fields
    if input_data.get("contact_name"):
        values["contact_name"] = input_data["contact_name"]
    if input_data.get("email"):
        values["email_from"] = input_data["email"]
    if input_data.get("phone"):
        values["phone"] = input_data["phone"]
    if input_data.get("description"):
        values["description"] = input_data["description"]
    if input_data.get("partner_id"):
        values["partner_id"] = input_data["partner_id"]
    if input_data.get("team_id"):
        values["team_id"] = input_data["team_id"]

    if dry_run:
        _logger.info(f"[DRY RUN] Would create lead: {values}")
        return {
            "dry_run": True,
            "would_create": values,
            "message": f"Would create lead: {values['name']}",
        }

    # Create the lead
    lead = Lead.create(values)
    _logger.info(f"Created lead {lead.id}: {lead.name}")

    return {
        "lead_id": lead.id,
        "name": lead.name,
        "message": f"Successfully created lead: {lead.name}",
    }


def update_lead(env, input_data, dry_run=False):
    """Update an existing CRM lead.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - lead_id (required): ID of lead to update
            - name: New lead name
            - stage_id: Stage to move to
            - expected_revenue: Expected revenue
            - probability: Win probability (0-100)
            - description: Updated description
        dry_run: If True, validate but don't update

    Returns:
        dict with lead_id and message
    """
    Lead = env["crm.lead"]

    lead_id = input_data.get("lead_id")
    if not lead_id:
        raise ValidationError("lead_id is required.")

    lead = Lead.browse(lead_id)
    if not lead.exists():
        raise ValidationError(f"Lead {lead_id} not found.")

    # Prepare update values
    values = {}
    if input_data.get("name"):
        values["name"] = input_data["name"]
    if input_data.get("stage_id"):
        values["stage_id"] = input_data["stage_id"]
    if input_data.get("expected_revenue") is not None:
        values["expected_revenue"] = input_data["expected_revenue"]
    if input_data.get("probability") is not None:
        values["probability"] = input_data["probability"]
    if input_data.get("description"):
        values["description"] = input_data["description"]

    if not values:
        return {
            "lead_id": lead_id,
            "message": "No fields to update.",
        }

    if dry_run:
        _logger.info(f"[DRY RUN] Would update lead {lead_id}: {values}")
        return {
            "dry_run": True,
            "lead_id": lead_id,
            "would_update": values,
            "message": f"Would update lead {lead_id}",
        }

    lead.write(values)
    _logger.info(f"Updated lead {lead_id}")

    return {
        "lead_id": lead_id,
        "name": lead.name,
        "message": f"Successfully updated lead: {lead.name}",
    }


def search_leads(env, input_data, dry_run=False):
    """Search for CRM leads.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - query: Search query (searches name, contact_name, email)
            - limit: Maximum results (default 10)
            - stage_id: Filter by stage
            - user_id: Filter by salesperson
        dry_run: Ignored for search operations

    Returns:
        dict with leads list
    """
    Lead = env["crm.lead"]

    domain = []
    query = input_data.get("query", "")
    if query:
        domain = [
            "|", "|",
            ("name", "ilike", query),
            ("contact_name", "ilike", query),
            ("email_from", "ilike", query),
        ]

    if input_data.get("stage_id"):
        domain.append(("stage_id", "=", input_data["stage_id"]))
    if input_data.get("user_id"):
        domain.append(("user_id", "=", input_data["user_id"]))

    limit = min(input_data.get("limit", 10), 50)
    leads = Lead.search(domain, limit=limit)

    return {
        "count": len(leads),
        "leads": [
            {
                "id": lead.id,
                "name": lead.name,
                "contact_name": lead.contact_name,
                "email": lead.email_from,
                "phone": lead.phone,
                "stage": lead.stage_id.name if lead.stage_id else None,
            }
            for lead in leads
        ],
    }
