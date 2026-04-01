"""Azure Function entrypoints for Meta CAPI Bridge.

Endpoints:
  POST /api/capi-relay     — Receive canonical events from Odoo, relay to Meta CAPI
  POST /api/capi-webhook   — Receive inbound Meta webhook callbacks
  GET  /api/capi-health    — Health check
"""

import json
import logging
import uuid

import azure.functions as func

from meta_capi_bridge.client import MetaCapiError, send_events
from meta_capi_bridge.config import config
from meta_capi_bridge.deadletter import enqueue_dead_letter
from meta_capi_bridge.events import EVENT_MAP, to_capi_payload
from meta_capi_bridge.webhook import verify_signature

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
logger = logging.getLogger("meta_capi_bridge")


@app.route(route="capi-relay", methods=["POST"])
def capi_relay(req: func.HttpRequest) -> func.HttpResponse:
    """Receive canonical business events from Odoo and relay to Meta CAPI.

    Expected JSON body:
    {
      "events": [
        {
          "event_type": "lead_created",
          "event_id": "uuid-or-odoo-id",
          "user": {"email": "...", "phone": "..."},
          "custom_data": {"value": 100.0, "currency": "PHP"},
          "source_url": "https://erp.insightpulseai.com/..."
        }
      ]
    }
    """
    correlation_id = req.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    logger.info(f"capi-relay invoked, correlation_id={correlation_id}")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    raw_events = body.get("events", [])
    if not raw_events:
        return func.HttpResponse(
            json.dumps({"error": "No events provided"}),
            status_code=400,
            mimetype="application/json",
        )

    # Validate event types
    invalid = [e for e in raw_events if e.get("event_type") not in EVENT_MAP]
    if invalid:
        bad_types = [e.get("event_type", "?") for e in invalid]
        return func.HttpResponse(
            json.dumps({
                "error": f"Unknown event types: {bad_types}",
                "valid_types": list(EVENT_MAP.keys()),
            }),
            status_code=400,
            mimetype="application/json",
        )

    # Ensure idempotency keys
    for event in raw_events:
        if "event_id" not in event:
            event["event_id"] = str(uuid.uuid4())

    # Transform to CAPI payloads
    capi_events = [to_capi_payload(e) for e in raw_events]

    # Send to Meta
    try:
        result = send_events(capi_events)
        return func.HttpResponse(
            json.dumps({
                "status": "delivered",
                "events_received": result.get("events_received"),
                "correlation_id": correlation_id,
            }),
            status_code=200,
            mimetype="application/json",
        )
    except MetaCapiError as e:
        # Dead-letter all events in the batch
        for event in raw_events:
            enqueue_dead_letter(event, str(e), attempt_count=3)

        logger.error(f"CAPI delivery failed: {e}", extra={"correlation_id": correlation_id})
        return func.HttpResponse(
            json.dumps({
                "status": "dead_lettered",
                "error": str(e),
                "correlation_id": correlation_id,
                "events_count": len(raw_events),
            }),
            status_code=502,
            mimetype="application/json",
        )


@app.route(route="capi-webhook", methods=["POST", "GET"])
def capi_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """Inbound Meta webhook — verification challenge + event processing.

    GET: Hub verification challenge (subscribe flow).
    POST: Event notifications with signature verification.
    """
    # GET — Meta verification challenge
    if req.method == "GET":
        mode = req.params.get("hub.mode")
        token = req.params.get("hub.verify_token")
        challenge = req.params.get("hub.challenge")

        verify_token = config.META_APP_SECRET[:16] if config.META_APP_SECRET else ""
        if mode == "subscribe" and token == verify_token:
            return func.HttpResponse(challenge, status_code=200)
        return func.HttpResponse("Forbidden", status_code=403)

    # POST — Event notification
    signature = req.headers.get("X-Hub-Signature-256", "")
    body_bytes = req.get_body()

    if not verify_signature(body_bytes, signature):
        logger.warning("Webhook signature verification failed")
        return func.HttpResponse("Invalid signature", status_code=403)

    try:
        payload = json.loads(body_bytes)
        logger.info(
            "Webhook received",
            extra={"object": payload.get("object"), "entry_count": len(payload.get("entry", []))},
        )
        # Process inbound events (ad insights, delivery confirmations, etc.)
        # Future: route to Databricks bronze ingestion
        return func.HttpResponse(json.dumps({"status": "received"}), status_code=200, mimetype="application/json")
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return func.HttpResponse("Processing error", status_code=500)


@app.route(route="capi-health", methods=["GET"])
def capi_health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    errors = config.validate()
    status = "healthy" if not errors else "unhealthy"
    return func.HttpResponse(
        json.dumps({
            "status": status,
            "app_id": config.META_APP_ID,
            "api_version": config.META_API_VERSION,
            "pixel_configured": bool(config.META_PIXEL_ID),
            "token_configured": bool(config.META_ACCESS_TOKEN),
            "errors": errors,
        }),
        status_code=200 if not errors else 503,
        mimetype="application/json",
    )
