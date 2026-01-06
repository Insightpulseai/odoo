# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """Recompute risk for all modules after installation."""
    modules = env["ir.module.module"].search([])
    modules._compute_x_risk_fields()
