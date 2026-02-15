# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def _post_init_hook(env):
    """Set InsightPulseAI homepage as the website homepage."""
    page = env.ref(
        "ipai_website_coming_soon.page_coming_soon", raise_if_not_found=False
    )
    if not page:
        _logger.warning("Homepage page record not found — skipping homepage_id assignment")
        return
    for website in env["website"].search([]):
        website.homepage_id = page
        _logger.info("Set homepage_id=%s for website %s", page.id, website.name)


def _uninstall_hook(env):
    """Restore default homepage (clear override)."""
    for website in env["website"].search([]):
        website.homepage_id = False
