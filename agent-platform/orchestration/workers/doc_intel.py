"""Document Intelligence specialist worker.

Handles: invoice, receipt, ocr
Replaces Odoo IAP with Azure Document Intelligence.
Per: addons/ipai/ipai_odoo_copilot/controllers/copilot_gateway.py (OCR route)
"""

import logging

logger = logging.getLogger(__name__)


def handle(request: dict) -> dict:
    """Handle a document intelligence task dispatched by the supervisor."""
    from agent_platform.orchestration.supervisor.server import build_result_envelope

    task_type = request.get("task_type", "unknown")
    message = request["input_contract"].get("message", "")

    return build_result_envelope(
        request_id=request["request_id"],
        workflow_id=request["workflow_id"],
        step_id=f"worker.doc_intel.{task_type}",
        agent_id="doc_intel",
        status="success",
        payload={
            "type": task_type,
            "message": f"Document Intelligence stub for: {message[:100]}",
            "note": "Full implementation calls Azure Document Intelligence via copilot_gateway.py OCR route",
        },
    )
