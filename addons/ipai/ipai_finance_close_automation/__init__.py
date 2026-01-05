# -*- coding: utf-8 -*-
from . import models, wizard


def post_init_hook(cr, registry):
    """Apply deadline offsets to template tasks after installation."""
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ipai.finance.close.service"]._apply_template_deadline_offsets()
