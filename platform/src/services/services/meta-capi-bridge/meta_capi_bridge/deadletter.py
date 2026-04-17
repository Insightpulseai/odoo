"""Dead-letter queue for failed CAPI deliveries.

Uses Azure Storage Queue for persistence. Failed events are written
with full context for manual replay.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger("meta_capi_bridge")


def enqueue_dead_letter(
    event: dict[str, Any],
    error: str,
    attempt_count: int,
) -> None:
    """Send failed event to dead-letter queue.

    In production, uses Azure Storage Queue.
    Falls back to logging if queue is unavailable.
    """
    dead_letter = {
        "original_event": event,
        "error": error,
        "attempt_count": attempt_count,
        "queue": os.environ.get("DEAD_LETTER_QUEUE", "meta-capi-deadletter"),
    }

    try:
        connection_string = os.environ.get("AzureWebJobsStorage", "")
        if connection_string and connection_string != "UseDevelopmentStorage=true":
            from azure.storage.queue import QueueClient

            queue_client = QueueClient.from_connection_string(
                connection_string,
                queue_name=dead_letter["queue"],
            )
            queue_client.send_message(json.dumps(dead_letter))
            logger.info(f"Dead-lettered event {event.get('event_id', '?')}")
        else:
            # Local dev fallback — log only
            logger.warning(
                f"Dead-letter (no queue): {json.dumps(dead_letter, default=str)}"
            )
    except Exception as e:
        logger.error(f"Failed to dead-letter event: {e}. Event: {json.dumps(dead_letter, default=str)}")
