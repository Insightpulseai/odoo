# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Load seed data after module installation."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    from .seed.loader import load_seed_bundle
    load_seed_bundle(env, module_name="ipai_finance_month_end")
