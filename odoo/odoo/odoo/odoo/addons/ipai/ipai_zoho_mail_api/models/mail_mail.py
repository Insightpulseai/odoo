# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Compatibility shim for OCA mail_tracking + Odoo 19.

Problem resolved via a two-part fix:
1. OCA mail_tracking's _prepare_outgoing_list now accepts **kwargs and forwards
   them as keywords to super() (patched on host at
   addons/OCA/mail/mail_tracking/models/mail_mail.py).
2. This shim sits between mail_tracking and the base mail model in the MRO
   (load order: mass_mailing → mail_tracking → ipai_zoho_mail_api → mail).
   It strips any extra kwargs that the base mail._prepare_outgoing_list
   does not accept (e.g. recipients_follower_status) before forwarding.
"""

import logging

from odoo import models

_logger = logging.getLogger(__name__)

# kwargs accepted by the base mail.models.mail_mail._prepare_outgoing_list
_MAIL_BASE_KWARGS = frozenset({"mail_server", "doc_to_followers"})


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _prepare_outgoing_list(self, mail_server=False, **kwargs):
        """Odoo 19 + OCA mail_tracking MRO compatibility shim.

        OCA mail_tracking._prepare_outgoing_list (post host-patch) passes
        recipients_follower_status= and potentially other kwargs via **kwargs.
        Odoo 19 base mail._prepare_outgoing_list only accepts mail_server and
        doc_to_followers.  This shim sits between the two in MRO order:

            mass_mailing → mail_tracking (patched) → ipai_zoho_mail_api (this) → mail

        It strips unknown kwargs before forwarding, and warns when it does so —
        unexpected kwargs indicate the host patch is missing or OCA changed its
        signature again.  See runtime/patches/README.md for patch inventory.
        """
        # Strip kwargs the base method doesn't understand
        filtered = {k: v for k, v in kwargs.items() if k in _MAIL_BASE_KWARGS}
        stripped = kwargs.keys() - _MAIL_BASE_KWARGS
        if stripped:
            _logger.warning(
                "ipai_zoho_mail_api._prepare_outgoing_list: stripping unexpected kwargs %s "
                "(Odoo19+OCA mail_tracking MRO mismatch — check OCA patch is applied)",
                sorted(stripped),
            )
        return super()._prepare_outgoing_list(mail_server=mail_server, **filtered)
