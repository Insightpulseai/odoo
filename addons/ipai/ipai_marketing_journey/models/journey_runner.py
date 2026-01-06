# -*- coding: utf-8 -*-
"""Marketing Journey Runner - cron-based execution engine."""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MarketingJourneyRunner(models.AbstractModel):
    """Runner service for executing marketing journeys."""

    _name = "marketing.journey.runner"
    _description = "Marketing Journey Runner"

    @api.model
    def run_all_journeys(self):
        """
        Cron entry point: process all running journeys.

        This method is called by the scheduled action to:
        1. Enroll new participants in running journeys
        2. Process participants ready for next step
        """
        journeys = self.env["marketing.journey"].search([("state", "=", "running")])
        _logger.info("Processing %d running journeys", len(journeys))

        for journey in journeys:
            try:
                self._process_journey(journey)
            except Exception as e:
                _logger.error("Error processing journey %s: %s", journey.name, str(e))

        return True

    def _process_journey(self, journey):
        """Process a single journey."""
        # 1. Enroll new participants
        enrolled = self.enroll_participants(journey)
        if enrolled:
            _logger.info("Journey %s: enrolled %d new participants", journey.name, enrolled)

        # 2. Process participants ready for next step
        processed = self.process_ready_participants(journey)
        if processed:
            _logger.info("Journey %s: processed %d participants", journey.name, processed)

        # Update last run timestamp
        journey.write({"last_run": fields.Datetime.now()})

    @api.model
    def enroll_participants(self, journey):
        """
        Enroll new participants matching journey criteria.

        Args:
            journey: marketing.journey record

        Returns:
            int: number of newly enrolled participants
        """
        if journey.state != "running":
            return 0

        # Get target model
        Model = self.env[journey.model_id.model]

        # Parse domain
        domain = eval(journey.domain or "[]")

        # Find existing participant record IDs
        existing_ids = set(
            journey.participant_ids.filtered(
                lambda p: p.res_model == journey.model_id.model
            ).mapped("res_id")
        )

        # Find eligible records not yet enrolled
        candidates = Model.search(domain)
        new_records = candidates.filtered(lambda r: r.id not in existing_ids)

        # Get entry node
        entry_node = journey.get_entry_node()
        if not entry_node:
            _logger.warning("Journey %s has no entry node", journey.name)
            return 0

        # Create participants
        Participant = self.env["marketing.journey.participant"]
        count = 0

        for record in new_records:
            try:
                participant = Participant.create_from_record(journey, record)
                # Set to entry node and mark as in_progress
                participant.write({
                    "current_node_id": entry_node.id,
                    "state": "in_progress",
                })
                count += 1
            except Exception as e:
                _logger.error(
                    "Failed to enroll record %s/%s: %s",
                    record._name, record.id, str(e)
                )

        return count

    @api.model
    def process_ready_participants(self, journey):
        """
        Process participants ready for their next step.

        Args:
            journey: marketing.journey record

        Returns:
            int: number of participants processed
        """
        if journey.state != "running":
            return 0

        # Find participants ready to process
        now = fields.Datetime.now()
        participants = journey.participant_ids.filtered(
            lambda p: p.state in ("enrolled", "in_progress", "waiting")
            and (not p.wait_until or p.wait_until <= now)
        )

        count = 0
        for participant in participants:
            try:
                if self.process_participant(participant):
                    count += 1
            except Exception as e:
                _logger.error(
                    "Error processing participant %s: %s",
                    participant.id, str(e)
                )
                participant.write({
                    "state": "error",
                    "error_message": str(e),
                })

        return count

    @api.model
    def process_participant(self, participant):
        """
        Process a single participant's current node and advance.

        Args:
            participant: marketing.journey.participant record

        Returns:
            bool: True if successfully processed
        """
        if not participant.is_ready_to_process():
            return False

        node = participant.current_node_id
        if not node:
            # No current node - find entry
            node = participant.journey_id.get_entry_node()
            if not node:
                participant.write({
                    "state": "error",
                    "error_message": "No entry node found",
                })
                return False
            participant.write({"current_node_id": node.id})

        # Execute current node
        result = node.execute(participant)

        # Log execution
        self.env["marketing.journey.execution.log"].log_execution(
            participant, node, result
        )

        if not result.get("success"):
            participant.write({
                "state": "error",
                "error_message": result.get("error", "Unknown error"),
            })
            return False

        # If waiting (delay node), stop here
        if participant.state == "waiting":
            return True

        # If completed (exit node), stop here
        if participant.state == "completed":
            participant.write({"completed_date": fields.Datetime.now()})
            return True

        # Advance to next node
        next_nodes = node.get_next_nodes(participant)
        if next_nodes:
            next_node = next_nodes[0]  # Take first (for branching, already filtered)
            participant.write({
                "current_node_id": next_node.id,
                "last_action_date": fields.Datetime.now(),
                "state": "in_progress",
            })
            # Recursively process next node immediately (unless it's a delay)
            if next_node.node_type != "delay":
                return self.process_participant(participant)
        else:
            # No next node - journey complete
            participant.write({
                "state": "completed",
                "completed_date": fields.Datetime.now(),
            })

        return True
