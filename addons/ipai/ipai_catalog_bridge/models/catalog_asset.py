# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class CatalogAsset(models.Model):
    """Local cache of catalog assets for UI and quick lookups.

    This model mirrors the Supabase catalog.assets table for offline/fast access.
    The source of truth remains Supabase; this is a read-through cache.
    """

    _name = "ipai.catalog.asset"
    _description = "Catalog Asset"
    _order = "fqdn"
    _rec_name = "title"

    # Identity
    fqdn = fields.Char(
        string="FQDN",
        required=True,
        index=True,
        help="Fully Qualified Domain Name (e.g., odoo.odoo_core.account.move)",
    )
    asset_type = fields.Selection(
        selection=[
            ("table", "Table"),
            ("view", "View"),
            ("file", "File"),
            ("model", "Model"),
            ("function", "Function"),
            ("dashboard", "Dashboard"),
            ("odoo_model", "Odoo Model"),
            ("odoo_action", "Odoo Action"),
            ("odoo_menu", "Odoo Menu"),
            ("odoo_view", "Odoo View"),
            ("odoo_report", "Odoo Report"),
            ("scout_layer", "Scout Layer"),
            ("ai_prompt", "AI Prompt"),
            ("ai_agent", "AI Agent"),
            ("notebook", "Notebook"),
            ("pipeline", "Pipeline"),
        ],
        string="Type",
        required=True,
        index=True,
    )
    system = fields.Selection(
        selection=[
            ("odoo", "Odoo"),
            ("supabase", "Supabase"),
            ("databricks", "Databricks"),
            ("scout", "Scout"),
            ("files", "Files"),
            ("n8n", "n8n"),
            ("mcp", "MCP"),
            ("external", "External"),
        ],
        string="System",
        required=True,
        index=True,
    )

    # Metadata
    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    owner = fields.Char(string="Owner")
    tags = fields.Char(string="Tags", help="Comma-separated tags")
    uri = fields.Char(string="URI", help="Deep link URL")
    metadata_json = fields.Text(string="Metadata JSON")

    # Status
    status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("deprecated", "Deprecated"),
            ("archived", "Archived"),
            ("draft", "Draft"),
        ],
        string="Status",
        default="active",
    )

    # Sync tracking
    supabase_id = fields.Char(string="Supabase ID", index=True)
    last_sync = fields.Datetime(string="Last Sync")

    # Links to Odoo objects (for odoo_* types)
    res_model = fields.Char(string="Model Name")
    res_id = fields.Integer(string="Record ID")

    _sql_constraints = [
        ("fqdn_unique", "unique(fqdn)", "FQDN must be unique."),
    ]

    @api.model
    def build_fqdn(self, system, *parts):
        """Build a canonical FQDN from parts.

        Examples:
            build_fqdn('odoo', 'odoo_core', 'account.move')
            → 'odoo.odoo_core.account.move'
        """
        return ".".join([system] + list(parts))

    @api.model
    def get_odoo_model_fqdn(self, model_name):
        """Get FQDN for an Odoo model."""
        db_name = self.env.cr.dbname
        return self.build_fqdn("odoo", db_name, model_name)

    @api.model
    def get_odoo_action_fqdn(self, action_xmlid):
        """Get FQDN for an Odoo action."""
        db_name = self.env.cr.dbname
        return self.build_fqdn("odoo", db_name, "action", action_xmlid)

    def action_open_uri(self):
        """Open the asset's URI in a new window."""
        self.ensure_one()
        if self.uri:
            return {
                "type": "ir.actions.act_url",
                "url": self.uri,
                "target": "new",
            }
        return {"type": "ir.actions.act_window_close"}

    def action_sync_from_catalog(self):
        """Pull latest data from Supabase catalog."""
        self.ensure_one()
        sync_service = self.env["ipai.catalog.sync"]
        sync_service.sync_asset_from_catalog(self.fqdn)

    @api.model
    def search_catalog(self, query, asset_type=None, system=None, limit=20):
        """Search local catalog cache.

        Args:
            query: Search string (searches fqdn, title, description)
            asset_type: Filter by asset type
            system: Filter by system
            limit: Max results

        Returns:
            List of dicts with asset info
        """
        domain = [("status", "=", "active")]

        if query:
            domain.append(
                "|",
            )
            domain.append("|")
            domain.append(("fqdn", "ilike", query))
            domain.append(("title", "ilike", query))
            domain.append(("description", "ilike", query))

        if asset_type:
            domain.append(("asset_type", "=", asset_type))

        if system:
            domain.append(("system", "=", system))

        assets = self.search(domain, limit=limit)
        return [
            {
                "fqdn": a.fqdn,
                "title": a.title,
                "description": a.description,
                "asset_type": a.asset_type,
                "system": a.system,
                "uri": a.uri,
                "tags": a.tags,
            }
            for a in assets
        ]


class CatalogTool(models.Model):
    """Tool definitions for AI copilot.

    Mirrors catalog.tools from Supabase for local access and UI.
    """

    _name = "ipai.catalog.tool"
    _description = "Catalog Tool"
    _order = "tool_key"
    _rec_name = "name"

    # Identity
    tool_key = fields.Char(
        string="Tool Key",
        required=True,
        index=True,
        help="Unique identifier (e.g., odoo.create_record)",
    )
    tool_type = fields.Selection(
        selection=[
            ("query", "Query"),
            ("action", "Action"),
            ("rpc", "RPC"),
            ("edge_function", "Edge Function"),
            ("n8n_workflow", "n8n Workflow"),
            ("mcp_tool", "MCP Tool"),
        ],
        string="Type",
        required=True,
    )

    # Metadata
    name = fields.Char(string="Name", required=True)
    description = fields.Text(
        string="Description",
        required=True,
        help="Description used for LLM tool selection",
    )

    # Schema (JSON)
    parameters_json = fields.Text(string="Parameters JSON")
    returns_json = fields.Text(string="Returns JSON")

    # Access control
    requires_confirmation = fields.Boolean(
        string="Requires Confirmation",
        default=True,
        help="Preview → Apply pattern for writes",
    )
    allowed_roles = fields.Char(
        string="Allowed Roles",
        help="Comma-separated role XML IDs (empty = all)",
    )

    # Tags
    tags = fields.Char(string="Tags", help="Comma-separated tags")

    # Status
    active = fields.Boolean(string="Active", default=True)

    # Sync tracking
    supabase_id = fields.Char(string="Supabase ID", index=True)
    last_sync = fields.Datetime(string="Last Sync")

    _sql_constraints = [
        ("tool_key_unique", "unique(tool_key)", "Tool key must be unique."),
    ]

    @api.model
    def get_tools_for_copilot(self, tags=None, include_schema=True):
        """Get tool definitions formatted for LLM function calling.

        Args:
            tags: Optional list of tags to filter by
            include_schema: Include parameter/return schemas

        Returns:
            List of tool definitions in OpenAI-compatible format
        """
        domain = [("active", "=", True)]

        if tags:
            for tag in tags:
                domain.append(("tags", "ilike", tag))

        tools = self.search(domain)
        result = []

        for tool in tools:
            tool_def = {
                "name": tool.tool_key,
                "description": tool.description,
            }

            if include_schema and tool.parameters_json:
                try:
                    import json

                    tool_def["parameters"] = json.loads(tool.parameters_json)
                except Exception:
                    pass

            result.append(tool_def)

        return result
