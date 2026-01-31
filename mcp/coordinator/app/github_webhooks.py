"""
GitHub Webhook Handler

Handles:
- Webhook signature verification (HMAC-SHA256)
- Event routing (push, pull_request, issue_comment)
- Secure event processing
"""
import hashlib
import hmac
import logging
from typing import Optional, Dict, Any

from fastapi import APIRouter, Request, Header, HTTPException

from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.

    GitHub sends the signature in X-Hub-Signature-256 header as:
    sha256=<hex-digest>
    """
    if not settings.github_webhook_secret:
        logger.warning("GitHub webhook secret not configured")
        return False

    if not signature or not signature.startswith("sha256="):
        return False

    expected_signature = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


async def handle_ping_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ping event (sent when webhook is first configured)."""
    return {
        "event": "ping",
        "zen": payload.get("zen", "ok"),
        "hook_id": payload.get("hook_id"),
    }


async def handle_push_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle push event.

    Can be used to:
    - Trigger deployments
    - Forward to n8n for workflow automation
    - Update MCP server caches
    """
    ref = payload.get("ref", "")
    repository = payload.get("repository", {})
    pusher = payload.get("pusher", {})
    commits = payload.get("commits", [])

    logger.info(
        f"Push event: {repository.get('full_name')} "
        f"ref={ref} commits={len(commits)} by={pusher.get('name')}"
    )

    return {
        "event": "push",
        "ref": ref,
        "repository": repository.get("full_name"),
        "pusher": pusher.get("name"),
        "commit_count": len(commits),
        "processed": True,
    }


async def handle_pull_request_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle pull_request event.

    Can be used to:
    - Create Odoo tasks for PR reviews
    - Forward to MCP targets for analysis
    - Trigger CI/CD pipelines
    """
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    repository = payload.get("repository", {})

    logger.info(
        f"PR event: {repository.get('full_name')} "
        f"#{pr.get('number')} action={action}"
    )

    return {
        "event": "pull_request",
        "action": action,
        "pr_number": pr.get("number"),
        "pr_title": pr.get("title"),
        "repository": repository.get("full_name"),
        "processed": True,
    }


async def handle_issue_comment_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle issue_comment event.

    Can be used to:
    - Check for @claude mentions and route to agent
    - Process bot commands
    - Update Odoo tasks
    """
    action = payload.get("action", "")
    comment = payload.get("comment", {})
    issue = payload.get("issue", {})
    repository = payload.get("repository", {})

    comment_body = comment.get("body", "")
    is_claude_mention = "@claude" in comment_body.lower()

    logger.info(
        f"Issue comment: {repository.get('full_name')} "
        f"#{issue.get('number')} action={action} claude_mention={is_claude_mention}"
    )

    return {
        "event": "issue_comment",
        "action": action,
        "issue_number": issue.get("number"),
        "comment_id": comment.get("id"),
        "repository": repository.get("full_name"),
        "claude_mention": is_claude_mention,
        "processed": True,
    }


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
):
    """
    Receive and process GitHub webhook events.

    All webhooks are verified using HMAC-SHA256 signature.
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify signature
    if not verify_webhook_signature(body, x_hub_signature_256 or ""):
        logger.warning(f"Invalid webhook signature for delivery {x_github_delivery}")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

    event_type = x_github_event or "unknown"
    logger.info(f"Received GitHub webhook: event={event_type} delivery={x_github_delivery}")

    # Route to appropriate handler
    handlers = {
        "ping": handle_ping_event,
        "push": handle_push_event,
        "pull_request": handle_pull_request_event,
        "issue_comment": handle_issue_comment_event,
    }

    handler = handlers.get(event_type)
    if handler:
        result = await handler(payload)
        return {
            "status": "processed",
            "delivery": x_github_delivery,
            **result,
        }

    # Unknown event type - log and accept
    logger.info(f"Unhandled event type: {event_type}")
    return {
        "status": "ignored",
        "event": event_type,
        "delivery": x_github_delivery,
        "message": f"Event type '{event_type}' not handled",
    }
