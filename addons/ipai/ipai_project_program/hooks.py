# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Load seed data after module installation."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    from .seed.loader import load_seed_bundle

    load_seed_bundle(env, module_name="ipai_project_program")
