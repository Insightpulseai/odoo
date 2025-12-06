# -*- coding: utf-8 -*-
"""
ADE Orchestrator - The Brain of the Extraction Engine.

Reads YAML pipelines and executes steps in sequence, managing
state, conditions, and final routing decisions.
"""
import logging
from typing import Any, Dict, List, Optional

from .pipelines import PipelineRegistry
from .tools import ADETools

_logger = logging.getLogger(__name__)


class ADEOrchestrator:
    """
    Agentic Document Extraction Orchestrator.

    Executes multi-step extraction pipelines defined in YAML,
    coordinating LLM calls, parsers, and validation.
    """

    def __init__(self, env, pipeline_registry: Optional[PipelineRegistry] = None):
        """
        Initialize the ADE orchestrator.

        Args:
            env: Odoo environment
            pipeline_registry: Optional custom pipeline registry
        """
        self.env = env
        self.registry = pipeline_registry or PipelineRegistry()

    def run(self, pipeline_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an ADE pipeline.

        Args:
            pipeline_id: Pipeline identifier (e.g., 'invoice_basic_v1')
            context: Initial context containing at minimum:
                     - ocr_text: The OCR-extracted text
                     - doc_id: Optional document ID

        Returns:
            dict: {
                'status': 'ok' | 'needs_review' | 'failed',
                'action': Optional action to take (e.g., 'send_to_review'),
                'state': Final state with all extracted fields,
                'trace': List of step executions with results,
                'reason': Optional failure reason
            }
        """
        _logger.info("Starting ADE pipeline: %s", pipeline_id)

        try:
            pipeline = self.registry.load(pipeline_id)
        except FileNotFoundError:
            return {
                "status": "failed",
                "reason": f"Pipeline not found: {pipeline_id}",
                "state": context,
                "trace": [],
            }

        tools = ADETools(self.env, pipeline_id)
        state: Dict[str, Any] = dict(context)
        state["pipeline_id"] = pipeline_id
        trace: List[Dict[str, Any]] = []

        # Execute each step
        for step in pipeline.get("steps", []):
            step_id = step.get("id", "unknown")
            step_type = step.get("type")

            _logger.debug("Evaluating step: %s (type=%s)", step_id, step_type)

            # Check conditional execution
            if "when" in step:
                condition = step["when"]
                if not self._eval_condition(condition, state):
                    _logger.debug("Skipping step %s: condition not met", step_id)
                    trace.append({
                        "step": step_id,
                        "type": step_type,
                        "skipped": True,
                        "reason": f"Condition not met: {condition}",
                    })
                    continue

            # Execute step based on type
            try:
                if step_type == "llm":
                    result = self._run_llm_step(step, state, tools)
                elif step_type == "parser":
                    result = self._run_parser_step(step, state, tools)
                elif step_type == "validation":
                    result = self._run_validation_step(step, state, tools)
                else:
                    _logger.warning("Unknown step type: %s", step_type)
                    result = {}

                # Update state with results
                state.update(result)
                trace.append({
                    "step": step_id,
                    "type": step_type,
                    "result": result,
                    "skipped": False,
                })

                _logger.debug("Step %s completed: %s", step_id, list(result.keys()))

            except Exception as e:
                _logger.exception("Step %s failed", step_id)
                trace.append({
                    "step": step_id,
                    "type": step_type,
                    "error": str(e),
                    "skipped": False,
                })
                return {
                    "status": "failed",
                    "reason": f"Step {step_id} failed: {str(e)}",
                    "state": state,
                    "trace": trace,
                }

            # Check for early stop
            if "stop_if" in step:
                stop_config = step["stop_if"]
                condition = stop_config.get("condition", "False")
                action = stop_config.get("action", "fail")

                if self._eval_condition(condition, state):
                    _logger.info(
                        "Early stop at step %s: %s -> %s",
                        step_id,
                        condition,
                        action,
                    )
                    return {
                        "status": "failed" if action == "fail" else "needs_review",
                        "reason": f"Stopped at step {step_id}: {condition}",
                        "state": state,
                        "trace": trace,
                    }

        # Final decision based on target criteria
        return self._make_final_decision(pipeline, state, trace)

    def _eval_condition(self, expr: str, state: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression against current state.

        Uses a restricted eval with only state variables available.
        Safe for simple boolean expressions.

        Args:
            expr: Condition expression (e.g., "confidence < 0.9")
            state: Current state dict

        Returns:
            bool: Evaluation result
        """
        try:
            # Create a safe evaluation context
            safe_globals = {"__builtins__": {}}
            return bool(eval(expr, safe_globals, state))
        except Exception as e:
            _logger.warning("Condition eval failed: %s (%s)", expr, e)
            return False

    def _run_llm_step(
        self, step: Dict[str, Any], state: Dict[str, Any], tools: ADETools
    ) -> Dict[str, Any]:
        """
        Execute an LLM step.

        Args:
            step: Step configuration
            state: Current state
            tools: ADE tools instance

        Returns:
            dict: LLM response fields
        """
        prompt_ref = step.get("prompt_ref")
        if not prompt_ref:
            raise ValueError(f"LLM step missing prompt_ref: {step.get('id')}")

        # Gather inputs
        inputs = {}
        for input_key in step.get("inputs", []):
            if input_key == "current_fields":
                inputs[input_key] = tools.get_current_fields(state)
            elif input_key in state:
                inputs[input_key] = state[input_key]

        # Call LLM
        result = tools.call_llm(prompt_ref, **inputs)

        # Filter to declared outputs if specified
        outputs = step.get("outputs")
        if outputs:
            result = {k: v for k, v in result.items() if k in outputs}

        return result

    def _run_parser_step(
        self, step: Dict[str, Any], state: Dict[str, Any], tools: ADETools
    ) -> Dict[str, Any]:
        """
        Execute a parser step.

        Args:
            step: Step configuration with 'operations' list
            state: Current state
            tools: ADE tools instance

        Returns:
            dict: Parsed field values
        """
        result = {}
        for op in step.get("operations", []):
            field = op.get("field")
            parser = op.get("parser")
            if not field or not parser:
                continue

            value = state.get(field)
            if value is not None:
                result[field] = tools.parse_field(parser, value)

        return result

    def _run_validation_step(
        self, step: Dict[str, Any], state: Dict[str, Any], tools: ADETools
    ) -> Dict[str, Any]:
        """
        Execute a validation step.

        Args:
            step: Step configuration with 'rule_set'
            state: Current state
            tools: ADE tools instance

        Returns:
            dict: Validation results
        """
        rule_set = step.get("rule_set", "default")
        validation = tools.validate(rule_set, state)

        result = {
            "validation_status": validation.get("status", "unknown"),
            "validation_errors": validation.get("errors", []),
        }

        # Also set final_status if this is a final validation
        if step.get("id", "").startswith("final"):
            result["final_status"] = result["validation_status"]
            result["final_errors"] = result["validation_errors"]

        return result

    def _make_final_decision(
        self, pipeline: Dict[str, Any], state: Dict[str, Any], trace: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make final routing decision based on target criteria.

        Args:
            pipeline: Pipeline configuration
            state: Final state
            trace: Execution trace

        Returns:
            dict: Final result with status and action
        """
        target = pipeline.get("target", {})
        min_confidence = target.get("min_confidence", 0.0)
        require_status = target.get("require_final_status")
        on_fail = target.get("on_fail", "send_to_review")

        final_status = state.get("final_status", state.get("validation_status", "unknown"))
        confidence = state.get("overall_confidence", 0.0)

        # Check if we meet target criteria
        status_ok = not require_status or final_status == require_status
        confidence_ok = confidence >= min_confidence

        if status_ok and confidence_ok:
            _logger.info(
                "ADE pipeline OK: confidence=%.2f, status=%s",
                confidence,
                final_status,
            )
            return {
                "status": "ok",
                "state": state,
                "trace": trace,
            }

        # Doesn't meet criteria
        _logger.info(
            "ADE pipeline needs review: confidence=%.2f (min=%.2f), status=%s (required=%s)",
            confidence,
            min_confidence,
            final_status,
            require_status,
        )
        return {
            "status": "needs_review",
            "action": on_fail,
            "state": state,
            "trace": trace,
            "reason": f"Confidence {confidence:.2f} < {min_confidence} or status {final_status} != {require_status}",
        }
