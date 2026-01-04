# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Idempotent seed on install (safe for production)."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ipai.finance.seed.service"].seed_if_empty()
