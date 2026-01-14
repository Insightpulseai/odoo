# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════════════
# res_partner extension - Smart Delta Pattern (Odoo 18 CE)
# ═══════════════════════════════════════════════════════════════════════════════

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """
    Extend res.partner with a simple greeting field.

    Smart Delta Pattern:
    - Use _inherit to add fields to existing model
    - Prefix fields with ipai_ to avoid collisions
    """
    _inherit = 'res.partner'

    # Simple greeting field
    ipai_greeting = fields.Char(
        string='Greeting',
        help='Custom greeting message for this contact',
        default='Hello!',
    )
