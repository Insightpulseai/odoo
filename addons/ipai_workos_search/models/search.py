# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosSearch(models.TransientModel):
    """Search - Transient model for search operations."""

    _name = "ipai.workos.search"
    _description = "Work OS Search"

    query = fields.Char(string="Search Query")
    scope = fields.Selection(
        [
            ("global", "All Workspaces"),
            ("workspace", "Current Workspace"),
            ("space", "Current Space"),
            ("database", "Current Database"),
        ],
        string="Scope",
        default="global",
    )
    scope_id = fields.Integer(string="Scope ID")

    # Results (computed)
    page_results = fields.Text(string="Page Results (JSON)")
    database_results = fields.Text(string="Database Results (JSON)")
    block_results = fields.Text(string="Block Results (JSON)")

    @api.model
    def search_global(self, query, limit=20):
        """Perform global search across all content types."""
        results = {
            "pages": self._search_pages(query, limit=limit),
            "databases": self._search_databases(query, limit=limit),
            "blocks": self._search_blocks(query, limit=limit),
        }
        return results

    @api.model
    def search_scoped(self, query, scope, scope_id, limit=20):
        """Perform scoped search within a specific container."""
        domain_extra = []

        if scope == "workspace":
            domain_extra = [("workspace_id", "=", scope_id)]
        elif scope == "space":
            domain_extra = [("space_id", "=", scope_id)]
        elif scope == "database":
            return {
                "pages": [],
                "databases": [],
                "rows": self._search_rows(query, scope_id, limit),
            }

        return {
            "pages": self._search_pages(query, limit, domain_extra),
            "databases": self._search_databases(query, limit, domain_extra),
            "blocks": self._search_blocks(query, limit, domain_extra),
        }

    def _search_pages(self, query, limit=20, domain_extra=None):
        """Search pages by title."""
        Page = self.env["ipai.workos.page"]
        domain = [("name", "ilike", query)]
        if domain_extra:
            domain.extend(domain_extra)

        pages = Page.search(domain, limit=limit)
        return [
            {
                "id": p.id,
                "name": p.name,
                "icon": p.icon,
                "space_id": p.space_id.id,
                "space_name": p.space_id.name,
                "model": "ipai.workos.page",
            }
            for p in pages
        ]

    def _search_databases(self, query, limit=20, domain_extra=None):
        """Search databases by name."""
        Database = self.env["ipai.workos.database"]
        domain = [("name", "ilike", query)]
        if domain_extra:
            domain.extend(domain_extra)

        dbs = Database.search(domain, limit=limit)
        return [
            {
                "id": d.id,
                "name": d.name,
                "icon": d.icon,
                "row_count": d.row_count,
                "model": "ipai.workos.database",
            }
            for d in dbs
        ]

    def _search_blocks(self, query, limit=20, domain_extra=None):
        """Search blocks by content text."""
        Block = self.env["ipai.workos.block"]
        domain = [("content_text", "ilike", query)]
        if domain_extra:
            # Blocks don't have direct workspace/space, filter through page
            pass

        blocks = Block.search(domain, limit=limit)
        return [
            {
                "id": b.id,
                "type": b.block_type,
                "preview": (b.content_text or "")[:100],
                "page_id": b.page_id.id,
                "page_name": b.page_id.name,
                "model": "ipai.workos.block",
            }
            for b in blocks
        ]

    def _search_rows(self, query, database_id, limit=20):
        """Search rows in a specific database."""
        Row = self.env["ipai.workos.row"]
        domain = [
            ("database_id", "=", database_id),
            ("name", "ilike", query),
        ]
        rows = Row.search(domain, limit=limit)
        return [
            {
                "id": r.id,
                "name": r.name,
                "model": "ipai.workos.row",
            }
            for r in rows
        ]


class IpaiWorkosSearchHistory(models.Model):
    """Search History - Track recent searches per user."""

    _name = "ipai.workos.search.history"
    _description = "Work OS Search History"
    _order = "create_date desc"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        index=True,
    )
    query = fields.Char(string="Query", required=True)
    result_count = fields.Integer(string="Results Found")

    @api.model
    def log_search(self, query, result_count=0):
        """Log a search query."""
        return self.create(
            {
                "query": query,
                "result_count": result_count,
            }
        )

    @api.model
    def get_recent_searches(self, limit=10):
        """Get recent searches for current user."""
        return self.search(
            [
                ("user_id", "=", self.env.user.id),
            ],
            limit=limit,
        )
