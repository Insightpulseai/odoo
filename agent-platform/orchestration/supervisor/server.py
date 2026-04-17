"""Pulser Supervisor — MAF-based A2A server.

Implements the supervisor-mediated orchestration model from
docs/architecture/agent-orchestration-model.md.

Flow: client → intake → plan → dispatch workers → judge → synthesize → respond

Runtime: Microsoft Agent Framework (agent-framework package)
Protocol: A2A v0.2.0 (/.well-known/agent-card.json)
Auth: Managed Identity → Foundry (gpt-4.1)
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------
FOUNDRY_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://ipai-copilot-resource.openai.azure.com",
)
FOUNDRY_MODEL = os.getenv("FOUNDRY_MODEL", "gpt-4.1")
ODOO_STAGE = os.getenv("ODOO_STAGE", "dev")


# ---------------------------------------------------------------------------
# Agent Card (A2A v0.2.0)
# ---------------------------------------------------------------------------
AGENT_CARD = {
    "name": "Pulser Supervisor",
    "description": "Orchestrates Pulser specialist workers for Odoo ERP operations",
    "url": os.getenv("SUPERVISOR_URL", "http://localhost:8080"),
    "version": "0.1.0",
    "protocolVersion": "0.2.0",
    "provider": {"organization": "InsightPulse AI"},
    "capabilities": {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True,
    },
    "authentication": {
        "schemes": ["bearer"],
    },
    "defaultInputModes": ["text/plain", "application/json"],
    "defaultOutputModes": ["text/plain", "application/json"],
    "skills": [
        {
            "id": "route",
            "name": "Route request to specialist",
            "description": "Classifies intent and dispatches to the correct specialist worker",
        },
    ],
}


# ---------------------------------------------------------------------------
# Envelope builders (match agent-platform/contracts/envelopes/)
# ---------------------------------------------------------------------------
def build_request_envelope(
    agent_id: str,
    task_type: str,
    input_contract: dict,
    policy_context: dict | None = None,
    allowed_tools: list[str] | None = None,
    timeout_s: int = 120,
) -> dict:
    """Build canonical agent_request envelope."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "request_id": str(uuid.uuid4()),
        "workflow_id": str(uuid.uuid4()),
        "step_id": f"supervisor.dispatch.{agent_id}",
        "agent_id": agent_id,
        "task_type": task_type,
        "input_contract": input_contract,
        "policy_context": policy_context or {
            "approval_band": "L1_auto",
            "mutation_safety": "read_only",
            "tenant_isolation": True,
        },
        "allowed_tools": allowed_tools or [],
        "timeout_s": timeout_s,
        "retry_budget": {"max_retries": 1, "retry_on": ["timeout", "retryable_error"]},
        "expected_output_schema": {},
        "created_at": now,
    }


def build_result_envelope(
    request_id: str,
    workflow_id: str,
    step_id: str,
    agent_id: str,
    status: str,
    payload: dict | None = None,
    confidence: float = 1.0,
    error: dict | None = None,
) -> dict:
    """Build canonical agent_result envelope."""
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "request_id": request_id,
        "workflow_id": workflow_id,
        "step_id": step_id,
        "agent_id": agent_id,
        "status": status,
        "confidence": confidence,
        "evidence_refs": [],
        "output_payload": payload or {},
        "policy_flags": [],
        "cost_tokens": {"input": 0, "output": 0, "total": 0},
        "latency_ms": 0,
        "model_used": {
            "provider": "foundry_cloud",
            "model": FOUNDRY_MODEL,
            "version": "2025-04-14",
        },
        "completed_at": now,
    }
    if error:
        result["error"] = error
    return result


# ---------------------------------------------------------------------------
# Intent classifier (nano gate before full reasoning)
# ---------------------------------------------------------------------------
INTENT_MAP = {
    "standup": "pulser_scrum_master",
    "velocity": "pulser_scrum_master",
    "retro": "pulser_scrum_master",
    "drift": "pulser_scrum_master",
    "invoice": "doc_intel",
    "receipt": "doc_intel",
    "ocr": "doc_intel",
    "tax": "tax_guru",
    "bir": "tax_guru",
    "withholding": "tax_guru",
    "reconcile": "bank_recon",
    "recon": "bank_recon",
    "bank": "bank_recon",
    "deploy": "odoo_deploy",
    "build": "odoo_deploy",
    "staging": "odoo_deploy",
    "backup": "odoo_ops",
    "restore": "odoo_ops",
    "monitor": "odoo_ops",
}


