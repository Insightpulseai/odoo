# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

"""Calendar tools for AI agents.

These functions are called by the AI Agent tool executor.
"""

import logging
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def create_event(env, input_data, dry_run=False):
    """Create a new calendar event.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - name (required): Event title
            - start (required): Start datetime (ISO format or datetime)
            - stop (required): End datetime (ISO format or datetime)
            - description: Event description
            - location: Event location
            - attendee_emails: List of attendee emails
            - partner_ids: List of partner IDs to invite
            - allday: Whether this is an all-day event
        dry_run: If True, validate but don't create

    Returns:
        dict with event_id, name, and message
    """
    Event = env["calendar.event"]

    # Validate required fields
    if not input_data.get("name"):
        raise ValidationError("Event name is required.")
    if not input_data.get("start"):
        raise ValidationError("Start datetime is required.")
    if not input_data.get("stop"):
        raise ValidationError("Stop datetime is required.")

    # Parse dates
    start = _parse_datetime(input_data["start"])
    stop = _parse_datetime(input_data["stop"])

    if stop <= start:
        raise ValidationError("End time must be after start time.")

    # Prepare values
    values = {
        "name": input_data["name"],
        "start": start,
        "stop": stop,
    }

    if input_data.get("description"):
        values["description"] = input_data["description"]
    if input_data.get("location"):
        values["location"] = input_data["location"]
    if input_data.get("allday"):
        values["allday"] = True

    # Handle attendees
    partner_ids = list(input_data.get("partner_ids", []))

    # Look up partners by email
    if input_data.get("attendee_emails"):
        Partner = env["res.partner"]
        for email in input_data["attendee_emails"]:
            partner = Partner.search([("email", "=ilike", email)], limit=1)
            if partner:
                partner_ids.append(partner.id)
            else:
                _logger.warning(f"No partner found for email: {email}")

    if partner_ids:
        values["partner_ids"] = [(6, 0, partner_ids)]

    if dry_run:
        _logger.info(f"[DRY RUN] Would create event: {values}")
        return {
            "dry_run": True,
            "would_create": {
                "name": values["name"],
                "start": str(values["start"]),
                "stop": str(values["stop"]),
                "partner_count": len(partner_ids),
            },
            "message": f"Would create event: {values['name']}",
        }

    # Create the event
    event = Event.create(values)
    _logger.info(f"Created event {event.id}: {event.name}")

    return {
        "event_id": event.id,
        "name": event.name,
        "start": str(event.start),
        "stop": str(event.stop),
        "message": f"Successfully created event: {event.name}",
    }


def update_event(env, input_data, dry_run=False):
    """Update an existing calendar event.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - event_id (required): ID of event to update
            - name: New event name
            - start: New start datetime
            - stop: New stop datetime
            - description: Updated description
            - location: Updated location
        dry_run: If True, validate but don't update

    Returns:
        dict with event_id and message
    """
    Event = env["calendar.event"]

    event_id = input_data.get("event_id")
    if not event_id:
        raise ValidationError("event_id is required.")

    event = Event.browse(event_id)
    if not event.exists():
        raise ValidationError(f"Event {event_id} not found.")

    # Prepare update values
    values = {}
    if input_data.get("name"):
        values["name"] = input_data["name"]
    if input_data.get("start"):
        values["start"] = _parse_datetime(input_data["start"])
    if input_data.get("stop"):
        values["stop"] = _parse_datetime(input_data["stop"])
    if input_data.get("description"):
        values["description"] = input_data["description"]
    if input_data.get("location"):
        values["location"] = input_data["location"]

    if not values:
        return {
            "event_id": event_id,
            "message": "No fields to update.",
        }

    if dry_run:
        _logger.info(f"[DRY RUN] Would update event {event_id}: {values}")
        return {
            "dry_run": True,
            "event_id": event_id,
            "would_update": {k: str(v) for k, v in values.items()},
            "message": f"Would update event {event_id}",
        }

    event.write(values)
    _logger.info(f"Updated event {event_id}")

    return {
        "event_id": event_id,
        "name": event.name,
        "message": f"Successfully updated event: {event.name}",
    }


def search_events(env, input_data, dry_run=False):
    """Search for calendar events.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - query: Search query (searches name)
            - start_from: Only events starting after this datetime
            - start_until: Only events starting before this datetime
            - limit: Maximum results (default 10)
        dry_run: Ignored for search operations

    Returns:
        dict with events list
    """
    Event = env["calendar.event"]

    domain = []
    query = input_data.get("query", "")
    if query:
        domain.append(("name", "ilike", query))

    if input_data.get("start_from"):
        domain.append(("start", ">=", _parse_datetime(input_data["start_from"])))
    if input_data.get("start_until"):
        domain.append(("start", "<=", _parse_datetime(input_data["start_until"])))

    limit = min(input_data.get("limit", 10), 50)
    events = Event.search(domain, limit=limit, order="start asc")

    return {
        "count": len(events),
        "events": [
            {
                "id": event.id,
                "name": event.name,
                "start": str(event.start),
                "stop": str(event.stop),
                "location": event.location,
                "allday": event.allday,
            }
            for event in events
        ],
    }


def _parse_datetime(value):
    """Parse datetime from various formats.

    Args:
        value: datetime object, ISO string, or relative description

    Returns:
        datetime object
    """
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        # Try ISO format
        for fmt in [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Handle relative descriptions
        value_lower = value.lower()
        now = datetime.now()
        if value_lower == "now":
            return now
        if value_lower == "tomorrow":
            return now + timedelta(days=1)
        if "hour" in value_lower:
            # Extract number
            import re
            match = re.search(r"(\d+)", value)
            if match:
                hours = int(match.group(1))
                if "ago" in value_lower:
                    return now - timedelta(hours=hours)
                return now + timedelta(hours=hours)

    raise ValidationError(f"Could not parse datetime: {value}")
