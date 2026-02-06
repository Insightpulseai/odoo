# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiAiMixin(models.AbstractModel):
    """Abstract mixin for AI-enhanced records.

    Inherit this mixin to add AI metadata fields to any model:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['ipai.ai.mixin']
    """

    _name = "ipai.ai.mixin"
    _description = "IPAI AI Mixin"

    ipai_ai_summary = fields.Text(
        string="AI Summary",
        help="AI-generated summary of this record",
    )
    ipai_ai_tags = fields.Char(
        string="AI Tags",
        help="Comma-separated AI-generated tags",
    )
    ipai_ai_confidence = fields.Float(
        string="AI Confidence",
        help="Confidence score of AI analysis (0-1)",
    )
    ipai_ai_last_run = fields.Datetime(
        string="AI Last Run",
        help="Last time AI analysis was performed",
    )
    ipai_ai_model_version = fields.Char(
        string="AI Model Version",
        help="Version of AI model used for analysis",
    )

    def action_run_ai_analysis(self):
        """Trigger AI analysis for this record.

        Override in inheriting models to implement specific analysis logic.
        By default, this enqueues a job to the external AI system.
        """
        IpaiJob = self.env["ipai.job"]
        for record in self:
            IpaiJob.create(
                {
                    "name": f"AI Analysis: {record.display_name}",
                    "job_type": "ai_analysis",
                    "model_name": record._name,
                    "record_id": record.id,
                    "state": "pending",
                }
            )
