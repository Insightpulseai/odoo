# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """
        Override OAuth signin to make new users Internal Users.

        The standard auth_oauth module creates users with portal group.
        This override ensures users get the internal user group instead,
        giving them access to the full Odoo backend.
        """
        # Call the original method to create/find the user
        login = super()._auth_oauth_signin(provider, validation, params)

        # Find the user that was just created/logged in
        user = self.search([("login", "=", login)], limit=1)
        if user:
            self._promote_to_internal_user(user)

        return login

    def _promote_to_internal_user(self, user):
        """
        Promote a user to internal user status.

        This method:
        1. Adds the Internal User group (base.group_user)
        2. Removes the Portal group (base.group_portal) if present

        Args:
            user: res.users record to promote
        """
        try:
            internal_group = self.env.ref("base.group_user")
            portal_group = self.env.ref("base.group_portal")

            # Check if user is already an internal user
            if internal_group in user.groups_id:
                _logger.debug(
                    "OAuth user %s (id=%s) is already an internal user",
                    user.login,
                    user.id,
                )
                return

            _logger.info(
                "Promoting OAuth user %s (id=%s) from portal to internal user",
                user.login,
                user.id,
            )

            # Use sudo() to bypass access rights during promotion
            user_sudo = user.sudo()

            # Build the groups_id update commands
            groups_update = [
                (4, internal_group.id),  # Add internal user group
            ]

            # Remove portal group if present
            if portal_group in user.groups_id:
                groups_update.append((3, portal_group.id))

            user_sudo.write({"groups_id": groups_update})

            _logger.info(
                "Successfully promoted OAuth user %s to internal user. " "Groups: %s",
                user.login,
                [g.full_name for g in user_sudo.groups_id],
            )

        except Exception as e:
            _logger.error(
                "Failed to promote OAuth user %s to internal user: %s",
                user.login if user else "unknown",
                str(e),
            )
            # Don't raise - allow login to proceed even if promotion fails
            # The user can be manually promoted via UI
