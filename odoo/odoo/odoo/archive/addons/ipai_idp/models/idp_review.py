# -*- coding: utf-8 -*-
"""
IDP Review Model.

Human-in-the-loop review and correction tracking.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpReview(models.Model):
    """
    IDP Document Review.

    Records human corrections to automated extractions.
    Used for:
    - Quality assurance
    - Training data collection
    - Audit trail

    Each correction can feed back into model improvement.

    Attributes:
        _name: idp.review
        _description: IDP Document Review
    """

    _name = "idp.review"
    _description = "IDP Document Review"
    _order = "create_date desc"

    # Core fields
    document_id = fields.Many2one(
        "idp.document",
        string="Document",
        required=True,
        ondelete="cascade",
    )
    extraction_id = fields.Many2one(
        "idp.extraction",
        string="Original Extraction",
        help="The extraction being reviewed/corrected",
    )

    # Review content
    original_json = fields.Text(
        string="Original Data (JSON)",
        help="The original extracted data before correction",
    )
    corrected_json = fields.Text(
        string="Corrected Data (JSON)",
        required=True,
        help="The human-corrected data",
    )
    diff_json = fields.Text(
        string="Changes (JSON)",
        compute="_compute_diff",
        store=True,
        help="Diff between original and corrected data",
    )

    # Reviewer info
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        default=lambda self: self.env.uid,
        required=True,
    )
    review_notes = fields.Text(
        string="Review Notes",
        help="Reviewer comments about the corrections",
    )

    # Review status
    status = fields.Selection(
        [
            ("pending", "Pending Review"),
            ("in_progress", "In Progress"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="pending",
        required=True,
    )

    # Quality metrics
    correction_count = fields.Integer(
        string="Fields Corrected",
        compute="_compute_correction_count",
        store=True,
    )
    review_time_seconds = fields.Integer(
        string="Review Time (seconds)",
        help="Time spent on this review",
    )

    # Training data flag
    use_for_training = fields.Boolean(
        string="Use for Training",
        default=True,
        help="Include this correction in training data exports",
    )

    @api.depends("original_json", "corrected_json")
    def _compute_diff(self):
        """Compute the diff between original and corrected data."""
        for record in self:
            if not record.original_json or not record.corrected_json:
                record.diff_json = "{}"
                continue

            try:
                original = json.loads(record.original_json)
                corrected = json.loads(record.corrected_json)
                diff = record._compute_json_diff(original, corrected)
                record.diff_json = json.dumps(diff)
            except json.JSONDecodeError:
                record.diff_json = "{}"

    @api.depends("diff_json")
    def _compute_correction_count(self):
        """Count the number of fields that were corrected."""
        for record in self:
            if record.diff_json:
                try:
                    diff = json.loads(record.diff_json)
                    record.correction_count = len(diff)
                except json.JSONDecodeError:
                    record.correction_count = 0
            else:
                record.correction_count = 0

    @staticmethod
    def _compute_json_diff(original, corrected, path=""):
        """
        Recursively compute differences between two JSON objects.

        Args:
            original: Original dict
            corrected: Corrected dict
            path: Current path for nested keys

        Returns:
            dict: Changes with old/new values
        """
        diff = {}
        all_keys = set(original.keys()) | set(corrected.keys())

        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            orig_val = original.get(key)
            corr_val = corrected.get(key)

            if orig_val != corr_val:
                if isinstance(orig_val, dict) and isinstance(corr_val, dict):
                    nested_diff = IdpReview._compute_json_diff(
                        orig_val, corr_val, current_path
                    )
                    diff.update(nested_diff)
                else:
                    diff[current_path] = {
                        "old": orig_val,
                        "new": corr_val,
                    }

        return diff

    def action_approve(self):
        """Approve the review and update the document."""
        for record in self:
            record.write({"status": "approved"})
            # Update document status
            record.document_id.write({"status": "reviewed"})
            _logger.info(
                "Review %s approved by %s for document %s",
                record.id,
                record.reviewer_id.name,
                record.document_id.id,
            )

    def action_reject(self):
        """Reject the review."""
        for record in self:
            record.write({"status": "rejected"})

    def action_start_review(self):
        """Mark review as in progress."""
        for record in self:
            record.write({"status": "in_progress"})

    def get_corrected_data(self):
        """
        Return corrected data as a Python dict.

        Returns:
            dict: Parsed corrected data
        """
        self.ensure_one()
        if self.corrected_json:
            try:
                return json.loads(self.corrected_json)
            except json.JSONDecodeError:
                return {}
        return {}

    @api.model
    def create_from_extraction(self, extraction):
        """
        Create a review record from an extraction.

        Args:
            extraction: idp.extraction record

        Returns:
            idp.review record
        """
        return self.create(
            {
                "document_id": extraction.document_id.id,
                "extraction_id": extraction.id,
                "original_json": extraction.extracted_json,
                "corrected_json": extraction.extracted_json,  # Start with original
                "status": "pending",
            }
        )
