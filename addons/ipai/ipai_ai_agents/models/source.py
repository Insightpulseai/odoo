# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IPAIAISource(models.Model):
    _name = "ipai.ai.source"
    _description = "AI Knowledge Source (metadata only; indexing is external)"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    enabled = fields.Boolean(
        default=True, help="If disabled, source won't be used for retrieval"
    )

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    source_type = fields.Selection(
        [
            ("docs", "Docs Site"),
            ("github", "GitHub Repository"),
            ("pdf", "PDF Documents"),
            ("knowledge", "Odoo Knowledge"),
            ("openapi", "OpenAPI Spec"),
            ("confluence", "Confluence"),
            ("notion", "Notion"),
            ("custom", "Custom"),
        ],
        required=True,
        default="docs",
    )
    url = fields.Char(
        help="Docs URL / repo URL / or reference used by your external indexer"
    )

    # GitHub-specific
    github_repo = fields.Char(help="Repository in format owner/repo")
    github_branch = fields.Char(default="main")
    github_paths = fields.Text(help="Comma-separated path patterns to include")

    # Indexing status
    last_indexed = fields.Datetime(readonly=True)
    last_indexed_version = fields.Char(
        readonly=True, help="Commit hash or version identifier"
    )
    index_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("indexing", "Indexing"),
            ("success", "Success"),
            ("error", "Error"),
        ],
        default="pending",
        readonly=True,
    )
    index_error = fields.Text(readonly=True)
    chunk_count = fields.Integer(
        readonly=True, help="Number of chunks indexed from this source"
    )

    notes = fields.Text()

    def action_trigger_reindex(self):
        """Trigger a reindex for this source (stub - actual implementation in ipai_ai_sources_odoo)."""
        self.ensure_one()
        self.write(
            {
                "index_status": "pending",
                "index_error": False,
            }
        )
        # TODO: Trigger actual reindex via queue_job or cron

    def action_view_chunks(self):
        """Open a view showing chunks from this source (requires Supabase integration)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Chunks - {self.name}",
            "res_model": "ir.ui.view",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_source_id": self.id,
            },
        }