def classify_intent(message: str) -> tuple[str, str]:
    """Classify user intent → (agent_id, task_type).

    Uses keyword matching as a fast gate. In production, this would
    call gpt-4.1-nano for classification before full reasoning.
    """
    msg_lower = message.lower()
    for keyword, agent in INTENT_MAP.items():
        if keyword in msg_lower:
            return agent, keyword
    return "pulser_planner", "general"


# ---------------------------------------------------------------------------
# Supervisor dispatch loop
# ---------------------------------------------------------------------------
def handle_message(message: str, context: dict | None = None) -> dict:
    """Main supervisor entry point.

    1. Classify intent (intake)
    2. Route to specialist (plan)
    3. Dispatch worker (execute)
    4. Judge result (validate)
    5. Synthesize response (respond)
    """
    workflow_id = str(uuid.uuid4())
    context = context or {}

    # Step 1: Intake — classify
    agent_id, task_type = classify_intent(message)
    logger.info(
        "supervisor: classified intent=%s agent=%s workflow=%s",
        task_type, agent_id, workflow_id,
    )

    # Step 2: Build request envelope
    request = build_request_envelope(
        agent_id=agent_id,
        task_type=task_type,
        input_contract={"message": message, "context": context},
    )
    request["workflow_id"] = workflow_id

    # Step 3: Dispatch to worker
    # In production: A2A call to the worker's Agent Card URL
    # For now: inline dispatch to the worker function
    try:
        worker_result = dispatch_to_worker(agent_id, task_type, request)
    except Exception as exc:
        logger.exception("supervisor: worker dispatch failed: %s", exc)
        worker_result = build_result_envelope(
            request_id=request["request_id"],
            workflow_id=workflow_id,
            step_id=f"supervisor.dispatch.{agent_id}",
            agent_id=agent_id,
            status="hard_error",
            error={"code": "DISPATCH_FAILED", "message": str(exc), "is_retryable": False},
        )

    # Step 4: Judge (placeholder — validates output contract)
    if worker_result.get("status") == "success":
        # In production: dispatch to judge workers via A2A
        worker_result["judged"] = True

    # Step 5: Synthesize
    return worker_result


def dispatch_to_worker(agent_id: str, task_type: str, request: dict) -> dict:
    """Dispatch to a specialist worker.

    In production: this makes an A2A call to the worker's Agent Card URL.
    For now: routes to inline worker functions for the MVP.
    """
    # Import workers lazily to avoid circular deps
    if agent_id == "pulser_scrum_master":
        from agent_platform.orchestration.workers import scrum_master
        return scrum_master.handle(request)
    elif agent_id == "doc_intel":
        from agent_platform.orchestration.workers import doc_intel
        return doc_intel.handle(request)
    else:
        # Fallback: call Foundry directly for general questions
        return _fallback_foundry_call(request)


def _fallback_foundry_call(request: dict) -> dict:
    """Fallback: direct Foundry call for unrouted questions."""
    message = request["input_contract"].get("message", "")

    try:
        from azure.identity import DefaultAzureCredential
        import urllib.request

        cred = DefaultAzureCredential()
        token = cred.get_token("https://cognitiveservices.azure.com/.default")

        url = f"{FOUNDRY_ENDPOINT}/openai/deployments/{FOUNDRY_MODEL}/chat/completions?api-version=2024-12-01-preview"
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": "You are Pulser, an AI assistant for Odoo 18 ERP. Answer concisely."},
                {"role": "user", "content": message},
            ],
            "max_tokens": 500,
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        answer = result["choices"][0]["message"]["content"]

        return build_result_envelope(
            request_id=request["request_id"],
            workflow_id=request["workflow_id"],
            step_id="supervisor.fallback",
            agent_id="pulser_planner",
            status="success",
            payload={"response": answer},
        )
    except Exception as exc:
        return build_result_envelope(
            request_id=request["request_id"],
            workflow_id=request["workflow_id"],
            step_id="supervisor.fallback",
            agent_id="pulser_planner",
            status="hard_error",
            error={"code": "FOUNDRY_ERROR", "message": str(exc), "is_retryable": True},
        )


# ---------------------------------------------------------------------------
# A2A HTTP server (lightweight, no framework dependency for MVP)
# ---------------------------------------------------------------------------
def serve(host: str = "0.0.0.0", port: int = 8080):
    """Start the A2A HTTP server."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class A2AHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/.well-known/agent-card.json":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(AGENT_CARD).encode())
            elif self.path == "/healthz":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/a2a/message/send":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                message = body.get("message", body.get("text", ""))
                context = body.get("context", {})

                result = handle_message(message, context)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer((host, port), A2AHandler)
    logger.info("Pulser Supervisor A2A server on %s:%d", host, port)
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
