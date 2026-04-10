# -*- coding: utf-8 -*-
"""
expense_boundary_doc.py — Layer ownership boundary documentation model.

Records proven/declared/candidate coverage for the expense stack.
This is the SSOT boundary map in DB form — queryable, extensible, and
auditable without a separate markdown-only artifact.

Layers:
  ce_native       — Odoo CE hr_expense (base execution surface)
  oca_direct      — OCA hr-expense modules (advance clearing, payment, tier)
  oca_adjacent    — Adjacent OCA infrastructure (dms, auditlog, queue_job)
  custom_delta    — ipai_* thin delta (PH-specific only)
  bridge          — External bridge services (OCR, card feeds)

Status:
  proven          — Capability implemented and runtime-verified
  declared        — Mapped to CE/OCA/custom but not runtime-verified here
  candidate       — Likely exists compositionally, needs proof
  gap             — No CE/OCA/custom coverage, bridge or future work required
"""

from odoo import fields, models


class ExpenseBoundaryDoc(models.Model):
    """Layer ownership boundary record for the expense stack.

    Pre-loaded via expense_parity_data.xml. Editable at runtime by
    administrators to track verification progress.
    """

    _name = "expense.boundary.doc"
    _description = "Expense Stack Boundary Documentation"
    _order = "layer, module_name"
    _rec_name = "capability"

    layer = fields.Selection(
        [
            ("ce_native", "CE Native (hr_expense)"),
            ("oca_direct", "OCA Direct (hr-expense)"),
            ("oca_adjacent", "OCA Adjacent (composable infra)"),
            ("custom_delta", "Custom Delta (ipai_*)"),
            ("bridge", "External Bridge"),
        ],
        string="Layer",
        required=True,
        index=True,
    )

    module_name = fields.Char(
        string="Module / Service",
        required=True,
        help="Technical name of the module or service that owns this capability.",
    )

    capability = fields.Char(
        string="Capability",
        required=True,
        help="Short description of the capability provided by this layer.",
    )

    status = fields.Selection(
        [
            ("proven", "Proven"),
            ("declared", "Declared"),
            ("candidate", "Candidate"),
            ("gap", "Gap"),
        ],
        string="Status",
        required=True,
        default="declared",
        index=True,
        help=(
            "proven: implemented and runtime-verified. "
            "declared: mapped but not verified. "
            "candidate: likely exists, needs proof. "
            "gap: no coverage, bridge or future work required."
        ),
    )

    notes = fields.Text(
        string="Notes",
        help="Any additional context, constraints, or verification evidence.",
    )

    verified_date = fields.Date(
        string="Verified Date",
        help="Date when proven status was confirmed.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
