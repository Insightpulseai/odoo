# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IntegrationBot(models.Model):
    """Bot account configuration for integrations."""

    _name = "ipai.integration.bot"
    _description = "Integration Bot"
    _order = "name"

    name = fields.Char(required=True)
    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade"
    )
    active = fields.Boolean(default=True)

    # Bot identity
    bot_username = fields.Char(required=True)
    bot_display_name = fields.Char()
    bot_description = fields.Text()
    bot_icon = fields.Binary(attachment=True)

    # Authentication
    bot_token = fields.Char(
        groups="ipai_integrations.group_integration_admin",
        help="Bot access token (stored encrypted)"
    )

    # Permissions
    permission_post = fields.Boolean(
        default=True,
        help="Can post messages to channels"
    )
    permission_read = fields.Boolean(
        default=True,
        help="Can read channel messages"
    )
    permission_manage = fields.Boolean(
        default=False,
        help="Can manage channels and users"
    )

    # Slash commands
    slash_command_ids = fields.One2many(
        "ipai.integration.bot.command",
        "bot_id",
        string="Slash Commands"
    )

    # Status
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("disabled", "Disabled"),
    ], default="draft")
    last_active = fields.Datetime(readonly=True)

    def action_activate(self):
        """Activate the bot."""
        self.ensure_one()
        self.state = "active"

    def action_disable(self):
        """Disable the bot."""
        self.ensure_one()
        self.state = "disabled"


class IntegrationBotCommand(models.Model):
    """Slash command definitions for bots."""

    _name = "ipai.integration.bot.command"
    _description = "Bot Slash Command"
    _order = "command"

    bot_id = fields.Many2one(
        "ipai.integration.bot",
        required=True,
        ondelete="cascade"
    )
    command = fields.Char(
        required=True,
        help="Command trigger (e.g., /task, /invoice)"
    )
    description = fields.Char(
        help="Description shown in autocomplete"
    )
    hint = fields.Char(
        help="Usage hint (e.g., '[task name]')"
    )

    # Handler
    handler_model = fields.Char(
        help="Odoo model to handle this command"
    )
    handler_method = fields.Char(
        default="_handle_slash_command",
        help="Method to call on the handler model"
    )

    # Response
    response_type = fields.Selection([
        ("ephemeral", "Ephemeral (visible only to user)"),
        ("in_channel", "In Channel (visible to all)"),
    ], default="ephemeral")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("bot_command_uniq", "unique(bot_id, command)",
         "Command must be unique per bot!"),
    ]
