import logging
import os

_logger = logging.getLogger(__name__)

DIVA_GOALS_ENDPOINT = os.environ.get(
    'DIVA_GOALS_ENDPOINT', 'http://localhost:3100/api'
)


class DivaBridge:
    """Bridge between Odoo Copilot and the Diva Goals backend.

    All methods are stubs that log the call and return placeholder
    responses.  The real implementation will POST to the Diva Goals
    API once the backend is wired.
    """

    def __init__(self, endpoint: str | None = None):
        self._endpoint = endpoint or DIVA_GOALS_ENDPOINT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_context(self, context_envelope: dict) -> dict:
        """Send an Odoo context envelope to the Diva Goals backend.

        Args:
            context_envelope: Structured context built by
                OdooContextBuilder (record, company, user, tax slices).

        Returns:
            Acknowledgement dict with a correlation id.
        """
        _logger.info(
            'DivaBridge.send_context: envelope keys=%s endpoint=%s',
            list(context_envelope.keys()),
            self._endpoint,
        )
        return {
            'status': 'accepted',
            'correlation_id': 'stub-corr-001',
            'message': 'Context envelope queued (stub)',
        }

    def get_review_status(self, goal_id: str) -> dict:
        """Retrieve the current review status for a goal.

        Args:
            goal_id: The Diva Goals identifier (e.g. "goal-001").

        Returns:
            Goal status dict with progress, confidence, and evidence
            summary.
        """
        _logger.info(
            'DivaBridge.get_review_status: goal_id=%s', goal_id,
        )
        return {
            'goal_id': goal_id,
            'status': 'on_track',
            'progress': 72,
            'confidence': 85,
            'evidence_count': 3,
            'message': 'Placeholder status (stub)',
        }

    def submit_action(self, action_type: str, payload: dict) -> dict:
        """Submit an approved action back to the Diva Goals backend.

        Args:
            action_type: One of ``approve``, ``reject``, ``defer``,
                ``escalate``.
            payload: Action-specific data (reason, approver, etc.).

        Returns:
            Confirmation dict.
        """
        _logger.info(
            'DivaBridge.submit_action: type=%s payload_keys=%s',
            action_type,
            list(payload.keys()),
        )
        return {
            'action_type': action_type,
            'status': 'queued',
            'message': 'Action submitted (stub)',
        }
