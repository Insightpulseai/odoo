#!/usr/bin/env python3
"""Audit envelope creation and validation for governed tool use.

Every copilot tool execution must emit an audit envelope containing:
  trace_id, user_id, timestamp, tool_name, tool_args, result_status, duration_ms

This module provides:
- create_envelope(): build a single envelope dict
- validate_envelope(): check required fields
- AuditEnvelopeEmitter: batch emitter with file sink
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any


REQUIRED_FIELDS = [
    "trace_id",
    "user_id",
    "timestamp",
    "tool_name",
    "tool_args",
    "result_status",
    "duration_ms",
]


def create_envelope(
    tool_name: str,
    tool_args: dict[str, Any],
    result_status: str,
    duration_ms: int,
    user_id: int,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Create a single audit envelope dict."""
    return {
        "trace_id": trace_id or str(uuid.uuid4()),
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "tool_args": tool_args,
        "result_status": result_status,
        "duration_ms": duration_ms,
    }


def validate_envelope(envelope: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate that an envelope has all required fields with non-null values.

    Returns:
        (is_valid, list_of_errors)
    """
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in envelope:
            errors.append(f"missing field: {field}")
        elif envelope[field] is None:
            errors.append(f"null value: {field}")
    return (len(errors) == 0, errors)


class AuditEnvelopeEmitter:
    """Batch emitter that collects envelopes and writes them to a JSON file."""

    def __init__(self, sink_dir: str | None = None):
        self._envelopes: list[dict] = []
        self._sink_dir = sink_dir

    def emit(self, **kwargs) -> dict[str, Any]:
        """Create and store an envelope. Returns the envelope."""
        envelope = create_envelope(**kwargs)
        self._envelopes.append(envelope)
        return envelope

    def flush(self) -> str | None:
        """Write all collected envelopes to sink_dir/envelopes.json."""
        if not self._sink_dir or not self._envelopes:
            return None
        os.makedirs(self._sink_dir, exist_ok=True)
        path = os.path.join(self._sink_dir, "envelopes.json")
        with open(path, "w") as f:
            json.dump(self._envelopes, f, indent=2)
        return path
