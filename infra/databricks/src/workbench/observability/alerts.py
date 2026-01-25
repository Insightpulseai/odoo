"""Alerting utilities for data quality and pipeline failures."""

from __future__ import annotations

import json
from typing import Any

import httpx

from workbench.config.logging import get_logger

logger = get_logger(__name__)


def send_alert(
    webhook_url: str,
    title: str,
    message: str,
    severity: str = "warning",
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Send an alert via webhook (Slack/Teams compatible).

    Args:
        webhook_url: Webhook URL to POST to
        title: Alert title
        message: Alert message body
        severity: Alert severity (info, warning, error, critical)
        metadata: Additional metadata to include

    Returns:
        True if alert was sent successfully
    """
    severity_colors = {
        "info": "#36a64f",
        "warning": "#ffcc00",
        "error": "#ff6600",
        "critical": "#ff0000",
    }

    color = severity_colors.get(severity, "#808080")

    # Build Slack-compatible payload
    payload = {
        "attachments": [
            {
                "color": color,
                "title": title,
                "text": message,
                "fields": [],
            }
        ]
    }

    if metadata:
        for key, value in metadata.items():
            payload["attachments"][0]["fields"].append(
                {"title": key, "value": str(value), "short": True}
            )

    try:
        response = httpx.post(webhook_url, json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info(f"Alert sent: {title}")
        return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to send alert: {e}")
        return False


def send_dq_alert(
    webhook_url: str,
    table_name: str,
    check_name: str,
    failed_rows: int,
    total_rows: int,
    threshold: float,
) -> bool:
    """Send a data quality alert.

    Args:
        webhook_url: Webhook URL
        table_name: Name of the table with issues
        check_name: Name of the failed check
        failed_rows: Number of rows that failed
        total_rows: Total number of rows checked
        threshold: Allowed failure threshold

    Returns:
        True if alert was sent
    """
    failure_pct = (failed_rows / total_rows * 100) if total_rows > 0 else 0
    severity = "error" if failure_pct > threshold * 2 else "warning"

    return send_alert(
        webhook_url=webhook_url,
        title=f"Data Quality Alert: {table_name}",
        message=f"Check `{check_name}` failed with {failure_pct:.2f}% failures (threshold: {threshold}%)",
        severity=severity,
        metadata={
            "Table": table_name,
            "Check": check_name,
            "Failed Rows": failed_rows,
            "Total Rows": total_rows,
            "Failure %": f"{failure_pct:.2f}%",
        },
    )


def send_pipeline_alert(
    webhook_url: str,
    pipeline_name: str,
    status: str,
    error_message: str | None = None,
    run_id: str | None = None,
) -> bool:
    """Send a pipeline status alert.

    Args:
        webhook_url: Webhook URL
        pipeline_name: Name of the pipeline
        status: Pipeline status (success, failed, etc.)
        error_message: Error message if failed
        run_id: Pipeline run ID

    Returns:
        True if alert was sent
    """
    severity = "error" if status == "failed" else "info"
    message = f"Pipeline `{pipeline_name}` finished with status: {status}"
    if error_message:
        message += f"\nError: {error_message}"

    metadata: dict[str, Any] = {"Pipeline": pipeline_name, "Status": status}
    if run_id:
        metadata["Run ID"] = run_id

    return send_alert(
        webhook_url=webhook_url,
        title=f"Pipeline Alert: {pipeline_name}",
        message=message,
        severity=severity,
        metadata=metadata,
    )
