"""
Tool contract validators for agent tool calling.
"""

import json
from typing import Any, Dict, Tuple, Optional


def tool_contract_valid(
    tool_call: Dict[str, Any], schema: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validate tool call matches expected schema.

    Args:
        tool_call: The tool call dictionary
        schema: Expected schema with 'required' and 'properties' fields

    Returns:
        (success, message) tuple
    """
    try:
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in tool_call:
                return False, f"Missing required field: {field}"

        # Check field types if properties defined
        properties = schema.get("properties", {})
        for field, value in tool_call.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not _type_matches(value, expected_type):
                    return (
                        False,
                        f"Field '{field}' has wrong type: expected {expected_type}",
                    )

        return True, "Tool contract valid"

    except Exception as e:
        return False, f"Contract validation error: {e}"


def _type_matches(value: Any, expected_type: str) -> bool:
    """Check if value matches expected JSON Schema type."""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    expected = type_map.get(expected_type)
    if expected is None:
        return True  # Unknown type, allow
    return isinstance(value, expected)


def schema_validate(
    data: Dict[str, Any], schema: Dict[str, Any], strict: bool = False
) -> Tuple[bool, str]:
    """
    Validate data against a JSON Schema-like definition.

    Args:
        data: Data to validate
        schema: Schema definition
        strict: If True, reject unknown fields

    Returns:
        (success, message) tuple
    """
    try:
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"

        properties = schema.get("properties", {})

        # Check for unknown fields in strict mode
        if strict:
            unknown = set(data.keys()) - set(properties.keys())
            if unknown:
                return False, f"Unknown fields in strict mode: {unknown}"

        # Validate each field
        for field, value in data.items():
            if field not in properties:
                continue

            field_schema = properties[field]

            # Type check
            expected_type = field_schema.get("type")
            if expected_type and not _type_matches(value, expected_type):
                return (
                    False,
                    f"Field '{field}' type mismatch: expected {expected_type}",
                )

            # Enum check
            enum_values = field_schema.get("enum")
            if enum_values and value not in enum_values:
                return False, f"Field '{field}' value not in enum: {enum_values}"

            # Min/max for numbers
            if isinstance(value, (int, float)):
                minimum = field_schema.get("minimum")
                maximum = field_schema.get("maximum")
                if minimum is not None and value < minimum:
                    return False, f"Field '{field}' below minimum: {minimum}"
                if maximum is not None and value > maximum:
                    return False, f"Field '{field}' above maximum: {maximum}"

            # Pattern for strings
            if isinstance(value, str):
                pattern = field_schema.get("pattern")
                if pattern:
                    import re

                    if not re.match(pattern, value):
                        return False, f"Field '{field}' doesn't match pattern: {pattern}"

        return True, "Schema validation passed"

    except Exception as e:
        return False, f"Schema validation error: {e}"


def validate_mcp_tool_response(
    response: Dict[str, Any], expected_tool: str
) -> Tuple[bool, str]:
    """
    Validate MCP server tool response format.

    Args:
        response: MCP tool response
        expected_tool: Expected tool name

    Returns:
        (success, message) tuple
    """
    # MCP responses typically have content and tool info
    if "content" not in response and "result" not in response:
        return False, "MCP response missing content/result field"

    if "tool" in response and response["tool"] != expected_tool:
        return (
            False,
            f"Tool mismatch: expected {expected_tool}, got {response['tool']}",
        )

    # Check for error indicators
    if response.get("error"):
        return False, f"MCP tool returned error: {response['error']}"

    return True, "MCP tool response valid"


def validate_openapi_tool_call(
    tool_call: Dict[str, Any], openapi_spec: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validate tool call against OpenAPI specification.

    Args:
        tool_call: Tool call with 'operation_id' and 'parameters'
        openapi_spec: OpenAPI spec dictionary

    Returns:
        (success, message) tuple
    """
    operation_id = tool_call.get("operation_id")
    if not operation_id:
        return False, "Tool call missing operation_id"

    # Find operation in spec
    paths = openapi_spec.get("paths", {})
    found_operation = None

    for path, methods in paths.items():
        for method, operation in methods.items():
            if isinstance(operation, dict) and operation.get("operationId") == operation_id:
                found_operation = operation
                break

    if not found_operation:
        return False, f"Operation '{operation_id}' not found in OpenAPI spec"

    # Validate required parameters
    parameters = found_operation.get("parameters", [])
    provided_params = tool_call.get("parameters", {})

    for param in parameters:
        if param.get("required", False):
            param_name = param.get("name")
            if param_name not in provided_params:
                return False, f"Missing required parameter: {param_name}"

    return True, "OpenAPI tool call valid"
