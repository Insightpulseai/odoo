# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    scout_store_code = fields.Char(
        string="Scout Store Code",
        help="Stable store identifier used by Scout Analytics.",
        index=True,
        copy=False,
    )
    scout_store_type = fields.Selection(
        [
            ("sari_sari", "Sari-sari Store"),
            ("grocery", "Grocery"),
            ("pharmacy", "Pharmacy"),
            ("modern_trade", "Modern Trade"),
            ("ho_re_ca", "HoReCa"),
            ("distributor", "Distributor"),
            ("wholesaler", "Wholesaler"),
            ("other", "Other"),
        ],
        string="Store Type",
        help="Classification of retail outlet type for Scout analytics.",
    )
    scout_banner = fields.Char(
        string="Retail Banner",
        help="Banner or chain this store belongs to (e.g., 7-Eleven, SM).",
    )
    scout_region_code = fields.Char(
        string="Region Code",
        help="Philippine region code aligned with Scout regions (e.g., NCR, Region III).",
        index=True,
    )
    scout_province = fields.Char(
        string="Province",
        help="Province name for Scout regional reporting.",
    )
    scout_cluster = fields.Char(
        string="Cluster",
        help="Custom cluster name used in Scout dashboards.",
    )
    scout_channel = fields.Selection(
        [
            ("traditional", "Traditional Trade"),
            ("modern", "Modern Trade"),
            ("ecommerce", "E-commerce"),
            ("institutional", "Institutional"),
        ],
        string="Trade Channel",
        help="High-level channel classification for Scout.",
    )
    is_retail_outlet = fields.Boolean(
        string="Retail Outlet",
        default=False,
        help="Flag partners that should appear as stores in Scout.",
    )
    scout_active = fields.Boolean(
        string="Active in Scout",
        default=True,
        help="Whether this store should be included in Scout analytics.",
    )
    scout_latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
        help="GPS latitude for store mapping.",
    )
    scout_longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
        help="GPS longitude for store mapping.",
    )
    scout_last_visit_date = fields.Date(
        string="Last Visit Date",
        help="Date of last field visit recorded by Scout.",
    )
    scout_visit_frequency = fields.Selection(
        [
            ("weekly", "Weekly"),
            ("biweekly", "Bi-weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("on_demand", "On Demand"),
        ],
        string="Visit Frequency",
        help="Expected visit frequency for this outlet.",
    )

    _sql_constraints = [
        (
            "scout_store_code_unique",
            "UNIQUE(scout_store_code)",
            "Scout Store Code must be unique.",
        ),
    ]

    @api.model
    def _generate_scout_store_code(self, store_type, region_code):
        """Generate a unique Scout store code based on type and region."""
        prefix_map = {
            "sari_sari": "SSS",
            "grocery": "GRC",
            "pharmacy": "PHR",
            "modern_trade": "MTR",
            "ho_re_ca": "HRC",
            "distributor": "DST",
            "wholesaler": "WHL",
            "other": "OTH",
        }
        prefix = prefix_map.get(store_type, "OTH")
        region = (region_code or "XX")[:3].upper()
        sequence = self.env["ir.sequence"].next_by_code("scout.store.code") or "0001"
        return f"{prefix}-{region}-{sequence}"
