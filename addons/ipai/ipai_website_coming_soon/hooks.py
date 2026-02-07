# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def _post_init_hook(env):
    """Set Coming Soon page as the website homepage."""
    page = env.ref(
        "ipai_website_coming_soon.page_coming_soon", raise_if_not_found=False
    )
    if not page:
        return
    for website in env["website"].search([]):
        website.homepage_id = page


def _uninstall_hook(env):
    """Restore default homepage (clear override)."""
    for website in env["website"].search([]):
        website.homepage_id = False
