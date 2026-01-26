# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging
import time

from odoo import models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class IpaiAiToolExecutor(models.AbstractModel):
    """Service for executing tools with permission checking and audit logging."""

    _name = "ipai.ai.tool.executor"
    _description = "IPAI AI Tool Executor"

    def execute(self, run, tool_key, input_json, dry_run=False):
        """Execute a tool and log the result.

        Args:
            run: The ipai.ai.run record
            tool_key: The unique key of the tool to execute
            input_json: Input parameters (dict or JSON string)
            dry_run: Whether to execute in dry-run mode

        Returns:
            dict with status, output, and tool_call record
        """
        # Find the tool
        tool = self.env["ipai.ai.tool"].search([("key", "=", tool_key)], limit=1)
        if not tool:
            return self._create_error_result(run, tool_key, f"Tool not found: {tool_key}")

        # Parse input if string
        if isinstance(input_json, str):
            try:
                input_json = json.loads(input_json)
            except json.JSONDecodeError as e:
                return self._create_error_result(run, tool_key, f"Invalid JSON input: {e}")

        # Permission check
        if not tool.check_permission():
            return self._create_error_result(
                run, tool_key,
                f"Permission denied for tool: {tool_key}",
                tool_id=tool.id,
            )

        # Dry run check
        if dry_run and not tool.dry_run_supported:
            return self._create_error_result(
                run, tool_key,
                f"Tool does not support dry-run: {tool_key}",
                tool_id=tool.id,
            )

        # Create tool call record
        tool_call = self.env["ipai.ai.tool.call"].create({
            "run_id": run.id,
            "tool_id": tool.id,
            "input_json": json.dumps(input_json),
            "status": "pending",
            "dry_run": dry_run,
        })

        # Log event
        run.log_event("tool", {
            "tool_key": tool_key,
            "input": input_json,
            "dry_run": dry_run,
        })

        # Execute tool
        start_time = time.time()
        try:
            output = tool.execute(self.env, input_json, dry_run=dry_run)
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Update tool call record
            tool_call.write({
                "output_json": json.dumps(output) if output else None,
                "status": "dry_run" if dry_run else "success",
                "execution_time_ms": execution_time_ms,
            })

            _logger.info(
                f"Tool executed: {tool_key}, "
                f"user={self.env.uid}, "
                f"dry_run={dry_run}, "
                f"time={execution_time_ms}ms"
            )

            return {
                "status": "dry_run" if dry_run else "success",
                "output": output,
                "tool_call_id": tool_call.id,
                "execution_time_ms": execution_time_ms,
            }

        except (AccessError, ValidationError) as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            tool_call.write({
                "status": "error",
                "error_message": str(e),
                "execution_time_ms": execution_time_ms,
            })
            _logger.warning(f"Tool execution failed: {tool_key}, error={e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_call_id": tool_call.id,
                "execution_time_ms": execution_time_ms,
            }
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            tool_call.write({
                "status": "error",
                "error_message": str(e),
                "execution_time_ms": execution_time_ms,
            })
            _logger.exception(f"Tool execution error: {tool_key}")
            return {
                "status": "error",
                "error": str(e),
                "tool_call_id": tool_call.id,
                "execution_time_ms": execution_time_ms,
            }

    def _create_error_result(self, run, tool_key, error_message, tool_id=None):
        """Create an error result and log it.

        Args:
            run: The ipai.ai.run record
            tool_key: The tool key
            error_message: The error message
            tool_id: Optional tool ID if found

        Returns:
            dict with error status
        """
        # Create tool call record if we have a tool
        tool_call = None
        if tool_id:
            tool_call = self.env["ipai.ai.tool.call"].create({
                "run_id": run.id,
                "tool_id": tool_id,
                "status": "error",
                "error_message": error_message,
            })

        run.log_event("tool", {
            "tool_key": tool_key,
            "error": error_message,
        })

        return {
            "status": "error",
            "error": error_message,
            "tool_call_id": tool_call.id if tool_call else None,
        }
