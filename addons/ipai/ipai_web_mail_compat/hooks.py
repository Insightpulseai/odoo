# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)

# Unique marker greppable from CI / log tails:
#   grep "IPAI_COMPAT_ACTIVE" odoo.log
MARKER = "IPAI_COMPAT_ACTIVE module=ipai_web_mail_compat target=OCA/mail_tracking version=19.0.1.0.8"


def post_init_hook(env):
    """Emit a one-line marker so healthchecks / CI can confirm the compat
    overlay was actually installed and its post-init ran.

    Validation::
        grep "IPAI_COMPAT_ACTIVE" /var/log/odoo/odoo.log
        # → IPAI_COMPAT_ACTIVE module=ipai_web_mail_compat ...
    """
    _logger.warning(MARKER)
