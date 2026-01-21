# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    ces_pitch_type = fields.Selection(
        [
            ("new_business", "New Business Pitch"),
            ("project", "Project Pitch"),
            ("retainer", "Retainer Renewal"),
            ("organic", "Organic Growth"),
            ("referral", "Referral"),
        ],
        string="Pitch Type",
        help="Classification of opportunity type for CES.",
    )
    ces_brand = fields.Char(
        string="Brand (CES)",
        help="Brand being pitched.",
    )
    ces_industry = fields.Selection(
        [
            ("fmcg", "FMCG"),
            ("telco", "Telco"),
            ("banking", "Banking/Finance"),
            ("retail", "Retail"),
            ("auto", "Automotive"),
            ("pharma", "Pharma/Healthcare"),
            ("tech", "Technology"),
            ("fmb", "Food & Beverage"),
            ("travel", "Travel/Tourism"),
            ("government", "Government"),
            ("ngo", "NGO/Non-profit"),
            ("other", "Other"),
        ],
        string="Industry",
        help="Client industry classification.",
    )
    ces_estimated_annual = fields.Monetary(
        string="Est. Annual Revenue",
        currency_field="company_currency",
        help="Estimated annual revenue if won.",
    )
    ces_pitch_date = fields.Date(
        string="Pitch Date",
        help="Date of pitch presentation.",
    )
    ces_decision_date = fields.Date(
        string="Expected Decision Date",
        help="Expected date for client decision.",
    )
    ces_competitors = fields.Char(
        string="Competing Agencies",
        help="Comma-separated list of competing agencies.",
    )
    ces_is_incumbent = fields.Boolean(
        string="Incumbent",
        help="Check if we are the incumbent agency.",
    )
    ces_scope = fields.Selection(
        [
            ("full_service", "Full Service"),
            ("creative_only", "Creative Only"),
            ("media_only", "Media Only"),
            ("digital_only", "Digital Only"),
            ("pr_only", "PR Only"),
            ("project", "Project-based"),
        ],
        string="Scope of Work",
        help="Scope of work being pitched.",
    )
