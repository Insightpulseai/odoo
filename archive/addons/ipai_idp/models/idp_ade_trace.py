# -*- coding: utf-8 -*-
"""
IDP ADE Execution Trace Model.

Audit trail for every ADE orchestrator execution, enabling debugging,
A/B testing analysis, and prompt tuning over time.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpADETrace(models.Model):
    """
    IDP ADE Execution Trace.

    Stores the complete execution trace for every ADE pipeline run,
    including all steps executed, their inputs/outputs, and timing.
    Useful for:
    - Debugging extraction issues
    - A/B testing different pipelines
    - Prompt tuning and optimization
    - Audit trail for compliance

    Attributes:
        _name: idp.ade.trace
        _description: IDP ADE Execution Trace
    """

    _name = "idp.ade.trace"
    _description = "IDP ADE Execution Trace"
    _order = "create_date desc"

    # Core links
    document_id = fields.Many2one(
        "idp.document",
        string="Document",
        required=True,
        ondelete="cascade",
        index=True,
    )
    extraction_id = fields.Many2one(
        "idp.extraction",
        string="Extraction",
        ondelete="set null",
        help="Extraction record created (if any)",
    )
    company_id = fields.Many2one(
        related="document_id.company_id",
        store=True,
        index=True,
    )

    # Pipeline identification
    pipeline_id = fields.Char(
        string="Pipeline ID",
        required=True,
        index=True,
        help="Pipeline identifier (e.g., invoice_basic_v1)",
    )
    pipeline_doc_type = fields.Char(
        string="Pipeline Doc Type",
        help="Document type from pipeline config",
    )

    # Execution result
    status = fields.Selection(
        [
            ("ok", "OK"),
            ("needs_review", "Needs Review"),
            ("failed", "Failed"),
        ],
        string="Status",
        required=True,
        index=True,
    )
    action = fields.Char(
        string="Action",
        help="Action taken (e.g., send_to_review)",
    )
    reason = fields.Text(
        string="Reason",
        help="Reason for status if not OK",
    )

    # Execution metrics
    step_count = fields.Integer(
        string="Step Count",
        help="Number of steps executed",
    )
    steps_skipped = fields.Integer(
        string="Steps Skipped",
        help="Number of steps skipped due to conditions",
    )
    execution_time_ms = fields.Integer(
        string="Execution Time (ms)",
        help="Total pipeline execution time",
    )

    # Confidence tracking
    initial_confidence = fields.Float(
        string="Initial Confidence",
        help="Confidence after first extraction",
    )
    final_confidence = fields.Float(
        string="Final Confidence",
        help="Confidence after corrections (if any)",
    )
    confidence_delta = fields.Float(
        string="Confidence Delta",
        compute="_compute_confidence_delta",
        store=True,
    )

    # Validation tracking
    validation_passed_first = fields.Boolean(
        string="Passed First Validation",
        help="Whether initial extraction passed validation",
    )
    validation_passed_final = fields.Boolean(
        string="Passed Final Validation",
        help="Whether final extraction passed validation",
    )
    correction_applied = fields.Boolean(
        string="Correction Applied",
        help="Whether a correction round was executed",
    )

    # Full trace data
    trace_json = fields.Text(
        string="Trace (JSON)",
        help="Full step-by-step trace as JSON",
    )
    final_state_json = fields.Text(
        string="Final State (JSON)",
        help="Final state dict as JSON",
    )
    error_message = fields.Text(
        string="Error Message",
        help="Error message if pipeline failed",
    )

    @api.depends("initial_confidence", "final_confidence")
    def _compute_confidence_delta(self):
        """Compute improvement in confidence from corrections."""
        for record in self:
            if record.initial_confidence and record.final_confidence:
                record.confidence_delta = (
                    record.final_confidence - record.initial_confidence
                )
            else:
                record.confidence_delta = 0.0

    @api.model
    def create_from_ade_result(
        self, document, result, extraction=None, execution_time_ms=0
    ):
        """
        Create a trace record from an ADE orchestrator result.

        Args:
            document: idp.document record
            result: ADE orchestrator result dict
            extraction: Optional idp.extraction record
            execution_time_ms: Pipeline execution time in ms

        Returns:
            idp.ade.trace: Created trace record
        """
        status = result.get("status", "failed")
        state = result.get("state", {})
        trace = result.get("trace", [])

        # Extract metrics from trace
        steps_executed = len([s for s in trace if not s.get("skipped")])
        steps_skipped = len([s for s in trace if s.get("skipped")])

        # Find confidence values
        initial_confidence = None
        final_confidence = state.get("overall_confidence")

        for step in trace:
            if step.get("step") == "extract_core_fields":
                initial_confidence = step.get("result", {}).get("overall_confidence")
                break

        # Check validation results
        validation_passed_first = False
        validation_passed_final = False
        correction_applied = False

        for step in trace:
            step_id = step.get("step", "")
            result_data = step.get("result", {})

            if step_id == "validate_business_rules":
                validation_passed_first = result_data.get("validation_status") == "pass"
            elif step_id == "correction_round" and not step.get("skipped"):
                correction_applied = True
            elif step_id == "final_validation":
                validation_passed_final = result_data.get("final_status") == "pass"

        vals = {
            "document_id": document.id,
            "extraction_id": extraction.id if extraction else False,
            "pipeline_id": state.get("pipeline_id", "unknown"),
            "status": status,
            "action": result.get("action"),
            "reason": result.get("reason"),
            "step_count": steps_executed,
            "steps_skipped": steps_skipped,
            "execution_time_ms": execution_time_ms,
            "initial_confidence": initial_confidence,
            "final_confidence": final_confidence,
            "validation_passed_first": validation_passed_first,
            "validation_passed_final": validation_passed_final,
            "correction_applied": correction_applied,
            "trace_json": json.dumps(trace, ensure_ascii=False),
            "final_state_json": json.dumps(state, ensure_ascii=False),
            "error_message": result.get("reason") if status == "failed" else None,
        }

        return self.create(vals)

    def get_trace_steps(self):
        """
        Parse and return the trace steps as a list.

        Returns:
            list: List of step dicts
        """
        self.ensure_one()
        if self.trace_json:
            try:
                return json.loads(self.trace_json)
            except json.JSONDecodeError:
                return []
        return []

    def get_final_state(self):
        """
        Parse and return the final state as a dict.

        Returns:
            dict: Final state
        """
        self.ensure_one()
        if self.final_state_json:
            try:
                return json.loads(self.final_state_json)
            except json.JSONDecodeError:
                return {}
        return {}
